import httpx
from typing import List, Dict
from config import config
import logging

logger = logging.getLogger(__name__)


class LLMHandler:
    def __init__(self):
        self.llm_type = config.LLM_TYPE
        self.session = httpx.AsyncClient(timeout=config.TIMEOUT)

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        try:
            if self.llm_type == "deepseek":
                return await self._call_deepseek(messages)
            elif self.llm_type == "qwen":
                return await self._call_qwen(messages)
            else:
                raise ValueError(f"Unsupported LLM type: {self.llm_type}")
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Sorry, I encountered an error while processing your request."

    async def _call_deepseek(self, messages: List[Dict[str, str]]) -> str:
        headers = {
            "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }

        response = await self.session.post(
            config.DEEPSEEK_API_URL,
            headers=headers,
            json=payload
        )

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def _call_qwen(self, messages: List[Dict[str, str]]) -> str:
        headers = {
            "Authorization": f"Bearer {config.QWEN_API_KEY}",
            "Content-Type": "application/json"
        }

        # Qwen expects the last message as input
        last_message = messages[-1]["content"]
        payload = {
            "model": "qwen-max",
            "input": {
                "messages": [
                    {"role": "user", "content": last_message}
                ]
            },
            "parameters": {
                "temperature": 0.7,
                "max_length": 2000
            }
        }

        response = await self.session.post(
            config.QWEN_API_URL,
            headers=headers,
            json=payload
        )

        response.raise_for_status()
        data = response.json()
        return data["output"]["text"]

    async def close(self):
        await self.session.aclose()
