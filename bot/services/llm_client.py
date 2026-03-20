"""
LLM client for intent classification and tool use.

Uses OpenAI-compatible API to call LLM with tool definitions.
"""

import json
import sys
from typing import Any

import httpx
from config import config


class LLMClient:
    """Client for LLM API with tool calling support."""

    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = None,
    ):
        self.api_key = api_key or config.llm_api_key
        self.base_url = (base_url or config.llm_api_base_url).rstrip("/")
        self.model = model or config.llm_model
        self.timeout = 30.0

    def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        max_turns: int = 5,
    ) -> str:
        """
        Chat with LLM, allowing it to call tools.
        
        Args:
            messages: Conversation history with role/content
            tools: List of tool schemas for the LLM to choose from
            max_turns: Maximum back-and-forth turns with LLM
            
        Returns:
            Final response from LLM after tool execution
        """
        for turn in range(max_turns):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    # Debug: log what we're sending
                    request_data = {
                        "model": self.model,
                        "messages": messages,
                        "tools": tools,
                        "tool_choice": "auto",
                    }
                    print(f"[llm] Sending request to {self.base_url}/chat/completions", file=sys.stderr)
                    print(f"[llm] Model: {self.model}", file=sys.stderr)
                    
                    response = client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json=request_data,
                    )
                    
                    if response.status_code != 200:
                        print(f"[llm] Error response: {response.status_code}", file=sys.stderr)
                        print(f"[llm] Response body: {response.text[:500]}", file=sys.stderr)
                    
                    response.raise_for_status()
                    data = response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    return "LLM error: HTTP 401 Unauthorized. Token may have expired."
                return f"LLM error: HTTP {e.response.status_code}"
            except httpx.ConnectError:
                return f"LLM error: cannot connect to {self.base_url}"
            except Exception as e:
                return f"LLM error: {str(e)}"

            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            
            # Check if LLM wants to call tools
            tool_calls = message.get("tool_calls", [])
            
            if not tool_calls:
                # LLM is done - return its response
                return message.get("content", "No response generated.")
            
            # Add LLM's message to conversation
            messages.append({
                "role": "assistant",
                "content": message.get("content"),
                "tool_calls": tool_calls,
            })
            
            # Execute each tool call
            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                tool_name = function.get("name", "")
                tool_args_str = function.get("arguments", "{}")
                
                try:
                    tool_args = json.loads(tool_args_str) if tool_args_str else {}
                except json.JSONDecodeError:
                    tool_args = {}
                
                # Execute the tool
                result = self._execute_tool(tool_name, tool_args)
                
                # Log for debugging
                print(f"[tool] LLM called: {tool_name}({tool_args})", file=sys.stderr)
                print(f"[tool] Result: {result}", file=sys.stderr)
                
                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", ""),
                    "content": json.dumps(result) if not isinstance(result, str) else result,
                })
            
            print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)
        
        # Max turns reached - ask LLM to summarize
        messages.append({
            "role": "system",
            "content": "Please provide a final answer based on the tool results above."
        })
        
        # One more call to get final answer
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "Done.")
        except Exception as e:
            return "Error getting final answer."

    def _execute_tool(self, name: str, args: dict) -> Any:
        """Execute a tool by name with given arguments."""
        # Import here to avoid circular imports
        from services.lms_api import lms_client
        
        tool_map = {
            "get_items": lambda: lms_client.get_items(),
            "get_learners": lambda: lms_client.get_learners(),
            "get_scores": lambda: lms_client.get_scores(args.get("lab", "")),
            "get_pass_rates": lambda: lms_client.get_pass_rates(args.get("lab", "")),
            "get_timeline": lambda: lms_client.get_timeline(args.get("lab", "")),
            "get_groups": lambda: lms_client.get_groups(args.get("lab", "")),
            "get_top_learners": lambda: lms_client.get_top_learners(
                args.get("lab", ""), args.get("limit", 5)
            ),
            "get_completion_rate": lambda: lms_client.get_completion_rate(args.get("lab", "")),
            "trigger_sync": lambda: lms_client.trigger_sync(),
        }
        
        if name in tool_map:
            return tool_map[name]()
        return {"error": f"Unknown tool: {name}"}


# Global client instance
llm_client = LLMClient()
