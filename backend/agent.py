import os
import pandas as pd
from triage_engine import process_chat

def process_tickets(input_csv=None, output_csv=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if input_csv is None:
        input_csv = os.path.join(base_dir, "support_tickets", "sample_support_tickets.csv")
    if output_csv is None:
        output_csv = os.path.join(base_dir, "support_tickets", "output.csv")
        
    df = pd.read_csv(input_csv)
    results = []
    
    for index, row in df.iterrows():
        issue = str(row.get("issue", ""))
        subject = str(row.get("subject", ""))
        company = str(row.get("company", "None"))
        
        user_message = f"Company: {company}\nSubject: {subject}\nIssue: {issue}"
        print(f"Processing ticket {index+1}/{len(df)}...")
        
        try:
            response = process_chat(user_message)
            results.append({
                "issue": issue,
                "subject": subject,
                "company": company,
                "domain": response["domain"],
                "request_type": response["request_type"],
                "risk_level": response["risk_level"],
                "action": response["action"],
                "response": response["response"]
            })
        except Exception as e:
            print(f"Error processing ticket {index+1}: {e}")
            results.append({
                "issue": issue,
                "subject": subject,
                "company": company,
                "domain": "ERROR",
                "request_type": "ERROR",
                "risk_level": "ERROR",
                "action": "ERROR",
                "response": str(e)
            })
            
        import time
        time.sleep(4)  # Prevent rate limits for free tier

    out_df = pd.DataFrame(results)
    out_df.to_csv(output_csv, index=False)
    print(f"Successfully processed {len(df)} tickets. Output saved to {output_csv}.")

if __name__ == "__main__":
    process_tickets()
