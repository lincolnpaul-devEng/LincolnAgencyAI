#!/usr/bin/env python3
"""
Outreach Agent - Personalizes cold emails using recipient data
Part of Lincoln Agency multi-agent system
"""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import os
from .gemini_adapter import AIClient
from .email_notifier import send_task_email



# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user

class OutreachAgent:
    def __init__(self):
        self.name = "OutreachAgent"
        self.status = "idle"
        self.logger = self._setup_logging()
        self.client = AIClient()

        
    def _setup_logging(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        
        Path("data/logs").mkdir(parents=True, exist_ok=True)
        
        handler = logging.FileHandler(f"data/logs/{self.name.lower()}.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
        
    async def personalize_email(self, recipient_info: dict, email_template: str, campaign_goal: str):
        """Personalize cold email based on recipient information"""
        self.status = "working"
        self.logger.info(f"Personalizing email for: {recipient_info.get('name', 'unknown')}")
        
        try:
            prompt = f"""
            Personalize this cold email template for Lincoln Agency based on the recipient's information:
            
            Recipient Info: {json.dumps(recipient_info)}
            Email Template: {email_template}
            Campaign Goal: {campaign_goal}
            
            Requirements:
            1. Personalize the greeting and opening
            2. Reference specific details about their business/role
            3. Show genuine understanding of their challenges
            4. Tailor the value proposition to their needs
            5. Include relevant case studies or examples
            6. Professional yet personable tone
            
            Format as JSON with: subject, personalized_email, personalization_notes
            """
            
            response = await asyncio.to_thread(
                self.client.client.chat.completions.create,
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            content_text = response.choices[0].message.content
            if not content_text:
                raise ValueError("No personalized email content received from OpenAI")
            personalized_email = json.loads(content_text)
            
            output_data = {
                "agent": self.name,
                "type": "personalized_email",
                "timestamp": datetime.now().isoformat(),
                "recipient_info": recipient_info,
                "campaign_goal": campaign_goal,
                "email": personalized_email
            }
            
            await self._save_to_queue(output_data)
            self.logger.info("Email personalized successfully")
            self.status = "idle"

            
             # 📧 Send email after task completion
            send_task_email(
                self.name,
                f"Personalized email for {recipient_info.get('name', 'Unnamed')}",
                json.dumps(personalized_email, indent=2)
            )
            return personalized_email
            
        except Exception as e:
            self.logger.error(f"Error personalizing email: {str(e)}")
            self.status = "error"
            raise
    
    async def _save_to_queue(self, data):
        """Save output to the queue system"""
        Path("data/queue").mkdir(parents=True, exist_ok=True)
        filename = f"data/queue/outreach_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def run_continuously(self):
        """Run the agent in continuous mode"""
        self.logger.info("OutreachAgent started in continuous mode")
        
        while True:
            try:
                self.status = "monitoring"
                await asyncio.sleep(50)
                
            except Exception as e:
                self.logger.error(f"Error in continuous mode: {str(e)}")
                await asyncio.sleep(15)
    
    def get_status(self):
        return {
            "name": self.name,
            "status": self.status,
            "last_active": datetime.now().isoformat()
        }