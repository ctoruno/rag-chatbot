"""Agentic RAG system for news events search."""

from .graph.workflow import create_workflow

__version__ = "1.0.0"
__all__ = ["create_workflow", "main"]