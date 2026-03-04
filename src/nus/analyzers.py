"""Provider-specific article analyzer implementations."""

import asyncio
from dataclasses import dataclass

import anthropic

from .base_analyzer import BaseAnalyzer
from .exceptions import AnalysisError
from .models import AnalysisResult, Article


@dataclass(frozen=True)
class AnalyzerConfig:
    """Configuration bundle for analyzer initialization."""

    api_key: str
    model: str
    max_tokens: int
    temperature: float
    max_concurrent: int


class AnthropicAnalyzer(BaseAnalyzer):
    """Claude-powered article analyzer."""

    def __init__(self, config: AnalyzerConfig) -> None:
        super().__init__(
            model=config.model,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            max_concurrent=config.max_concurrent,
        )
        self.client = anthropic.AsyncAnthropic(api_key=config.api_key)

    async def _analyze_article(
        self, article: Article, filter_clickbait: bool = True
    ) -> AnalysisResult:
        """Analyze a single article with Claude."""
        async with self.semaphore:
            prompt = self._build_prompt(article)

            try:
                message = await self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": prompt}],
                )

                # Parse structured response
                response_text = message.content[0].text
                parsed = self._parse_response(response_text)

                return AnalysisResult(
                    article=article,
                    category=parsed["category"],
                    is_clickbait=parsed["is_clickbait"],
                    confidence=parsed["confidence"],
                    reasoning=parsed.get("reasoning"),
                )

            except Exception as e:
                raise AnalysisError(f"Claude API error: {e}")


class GeminiAnalyzer(BaseAnalyzer):
    """Gemini-powered article analyzer."""

    def __init__(self, config: AnalyzerConfig) -> None:
        super().__init__(
            model=config.model,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            max_concurrent=config.max_concurrent,
        )
        import google.generativeai as genai

        genai.configure(api_key=config.api_key)
        self.client = genai.GenerativeModel(config.model)
        self.genai = genai

    async def _analyze_article(
        self, article: Article, filter_clickbait: bool = True
    ) -> AnalysisResult:
        """Analyze a single article with Gemini."""
        async with self.semaphore:
            prompt = self._build_prompt(article)

            try:
                # google-generativeai is sync, so use asyncio.to_thread
                response = await asyncio.to_thread(
                    self._call_gemini,
                    prompt,
                )

                # Parse structured response
                parsed = self._parse_response(response)

                return AnalysisResult(
                    article=article,
                    category=parsed["category"],
                    is_clickbait=parsed["is_clickbait"],
                    confidence=parsed["confidence"],
                    reasoning=parsed.get("reasoning"),
                )

            except Exception as e:
                raise AnalysisError(f"Gemini API error: {e}")

    def _call_gemini(self, prompt: str) -> str:
        """Synchronous wrapper for Gemini API call."""
        generation_config = self.genai.types.GenerationConfig(
            max_output_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        response = self.client.generate_content(
            prompt,
            generation_config=generation_config,
        )
        # Extract text from response, handling multiple content blocks
        if hasattr(response, "text"):
            return response.text
        # Fallback: concatenate text from parts
        text_parts = []
        for part in response.parts:
            if hasattr(part, "text"):
                text_parts.append(part.text)
        if not text_parts:
            raise AnalysisError("No text content in Gemini response")
        return "".join(text_parts)
