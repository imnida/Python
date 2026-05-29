# PRD — Plateforme temps réel de matching CV / Offres d'emploi

**Version** : 0.1  
**Date** : 2026-05-29  
**Statut** : Draft  

---

## 1. Contexte et problème

Les candidats et recruteurs font face à une fragmentation des données :

- Les offres d'emploi sont dispersées sur LinkedIn, Indeed, Glassdoor avec des formats incompatibles
- Les CVs existent en formats PDF, Word, LinkedIn — non comparables directement
- L'analyse des écarts de compétences (gap analysis) est manuelle et lente
- Il n'existe pas de vue unifiée permettant des recommandations en temps réel

Ce projet construit un pipeline temps réel qui consolide ces sources hétérogènes,
calcule les gaps de compétences et recommande les meilleures opportunités.

---

## 2. Objectifs

| Objectif | Mesure de succès |
|---|---|
| Consolider N sources en un seul schéma | 100 % des sources couvertes sans code ad hoc |
| Recommandations en < 5 secondes après scrape | p95 latence end-to-end ≤ 5 s |
| Gap analysis automatique | Précision gaps ≥ 80 % vs évaluation humaine |
| Export Excel exploitable | Fichier généré en < 2 s, 0 erreur de format |
| Fonctionner sur Raspberry Pi 5 | RAM pic ≤ 6 Go, CPU pic ≤ 80 % |

---

## 3. Utilisateurs cibles

### Candidat
- Uploade son CV (PDF / Word / LinkedIn URL)
- Reçoit une liste classée d'offres correspondantes
- Voit ses gaps de compétences par rapport à chaque offre
- Exporte le rapport en Excel

### Recruteur
- Définit un profil de poste
- Reçoit en temps réel les CVs entrants correspondants
- Consulte le score de match et les gaps candidat

### Administrateur système
- Monitore le pipeline Kafka / Flink
- Configure les sources de scraping
- Gère les schémas et les adaptateurs

---

## 4. Fonctionnalités

### 4.1 Scraper multi-sources

**F-01** Le système scrappe automatiquement les offres d'emploi depuis :
- LinkedIn Jobs
- Indeed
- Glassdoor

**F-02** Le scraper publie chaque offre brute sur le topic Kafka `raw-jobs`
avec les métadonnées : `source`, `scraped_at`, `raw_payload`.

**F-03** Un mécanisme de déduplication (hash du contenu) évite les doublons
dans une fenêtre glissante de 24 h.

**F-04** Le scraper est extensible : ajouter une source = créer un adaptateur,
sans modifier le pipeline (pattern AdapterRegistry).

---

### 4.2 Parsing CV multi-formats

**F-05** Le système accepte des CVs en :
- PDF (extraction texte + layout)
- Word / DOCX
- URL LinkedIn (scraping profil)

**F-06** Chaque CV parsé est publié sur le topic Kafka `raw-cvs`.

**F-07** Les champs extraits minimaux :
```
nom, email, téléphone, localisation,
compétences (liste), expériences (poste/durée/entreprise),
formations (diplôme/établissement/année),
langues
```

---

### 4.3 Consolidation de schémas (couche 1)

**F-08** Un job Flink lit `raw-jobs` et `raw-cvs`, applique l'AdapterRegistry
et publie sur `consolidated-jobs` et `consolidated-cvs`.

**F-09** Le schéma consolidé `UnifiedJobRecord` contient :
```
id, source_type, title, company, location,
required_skills[], salary_range, remote_policy,
source_attributes (nullable bloc par source)
```

**F-10** Le schéma consolidé `UnifiedCvRecord` contient :
```
id, candidate_id, format_type,
skills[], experiences[], education[],
format_attributes (nullable bloc par format)
```

---

### 4.4 Gap Analysis temps réel (couche 2)

**F-11** Un job Flink joint `consolidated-cvs` et `consolidated-jobs`
dans une fenêtre glissante de 24 h.

**F-12** Pour chaque paire (CV, offre), le système calcule :
- **skills_match** : compétences présentes dans CV ∩ offre (%)
- **skills_missing** : compétences requises absentes du CV
- **skills_extra** : compétences CV non requises (signal de sur-qualification)
- **experience_gap** : écart années d'expérience demandées vs disponibles

**F-13** Les résultats sont publiés sur le topic `gap-results`.

---

### 4.5 Recommender temps réel (couche 3)

**F-14** Un job Flink lit `gap-results` et calcule un score de match
basé sur : skills_match (50 %), experience_gap (30 %), localisation (20 %).

**F-15** Pour chaque candidat, le système maintient un top-10 des offres
mis à jour en temps réel (fenêtre glissante 5 min).

**F-16** Les recommandations sont publiées sur `recommendations` et
disponibles via une API REST (GET `/recommendations/{candidate_id}`).

**F-17** Le modèle de scoring est configurable (poids ajustables)
sans redéploiement du job Flink.

---

### 4.6 Export Excel

**F-18** L'utilisateur peut déclencher un export Excel via :
- API REST : `POST /export/{candidate_id}`
- CLI : `python -m export --candidate-id <id>`

**F-19** Le fichier Excel contient 3 onglets :
- **Recommandations** : top offres classées avec score
- **Gap Analysis** : compétences manquantes par offre
- **Profil CV** : récapitulatif des compétences détectées

