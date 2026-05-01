import sys
print("Step 1")
import os
from dotenv import load_dotenv
print("Step 2")
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
print("Step 3")
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
print("Step 4")
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
print("Step 5")
from tools import create_ticket_tool
print("Step 6")
load_dotenv()
print("Step 7")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.0
)
print("Step 8")
class TriageOutput(BaseModel):
    domain: str = Field(description="HackerRank | Claude | Visa")
    request_type: str = Field(description="Detected category")
    risk_level: str = Field(description="LOW | MEDIUM | HIGH")
    action: str = Field(description="RESPOND | ESCALATE")
    response: str = Field(description="User-facing reply")
print("Step 9")
structured_llm = llm.with_structured_output(TriageOutput)
print("Step 10")
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
persist_dir = os.path.join(base_dir, "data", "chroma_db")
print("Step 11")
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
print("Step 12")
if os.path.exists(persist_dir):
    print("Step 13")
    vector_store = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    print("Step 14")
else:
    vector_store = None
    print("Step 15")
print("Done")
