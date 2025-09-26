#!/usr/bin/env python3
"""
Product Factory Agent - Generates ebooks and templates automatically
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

class ProductFactoryAgent:
    def __init__(self):
        self.name = "ProductFactory"
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
        
    async def generate_ebook(self, topic: str, target_audience: str, chapter_count: int = 7):
        """Generate a comprehensive ebook on the given topic"""
        self.status = "working"
        self.logger.info(f"Generating ebook on: {topic}")
        
        try:
            # Generate ebook outline first
            outline_prompt = f"""
            Create a detailed outline for an ebook titled about "{topic}" for {target_audience}.
            
            Include {chapter_count} chapters with:
            1. Chapter titles
            2. Key points for each chapter
            3. Learning objectives
            4. Practical exercises or examples
            
            Format as JSON with: title, description, target_audience, chapters array
            """
            
            outline_response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-5",
                messages=[{"role": "user", "content": outline_prompt}],
                response_format={"type": "json_object"}
            )
            
            content = outline_response.choices[0].message.content
            if not content:
                raise ValueError("No outline content received from OpenAI")
            outline = json.loads(content)
            
            # Generate full content for each chapter
            full_ebook = outline.copy()
            full_ebook["chapters_content"] = []
            
            for i, chapter in enumerate(outline["chapters"]):
                chapter_prompt = f"""
                Write the full content for Chapter {i+1}: {chapter.get('title', f'Chapter {i+1}')}
                
                Topic: {topic}
                Target Audience: {target_audience}
                Chapter Outline: {json.dumps(chapter)}
                
                Write engaging, informative content (800-1200 words) that includes:
                - Clear explanations
                - Practical examples
                - Actionable advice
                - Professional insights
                
                Format as plain text content.
                """
                
                chapter_response = await asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model="gpt-5",
                    messages=[{"role": "user", "content": chapter_prompt}]
                )
                
                full_ebook["chapters_content"].append({
                    "chapter_number": i + 1,
                    "title": chapter.get('title', f'Chapter {i+1}'),
                    "content": chapter_response.choices[0].message.content
                })
            
            output_data = {
                "agent": self.name,
                "type": "ebook",
                "timestamp": datetime.now().isoformat(),
                "topic": topic,
                "target_audience": target_audience,
                "ebook": full_ebook
            }
            
            await self._save_to_queue(output_data)
            self.logger.info("Ebook generated successfully")
            self.status = "idle"

            # 📧 Send email after task completion
            send_task_email(
                self.name,
                f"Generated ebook project: {topic}",
                json.dumps(full_ebook, indent=2)
            )

            return full_ebook
            
        except Exception as e:
            self.logger.error(f"Error generating ebook: {str(e)}")
            self.status = "error"
            raise
    
    async def generate_template(self, template_type: str, industry: str):
        """Generate business templates (contracts, proposals, etc.)"""
        self.status = "working"
        self.logger.info(f"Generating {template_type} template for {industry}")
        
        try:
            prompt = f"""
            Create a professional {template_type} template specifically for the {industry} industry.
            
            The template should:
            1. Include all necessary legal and business sections
            2. Use professional language and formatting
            3. Include placeholder fields marked with [FIELD_NAME]
            4. Be industry-specific and comprehensive
            5. Follow best practices for {template_type}
            
            Format the response as JSON with: title, description, sections array, placeholders array
            """
            
            response = await asyncio.to_thread(
                self.client.client.chat.completions.create,
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("No template content received from OpenAI")
            template = json.loads(content)
            
            output_data = {
                "agent": self.name,
                "type": "template",
                "timestamp": datetime.now().isoformat(),
                "template_type": template_type,
                "industry": industry,
                "template": template
            }
            
            await self._save_to_queue(output_data)
            self.logger.info("Template generated successfully")
            self.status = "idle"

            # 📧 Send email after task completion
            send_task_email(
                self.name,
                f"Generated {template_type} template for {industry}",
                json.dumps(template, indent=2)
            )

            return template
            
        except Exception as e:
            self.logger.error(f"Error generating template: {str(e)}")
            self.status = "error"
            raise
    
    async def _save_to_queue(self, data):
        """Save output to the queue system"""
        Path("data/queue").mkdir(parents=True, exist_ok=True)
        filename = f"data/queue/product_factory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def run_continuously(self):
        """Run the agent in continuous mode"""
        self.logger.info("ProductFactory agent started in continuous mode")
        
        while True:
            try:
                self.status = "monitoring"
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in continuous mode: {str(e)}")
                await asyncio.sleep(15)
    
    def get_status(self):
        return {
            "name": self.name,
            "status": self.status,
            "last_active": datetime.now().isoformat()
        }