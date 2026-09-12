import os

from groq import Groq


class GroqService:
    """Service responsible for communication with the Groq API."""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(api_key=self.api_key)

    def generate_response(
        self,
        prompt,
        model="openai/gpt-oss-120b",
        temperature=0.3,
        max_tokens=4000,
    ):
        """Generate an AI response from Groq."""

        if not prompt or not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            if not response.choices:
                raise RuntimeError(
                    "Groq returned an empty response."
                )

            content = response.choices[0].message.content

            if not content:
                raise RuntimeError(
                    "Groq returned empty content."
                )

            return content.strip()

        except Exception as e:
            raise RuntimeError(
                f"Groq API request failed: {str(e)}"
            ) from e
