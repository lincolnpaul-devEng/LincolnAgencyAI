"""Agents package for Lincoln Agency Multi-Agent System.

This file marks the 'agents' directory as a Python package so that
relative imports (e.g., from .gemini_adapter import AIClient) work
properly when modules are imported by orchestrator/main.
"""

# Optional: expose common classes for convenience imports
from .gig_hunter import GigHunterAgent  # noqa: F401
from .product_factory import ProductFactoryAgent  # noqa: F401
from .content_agent import ContentAgent  # noqa: F401
from .outreach_agent import OutreachAgent  # noqa: F401
from .fulfillment_agent import FulfillmentAgent  # noqa: F401
from .code_writer import CodeWriterAgent  # noqa: F401
from .code_reviewer import CodeReviewerAgent  # noqa: F401
