# Lincoln Agency Multi-Agent System

## Overview

Lincoln Agency is a sophisticated multi-agent business AI system built with FastAPI and Python. The platform operates as a comprehensive business partner, coordinating seven specialized AI agents to handle various business functions including freelance proposals, content creation, product generation, outreach, and code development. The system features a centralized orchestrator that manages agent coordination, a web-based dashboard for monitoring, and robust logging capabilities for tracking all agent activities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Multi-Agent Architecture
The system implements a coordinated multi-agent architecture with a central orchestrator managing seven specialized agents:
- **GigHunterAgent**: Generates tailored freelance proposals
- **ProductFactoryAgent**: Creates ebooks and digital products
- **ContentAgent**: Produces social media content across platforms
- **OutreachAgent**: Personalizes cold email campaigns
- **FulfillmentAgent**: Assembles final deliverables from agent outputs
- **CodeWriterAgent**: Generates complete code projects
- **CodeReviewerAgent**: Reviews and improves code quality

This design provides modular functionality where each agent specializes in specific business domains while the orchestrator coordinates their activities and manages inter-agent communication.

### Web Application Framework
Built on FastAPI for high-performance async operations, the system provides:
- RESTful API endpoints for agent interaction
- Jinja2-templated web dashboard for real-time monitoring
- Background task processing for long-running agent operations
- Static file serving for dashboard assets

### Logging and Monitoring System
Comprehensive logging architecture with:
- Individual log files for each agent in `data/logs/`
- Centralized orchestrator logging for system-wide events
- Structured JSON output for system status and agent communication
- Queue-based message passing stored in `data/queue/`

### Asynchronous Processing
The system leverages Python's asyncio for concurrent agent operations:
- Non-blocking agent initialization and execution
- Queue-based task distribution
- Background task processing for web requests
- Concurrent monitoring of multiple agents

## External Dependencies

### AI Services
- **OpenAI API**: Primary LLM service using GPT-5 model for all agent reasoning and content generation
- Requires `OPENAI_API_KEY` environment variable

### Python Framework Stack
- **FastAPI**: Web framework and API server
- **Uvicorn**: ASGI server for production deployment
- **Jinja2**: Template engine for web dashboard
- **asyncio**: Built-in async/await support for concurrent operations

### Development Tools
- **python-dotenv**: Environment variable management
- **logging**: Built-in Python logging framework
- **pathlib**: Modern file system path handling
- **json**: Data serialization for agent communication

### Infrastructure Requirements
- File system access for logging and queue storage (`data/` directory structure)
- Environment variable support for API keys
- Python 3.7+ for async/await syntax support