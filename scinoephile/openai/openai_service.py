#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Service for interacting with OpenAI API."""
from __future__ import annotations

import json

from openai import OpenAI
from pydantic import BaseModel


class OpenAiService:
    """Service for interacting with OpenAI API."""

    def __init__(self, model: str = "gpt-4o", temperature: float = 1.0):
        """Initalize.

        Arguments:
            model: OpenAI model to use
            temperature: Temperature to use when generating completions
        """
        self.model = model
        self.temperature = temperature
        self.client = OpenAI()

    def get_transcription(self, base64_image: str, language: str = "English") -> str:
        """Get transcription of text from an image.

        Arguments:
            base64_image: Image to transcribe
            language: Language of text in image
        Returns:
            Transcription of text from image
        """
        # Prepare query
        prompt = (
            "Transcribe the text in the following image. "
            f"The text is in {language}. "
            "Your responsibility is to match the text in the image; do not correct "
            "errors in the image text. "
            "If the image includes newlines, remove them. "
            "For colons, use a full-width colon (：). "
            "For commas, use a full-width comma (，). "
            "For ellipses, use three standard periods (...). "
            "For exclamation marks, use a full-width exclamation mark (！). "
            "For question marks, use a full-width question mark (？). "
            "Your response must be JSON; fill in the following template:\n"
            f"{json.dumps(self.TranscriptionModel.model_json_schema(), indent=4)}"
        )
        content = [
            {
                "type": "text",
                "text": prompt,
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}",
                    "detail": "high",
                },
            },
        ]

        # Query API
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            temperature=self.temperature,
            response_format=self.TranscriptionModel,
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
        )

        # Validate and return results
        message = completion.choices[0].message
        content = message.content
        response = self.TranscriptionModel.model_validate_json(content)
        transcription = response.model_dump()["transcription"].strip()
        return transcription

    def get_revision(
        self, base64_image: str, current_text: str, language: str = "English"
    ) -> str:
        """Get revised transcription of text from an image.

        Arguments:
            base64_image: Image to transcribe
            current_text: Current transcription of text from image
            language: Language of text in image
        Returns:
            Revised transcription of text from image
        """
        # Prepare query
        current_transcription = json.dumps({"transcription": current_text}, indent=4)
        prompt = (
            "Double-check and revise the transcription of the attached image. "
            f"The text is in {language}. "
            "Your responsibility is to match the text in the image; do not correct "
            "errors in the image text, only errors in transcription. "
            "If the image contains newlines, remove them. "
            "For colons, use a full-width colon (：). "
            "For commas, use a full-width comma (，). "
            "For ellipses, use three standard periods (...). "
            "For exclamation marks, use a full-width exclamation mark (！). "
            "For question marks, use a full-width question mark (？). "
            "Here is the current transcription:\n\n"
            f"{current_transcription}\n\n"
            "Respond with the revised transcription in the exact same JSON format."
        )

        # Query API
        content = [
            {
                "type": "text",
                "text": prompt,
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}",
                    "detail": "high",
                },
            },
        ]
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            temperature=self.temperature,
            response_format=self.TranscriptionModel,
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
        )

        # Validate and return results
        message = completion.choices[0].message
        content = message.content
        response = self.TranscriptionModel.model_validate_json(content)
        transcription = response.model_dump()["transcription"].strip()
        return transcription

    def get_chinese_revision_pair(
        self,
        simp_base64_image: str,
        simp_transcription: str,
        trad_base64_image: str,
        trad_transcription: str,
    ) -> tuple[str, str]:
        """Get revised transcription of Simplified and Chinese text from images of each.

        Arguments:
            simp_base64_image: Simplified Chinese image to transcribe
            simp_transcription: Current transcription of Simplified Chinese text
            trad_base64_image: Traditional Chinese image to transcribe
            trad_transcription: Current transcription of Traditional Chinese text
        Returns:
            Revised transcriptions of Simplified and Traditional Chinese text
        """
        # Prepare query
        current_transcriptions = json.dumps(
            {
                "simp_transcription": simp_transcription,
                "trad_transcription": trad_transcription,
            },
            indent=4,
        )
        prompt = (
            "Double-check and revise the transcriptions of the attached images. "
            "The first image is Simplified Chinese, and the second image is "
            "Traditional Chinese. "
            "They contain the same content, just in different scripts. "
            "The transcriptions should be the same length and differ only in script, "
            "with simp_transcription containing Simplified Chinese text and "
            "trad_transcription containing Traditional Chinese text. "
            "If the images contain newlines, remove them. "
            "For colons, use a full-width colon (：). "
            "For commas, use a full-width comma (，). "
            "For ellipses, use three standard periods (...). "
            "For exclamation marks, use a full-width exclamation mark (！). "
            "For question marks, use a full-width question mark (？). "
            "Here are the current transcriptions:\n\n"
            f"{current_transcriptions}\n\n"
            "Respond with the revised transcriptions in the exact same JSON format."
        )

        # Query API
        content = [
            {
                "type": "text",
                "text": prompt,
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{simp_base64_image}",
                    "detail": "high",
                },
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{trad_base64_image}",
                    "detail": "high",
                },
            },
        ]
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            temperature=self.temperature,
            response_format=self.TranscriptionPairModel,
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
        )

        # Validate and return results
        message = completion.choices[0].message
        content = message.content
        response = self.TranscriptionPairModel.model_validate_json(content)
        simp_transcription = response.model_dump()["simp_transcription"].strip()
        trad_transcription = response.model_dump()["trad_transcription"].strip()
        return simp_transcription, trad_transcription

    class TranscriptionModel(BaseModel):
        """Model for transcribing text from images."""

        transcription: str
        """Transcription of text from image."""

    class TranscriptionPairModel(BaseModel):
        """Model for transcribing text from pair of images."""

        simp_transcription: str
        """Transcription of Simplified Chinese text from image"""
        trad_transcription: str
        """Transcription of Traditional Chinese text from image."""
