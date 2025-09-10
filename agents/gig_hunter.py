#!/usr/bin/env python3
"""
Gig Hunter Agent - Drafts proposals for freelance/contract opportunities
Part of Lincoln Agency multi-agent system
"""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import os
from openai import OpenAI

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user

class GigHunterAgent:
    def __init__(self):
        self.name = "GigHunter"
        self.status = "idle"
        self.logger = self._setup_logging()
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
    def _setup_logging(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        Path("data/logs").mkdir(parents=True, exist_ok=True)
        
        handler = logging.FileHandler(f"data/logs/{self.name.lower()}.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
        
    async def generate_proposal(self, job_description: str, client_info: dict | None = None):
        """Generate a tailored proposal based on job description and client info"""
        self.status = "working"
        self.logger.info(f"Generating proposal for job: {job_description[:100]}...")
        
        try:
            prompt = f"""
            As an expert proposal writer for Lincoln Agency, create a compelling freelance proposal for this job:
            
            Job Description: {job_description}
            Client Info: {json.dumps(client_info or {}) if client_info else "Not provided"}
            
            Create a professional, personalized proposal that:
            1. Addresses the client's specific needs
            2. Highlights relevant Lincoln Agency expertise
            3. Provides clear project approach
            4. Includes realistic timeline and deliverables
            5. Shows understanding of the industry/niche
            
            Format the response as JSON with fields: title, introduction, approach, timeline, pricing_notes, closing
            """
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("No content received from OpenAI")
            proposal = json.loads(content)
            
            # Save to queue
            output_data = {
                "agent": self.name,
                "type": "proposal",
                "timestamp": datetime.now().isoformat(),
                "job_description": job_description,
                "proposal": proposal
            }
            
            await self._save_to_queue(output_data)
            self.logger.info("Proposal generated successfully")
            self.status = "idle"
            return proposal
            
        except Exception as e:
            self.logger.error(f"Error generating proposal: {str(e)}")
            self.status = "error"
            raise
    
    async def _save_to_queue(self, data):
        """Save output to the queue system"""
        Path("data/queue").mkdir(parents=True, exist_ok=True)
        filename = f"data/queue/gig_hunter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def run_continuously(self):
        """Run the agent in continuous mode, checking for new jobs"""
        self.logger.info("GigHunter agent started in continuous mode")
        
        while True:
            try:
                # In a real implementation, this would check job boards, email, etc.
                # For now, just simulate periodic activity
                self.status = "monitoring"
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in continuous mode: {str(e)}")
                await asyncio.sleep(10)
    
    def get_status(self):
        return {
            "name": self.name,
            "status": self.status,
            "last_active": datetime.now().isoformat()
        }