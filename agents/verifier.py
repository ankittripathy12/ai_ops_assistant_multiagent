from typing import Dict, Any, List
from llm.client import LLMClient
from config import Config


class VerifierAgent:
    def __init__(self):
        self.llm_client = LLMClient()

    def verify_and_format(self,
                          original_task: str,
                          execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify results and format final output"""

        # Check for failures
        failed_steps = [r for r in execution_results if not r["success"]]
        successful_results = [r["result"] for r in execution_results if r["success"]]

        if failed_steps and not successful_results:
            return {
                "status": "failed",
                "task": original_task,
                "error": "All steps failed",
                "failed_steps": failed_steps,
                "formatted_result": None
            }

        # Format the final answer
        prompt = f"""
        You are a Verification Agent. Format the following execution results into a clear, 
        structured answer for the original user task.

        Original Task: {original_task}

        Execution Results:
        {self._format_results(execution_results)}

        Format the final answer as a JSON with this structure:
        {{
            "summary": "Brief summary of what was accomplished",
            "data": {{ "key_results": "from the execution" }},
            "details": ["Detailed", "information", "in", "list", "format"],
            "status": "success/partial",
            "notes": "Any important notes or limitations"
        }}

        Rules:
        1. Include all relevant information from the results
        2. Structure the data logically
        3. Handle partial failures gracefully
        4. Be concise but complete
        5. Return ONLY valid JSON, no other text
        """

        messages = [
            {"role": "system", "content": "You are a helpful verification assistant that formats execution results."},
            {"role": "user", "content": prompt}
        ]

        formatted_result = self.llm_client.generate_json(messages, temperature=Config.VERIFIER_TEMPERATURE)

        # Determine final status
        status = "partial" if failed_steps else "success"

        return {
            "status": status,
            "task": original_task,
            "failed_steps": failed_steps if failed_steps else [],
            "formatted_result": formatted_result
        }

    def _format_results(self, results: List[Dict[str, Any]]) -> str:
        """Format execution results for the LLM prompt"""
        formatted = []
        for result in results:
            step_info = f"Step {result['step']}: "
            if result["success"]:
                step_info += f"Success - {result['result']}"
            else:
                step_info += f"Failed - {result['error']}"
            formatted.append(step_info)

        return "\n".join(formatted)