**F-20** Le fichier est généré en < 2 secondes pour un top-10.

---

## 5. Architecture technique

```
┌─────────────────────────────────────────────────────────────┐
│  SOURCES                                                    │
│  LinkedIn Scraper ──┐                                       │
│  Indeed Scraper ────┼──▶ Kafka: raw-jobs                   │
│  Glassdoor Scraper ─┘                                       │
│  PDF/Word/LinkedIn CV ──▶ Kafka: raw-cvs                   │
└──────────────────────────────────┬──────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────┐
│  FLINK JOB 1 — Schema Consolidation                        │
│  AdapterRegistry (pattern existant)                        │
│  raw-jobs ──▶ consolidated-jobs                            │
│  raw-cvs  ──▶ consolidated-cvs                             │
└──────────────────────────────────┬──────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────┐
│  FLINK JOB 2 — Gap Analysis                                │
│  JOIN consolidated-jobs + consolidated-cvs                 │
│  Window: SlidingEventTime(24h, 1h)                         │
│  ──▶ gap-results                                           │
└──────────────────────────────────┬──────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────┐
│  FLINK JOB 3 — Recommender                                 │
│  Scoring TF-IDF / weighted match                           │
│  Top-K par candidat (fenêtre 5 min)                        │
│  ──▶ recommendations                                       │
└──────────────────────────────────┬──────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────┐
│  SINKS                                                      │
│  API REST (FastAPI)                                         │
│  Excel Export (openpyxl)                                    │
│  Base de données (SQLite / PostgreSQL)                      │
└─────────────────────────────────────────────────────────────┘
```

### Stack technique

| Composant | Technologie |
|---|---|
| Streaming broker | Apache Kafka 3.x (KRaft) |
| Stream processing | Apache Flink 1.18 + PyFlink |
| Schema consolidation | Pattern AdapterRegistry (Python, existant) |
| CV parsing PDF | `pdfplumber` |
| CV parsing DOCX | `python-docx` |
| Scraping | `playwright` ou `requests` + `beautifulsoup4` |
| Scoring / NLP | `scikit-learn` (TF-IDF), optionnel `sentence-transformers` |
| API | `FastAPI` |
| Export Excel | `openpyxl` |
| Infrastructure | Raspberry Pi 5 (dev), Docker Compose |

---

## 6. Exigences non-fonctionnelles

| Exigence | Cible |
|---|---|
| Latence end-to-end (scrape → recommandation) | p95 ≤ 5 s |
| Débit | ≥ 50 offres/min, ≥ 10 CVs/min |
| Disponibilité | 99 % en heures ouvrées (mode dev/Pi 5) |
| RAM totale | ≤ 6 Go (Pi 5 8 Go) |
| Extensibilité | Nouvelle source = 1 classe + 1 ligne registre |
| Testabilité | Couverture tests ≥ 80 %, 0 dépendance infra en tests unitaires |
| Sécurité données | CVs stockés localement uniquement, pas de cloud tiers |

---

## 7. Contraintes

- **Matériel** : Raspberry Pi 5 (8 Go RAM recommandé, 4 Go minimum)
- **Légal scraping** : respect des CGU LinkedIn/Indeed (rate limiting, pas de bulk)
- **PII** : données CV non transmises à des services externes sans consentement
- **Offline-first** : le pipeline doit fonctionner sans internet après le scraping

---

## 8. Hors périmètre (v1)

- Interface graphique (UI web)
- Authentification utilisateur
- Multi-tenant (plusieurs utilisateurs simultanés)
- Modèle LLM pour l'analyse sémantique des CVs
- Intégration ATS (Applicant Tracking Systems)
- Déploiement cloud

---

## 9. Phases de livraison

### Phase 1 — Fondations (semaines 1–2)
- [x] Pattern AdapterRegistry Python
- [x] Modèles de données (`UnifiedJobRecord`, `UnifiedCvRecord`)
- [ ] Kafka topics + schémas
- [ ] Scraper LinkedIn (basique, rate-limited)

### Phase 2 — Pipeline temps réel (semaines 3–4)
- [ ] Flink Job 1 : consolidation jobs + CVs
- [ ] CV parser PDF + DOCX
- [ ] Flink Job 2 : gap analysis (windowed join)

### Phase 3 — Recommender + Export (semaines 5–6)
- [ ] Flink Job 3 : scoring et top-K
- [ ] API REST FastAPI
- [ ] Export Excel (3 onglets)

### Phase 4 — Stabilisation (semaine 7)
- [ ] Tests d'intégration end-to-end
- [ ] Tuning mémoire Pi 5
- [ ] Documentation opérationnelle

---

## 10. Questions ouvertes

| # | Question | Impact | Décision requise |
|---|---|---|---|
| Q1 | Scraping LinkedIn : API officielle ou HTML scraping ? | Légal + fiabilité | Avant Phase 1 |
| Q2 | Modèle de scoring : TF-IDF ou sentence-transformers ? | RAM Pi 5 (transformers = +1 Go) | Avant Phase 3 |
| Q3 | Persistance : SQLite (simple) ou PostgreSQL (robuste) ? | Opérationnel | Avant Phase 2 |
| Q4 | Export Excel : template fixe ou configurable ? | UX | Avant Phase 3 |
| Q5 | Flink jobs séparés ou pipeline unique (Pi 5 4 Go) ? | Mémoire | Avant Phase 2 |
