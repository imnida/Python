# 🗺️ Mapping ArchiMate - Écosystème de Paiement

## 📖 Introduction

Ce document décrit le mapping complet entre les concepts métier de l'écosystème de paiement et les types d'éléments ArchiMate 3.2.

---

## 🎯 Concepts Stratégiques → **Motivation Layer**

### Principes Architecturaux

| Concept Métier | Type ArchiMate | Justification |
|----------------|----------------|---------------|
| **Ligne de confiance (Trust)** | `principle` | Principe fondamental guidant l'architecture |
| **Invisibilité des paiements** | `principle` | Principe d'expérience utilisateur (frictionless) |

### Exigences

| Concept Métier | Type ArchiMate | Justification |
|----------------|----------------|---------------|
| **Observabilité & Traçabilité** | `requirement` | Exigence réglementaire et technique |

### Objets Métier

| Concept Métier | Type ArchiMate | Justification |
|----------------|----------------|---------------|
| **Mandat** | `business-object` | Objet métier manipulé (autorisation de paiement) |
| **Intent** | `business-object` | Objet métier exprimant l'intention de payer |

---

## 👥 Acteurs → **Business Layer**

### Tiers de Confiance (Acteurs Externes)

| Concept Métier | Type ArchiMate | Propriétés Choke Point |
|----------------|----------------|------------------------|
| **Scheme** (générique) | `business-actor` | `CP_Type: External` |
| **Visa/Mastercard** | `business-actor` | `CP_Type: External`, `CP_Juridiction: US`, Score ~86 (CRITIQUE) |
| **EPI (European Payment Initiative)** | `business-actor` | `CP_Type: External`, `CP_Juridiction: EU`, Score ~40 (ACCEPTABLE) |
| **EUDI Wallet** | `business-actor` | `CP_Type: External`, `CP_Juridiction: EU`, Score ~35 (ACCEPTABLE) |
| **Acteurs Publics** | `business-actor` | Régulateurs, BCE, Banque de France |
| **Acteurs Privés** | `business-actor` | Paytech, Bigtech, PSP |
| **Banques** | `business-actor` | Établissements bancaires traditionnels |
| **Paytech** | `business-actor` | `CP_Type: External` (Stripe, Adyen, etc.) |
| **Bigtech** | `business-actor` | `CP_Type: External` (Apple, Google, Amazon) |
| **PSP** | `business-actor` | Payment Service Providers |
| **Régulateurs** | `business-actor` | ACPR, BCE, EBA |

**Justification:** Les acteurs externes sont systématiquement marqués `CP_Type: External` pour permettre l'analyse de choke points.

### Clients (Rôles Métier)

| Concept Métier | Type ArchiMate | Justification |
|----------------|----------------|---------------|
| **Particulier** | `business-role` | Rôle client B2C |
| **Commerçant** | `business-role` | Rôle acceptant les paiements |
| **Professionnel** | `business-role` | TPE / PME |
| **ETI** | `business-role` | Entreprise de Taille Intermédiaire |

**Justification:** `business-role` plutôt que `business-actor` car un même acteur (personne physique) peut jouer plusieurs rôles (particulier et commerçant).

---

## 📱 Canaux → **Application Layer**

### Interfaces Applicatives

| Concept Métier | Type ArchiMate | Justification |
|----------------|----------------|---------------|
| **Canal App Mobile** | `application-interface` | Point d'accès applicatif (iOS/Android) |
| **Canal Web** | `application-interface` | Point d'accès navigateur |
| **Canal B2B** | `application-interface` | API pour intégrations entreprises |
| **Canal IA Natif** | `application-interface` | Interface conversationnelle (voix, chat) |
| **Autres Canaux** | `application-interface` | POS physique, IoT, etc. |

**Justification:** `application-interface` représente les points d'accès exposés aux utilisateurs/systèmes externes.

---

## 🚂 Rails de Paiement → **Business Services**

### Carte v1 (Schémas Traditionnels)

| Concept Métier | Type ArchiMate | Relations |
|----------------|----------------|-----------|
| **Acquisition Monétique** | `business-service` | `serves` → Commerçant<br>`assigned-to` ← Visa/MC |
| **Émission Carte** | `business-service` | `serves` → Particulier<br>`assigned-to` ← Visa/MC |

