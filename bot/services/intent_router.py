"""
Intent router - uses LLM to route natural language to API tools.

The LLM receives:
1. User message
2. Tool definitions (9 backend endpoints)
3. System prompt encouraging tool use

The LLM responds with tool calls, which are executed and fed back.
"""

import json
from services.llm_client import llm_client


# Tool definitions for the LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all labs and tasks available in the system",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of all enrolled learners/students",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task pass rates and attempt counts for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submission timeline (submissions per day) for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group performance and student counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top learners to return (default: 5)",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL pipeline sync to refresh data from autochecker",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# System prompt for the LLM
SYSTEM_PROMPT = """You are an AI assistant for a Learning Management System (LMS). 
You have access to tools that fetch data about labs, students, scores, and analytics.

When a user asks a question:
1. Think about what data you need to answer
2. Call the appropriate tool(s) to get that data
3. Use the tool results to provide a helpful, accurate answer

Available tools:
- get_items: List all labs and tasks
- get_learners: List all enrolled students
- get_pass_rates: Get pass rates for a specific lab (requires lab parameter)
- get_scores: Get score distribution for a lab
- get_timeline: Get submission timeline for a lab
- get_groups: Get per-group performance for a lab
- get_top_learners: Get top students for a lab
- get_completion_rate: Get completion rate for a lab
- trigger_sync: Refresh data from autochecker

For questions about specific labs, always use the lab identifier like "lab-01", "lab-04", etc.
If the user doesn't specify which lab, ask them to clarify or use get_items first to see available labs.

Be helpful and friendly. If you don't understand the question, ask for clarification."""


def route_intent(message: str) -> str:
    """
    Route a user message through the LLM intent router.
    
    Args:
        message: User's natural language message
        
    Returns:
        Response from the LLM after tool execution
    """
    # Build conversation history
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]
    
    # Call LLM with tools
    response = llm_client.chat_with_tools(messages, TOOLS)
    return response
