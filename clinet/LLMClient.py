import httpx
import openai

class LLMClient:
    def __init__(self, api_key, base_url, model):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = openai.Client(api_key=self.api_key, base_url=self.base_url)

    def completions(self, messages, max_tokens=8192, temperature=0, top_p=1, stream=False, frequency_penalty=0.2, presence_penalty=0.1):
        response = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stream=stream,
            top_p=top_p,
            timeout=httpx.Timeout(240.0)
        )
        return response.choices[0].message.content
