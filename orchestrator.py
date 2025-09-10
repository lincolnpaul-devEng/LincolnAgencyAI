#!/usr/bin/env python3
"""
Orchestrator - Runs all agents concurrently for Lincoln Agency
Main coordination system for multi-agent business AI partner
"""
import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path
import importlib.util
import sys
import os

# Import all agent classes
from agents.gig_hunter import GigHunterAgent
from agents.product_factory import ProductFactoryAgent
from agents.content_agent import ContentAgent
from agents.outreach_agent import OutreachAgent
from agents.fulfillment_agent import FulfillmentAgent
from agents.code_writer import CodeWriterAgent
from agents.code_reviewer import CodeReviewerAgent

class AgentOrchestrator:
    def __init__(self):
        self.name = "Orchestrator"
        self.agents = {}
        self.status = "initializing"
        self.logger = self._setup_logging()
        self.tasks_queue = asyncio.Queue()
        self.results_storage = []
        
    def _setup_logging(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        
        Path("data/logs").mkdir(parents=True, exist_ok=True)
        
        handler = logging.FileHandler("data/logs/orchestrator.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def initialize_agents(self):
        """Initialize all agents"""
        self.logger.info("Initializing all agents...")
        
        try:
            self.agents = {
                "gig_hunter": GigHunterAgent(),
                "product_factory": ProductFactoryAgent(),
                "content_agent": ContentAgent(),
                "outreach_agent": OutreachAgent(),
                "fulfillment_agent": FulfillmentAgent(),
                "code_writer": CodeWriterAgent(),
                "code_reviewer": CodeReviewerAgent()
            }
            
            self.logger.info(f"Initialized {len(self.agents)} agents successfully")
            self.status = "ready"
            
        except Exception as e:
            self.logger.error(f"Error initializing agents: {str(e)}")
            self.status = "error"
            raise
    
    async def start_all_agents(self):
        """Start all agents in concurrent mode"""
        if not self.agents:
            await self.initialize_agents()
        
        self.logger.info("Starting all agents concurrently...")
        self.status = "running"
        
        # Create tasks for all agents to run continuously
        agent_tasks = []
        for agent_name, agent in self.agents.items():
            task = asyncio.create_task(
                agent.run_continuously(),
                name=f"{agent_name}_continuous"
            )
            agent_tasks.append(task)
            self.logger.info(f"Started {agent_name} agent")
        
        # Also start the orchestrator's own monitoring task
        orchestrator_task = asyncio.create_task(
            self._monitor_system(),
            name="orchestrator_monitor"
        )
        agent_tasks.append(orchestrator_task)
        
        try:
            # Run all agents concurrently
            await asyncio.gather(*agent_tasks, return_exceptions=True)
        except Exception as e:
            self.logger.error(f"Error in concurrent agent execution: {str(e)}")
            self.status = "error"
            raise
    
    async def _monitor_system(self):
        """Monitor system health and agent performance"""
        self.logger.info("Orchestrator monitoring system started")
        
        while True:
            try:
                # Check agent statuses
                agent_statuses = {}
                for name, agent in self.agents.items():
                    agent_statuses[name] = agent.get_status()
                
                # Log system status every 2 minutes
                self.logger.info(f"System Status - Agents: {len([a for a in agent_statuses.values() if a['status'] != 'error'])}/{len(agent_statuses)} healthy")
                
                # Save system status to queue
                status_data = {
                    "agent": self.name,
                    "type": "system_status",
                    "timestamp": datetime.now().isoformat(),
                    "agent_statuses": agent_statuses,
                    "system_health": "healthy" if all(s['status'] != 'error' for s in agent_statuses.values()) else "degraded"
                }
                
                await self._save_status(status_data)
                
                await asyncio.sleep(120)  # Monitor every 2 minutes
                
            except Exception as e:
                self.logger.error(f"Error in system monitoring: {str(e)}")
                await asyncio.sleep(30)
    
    async def _save_status(self, status_data):
        """Save system status to queue"""
        Path("data/queue").mkdir(parents=True, exist_ok=True)
        filename = f"data/queue/orchestrator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(status_data, f, indent=2)
    
    def get_system_status(self):
        """Get current system status"""
        agent_statuses = {}
        if self.agents:
            for name, agent in self.agents.items():
                agent_statuses[name] = agent.get_status()
        
        return {
            "orchestrator_status": self.status,
            "timestamp": datetime.now().isoformat(),
            "agents_count": len(self.agents),
            "agents": agent_statuses
        }
    
    async def execute_task(self, task_type: str, task_data: dict):
        """Execute a specific task using appropriate agent"""
        self.logger.info(f"Executing task: {task_type}")
        
        try:
            if task_type == "generate_proposal" and "gig_hunter" in self.agents:
                return await self.agents["gig_hunter"].generate_proposal(
                    task_data.get("job_description", ""),
                    task_data.get("client_info")
                )
            elif task_type == "generate_ebook" and "product_factory" in self.agents:
                return await self.agents["product_factory"].generate_ebook(
                    task_data.get("topic", ""),
                    task_data.get("target_audience", ""),
                    task_data.get("chapter_count", 7)
                )
            elif task_type == "generate_template" and "product_factory" in self.agents:
                return await self.agents["product_factory"].generate_template(
                    task_data.get("template_type", ""),
                    task_data.get("industry", "")
                )
            elif task_type == "create_social_content" and "content_agent" in self.agents:
                return await self.agents["content_agent"].create_social_content(
                    task_data.get("platform", ""),
                    task_data.get("topic", ""),
                    task_data.get("brand_voice", "professional")
                )
            elif task_type == "create_video_script" and "content_agent" in self.agents:
                return await self.agents["content_agent"].create_video_script(
                    task_data.get("video_type", ""),
                    task_data.get("duration", 2),
                    task_data.get("topic", "")
                )
            elif task_type == "personalize_email" and "outreach_agent" in self.agents:
                return await self.agents["outreach_agent"].personalize_email(
                    task_data.get("recipient_info", {}),
                    task_data.get("email_template", ""),
                    task_data.get("campaign_goal", "")
                )
            elif task_type == "generate_code_project" and "code_writer" in self.agents:
                return await self.agents["code_writer"].generate_code_project(
                    task_data.get("project_spec", {}),
                    task_data.get("language", "python")
                )
            elif task_type == "review_code" and "code_reviewer" in self.agents:
                return await self.agents["code_reviewer"].review_code(
                    task_data.get("code_content", ""),
                    task_data.get("language", "python"),
                    task_data.get("review_criteria")
                )
            elif task_type == "assemble_deliverable" and "fulfillment_agent" in self.agents:
                return await self.agents["fulfillment_agent"].assemble_deliverable(
                    task_data.get("project_requirements", {}),
                    task_data.get("agent_outputs", [])
                )
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
        except Exception as e:
            self.logger.error(f"Error executing task {task_type}: {str(e)}")
            raise

# Global orchestrator instance
orchestrator = AgentOrchestrator()

async def main():
    """Main function to start the orchestrator"""
    try:
        await orchestrator.start_all_agents()
    except KeyboardInterrupt:
        logging.info("Orchestrator stopped by user")
    except Exception as e:
        logging.error(f"Orchestrator error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())