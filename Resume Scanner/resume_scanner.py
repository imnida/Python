# -*- coding: utf-8 -*-
"""
Pipeline d'analyse de similarité CV / offre d'emploi
avec notification WhatsApp via OpenWA.

Usage local :
    python resume_scanner.py \
        --resume python_resume.docx \
        --job job_description.docx \
        --chat 33612345678@c.us \
        --openwa-url http://localhost:3000 \
        --api-key VOTRE_CLE

Variables d'environnement alternatives :
    OPENWA_URL, OPENWA_API_KEY, OPENWA_SESSION
"""

import argparse
import os
import sys

import docx2txt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Le client OpenWA est un module local à la racine du projet
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from openwa_client import OpenWAClient


# ---------------------------------------------------------------------------
# Analyse
# ---------------------------------------------------------------------------

def compute_match(resume_path: str, job_path: str) -> float:
    """Retourne le score de similarité cosinus en pourcentage (0-100)."""
    resume = docx2txt.process(resume_path)
    job_desc = docx2txt.process(job_path)

    cv = CountVectorizer()
    matrix = cv.fit_transform([resume, job_desc])
    score = cosine_similarity(matrix)[0][1] * 100
    return round(score, 2)


# ---------------------------------------------------------------------------
# Notification WhatsApp
# ---------------------------------------------------------------------------

def notify_whatsapp(
    match_pct: float,
    resume_path: str,
    chat_id: str,
    openwa_url: str,
    api_key: str,
    session_id: str = "default",
    job_title: str = "ce poste",
    send_resume: bool = True,
) -> None:
    client = OpenWAClient(openwa_url, api_key, session_id)
    client.send_job_result(
        chat_id=chat_id,
        match_pct=match_pct,
        resume_path=resume_path if send_resume else None,
        job_title=job_title,
    )
    print(f"[WhatsApp] Notification envoyée à {chat_id}")


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Scanner de CV vs offre d'emploi")
    p.add_argument("--resume", required=True, help="Chemin du CV (.docx)")
    p.add_argument("--job", required=True, help="Chemin de la fiche de poste (.docx)")
    p.add_argument("--chat", help="Destinataire WhatsApp (ex: 33612345678@c.us)")
    p.add_argument("--openwa-url", default=os.getenv("OPENWA_URL"), help="URL OpenWA")
    p.add_argument("--api-key", default=os.getenv("OPENWA_API_KEY"), help="Clé API OpenWA")
    p.add_argument("--session", default=os.getenv("OPENWA_SESSION", "default"))
    p.add_argument("--job-title", default="ce poste", help="Intitulé du poste")
    p.add_argument("--no-send-resume", action="store_true", help="Ne pas joindre le CV")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    print(f"Analyse : {args.resume}  ↔  {args.job}")
    match_pct = compute_match(args.resume, args.job)
    print(f"Score de correspondance : {match_pct} %")

    if args.chat:
        if not args.openwa_url or not args.api_key:
            sys.exit(
                "Erreur : --openwa-url et --api-key sont requis pour envoyer une notification."
            )
        notify_whatsapp(
            match_pct=match_pct,
            resume_path=args.resume,
            chat_id=args.chat,
            openwa_url=args.openwa_url,
            api_key=args.api_key,
            session_id=args.session,
            job_title=args.job_title,
            send_resume=not args.no_send_resume,
        )
    else:
        print("(Aucun destinataire --chat fourni, notification WhatsApp ignorée)")


if __name__ == "__main__":
    main()