### Carte v2 (EPI - European Payment Initiative)

| Concept Métier | Type ArchiMate | Relations |
|----------------|----------------|-----------|
| **Acceptor PSP** | `business-service` | Service côté commerçant<br>`assigned-to` ← EPI |
| **Consumer PSP** | `business-service` | Service côté client<br>`assigned-to` ← EPI |

### Commerce & Open Banking

| Concept Métier | Type ArchiMate | Justification |
|----------------|----------------|---------------|
| **Virements Instantanés** | `business-service` | Service métier SEPA Inst |
| **API Open Banking** | `application-service` | Service technique (APIs PSD2) |
| **Open Banking** | `business-service` | Service métier réglementaire |
| **Open Finance** | `business-service` | Extension de l'Open Banking |

### Autres Domaines

| Concept Métier | Type ArchiMate | Justification |
|----------------|----------------|---------------|
| **Assurance** | `business-service` | Service financier complémentaire |
| **Crédit** | `business-service` | BNPL, crédit consommation |
| **Crypto** | `business-service` | Paiement en cryptomonnaies |

---

## 🏗️ Architecture Système → **Application Layer**

### Composants Applicatifs

| Concept Métier | Type ArchiMate | Justification |
|----------------|----------------|---------------|
| **Canal d'Acquisition (Agents IA)** | `application-component` | Système conversationnel IA |
| **Orchestration & Standards** | `application-component` | Moteur de routage des paiements |

### Services Applicatifs

| Concept Métier | Type ArchiMate | Relations |
|----------------|----------------|-----------|
| **Service Paiement Carte v1** | `application-service` | `realizes` → Émission Carte |
| **Service Paiement Carte v2 (EPI)** | `application-service` | `realizes` → Consumer PSP |
| **Service Paiement Commerce** | `application-service` | `realizes` → Virements Instantanés |
| **Service Commerce Numérique** | `application-service` | Intégrations plateformes |
| **Service Paiement Crypto** | `application-service` | `realizes` → Crypto (business) |

---

## 🔗 Relations ArchiMate Clés

### Motivation → Business

| Source | Relation | Target | Sémantique |
|--------|----------|--------|------------|
| Principe "Trust" | `influence-relationship` | EUDI Wallet | La confiance influence l'adoption EUDI |
| Principe "Trust" | `influence-relationship` | EPI | La confiance influence le choix EPI |
| Requirement "Observabilité" | `influence-relationship` | Régulateurs | L'exigence d'observabilité est imposée par régulateurs |

### Business Actors → Business Services

| Source (Acteur) | Relation | Target (Service) | Sémantique |
|-----------------|----------|------------------|------------|
| Visa/Mastercard | `assignment-relationship` | Acquisition Monétique | Visa/MC opère l'acquisition |
| Visa/Mastercard | `assignment-relationship` | Émission Carte | Visa/MC opère l'émission |
| EPI | `assignment-relationship` | Acceptor PSP | EPI opère le service accepteur |
| EPI | `assignment-relationship` | Consumer PSP | EPI opère le service consommateur |

### Business Services → Business Roles

| Source (Service) | Relation | Target (Rôle) | Sémantique |
|------------------|----------|---------------|------------|
| Émission Carte | `serving-relationship` | Particulier | Le service sert le particulier |
| Acquisition Monétique | `serving-relationship` | Commerçant | Le service sert le commerçant |
| Virements Instantanés | `serving-relationship` | Professionnel | Le service sert le pro |

### Application Services → Business Services

| Source (App) | Relation | Target (Business) | Sémantique |
|--------------|----------|-------------------|------------|
| Service Paiement Carte v1 | `realization-relationship` | Émission Carte | L'app réalise le service métier |
| Service Paiement Carte v2 | `realization-relationship` | Consumer PSP | L'app réalise le PSP consommateur |
| Service Paiement Commerce | `realization-relationship` | Virements Instantanés | L'app réalise les virements |
| API Open Banking | `serving-relationship` | Open Banking | L'API sert le service Open Banking |

### Application Interfaces → Application Components

