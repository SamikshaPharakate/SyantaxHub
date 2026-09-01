import logging
import httpx
from config import settings

logger = logging.getLogger("llm_provider")

class LLMProvider:
    def __init__(self):
        self.openrouter_key = settings.openrouter_api_key
        self.openrouter_model = settings.openrouter_model
        self.gemini_key = settings.gemini_api_key
        self.openai_key = settings.openai_api_key

    def generate_response(self, prompt: str, system_instruction: str = "") -> str:
        # 1. OpenRouter Integration (Primary)
        if self.openrouter_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "HTTP-Referer": settings.site_url,
                    "X-Title": settings.site_name,
                    "Content-Type": "application/json"
                }
                
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})

                payload = {
                    "model": self.openrouter_model,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 1500
                }

                with httpx.Client(timeout=40.0) as client:
                    response = client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.warning(f"OpenRouter API error [{response.status_code}]: {response.text}")
            except Exception as e:
                logger.warning(f"OpenRouter request failed: {e}")

        # 2. Google Gemini Fallback
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
                res = model.generate_content(full_prompt)
                return res.text
            except Exception as e:
                logger.warning(f"Gemini API invocation failed: {e}")

        # 3. OpenAI Direct Fallback
        if self.openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_key)
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})
                res = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                return res.choices[0].message.content
            except Exception as e:
                logger.warning(f"OpenAI API invocation failed: {e}")

        # 4. Fallback Synthesizer if API keys are not provided yet in env
        return f"[SyntaxHub AI Analysis Engine]\nQuery: '{prompt[:120]}...'\n\nNote: Provide your OPENROUTER_API_KEY in services/.env for live LLM analysis using models like {self.openrouter_model}."

llm_provider = LLMProvider()
