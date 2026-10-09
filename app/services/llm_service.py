import json
import re
from typing import Any, Literal

from groq import Groq

from app.config import get_settings
from app.schemas import QuizResponse, StudyPlanResponse, SummaryResponse


class LLMConfigurationError(RuntimeError):
    """Raised when the environment is missing a functioning Groq configuration."""


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = Groq(api_key=self.settings.groq_api_key) if self.settings.groq_api_key else None

    def is_configured(self) -> bool:
        return bool(self.settings.groq_api_key and self.settings.groq_model)

    def _require_configuration(self) -> None:
        if not self.is_configured():
            raise LLMConfigurationError(
                "Groq is not configured. Add GROQ_API_KEY and GROQ_MODEL to your .env file before using AI features."
            )

    @staticmethod
    def _extract_json(content: str | None) -> dict[str, Any]:
        if not content:
            raise ValueError("The model returned an empty response.")

        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                return parsed
            raise ValueError("The model response was not a JSON object.")
        except json.JSONDecodeError as exc:
            raise ValueError("The model returned malformed JSON.") from exc

    def chat_completion(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None, tool_choice: str | None = None):
        self._require_configuration()
        payload: dict[str, Any] = {
            "model": self.settings.groq_model,
            "messages": messages,
            "temperature": 0.7,
        }
        if tools:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        return self.client.chat.completions.create(**payload)

    async def generate_study_plan(self, subject: str, days: int, level: str, daily_minutes: int, notes: str | None = None) -> StudyPlanResponse:
        self._require_configuration()
        prompt = f"""
        Create a realistic study plan for {subject}.
        Requirements:
        - Days: {days}
        - Skill level: {level}
        - Daily study minutes: {daily_minutes}
        - Notes: {notes or 'None'}
        Return valid JSON only with this exact structure:
        {{
          "subject": "...",
          "days": {days},
          "level": "{level}",
          "daily_minutes": {daily_minutes},
          "notes": "...",
          "plan": [
            {{"day": 1, "focus": "...", "tasks": ["..."], "minutes": 45}},
            ...
          ]
        }}
        """
        response = self.client.chat.completions.create(
            model=self.settings.groq_model,
            messages=[
                {"role": "system", "content": "You are an expert study planner. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
        )
        data = self._extract_json(response.choices[0].message.content)
        return StudyPlanResponse.model_validate(data)

    async def summarize_text(self, text: str, style: Literal["Short summary", "Detailed summary", "Important points"]) -> SummaryResponse:
        self._require_configuration()
        response = self.client.chat.completions.create(
            model=self.settings.groq_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a study assistant that summarizes notes clearly and accurately. Return only the summary text.",
                },
                {
                    "role": "user",
                    "content": f"Create a {style.lower()} for the following notes:\n\n{text}",
                },
            ],
            temperature=0.5,
        )
        summary_text = response.choices[0].message.content or "No summary available."
        return SummaryResponse(summary=summary_text)

    async def generate_quiz(self, material: str, question_count: int) -> dict[str, Any]:
        self._require_configuration()
        prompt = f"""
        Generate {question_count} multiple-choice questions from this study material.
        Return valid JSON only with this shape:
        {{
          "questions": [
            {{
              "question": "...",
              "options": ["A", "B", "C", "D"],
              "correct_answer": "A",
              "explanation": "..."
            }}
          ]
        }}
        Study material:
        {material}
        """
        response = self.client.chat.completions.create(
            model=self.settings.groq_model,
            messages=[
                {"role": "system", "content": "You are a quiz generator. Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
        data = self._extract_json(response.choices[0].message.content)
        validated = QuizResponse.model_validate(data)
        return validated.model_dump()


llm_service = LLMService()
