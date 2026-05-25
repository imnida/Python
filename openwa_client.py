"""
Client Python pour OpenWA - WhatsApp API Gateway auto-hébergé.
Docs: https://github.com/rmyndharis/OpenWA
"""

import os
import mimetypes
import base64
import requests


class OpenWAClient:
    """Enveloppe HTTP pour l'API REST OpenWA."""

    def __init__(self, base_url: str, api_key: str, session_id: str = "default"):
        """
        Args:
            base_url:   URL de votre instance OpenWA, ex. "http://localhost:3000"
            api_key:    Valeur de l'en-tête X-API-Key
            session_id: Identifiant de session WhatsApp (par défaut "default")
        """
        self.base_url = base_url.rstrip("/")
        self.session_id = session_id
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key, "Content-Type": "application/json"})

    # ------------------------------------------------------------------
    # Primitives
    # ------------------------------------------------------------------

    def _url(self, path: str) -> str:
        return f"{self.base_url}/sessions/{self.session_id}/{path}"

    def _post(self, path: str, payload: dict) -> dict:
        response = self.session.post(self._url(path), json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # Messages texte
    # ------------------------------------------------------------------

    def send_text(self, chat_id: str, text: str) -> dict:
        """Envoie un message texte à un contact ou groupe WhatsApp.

        Args:
            chat_id: Numéro international sans '+', ex. "33612345678@c.us"
                     Pour un groupe : "<id_groupe>@g.us"
            text:    Corps du message
        """
        return self._post("messages/send-text", {"chatId": chat_id, "text": text})

    # ------------------------------------------------------------------
    # Documents / fichiers
    # ------------------------------------------------------------------

    def send_document(self, chat_id: str, file_path: str, caption: str = "") -> dict:
        """Envoie un fichier (PDF, DOCX, etc.) encodé en base64.

        Args:
            chat_id:   Destinataire WhatsApp
            file_path: Chemin local vers le fichier à envoyer
            caption:   Légende optionnelle affichée sous le document
        """
        mime, _ = mimetypes.guess_type(file_path)
        mime = mime or "application/octet-stream"
        filename = os.path.basename(file_path)

        with open(file_path, "rb") as f:
            data_b64 = base64.b64encode(f.read()).decode()

        payload = {
            "chatId": chat_id,
            "file": {
                "mimetype": mime,
                "filename": filename,
                "data": data_b64,
            },
            "caption": caption,
        }
        return self._post("messages/send-file", payload)

    # ------------------------------------------------------------------
    # Utilitaires pipeline
    # ------------------------------------------------------------------

    def send_job_result(
        self,
        chat_id: str,
        match_pct: float,
        resume_path: str | None = None,
        job_title: str = "ce poste",
    ) -> None:
        """Notifie le résultat d'analyse de job et envoie optionnellement le CV.

        Args:
            chat_id:     Destinataire WhatsApp
            match_pct:   Score de similarité en pourcentage (0-100)
            resume_path: Chemin local du CV à joindre (optionnel)
            job_title:   Intitulé du poste analysé
        """
        emoji = "✅" if match_pct >= 60 else "⚠️" if match_pct >= 40 else "❌"
        message = (
            f"{emoji} *Analyse de candidature — {job_title}*\n\n"
            f"Score de correspondance : *{match_pct:.1f} %*\n\n"
        )
        if match_pct >= 60:
            message += "Votre profil correspond bien à l'offre. Bonne candidature !"
        elif match_pct >= 40:
            message += "Profil partiellement aligné. Pensez à adapter votre CV."
        else:
            message += "Profil peu aligné avec cette offre. Consultez les compétences manquantes."

        self.send_text(chat_id, message)

        if resume_path:
            self.send_document(
                chat_id,
                resume_path,
                caption=f"CV analysé pour : {job_title}",
            )
