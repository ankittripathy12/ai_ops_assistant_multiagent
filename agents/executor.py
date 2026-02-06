from typing import Dict, Any, List
from tools.github_tool import GitHubTool
from tools.weather_tool import WeatherTool


class ExecutorAgent:
    def __init__(self):
        self.tools = {
            "github_search": GitHubTool(),
            "weather": WeatherTool()
        }

    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step from the plan"""
        tool_name = step.get("tool")
        parameters = step.get("parameters", {})

        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        try:
            tool = self.tools[tool_name]
            result = tool.execute(**parameters)

            return {
                "step": step["step_number"],
                "success": True,
                "result": result,
                "error": None
            }
        except Exception as e:
            return {
                "step": step["step_number"],
                "success": False,
                "result": None,
                "error": str(e)
            }

    def execute_plan(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute all steps in the plan"""
        results = []

        for step in steps:
            step_result = self.execute_step(step)
            results.append(step_result)

            # If step fails, we might want to handle it differently
            # For now, we continue with other steps

        return results