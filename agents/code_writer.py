#!/usr/bin/env python3
"""
Code Writer Agent - Generates working code projects from specifications
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

class CodeWriterAgent:
    def __init__(self):
        self.name = "CodeWriter"
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
        
    async def generate_code_project(self, project_spec: dict, language: str = "python"):
        """Generate a complete code project based on specifications"""
        self.status = "working"
        self.logger.info(f"Generating {language} project: {project_spec.get('name', 'Unnamed')}")
        
        try:
            prompt = f"""
            Generate a complete {language} code project based on these specifications:
            
            Project Specifications: {json.dumps(project_spec)}
            
            Requirements:
            1. Create a well-structured project with proper file organization
            2. Include all necessary files (main code, config, requirements, etc.)
            3. Write clean, documented, and production-ready code
            4. Include error handling and validation
            5. Add appropriate comments and docstrings
            6. Follow best practices for the chosen language
            
            Format as JSON with: project_structure, files (array with filename, content, description), setup_instructions, usage_examples
            """
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            content_text = response.choices[0].message.content
            if not content_text:
                raise ValueError("No code project content received from OpenAI")
            code_project = json.loads(content_text)
            
            output_data = {
                "agent": self.name,
                "type": "code_project",
                "timestamp": datetime.now().isoformat(),
                "project_spec": project_spec,
                "language": language,
                "project": code_project
            }
            
            await self._save_to_queue(output_data)
            self.logger.info("Code project generated successfully")
            self.status = "idle"
            return code_project
            
        except Exception as e:
            self.logger.error(f"Error generating code project: {str(e)}")
            self.status = "error"
            raise
    
    async def _save_to_queue(self, data):
        """Save output to the queue system"""
        Path("data/queue").mkdir(parents=True, exist_ok=True)
        filename = f"data/queue/code_writer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def run_continuously(self):
        """Run the agent in continuous mode"""
        self.logger.info("CodeWriter started in continuous mode")
        
        while True:
            try:
                self.status = "monitoring"
                await asyncio.sleep(70)
                
            except Exception as e:
                self.logger.error(f"Error in continuous mode: {str(e)}")
                await asyncio.sleep(20)
    
    def get_status(self):
        return {
            "name": self.name,
            "status": self.status,
            "last_active": datetime.now().isoformat()
        }