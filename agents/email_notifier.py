import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_task_email(agent_name: str, task_description: str, result: str):
    """
    Sends an email after an agent completes a task.
    """
    try:
        message = Mail(
            from_email=os.getenv("SENDGRID_FROM_EMAIL"),
            to_emails=os.getenv("SENDGRID_TO_EMAIL"),
            subject=f"[Lincoln Agency] {agent_name} completed a task",
            plain_text_content=f"""
            Agent: {agent_name}
            Task: {task_description}
            Result:
            {result}
            """
        )
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        sg.send(message)
        print(f"✅ Email sent for {agent_name}'s task.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
