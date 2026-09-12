import os

from groq import Groq


LESSON_PLAN_SCHEMA = {
    "name": "lesson_plan",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "lesson_information": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "curriculum": {"type": "string"},
                    "grade": {"type": "string"},
                    "subject": {"type": "string"},
                    "topic": {"type": "string"},
                    "duration_minutes": {"type": "integer"},
                    "language": {"type": "string"}
                },
                "required": [
                    "curriculum",
                    "grade",
                    "subject",
                    "topic",
                    "duration_minutes",
                    "language"
                ]
            },

            "learning_objectives": {
                "type": "array",
                "items": {"type": "string"}
            },

            "prior_knowledge": {
                "type": "string"
            },

            "materials": {
                "type": "array",
                "items": {"type": "string"}
            },

            "lesson_sequence": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "stage": {"type": "string"},
                        "duration_minutes": {"type": "integer"},
                        "teacher_activity": {"type": "string"},
                        "student_activity": {"type": "string"},
                        "assessment_check": {"type": "string"}
                    },
                    "required": [
                        "stage",
                        "duration_minutes",
                        "teacher_activity",
                        "student_activity",
                        "assessment_check"
                    ]
                }
            },

            "assessment": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "formative": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "summative": {
                        "type": "string"
                    }
                },
                "required": [
                    "formative",
                    "summative"
                ]
            },

            "differentiation": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "support": {"type": "string"},
                    "extension": {"type": "string"}
                },
                "required": [
                    "support",
                    "extension"
                ]
            },

            "homework": {
                "type": "string"
            },

            "teacher_notes": {
                "type": "string"
            }
        },

        "required": [
            "lesson_information",
            "learning_objectives",
            "prior_knowledge",
            "materials",
            "lesson_sequence",
            "assessment",
            "differentiation",
            "homework",
            "teacher_notes"
        ]
    }
}


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
        """Generate a structured lesson plan from Groq."""

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

                response_format={
                    "type": "json_schema",
                    "json_schema": LESSON_PLAN_SCHEMA
                }
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
