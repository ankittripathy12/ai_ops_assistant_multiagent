from typing import Dict, Any, List
import json
import sys
import groq
from config import Config


class LLMClient:
    def __init__(self):
        # Check which provider to use
        if hasattr(Config, 'GROQ_API_KEY') and Config.GROQ_API_KEY:
            self.provider = "groq"
            self.api_key = Config.GROQ_API_KEY
            self.model = Config.GROQ_MODEL if hasattr(Config, 'GROQ_MODEL') else "mixtral-8x7b-32768"
            print(f" Using Groq provider with model: {self.model}")

        else:
            print(" ERROR: No API key found for any LLM provider!")
            print("   Please set either GROQ_API_KEY or OPENAI_API_KEY in .env")
            sys.exit(1)

    def generate_completion(self,
                            messages: List[Dict[str, str]],
                            temperature: float = 0.1,
                            response_format: Dict[str, Any] = None) -> str:
        """Generate completion from LLM"""
        try:
            if self.provider == "groq":
                return self._generate_groq_completion(messages, temperature, response_format)
            else:
                return self._generate_openai_completion(messages, temperature, response_format)
        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")

    def _generate_groq_completion(self,
                                  messages: List[Dict[str, str]],
                                  temperature: float,
                                  response_format: Dict[str, Any] = None) -> str:
        """Generate completion using Groq API"""


        client = groq.Groq(api_key=self.api_key)

        # Groq doesn't have direct response_format parameter like OpenAI
        # We need to add it to the system message
        if response_format and response_format.get("type") == "json_object":
            # Add JSON instruction to the first system message
            if messages and messages[0]["role"] == "system":
                messages[0][
                    "content"] += "\n\nIMPORTANT: You MUST respond with valid JSON only. Do not include any other text, explanations, or markdown formatting."
            else:
                messages.insert(0, {
                    "role": "system",
                    "content": "You MUST respond with valid JSON only. Do not include any other text, explanations, or markdown formatting."
                })

        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=False
        )

        return response.choices[0].message.content

    def generate_json(self,
                      messages: List[Dict[str, str]],
                      temperature: float = 0.1) -> Dict[str, Any]:
        """Generate JSON response from LLM"""
        try:
            content = self.generate_completion(messages, temperature)

            # Try to extract JSON if it's wrapped in markdown
            import re
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)

            # Remove any non-JSON text before/after
            json_match = re.search(r'(\{.*\})', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)

            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"  Raw LLM response that failed to parse: {content[:200]}...")
            raise Exception(f"Failed to parse LLM response as JSON: {str(e)}")