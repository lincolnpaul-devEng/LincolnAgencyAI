#!/usr/bin/env python3
"""
Code Reviewer Agent - Reviews and improves generated code quality
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

class CodeReviewerAgent:
    def __init__(self):
        self.name = "CodeReviewer"
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
        
    async def review_code(self, code_content: str, language: str, review_criteria: list | None = None):
        """Review code and provide detailed feedback and improvements"""
        self.status = "working"
        self.logger.info(f"Reviewing {language} code")
        
        try:
            default_criteria = [
                "code quality and readability",
                "security vulnerabilities",
                "performance optimizations", 
                "error handling",
                "best practices compliance",
                "documentation quality"
            ]
            
            criteria = review_criteria or default_criteria
            
            prompt = f"""
            Perform a comprehensive code review for this {language} code:
            
            Code to Review:
            ```{language}
            {code_content}
            ```
            
            Review Criteria: {', '.join(criteria)}
            
            Provide detailed analysis including:
            1. Overall code quality assessment (1-10 score)
            2. Specific issues found with line references
            3. Security concerns or vulnerabilities
            4. Performance improvement suggestions
            5. Code style and best practices feedback
            6. Suggested improvements with code examples
            7. Testing recommendations
            
            Format as JSON with: overall_score, issues (array), security_concerns, performance_suggestions, improvements, testing_recommendations
            """
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            content_text = response.choices[0].message.content
            if not content_text:
                raise ValueError("No code review content received from OpenAI")
            review_result = json.loads(content_text)
            
            output_data = {
                "agent": self.name,
                "type": "code_review",
                "timestamp": datetime.now().isoformat(),
                "language": language,
                "review_criteria": criteria,
                "review": review_result
            }
            
            await self._save_to_queue(output_data)
            self.logger.info("Code review completed successfully")
            self.status = "idle"
            return review_result
            
        except Exception as e:
            self.logger.error(f"Error reviewing code: {str(e)}")
            self.status = "error"
            raise
    
    async def _save_to_queue(self, data):
        """Save output to the queue system"""
        Path("data/queue").mkdir(parents=True, exist_ok=True)
        filename = f"data/queue/code_reviewer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def run_continuously(self):
        """Run the agent in continuous mode"""
        self.logger.info("CodeReviewer started in continuous mode")
        
        while True:
            try:
                self.status = "monitoring"
                await asyncio.sleep(80)
                
            except Exception as e:
                self.logger.error(f"Error in continuous mode: {str(e)}")
                await asyncio.sleep(25)
    
    def get_status(self):
        return {
            "name": self.name,
            "status": self.status,
            "last_active": datetime.now().isoformat()
        }