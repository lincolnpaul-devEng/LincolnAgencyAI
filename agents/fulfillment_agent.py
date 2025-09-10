#!/usr/bin/env python3
"""
Fulfillment Agent - Assembles deliverables from multiple agent outputs
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

class FulfillmentAgent:
    def __init__(self):
        self.name = "FulfillmentAgent"
        self.status = "idle"
        self.logger = self._setup_logging()
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
    def _setup_logging(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        
        Path("data/logs").mkdir(parents=True, exist_ok=True)
        
        handler = logging.FileHandler(f"data/logs/{self.name.lower()}.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
        
    async def assemble_deliverable(self, project_requirements: dict, agent_outputs: list):
        """Assemble final deliverable from various agent outputs"""
        self.status = "working"
        self.logger.info(f"Assembling deliverable: {project_requirements.get('name', 'Unnamed Project')}")
        
        try:
            prompt = f"""
            Assemble a comprehensive deliverable package based on these requirements and agent outputs:
            
            Project Requirements: {json.dumps(project_requirements)}
            
            Agent Outputs Available: {json.dumps([{'agent': output.get('agent'), 'type': output.get('type'), 'timestamp': output.get('timestamp')} for output in agent_outputs])}
            
            Full Agent Data: {json.dumps(agent_outputs)}
            
            Create a professional deliverable package that:
            1. Combines all relevant outputs into a cohesive package
            2. Ensures consistency across all components
            3. Adds executive summary and project overview
            4. Includes implementation timeline and next steps
            5. Provides quality assurance notes
            6. Formats everything professionally
            
            Format as JSON with: executive_summary, deliverable_components (array), implementation_plan, quality_notes, next_steps
            """
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            content_text = response.choices[0].message.content
            if not content_text:
                raise ValueError("No deliverable content received from OpenAI")
            deliverable = json.loads(content_text)
            
            output_data = {
                "agent": self.name,
                "type": "final_deliverable",
                "timestamp": datetime.now().isoformat(),
                "project_requirements": project_requirements,
                "source_agents": [output.get('agent') for output in agent_outputs],
                "deliverable": deliverable
            }
            
            await self._save_to_queue(output_data)
            self.logger.info("Deliverable assembled successfully")
            self.status = "idle"
            return deliverable
            
        except Exception as e:
            self.logger.error(f"Error assembling deliverable: {str(e)}")
            self.status = "error"
            raise
    
    async def _save_to_queue(self, data):
        """Save output to the queue system"""
        Path("data/queue").mkdir(parents=True, exist_ok=True)
        filename = f"data/queue/fulfillment_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def run_continuously(self):
        """Run the agent in continuous mode"""
        self.logger.info("FulfillmentAgent started in continuous mode")
        
        while True:
            try:
                self.status = "monitoring"
                await asyncio.sleep(90)
                
            except Exception as e:
                self.logger.error(f"Error in continuous mode: {str(e)}")
                await asyncio.sleep(30)
    
    def get_status(self):
        return {
            "name": self.name,
            "status": self.status,
            "last_active": datetime.now().isoformat()
        }