"""
Python client for the OpenWA API Gateway.
OpenWA is an open-source WhatsApp HTTP API (https://github.com/rmyndharis/OpenWA).

Usage:
    client = OpenWAClient("http://localhost:2785/api", api_key="your-api-key")
    client.sessions.create("my-session")
    client.messages.send_text("my-session", "62812345678@c.us", "Hello!")
"""

import base64
from pathlib import Path
from typing import Any

import requests


class OpenWAError(Exception):
    def __init__(self, status_code: int, message: str, data: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.data = data


class _Base:
    def __init__(self, session: requests.Session, base_url: str):
        self._session = session
        self._base = base_url.rstrip("/")

    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self._base}{path}"
        resp = self._session.request(method, url, **kwargs)
        try:
            body = resp.json()
        except Exception:
            body = {}
        if not resp.ok:
            msg = body.get("message") or resp.reason
            raise OpenWAError(resp.status_code, msg, body.get("data"))
        return body.get("data", body)


class Sessions(_Base):
    def create(self, session_id: str, webhooks: list[str] | None = None) -> dict:
        payload: dict = {"sessionId": session_id}
        if webhooks:
            payload["webhooks"] = webhooks
        return self._request("POST", "/sessions", json=payload)

    def list(self, page: int = 1, limit: int = 20) -> dict:
        return self._request("GET", "/sessions", params={"page": page, "limit": limit})

    def get(self, session_id: str) -> dict:
        return self._request("GET", f"/sessions/{session_id}")

    def get_qr(self, session_id: str) -> dict:
        return self._request("GET", f"/sessions/{session_id}/qr")

    def logout(self, session_id: str) -> dict:
        return self._request("POST", f"/sessions/{session_id}/logout")

    def delete(self, session_id: str) -> dict:
        return self._request("DELETE", f"/sessions/{session_id}")


class Messages(_Base):
    def send_text(self, session_id: str, to: str, text: str) -> dict:
        return self._request("POST", "/messages/send-text", json={
            "sessionId": session_id,
            "to": to,
            "text": text,
        })

    def send_image(
        self,
        session_id: str,
        to: str,
        image: str,
        caption: str = "",
        as_url: bool = True,
    ) -> dict:
        media = image if as_url else _encode_file(image)
        return self._request("POST", "/messages/send-image", json={
            "sessionId": session_id,
            "to": to,
            "image": media,
            "caption": caption,
        })

    def send_video(
        self,
        session_id: str,
        to: str,
        video: str,
        caption: str = "",
        as_url: bool = True,
    ) -> dict:
        media = video if as_url else _encode_file(video)
        return self._request("POST", "/messages/send-video", json={
            "sessionId": session_id,
            "to": to,
            "video": media,
            "caption": caption,
        })

    def send_audio(
        self,
        session_id: str,
        to: str,
        audio: str,
        as_voice_note: bool = False,
        as_url: bool = True,
    ) -> dict:
        media = audio if as_url else _encode_file(audio)
        return self._request("POST", "/messages/send-audio", json={
            "sessionId": session_id,
            "to": to,
            "audio": media,
            "asVoiceNote": as_voice_note,
        })

    def send_document(
        self,
        session_id: str,
        to: str,
        document: str,
        filename: str = "",
        as_url: bool = True,
    ) -> dict:
        media = document if as_url else _encode_file(document)
        return self._request("POST", "/messages/send-document", json={
            "sessionId": session_id,
            "to": to,
            "document": media,
            "filename": filename,
        })

    def send_bulk(self, session_id: str, recipients: list[str], text: str) -> dict:
        return self._request("POST", "/messages/send-bulk", json={
            "sessionId": session_id,
            "recipients": recipients,
            "text": text,
        })

    def get_batch_status(self, batch_id: str) -> dict:
        return self._request("GET", f"/messages/batch/{batch_id}")


class Contacts(_Base):
    def list(self, session_id: str) -> dict:
        return self._request("GET", "/contacts", params={"sessionId": session_id})

    def check(self, session_id: str, phone: str) -> dict:
        return self._request(
            "GET", f"/contacts/check/{phone}", params={"sessionId": session_id}
        )


class Groups(_Base):
    def list(self, session_id: str) -> dict:
        return self._request("GET", "/groups", params={"sessionId": session_id})

    def get(self, session_id: str, group_id: str) -> dict:
        return self._request(
            "GET", f"/groups/{group_id}", params={"sessionId": session_id}
        )

    def create(self, session_id: str, name: str, participants: list[str]) -> dict:
        return self._request("POST", "/groups", json={
            "sessionId": session_id,
            "name": name,
            "participants": participants,
        })


class Webhooks(_Base):
    def register(self, session_id: str, url: str, events: list[str] | None = None) -> dict:
        payload: dict = {"sessionId": session_id, "url": url}
        if events:
            payload["events"] = events
        return self._request("POST", "/webhooks", json=payload)

    def list(self, session_id: str) -> dict:
        return self._request("GET", "/webhooks", params={"sessionId": session_id})

    def delete(self, webhook_id: str) -> dict:
        return self._request("DELETE", f"/webhooks/{webhook_id}")


def _encode_file(path: str) -> str:
    data = Path(path).read_bytes()
    return "data:application/octet-stream;base64," + base64.b64encode(data).decode()


class OpenWAClient:
    """
    Top-level client for the OpenWA API.

    Args:
        base_url: Base URL of the OpenWA server, e.g. "http://localhost:2785/api"
        api_key:  API key for authentication (X-API-Key header)
        timeout:  Request timeout in seconds (default 30)
    """

    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self._http = requests.Session()
        self._http.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        })
        self._http.request = _wrap_timeout(self._http.request, timeout)

        self.sessions = Sessions(self._http, base_url)
        self.messages = Messages(self._http, base_url)
        self.contacts = Contacts(self._http, base_url)
        self.groups = Groups(self._http, base_url)
        self.webhooks = Webhooks(self._http, base_url)

    def close(self):
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def _wrap_timeout(original_request, timeout: int):
    def request(method, url, **kwargs):
        kwargs.setdefault("timeout", timeout)
        return original_request(method, url, **kwargs)
    return request


if __name__ == "__main__":
    import os

    BASE_URL = os.getenv("OPENWA_URL", "http://localhost:2785/api")
    API_KEY = os.getenv("OPENWA_API_KEY", "your-api-key")
    SESSION = "demo-session"
    RECIPIENT = "628123456789@c.us"

    with OpenWAClient(BASE_URL, API_KEY) as client:
        print("Creating session...")
        client.sessions.create(SESSION)

        print("QR code (scan with WhatsApp):", client.sessions.get_qr(SESSION))

        print("Sending message...")
        result = client.messages.send_text(SESSION, RECIPIENT, "Hello from OpenWA Python client!")
        print("Sent:", result)
