#!/usr/bin/env python3
"""
Content Agent - Creates short-form scripts and social media content
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

class ContentAgent:
    def __init__(self):
        self.name = "ContentAgent"
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
        
    async def create_social_content(self, platform: str, topic: str, brand_voice: str = "professional"):
        """Generate social media content for specific platforms"""
        self.status = "working"
        self.logger.info(f"Creating {platform} content about: {topic}")
        
        try:
            platform_specs = {
                "twitter": {"max_length": 280, "hashtags": True, "tone": "concise"},
                "linkedin": {"max_length": 1300, "hashtags": True, "tone": "professional"},
                "instagram": {"max_length": 2200, "hashtags": True, "tone": "visual"},
                "facebook": {"max_length": 500, "hashtags": False, "tone": "conversational"},
                "tiktok": {"max_length": 300, "hashtags": True, "tone": "trendy"}
            }
            
            specs = platform_specs.get(platform.lower(), platform_specs["linkedin"])
            
            prompt = f"""
            Create engaging {platform} content about "{topic}" with these specifications:
            - Brand voice: {brand_voice}
            - Platform tone: {specs['tone']}
            - Max length: {specs['max_length']} characters
            - Include hashtags: {specs['hashtags']}
            
            Requirements:
            1. Hook readers in the first line
            2. Provide value or insight
            3. Include a call-to-action
            4. Match the platform's style
            5. Optimize for engagement
            
            Format as JSON with: content, hashtags, engagement_tips, best_posting_time
            """
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            content_text = response.choices[0].message.content
            if not content_text:
                raise ValueError("No content received from OpenAI")
            content = json.loads(content_text)
            
            output_data = {
                "agent": self.name,
                "type": "social_content",
                "timestamp": datetime.now().isoformat(),
                "platform": platform,
                "topic": topic,
                "brand_voice": brand_voice,
                "content": content
            }
            
            await self._save_to_queue(output_data)
            self.logger.info(f"{platform} content created successfully")
            self.status = "idle"
            return content
            
        except Exception as e:
            self.logger.error(f"Error creating social content: {str(e)}")
            self.status = "error"
            raise
    
    async def create_video_script(self, video_type: str, duration: int, topic: str):
        """Generate video scripts for different formats"""
        self.status = "working"
        self.logger.info(f"Creating {video_type} script: {topic}")
        
        try:
            prompt = f"""
            Write a compelling {video_type} script about "{topic}" for a {duration}-minute video.
            
            Script requirements:
            1. Strong hook in first 5 seconds
            2. Clear structure with introduction, main points, conclusion
            3. Engaging transitions between sections
            4. Visual cues and direction notes
            5. Call-to-action at the end
            6. Time estimates for each section
            
            Format as JSON with: title, hook, sections array (each with content, visuals, timing), cta, total_duration
            """
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            content_text = response.choices[0].message.content
            if not content_text:
                raise ValueError("No script content received from OpenAI")
            script = json.loads(content_text)
            
            output_data = {
                "agent": self.name,
                "type": "video_script",
                "timestamp": datetime.now().isoformat(),
                "video_type": video_type,
                "duration": duration,
                "topic": topic,
                "script": script
            }
            
            await self._save_to_queue(output_data)
            self.logger.info("Video script created successfully")
            self.status = "idle"
            return script
            
        except Exception as e:
            self.logger.error(f"Error creating video script: {str(e)}")
            self.status = "error"
            raise
    
    async def _save_to_queue(self, data):
        """Save output to the queue system"""
        Path("data/queue").mkdir(parents=True, exist_ok=True)
        filename = f"data/queue/content_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def run_continuously(self):
        """Run the agent in continuous mode"""
        self.logger.info("ContentAgent started in continuous mode")
        
        while True:
            try:
                self.status = "monitoring"
                await asyncio.sleep(45)  # Check every 45 seconds
                
            except Exception as e:
                self.logger.error(f"Error in continuous mode: {str(e)}")
                await asyncio.sleep(15)
    
    def get_status(self):
        return {
            "name": self.name,
            "status": self.status,
            "last_active": datetime.now().isoformat()
        }