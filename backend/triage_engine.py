import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field

from tools import create_ticket_tool

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path, override=True)

# ---------------------------------------------------------------------------
# LLM Initialization with Fallback Support
# ---------------------------------------------------------------------------
def get_llm(model_name="gemini-1.5-flash"):
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.0,
        request_timeout=30,
        max_retries=1,
        api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    )

# Primary LLM
llm = get_llm("gemini-1.5-flash")

class TriageOutput(BaseModel):
    domain: str = Field(description="HackerRank | Claude | Visa")
    request_type: str = Field(description="Detected category (e.g. Billing, Login, Fraud, Bugs, General Inquiry, etc.)")
    risk_level: str = Field(description="LOW | MEDIUM | HIGH")
    action: str = Field(description="RESPOND | ESCALATE")
    response: str = Field(description="User-facing reply or escalation note")

# We'll use structured output on the primary LLM
structured_llm = llm.with_structured_output(TriageOutput)

# Fallback models (used if primary fails)
FALLBACK_MODELS = ["gemini-1.5-pro", "gemini-2.0-flash-exp", "gemini-2.0-flash-lite"]

# ---------------------------------------------------------------------------
# Vector Store
# ---------------------------------------------------------------------------
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
persist_dir = os.path.join(base_dir, "data", "chroma_db")
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
)

if os.path.exists(persist_dir):
    vector_store = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
else:
    vector_store = None
    print("Warning: Chroma DB not found at", persist_dir)

SYSTEM_PROMPT_TEMPLATE = """You are a Support Triage AI. 
Analyze the user's message and the provided context.

## TASKS:
1. Classify the **domain** (HackerRank, Claude, Visa, or UNKNOWN).
2. Identify the **request_type** (Billing, Login, Technical, Fraud, etc.).
3. Assess **risk_level** (LOW, MEDIUM, HIGH).
4. Decide **action** (RESPOND if you have a clear answer from context, ESCALATE otherwise).
5. Generate a **response** based ONLY on the context below.

## RULES:
- If risk_level is HIGH, action must be ESCALATE.
- If context is insufficient, action must be ESCALATE.
- Be professional and concise.

<context>
{retrieved_context}
</context>
"""

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    domain: str
    request_type: str
    risk_level: str
    action: str
    response: str
    ticket_id: str

def triage_node(state: AgentState):
    # --- STEP 1: Call Gemini (Classification + Response) ---
    latest_msg = state["messages"][-1].content if state["messages"] else ""
    
    # Context Retrieval
    retrieved_context = "No relevant information found."
    context_found = False
    if vector_store:
        try:
            docs = vector_store.similarity_search(latest_msg, k=2)
            if docs:
                retrieved_context = "\n\n".join([d.page_content for d in docs])
                context_found = True
        except Exception:
            pass

    prompt = SYSTEM_PROMPT_TEMPLATE.format(retrieved_context=retrieved_context)
    messages_for_llm = [SystemMessage(content=prompt)] + state["messages"]

    # --- STEP 2: Handle errors/fallbacks properly ---
    result = None
    try:
        result = structured_llm.invoke(messages_for_llm)
    except Exception as e:
        print(f"Primary model failed: {e}")
        for model_name in FALLBACK_MODELS:
            try:
                fallback_llm = get_llm(model_name).with_structured_output(TriageOutput)
                result = fallback_llm.invoke(messages_for_llm)
                if result: break
            except Exception:
                continue

    if not result:
        error_msg = "The AI model failed to process your request."
        return {
            "domain": "ERROR", 
            "request_type": "System Error", 
            "risk_level": "HIGH",
            "action": "ESCALATE", 
            "response": f"I encountered a technical issue while processing your request. Escalating to support. (Reason: Model Failure)",
            "ticket_id": None
        }

    # --- STEP 3: Decide escalation (rules) ---
    final_action = result.action
    final_response = result.response

    # Rule 1: High risk always escalates
    if result.risk_level == "HIGH":
        final_action = "ESCALATE"
    
    # Rule 2: No context found for known domains should escalate
    if not context_found and result.domain != "UNKNOWN" and result.domain != "ERROR":
        final_action = "ESCALATE"
        if final_action != result.action:
            final_response = f"I'm escalating this to our support team as I couldn't find specific documentation for your {result.domain} request."

    # --- STEP 4: Return clean response ---
    return {
        "domain": result.domain,
        "request_type": result.request_type,
        "risk_level": result.risk_level,
        "action": final_action,
        "response": final_response,
        "ticket_id": None
    }

def route_action(state: AgentState) -> Literal["escalate_node", "__end__"]:
    if state.get("action") == "ESCALATE":
        return "escalate_node"
    return "__end__"

def escalate_node(state: AgentState):
    latest_msg = state["messages"][-1].content if state["messages"] else "Unknown issue"
    ticket_id = create_ticket_tool(
        domain=state.get("domain", "UNKNOWN"),
        request_type=state.get("request_type", "UNKNOWN"),
        risk_level=state.get("risk_level", "HIGH"),
        issue_description=latest_msg
    )
    new_response = state.get("response", "") + f" (Ticket ID: {ticket_id})"
    return {
        "ticket_id": ticket_id,
        "response": new_response,
        "messages": [AIMessage(content=new_response)]
    }

def finalize_response_node(state: AgentState):
    return {
        "messages": [AIMessage(content=state.get("response", ""))]
    }

# Build Graph
builder = StateGraph(AgentState)
builder.add_node("triage_node", triage_node)
builder.add_node("escalate_node", escalate_node)
builder.add_node("finalize_response_node", finalize_response_node)

builder.add_edge(START, "triage_node")
builder.add_conditional_edges(
    "triage_node",
    route_action,
    {"escalate_node": "escalate_node", "__end__": "finalize_response_node"}
)
builder.add_edge("escalate_node", END)
builder.add_edge("finalize_response_node", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

def process_chat(message: str, session_id: str = "default") -> dict:
    config = {"configurable": {"thread_id": session_id}}
    try:
        result = graph.invoke({"messages": [HumanMessage(content=message)]}, config)
        return {
            "domain": result.get("domain", "ERROR"),
            "request_type": result.get("request_type", "ERROR"),
            "risk_level": result.get("risk_level", "ERROR"),
            "action": result.get("action", "ERROR"),
            "response": result.get("response", "Internal Error"),
            "ticket_id": result.get("ticket_id", None)
        }
    except Exception as e:
        return {
            "domain": "ERROR",
            "request_type": "Internal Error",
            "risk_level": "HIGH",
            "action": "ESCALATE",
            "response": f"Service error: {str(e)[:120]}",
            "ticket_id": None
        }
