import os
import csv
from datetime import datetime
import uuid

def create_ticket_tool(domain: str, request_type: str, risk_level: str, issue_description: str) -> str:
    """
    Logs an escalated issue to a CSV file and returns a unique Ticket ID.
    """
    ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.now().isoformat()
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tickets_dir = os.path.join(base_dir, "support_tickets")
    os.makedirs(tickets_dir, exist_ok=True)
    
    csv_file = os.path.join(tickets_dir, "support_tickets.csv")
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Ticket ID", "Timestamp", "Domain", "Request Type", "Risk Level", "Issue Description"])
        writer.writerow([ticket_id, timestamp, domain, request_type, risk_level, issue_description])
        
    return ticket_id