| Source (Interface) | Relation | Target (Component) | Sémantique |
|--------------------|----------|-------------------|------------|
| Canal IA Natif | `serving-relationship` | Agents IA | L'interface expose les agents IA |
| Canal App | `serving-relationship` | Orchestration | L'app mobile accède à l'orchestrateur |
| Canal Web | `serving-relationship` | Orchestration | Le web accède à l'orchestrateur |
| Canal B2B | `serving-relationship` | Orchestration | Les APIs B2B accèdent à l'orchestrateur |

### Application Components → Application Services

| Source (Component) | Relation | Target (Service) | Sémantique |
|--------------------|----------|------------------|------------|
| Orchestration | `serving-relationship` | Service Paiement Carte v1 | L'orchestrateur route vers Carte v1 |
| Orchestration | `serving-relationship` | Service Paiement Carte v2 | L'orchestrateur route vers Carte v2/EPI |
| Orchestration | `serving-relationship` | Service Paiement Commerce | L'orchestrateur route vers Commerce |
| Orchestration | `serving-relationship` | Service Paiement Crypto | L'orchestrateur route vers Crypto |

### Application Components → Business Objects

| Source (Component) | Relation | Target (Object) | Sémantique |
|--------------------|----------|-----------------|------------|
| Agents IA | `access-relationship` | Intent | Les agents IA traitent l'intent |
| Agents IA | `access-relationship` | Mandat | Les agents IA gèrent le mandat |

---

## 🎨 Conventions de Nommage

### Préfixes

- **Business Services:** Pas de préfixe (ex: "Acquisition Monétique")
- **Application Services:** "Service Paiement" (ex: "Service Paiement Carte v1")
- **Application Components:** Nom descriptif (ex: "Orchestration & Standards")
- **Application Interfaces:** "Canal" (ex: "Canal App Mobile")

### Suffixes

- **Acteurs externes:** Nom vendor/consortium (ex: "Visa/Mastercard", "EPI")
- **Services v1/v2:** Version explicite (ex: "Carte v1", "Carte v2")

---

## 🔍 Propriétés Personnalisées

### Pour les Choke Points (Acteurs Externes)

| Propriété | Type | Valeurs | Exemple |
|-----------|------|---------|---------|
| `CP_Type` | String | `External` / `Internal` | `External` |
| `CP_Vendor` | String | Nom vendor | `Visa/Mastercard` |
| `CP_Juridiction` | String | `EU` / `US` / `Other` | `US` |
| `CP_Concentration` | Integer | 0-100 | `90` (duopole) |
| `CP_Substituabilite` | Integer | 0-100 | `85` (difficile) |
| `CP_Externalites` | Integer | 0-100 | `95` (effet réseau fort) |
| `CP_Asymetrie` | Integer | 0-100 | `90` (leverage faible) |
| `CP_Opacite` | Integer | 0-100 | `60` (partiellement opaque) |
| `CP_Extraterritorialite` | Integer | 0-100 | `95` (Cloud Act applicable) |
| `CP_Score_Total` | Decimal | 0-100 | `86.0` (calculé) |
| `CP_Criticite` | String | `CRITIQUE` / `ELEVE` / `MOYEN` / `ACCEPTABLE` | `CRITIQUE` |

### Pour la Traçabilité

| Propriété | Type | Exemple |
|-----------|------|---------|
| `Source` | String | `Workshop 2025-01-10` |
| `Owner` | String | `Chief Architect` |
| `Last_Update` | Date | `2025-01-10` |
| `Version` | String | `1.0` |

---

## 📊 Vues Recommandées

### 1. Vue Stratégique (Motivation)
**Contenu:**
- Principes (Trust, Invisibilité)
- Exigences (Observabilité)
- Objets métier (Mandat, Intent)

**Objectif:** Alignement stratégique

### 2. Vue Acteurs & Rôles
**Contenu:**
- Tiers de confiance (ligne haut)
- Rôles clients (ligne bas)

**Objectif:** Cartographie écosystème

### 3. Vue Rails de Paiement
**Contenu:**
- Carte v1 (colonne gauche)
- Carte v2/EPI (colonne centre)
- Commerce/Open Banking (colonne droite)

**Objectif:** Compréhension rails techniques

