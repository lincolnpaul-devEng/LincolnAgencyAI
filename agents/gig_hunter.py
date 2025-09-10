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
import random
from openai import OpenAI
import trafilatura
import urllib.parse

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user

class GigHunterAgent:
    def __init__(self):
        self.name = "GigHunter"
        self.status = "idle"
        self.logger = self._setup_logging()
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.last_hunt_time = datetime.now()
        self.hunt_interval = 300  # Hunt every 5 minutes
        self.gig_platforms = {
            "fiverr": {
                "search_urls": [
                    "https://www.fiverr.com/search/gigs?query=programming",
                    "https://www.fiverr.com/search/gigs?query=website+development",
                    "https://www.fiverr.com/search/gigs?query=content+writing",
                    "https://www.fiverr.com/search/gigs?query=digital+marketing",
                    "https://www.fiverr.com/search/gigs?query=business+automation"
                ]
            },
            "gumroad": {
                "search_urls": [
                    "https://gumroad.com/discover?query=template",
                    "https://gumroad.com/discover?query=course",
                    "https://gumroad.com/discover?query=ebook",
                    "https://gumroad.com/discover?query=business"
                ]
            }
        }
        
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
    
    async def hunt_for_gigs(self):
        """Hunt for gigs on various platforms"""
        self.status = "hunting"
        self.logger.info("Starting gig hunt on platforms...")
        
        found_opportunities = []
        
        try:
            # Hunt on Fiverr - look for buyer requests or trending searches
            fiverr_ops = await self._analyze_fiverr_trends()
            found_opportunities.extend(fiverr_ops)
            
            # Hunt on Gumroad - analyze successful products for inspiration
            gumroad_ops = await self._analyze_gumroad_trends()
            found_opportunities.extend(gumroad_ops)
            
            # Generate proposals for found opportunities
            for opportunity in found_opportunities:
                try:
                    proposal = await self.generate_proposal(
                        opportunity["description"],
                        opportunity.get("client_info", {})
                    )
                    self.logger.info(f"Generated proposal for: {opportunity['title'][:50]}...")
                    await asyncio.sleep(2)  # Rate limiting
                except Exception as e:
                    self.logger.error(f"Error generating proposal for opportunity: {str(e)}")
            
            self.logger.info(f"Gig hunt completed. Found {len(found_opportunities)} opportunities")
            self.last_hunt_time = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error during gig hunt: {str(e)}")
            
        self.status = "monitoring"
        return found_opportunities
    
    async def _analyze_fiverr_trends(self):
        """Analyze Fiverr for trending services and opportunities"""
        opportunities = []
        
        try:
            # Use AI to identify trending service categories based on common Fiverr patterns
            prompt = """
            Based on current market trends in freelancing, identify 3-5 high-demand service opportunities that Lincoln Agency could offer on platforms like Fiverr. Consider:
            1. AI and automation services
            2. Content creation and marketing
            3. Business development and strategy
            4. Technical development services
            5. Digital product creation
            
            For each opportunity, provide a realistic service description that Lincoln Agency could fulfill.
            
            Format as JSON with: title, description, estimated_value, difficulty_level, market_demand
            """
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if content:
                trend_data = json.loads(content)
                
                # Convert trends into opportunities
                if "opportunities" in trend_data:
                    for opp in trend_data["opportunities"]:
                        opportunities.append({
                            "platform": "fiverr",
                            "title": opp.get("title", "Service Opportunity"),
                            "description": opp.get("description", ""),
                            "client_info": {
                                "platform": "Fiverr",
                                "estimated_value": opp.get("estimated_value", "$50-500"),
                                "market_demand": opp.get("market_demand", "medium")
                            }
                        })
                        
            self.logger.info(f"Analyzed Fiverr trends, found {len(opportunities)} opportunities")
            
        except Exception as e:
            self.logger.error(f"Error analyzing Fiverr trends: {str(e)}")
            
        return opportunities
    
    async def _analyze_gumroad_trends(self):
        """Analyze Gumroad for product opportunities"""
        opportunities = []
        
        try:
            # Use AI to identify trending digital product opportunities
            prompt = """
            Based on current trends in digital products and online education, identify 3-5 digital product opportunities that Lincoln Agency could create for platforms like Gumroad. Consider:
            1. Business templates and tools
            2. Educational courses and guides
            3. Software and automation tools
            4. Marketing and content templates
            5. Industry-specific resources
            
            For each opportunity, provide a detailed product concept that Lincoln Agency could develop.
            
            Format as JSON with: title, description, target_audience, estimated_price, development_effort
            """
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if content:
                product_data = json.loads(content)
                
                # Convert product ideas into opportunities
                if "opportunities" in product_data:
                    for opp in product_data["opportunities"]:
                        opportunities.append({
                            "platform": "gumroad",
                            "title": opp.get("title", "Digital Product Opportunity"),
                            "description": f"Create digital product: {opp.get('description', '')}",
                            "client_info": {
                                "platform": "Gumroad",
                                "target_audience": opp.get("target_audience", "Business professionals"),
                                "estimated_price": opp.get("estimated_price", "$20-100"),
                                "product_type": "digital"
                            }
                        })
                        
            self.logger.info(f"Analyzed Gumroad trends, found {len(opportunities)} opportunities")
            
        except Exception as e:
            self.logger.error(f"Error analyzing Gumroad trends: {str(e)}")
            
        return opportunities
    
    async def run_continuously(self):
        """Run the agent in continuous mode, actively hunting for gigs"""
        self.logger.info("GigHunter agent started in continuous mode - actively hunting for opportunities")
        
        while True:
            try:
                self.status = "monitoring"
                
                # Check if it's time to hunt for new gigs
                time_since_last_hunt = (datetime.now() - self.last_hunt_time).total_seconds()
                
                if time_since_last_hunt >= self.hunt_interval:
                    await self.hunt_for_gigs()
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in continuous mode: {str(e)}")
                await asyncio.sleep(30)
    
    def get_status(self):
        return {
            "name": self.name,
            "status": self.status,
            "last_active": datetime.now().isoformat()
        }