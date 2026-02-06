from typing import Dict, Any, List
import sys
import os

# Fix imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.client import LLMClient
from config import Config


class PlannerAgent:
    def __init__(self):
        self.llm_client = LLMClient()
        self.available_tools = [
            {
                "name": "github_search",
                "description": "Search GitHub repositories and fetch repository details",
                "parameters": {
                    "query": "Search query for repositories (e.g., 'python', 'machine learning')",
                    "per_page": "Number of results to return (default: 5)"
                }
            },
            {
                "name": "weather",
                "description": "Fetch current weather information for a city",
                "parameters": {
                    "city": "City name for weather information (e.g., 'London', 'Tokyo')"
                }
            }
        ]

    def create_plan(self, user_task: str) -> Dict[str, Any]:
        """Convert user task into a step-by-step execution plan"""
        prompt = f"""
        TASK: Convert this user request into an execution plan.

        USER REQUEST: {user_task}

        AVAILABLE TOOLS:
        1. github_search - Search GitHub repositories
           Parameters: query (required), per_page (optional, default: 5)
        2. weather - Get current weather by city
           Parameters: city (required)

        INSTRUCTIONS:
        1. Break down the user request into logical steps
        2. For each step, choose the right tool and parameters
        3. Extract parameters from the user request
        4. Create a JSON object with this exact structure:

        {{
            "task": "Original user task",
            "steps": [
                {{
                    "step_number": 1,
                    "description": "What to do in this step",
                    "tool": "tool_name",
                    "parameters": {{"param1": "value1"}}
                }}
            ]
        }}

        RULES:
        - Return ONLY the JSON object, no other text
        - Make sure the JSON is valid
        - Use the exact tool names from AVAILABLE TOOLS
        - Include all necessary parameters for each tool
        """

        messages = [
            {"role": "system",
             "content": "You are a planning assistant that creates execution plans. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ]

        try:
            plan = self.llm_client.generate_json(messages, temperature=Config.PLANNER_TEMPERATURE)
            return self._validate_plan(plan)
        except Exception as e:
            print(f"⚠️  Planner failed: {e}")
            return self._create_fallback_plan(user_task)

    def _create_fallback_plan(self, user_task: str) -> Dict[str, Any]:
        """Create a simple fallback plan if LLM fails"""
        import re

        steps = []
        step_num = 1

        # Check for weather request
        weather_patterns = [
            r'weather in (\w+)',
            r'temperature in (\w+)',
            r'climate in (\w+)'
        ]

        for pattern in weather_patterns:
            match = re.search(pattern, user_task.lower())
            if match:
                city = match.group(1).title()
                steps.append({
                    "step_number": step_num,
                    "description": f"Get weather information for {city}",
                    "tool": "weather",
                    "parameters": {"city": city}
                })
                step_num += 1
                break

        # Check for GitHub/search request
        search_patterns = [
            r'find (\w+) repositories',
            r'search for (\w+) repositories',
            r'show me (\w+) repositories',
            r'(\w+) projects',
            r'(\w+) libraries'
        ]

        for pattern in search_patterns:
            match = re.search(pattern, user_task.lower())
            if match:
                query = match.group(1)
                steps.append({
                    "step_number": step_num,
                    "description": f"Search GitHub for {query} repositories",
                    "tool": "github_search",
                    "parameters": {"query": query, "per_page": 5}
                })
                step_num += 1
                break

        # Default if no patterns matched
        if not steps:
            if 'weather' in user_task.lower():
                steps.append({
                    "step_number": 1,
                    "description": "Get weather information",
                    "tool": "weather",
                    "parameters": {"city": "London"}
                })
            elif any(word in user_task.lower() for word in ['github', 'repository', 'repo', 'search', 'find']):
                steps.append({
                    "step_number": 1,
                    "description": "Search GitHub repositories",
                    "tool": "github_search",
                    "parameters": {"query": "python", "per_page": 5}
                })

        return {
            "task": user_task,
            "steps": steps
        }

    def _validate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the plan structure"""
        required_keys = ["task", "steps"]
        if not all(key in plan for key in required_keys):
            raise ValueError("Plan missing required fields")

        if not isinstance(plan["steps"], list):
            raise ValueError("Steps must be a list")

        # Clean up parameters - remove 'operation' if it exists
        for step in plan["steps"]:
            if "parameters" in step and "operation" in step["parameters"]:
                step["parameters"].pop("operation", None)

        return plan