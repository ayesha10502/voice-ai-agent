"""
VapiService — wraps the Vapi REST API.

Vapi docs: https://docs.vapi.ai
"""
import httpx
import logging
from typing import Any, Optional

from app.core.config import get_settings
from app.core.scenarios import get_scenario

logger = logging.getLogger(__name__)
settings = get_settings()


class VapiError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class VapiService:
    def __init__(self):
        self.base_url = settings.vapi_base_url
        self.api_key = settings.vapi_api_key
        self.phone_number_id = settings.vapi_phone_number_id

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_assistant_payload(
        self,
        scenario_id: str,
        customer_name: Optional[str] = None,
        additional_context: Optional[str] = None,
    ) -> dict[str, Any]:
        scenario = get_scenario(scenario_id)
        if not scenario:
            raise VapiError(f"Unknown scenario: {scenario_id}", 400)

        system_prompt = scenario["systemPrompt"]

        # Inject customer name if provided
        if customer_name:
            system_prompt = (
                f"The customer's name is {customer_name}. "
                f"Use their name naturally in the conversation.\n\n"
                + system_prompt
            )

        # Inject any extra context
        if additional_context:
            system_prompt += f"\n\nAdditional context:\n{additional_context}"

        first_message = scenario["firstMessage"]
        if customer_name:
            # Personalise the greeting
            first_message = first_message.replace(
                "Hello!", f"Hello {customer_name}!"
            ).replace("Hi!", f"Hi {customer_name}!")

        return {
            "name": f"{scenario['agent']['name']} - {scenario['name']}",
            "model": {
                "provider": "groq",
                "model": "llama-3.3-70b-versatile",
                "systemPrompt": system_prompt,
                "temperature": 0.7,
            },
            "voice": {
                "provider": "vapi",
                "voiceId": "Elliot",  # ElevenLabs "Sarah" — warm, professional
            },
            "firstMessage": first_message,
            "firstMessageMode": "assistant-speaks-first",
            "endCallMessage": "Thank you for your time. Have a wonderful day! Goodbye.",
            "endCallPhrases": [
                "goodbye",
                "bye",
                "take care",
                "have a good day",
                "thanks, bye",
            ],
            "silenceTimeoutSeconds": 20,
            "maxDurationSeconds": 600,  # 10-minute max call
            "backgroundSound": "office",
            "backchannelingEnabled": True,
            "backgroundDenoisingEnabled": True,
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "en",
            },
        }

    async def initiate_call(
        self,
        phone_number: str,
        scenario_id: str,
        customer_name: Optional[str] = None,
        additional_context: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Create an outbound call via Vapi's /call endpoint.
        Returns the Vapi call object.
        """
        if not self.api_key:
            raise VapiError(
                "VAPI_API_KEY is not configured. Please set it in your .env file.",
                503,
            )
        if not self.phone_number_id:
            raise VapiError(
                "VAPI_PHONE_NUMBER_ID is not configured. Please set it in your .env file.",
                503,
            )

        assistant = self._build_assistant_payload(
            scenario_id, customer_name, additional_context
        )

        payload = {
            "phoneNumberId": self.phone_number_id,
            "customer": {
                "number": phone_number,
                **({"name": customer_name} if customer_name else {}),
            },
            "assistant": assistant,
        }

        # Attach webhook if configured
        webhook_url = settings.webhook_base_url
        if webhook_url:
            payload["assistantOverrides"] = {
                "serverUrl": f"{webhook_url}/api/webhook/vapi",
            }

        logger.info(
            f"Initiating Vapi call to {phone_number} for scenario {scenario_id}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/call",
                headers=self._headers,
                json=payload,
            )

        if response.status_code not in (200, 201):
            error_detail = response.text
            logger.error(
                f"Vapi API error {response.status_code}: {error_detail}")
            raise VapiError(
                f"Vapi API returned {response.status_code}: {error_detail}",
                response.status_code,
            )

        return response.json()

    async def get_call(self, call_id: str) -> dict[str, Any]:
        """Fetch call details from Vapi."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{self.base_url}/call/{call_id}",
                headers=self._headers,
            )

        if response.status_code == 404:
            raise VapiError(f"Call {call_id} not found", 404)
        if response.status_code != 200:
            raise VapiError(
                f"Vapi API error: {response.text}", response.status_code)

        return response.json()

    async def end_call(self, call_id: str) -> dict[str, Any]:
        """Terminate an active call."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.delete(
                f"{self.base_url}/call/{call_id}",
                headers=self._headers,
            )

        if response.status_code not in (200, 204):
            raise VapiError(
                f"Failed to end call: {response.text}", response.status_code)

        return {"success": True, "call_id": call_id}

    async def list_calls(self, limit: int = 20) -> list[dict[str, Any]]:
        """List recent calls from Vapi."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{self.base_url}/call",
                headers=self._headers,
                params={"limit": limit},
            )

        if response.status_code != 200:
            raise VapiError(
                f"Failed to list calls: {response.text}", response.status_code)

        return response.json()


# Singleton
vapi_service = VapiService()
