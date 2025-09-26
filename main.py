#!/usr/bin/env python3
"""
Main Entry Point - FastAPI server for Lincoln Agency Multi-Agent System
Provides web dashboard and API endpoints for the orchestrator
"""
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import asyncio
import logging
import os
from pathlib import Path
import sys
import uvicorn
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Import the orchestrator
from orchestrator import orchestrator

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Lincoln Agency Multi-Agent System",
    description="Business AI Partner with specialized agents",
    version="1.0.0"
)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to track orchestrator task
orchestrator_task = None

@app.on_event("startup")
async def startup_event():
    """Initialize the orchestrator when the app starts"""
    global orchestrator_task
    
    logger.info("Starting Lincoln Agency Multi-Agent System...")
    
    try:
        # Initialize agents
        await orchestrator.initialize_agents()
        logger.info("Agents initialized successfully")
        
        # Start orchestrator in background
        orchestrator_task = asyncio.create_task(orchestrator.start_all_agents())
        logger.info("Orchestrator started in background")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown of the orchestrator"""
    global orchestrator_task
    
    logger.info("Shutting down Lincoln Agency Multi-Agent System...")
    
    if orchestrator_task and not orchestrator_task.done():
        orchestrator_task.cancel()
        try:
            await orchestrator_task
        except asyncio.CancelledError:
            logger.info("Orchestrator task cancelled successfully")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/agent/{agent_name}", response_class=HTMLResponse)
async def agent_page(request: Request, agent_name: str):
    """Individual agent pages"""
    agent_templates = {
        "gig_hunter": "gig_hunter.html",
        "product_factory": "product_factory.html", 
        "content_agent": "content_agent.html",
        "outreach_agent": "outreach_agent.html",
        "fulfillment_agent": "fulfillment_agent.html",
        "code_writer": "code_writer.html",
        "code_reviewer": "code_reviewer.html"
    }
    
    template_name = agent_templates.get(agent_name)
    if not template_name:
        return JSONResponse(
            content={"error": f"Agent '{agent_name}' not found"},
            status_code=404
        )
    
    return templates.TemplateResponse(template_name, {"request": request, "agent_name": agent_name})

@app.get("/api/status")
async def get_system_status():
    """Get current system and agent status"""
    try:
        status = orchestrator.get_system_status()
        return JSONResponse(content=status)
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        return JSONResponse(
            content={
                "error": "Failed to get system status",
                "orchestrator_status": "error",
                "agents": {}
            },
            status_code=500
        )

@app.post("/api/execute-task")
async def execute_task(task_data: dict):
    """Execute a task using the appropriate agent"""
    try:
        task_type = task_data.get("task_type")
        if not task_type:
            return JSONResponse(
                content={"error": "task_type is required"},
                status_code=400
            )
        
        result = await orchestrator.execute_task(task_type, task_data)
        return JSONResponse(content={"success": True, "result": result})
        
    except Exception as e:
        logger.error(f"Error executing task: {str(e)}")
        return JSONResponse(
            content={"error": f"Failed to execute task: {str(e)}"},
            status_code=500
        )

@app.post("/api/hunt-gigs")
async def trigger_gig_hunt():
    """Manually trigger gig hunting for testing"""
    try:
        if "gig_hunter" not in orchestrator.agents:
            return JSONResponse(
                content={"error": "Gig Hunter agent not available"},
                status_code=503
            )
        
        agent = orchestrator.agents["gig_hunter"]
        opportunities = await agent.hunt_for_gigs()
        
        return JSONResponse(content={
            "success": True, 
            "message": f"Gig hunt completed successfully",
            "opportunities_found": len(opportunities),
            "opportunities": opportunities[:3]  # Return first 3 for preview
        })
        
    except Exception as e:
        logger.error(f"Error triggering gig hunt: {str(e)}")
        return JSONResponse(
            content={"error": f"Failed to trigger gig hunt: {str(e)}"},
            status_code=500
        )

@app.get("/api/agents")
async def get_agents():
    """Get list of all agents and their capabilities"""
    agents_info = {
        "gig_hunter": {
            "name": "Gig Hunter",
            "description": "Drafts compelling proposals for freelance and contract opportunities",
            "capabilities": ["generate_proposal"],
            "status": orchestrator.agents.get("gig_hunter", {}).get("status", "unknown") if orchestrator.agents else "unknown"
        },
        "product_factory": {
            "name": "Product Factory", 
            "description": "Generates ebooks and professional templates automatically",
            "capabilities": ["generate_ebook", "generate_template"],
            "status": orchestrator.agents.get("product_factory", {}).get("status", "unknown") if orchestrator.agents else "unknown"
        },
        "content_agent": {
            "name": "Content Agent",
            "description": "Creates engaging short-form scripts and social media content",
            "capabilities": ["create_social_content", "create_video_script"],
            "status": orchestrator.agents.get("content_agent", {}).get("status", "unknown") if orchestrator.agents else "unknown"
        },
        "outreach_agent": {
            "name": "Outreach Agent",
            "description": "Personalizes cold emails using recipient data and insights",
            "capabilities": ["personalize_email"],
            "status": orchestrator.agents.get("outreach_agent", {}).get("status", "unknown") if orchestrator.agents else "unknown"
        },
        "fulfillment_agent": {
            "name": "Fulfillment Agent",
            "description": "Assembles comprehensive deliverables from multiple agent outputs",
            "capabilities": ["assemble_deliverable"],
            "status": orchestrator.agents.get("fulfillment_agent", {}).get("status", "unknown") if orchestrator.agents else "unknown"
        },
        "code_writer": {
            "name": "Code Writer",
            "description": "Generates working code projects from specifications",
            "capabilities": ["generate_code_project"],
            "status": orchestrator.agents.get("code_writer", {}).get("status", "unknown") if orchestrator.agents else "unknown"
        },
        "code_reviewer": {
            "name": "Code Reviewer",
            "description": "Reviews and improves generated code quality and security",
            "capabilities": ["review_code"],
            "status": orchestrator.agents.get("code_reviewer", {}).get("status", "unknown") if orchestrator.agents else "unknown"
        }
    }
    
    return JSONResponse(content=agents_info)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(content={
        "status": "healthy",
        "service": "Lincoln Agency Multi-Agent System",
        "orchestrator_status": orchestrator.status
    })

def main():
    """Main function to run the FastAPI server"""
    # Ensure required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not set - agents may not function properly")
    
    # Create necessary directories
    Path("data/queue").mkdir(parents=True, exist_ok=True)
    Path("data/logs").mkdir(parents=True, exist_ok=True)
    Path("templates").mkdir(parents=True, exist_ok=True)
    
    # Start the FastAPI server
    logger.info("Starting FastAPI server on 0.0.0.0:5000")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()