### 4. Vue Architecture Applicative
**Contenu:**
- Canaux (haut)
- Composants (milieu)
- Services applicatifs (bas)

**Objectif:** Architecture technique

### 5. Vue Choke Points
**Contenu:**
- Acteurs externes uniquement
- Colorisation par criticité (rouge/orange/jaune/vert)

**Objectif:** Analyse risques de souveraineté

### 6. Vue d'Ensemble (Landscape)
**Contenu:**
- Sélection d'éléments clés de toutes les couches
- Relations inter-couches

**Objectif:** Vision globale COMEX

---

## 🔢 Statistiques du Modèle

### Répartition par Couche

| Couche ArchiMate | Éléments | % |
|------------------|----------|---|
| **Motivation** | 5 | 11% |
| **Business** | 26 | 57% |
| **Application** | 15 | 32% |
| **Total** | 46 | 100% |

### Répartition par Type

| Type ArchiMate | Nombre |
|----------------|--------|
| `business-actor` | 12 |
| `business-role` | 4 |
| `business-service` | 10 |
| `business-object` | 2 |
| `application-component` | 2 |
| `application-service` | 6 |
| `application-interface` | 5 |
| `principle` | 2 |
| `requirement` | 1 |
| **Total éléments** | 44 |
| **Relations** | ~30 |

### Choke Points Identifiés

| Acteur | Score Estimé | Criticité |
|--------|--------------|-----------|
| Visa/Mastercard | 86/100 | 🔴 CRITIQUE |
| EPI | 40/100 | 🟢 ACCEPTABLE |
| EUDI Wallet | 35/100 | 🟢 ACCEPTABLE |
| Paytech (Stripe, Adyen) | À scorer | TBD |
| Bigtech (Apple, Google) | À scorer | TBD |

---

## 🎯 Cas d'Usage du Modèle

### 1. Analyse de Souveraineté Numérique
**Objectif:** Identifier dépendances critiques aux acteurs non-EU

**Vues utilisées:**
- Vue Choke Points
- Vue Rails de Paiement

**Analyse:**
- Visa/Mastercard = choke point CRITIQUE (US, score 86)
- Mitigation: Quota 40% EPI obligatoire d'ici 2027

### 2. Transformation Digitale
**Objectif:** Roadmap migration vers canaux IA-natifs

**Vues utilisées:**
- Vue Architecture Applicative
- Vue d'Ensemble

**Analyse:**
- Canal IA Natif → Agents IA → Intent/Mandat
- Nouveau parcours frictionless

### 3. Conformité Réglementaire
**Objectif:** Démontrer conformité PSD2/DORA

**Vues utilisées:**
- Vue Stratégique (Observabilité)
- Vue Rails de Paiement (Open Banking)

**Analyse:**
- Exigence "Observabilité" influence Régulateurs
- API Open Banking réalise Open Banking

### 4. Présentation COMEX
**Objectif:** Décision stratégique sur choix schemes

**Vues utilisées:**
- Vue d'Ensemble (high-level)
- Vue Choke Points (risques)

**Analyse:**
- Comparaison Visa/MC (score 86) vs EPI (score 40)
- ROI souveraineté vs coût migration

---

## 📚 Références

### Standards
- [ArchiMate 3.2 Specification](https://pubs.opengroup.org/architecture/archimate3-doc/)
- [TOGAF 10.2](https://pubs.opengroup.org/togaf-standard/)

### Domaine Paiement
- [PSD2 (Payment Services Directive 2)](https://ec.europa.eu/info/law/payment-services-psd-2-directive-eu-2015-2366_en)
- [SEPA Instant Credit Transfer](https://www.europeanpaymentscouncil.eu/what-we-do/sepa-instant-credit-transfer)
- [EPI (European Payment Initiative)](https://www.epicompany.eu/)
- [EUDI Wallet](https://ec.europa.eu/digital-building-blocks/wikis/display/EBSI/What+is+ebsi)

### Méthodologie Choke Points
- Voir `Choke_Points/README_CHOKE_POINTS.md`

---

**Version 1.0 - 2025-01-10**

*Ce mapping est cohérent avec la méthodologie TOGAF ADM et la notation ArchiMate 3.2.*
