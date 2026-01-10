# 🎯 Méthodologie Choke Points - Automatisation jArchi

## 📖 Introduction

Cette collection de scripts jArchi automatise la **détection systématique des Points d'Étranglement (Choke Points)** dans les architectures ArchiMate, basée sur la méthodologie TOGAF/Constitutional AI.

### Qu'est-ce qu'un Choke Point ?

> *Un composant, acteur, ou flux dans l'architecture dont le contrôle par un tiers permettrait à ce dernier d'extraire de la rente, de limiter l'autonomie stratégique, ou de menacer la viabilité du système, sans possibilité de contournement économiquement viable dans un délai acceptable.*

---

## 🚀 Démarrage Rapide (5 minutes)

### Étape 1 : Initialiser les Propriétés

```
Exécuter: 01_Setup/init_choke_point_properties.ajs
```

Ce script ajoute les propriétés de choke point à tous vos composants:
- `CP_Concentration` (0-100)
- `CP_Substituabilite` (0-100)
- `CP_Externalites` (0-100)
- `CP_Asymetrie` (0-100)
- `CP_Opacite` (0-100)
- `CP_Extraterritorialite` (0-100)
- `CP_Vendor`, `CP_Juridiction`, `CP_Type`, etc.

### Étape 2 : Marquer les Composants Externes

Pour chaque composant externe (vendor, SaaS, cloud provider):

1. Sélectionner l'élément dans Archi
2. Dans les propriétés, définir:
   - `CP_Type` = `External`
   - `CP_Vendor` = nom du vendor (ex: `AWS`, `OpenAI`, `Stripe`)
   - `CP_Juridiction` = `EU`, `US`, ou `Other`

### Étape 3 : Scorer les 6 Dimensions

Pour chaque composant externe, évaluer les 6 dimensions (0-100):

#### 1. CP_Concentration (Structure du marché)
- **90-100**: Monopole (ex: SWIFT pour payments interbancaires)
- **70-89**: Duopole (ex: Visa/Mastercard)
- **40-69**: Oligopole (ex: AWS/Azure/GCP)
- **0-39**: Marché fragmenté

#### 2. CP_Substituabilite (Coûts de migration)
- **90-100**: Impossible ou >24 mois (ex: Core Banking System propriétaire)
- **70-89**: Très difficile, 12-24 mois
- **40-69**: Possible mais coûteux, 6-12 mois
- **0-39**: Facile, <6 mois

#### 3. CP_Externalites (Effets réseau, lock-in)
- **90-100**: Valeur exponentielle avec adoption (ex: Apple Wallet)
- **70-89**: Standards propriétaires dominants
- **40-69**: Standards mixtes
- **0-39**: Standards ouverts, multi-implémentations

#### 4. CP_Asymetrie (Dynamiques de pouvoir)
- **90-100**: Dépendance totale, vendor ne dépend pas de vous
- **70-89**: Leverage asymétrique important
- **40-69**: Dépendance mutuelle partielle
- **0-39**: Pouvoir de négociation équilibré

#### 5. CP_Opacite (Auditabilité)
- **90-100**: Boîte noire totale (closed-source, no observability)
- **70-89**: Documentation insuffisante, opacité partielle
- **40-69**: Partiellement auditable
- **0-39**: Open-source, transparent, auditable

#### 6. CP_Extraterritorialite (Souveraineté)
- **90-100**: US + Cloud Act applicable
- **70-89**: Juridiction non-EU (Chine, Russie, etc.)
- **40-69**: UK, Suisse (partiellement aligné EU)
- **0-39**: EU, RGPD-compliant

### Étape 4 : Calculer les Scores

```
Exécuter: 02_Analysis/calculate_choke_point_scores.ajs
```

Calcule automatiquement:
- **Score Total** (pondération des 6 dimensions)
- **Criticité** (CRITIQUE/ELEVE/MOYEN/ACCEPTABLE)
- **DHS** (Dependency Health Score)

### Étape 5 : Générer le Risk Register

```
Exécuter: 03_Reporting/generate_risk_register.ajs
```

Produit le rapport complet avec:
- Top 10 Choke Points
- Métriques globales (DHS, distribution criticité)
- Falsifiabilité (conditions échec/succès)
- Actions immédiates requises

---

## 📂 Structure des Scripts

```
Choke_Points/
├── 01_Setup/
│   └── init_choke_point_properties.ajs     # Initialiser propriétés
│
├── 02_Analysis/
│   ├── calculate_choke_point_scores.ajs    # Calculer scores totaux
│   ├── generate_choke_point_canvas.ajs     # Canvas détaillé par composant
│   └── dependency_analysis.ajs             # Détection SPOF
│
├── 03_Reporting/
│   └── generate_risk_register.ajs          # Risk Register complet
│
├── 04_Visualization/
│   └── visualize_choke_points.ajs          # Colorier vues par criticité
│
└── templates/
    └── choke_point_example.archimate       # Modèle exemple (TODO)
```

---

## 🔬 Méthodologie Détaillée

### Formule de Score Total

```
Score Total = (Concentration × 0.25) +
              (Substituabilite × 0.25) +
              (Externalites × 0.20) +
              (Asymetrie × 0.20) +
              (Opacite × 0.10) +
              (Extraterritorialite × 0.20)
```

### Seuils de Criticité

| Score | Criticité | Couleur | Action |
|-------|-----------|---------|--------|
| 80-100 | 🔴 CRITIQUE | Rouge | Mitigation OBLIGATOIRE |
| 60-79 | 🟠 ÉLEVÉ | Orange | Plan B documenté |
| 40-59 | 🟡 MOYEN | Jaune | Monitoring renforcé |
| 0-39 | 🟢 ACCEPTABLE | Vert | Monitoring standard |

### Dependency Health Score (DHS)

```
DHS = 100 - (Score Moyen des Choke Points)
```

**Interprétation:**
- **DHS ≥ 70**: Autonomie stratégique acceptable ✅
- **DHS 50-69**: Surveillance renforcée requise ⚠️
- **DHS < 50**: Architecture non souveraine, capture imminente 🚨

---

## 📊 Cas d'Usage

### Cas 1 : Architecture Cloud-Native

**Contexte:** Migration vers AWS pour application bancaire

**Workflow:**

1. Modéliser l'architecture dans Archi
2. Marquer composants AWS (EC2, RDS, Lambda, S3, etc.) comme `External`
3. Scorer:
   - `CP_Concentration`: 88 (oligopole AWS/Azure/GCP)
   - `CP_Substituabilite`: 85 (18 mois migration estimée)
   - `CP_Externalites`: 70 (services AWS complémentaires)
   - `CP_Asymetrie`: 90 (banque = <1% revenus AWS)
   - `CP_Opacite`: 60 (pricing opaque)
   - `CP_Extraterritorialite`: 95 (Cloud Act applicable)
4. Calculer: **Score Total = 82/100 → CRITIQUE**
5. Générer Risk Register
6. **Résultat:** Mitigation requise = Hybrid Gaia-X + GCP

### Cas 2 : LLM pour Assistant Virtuel

**Contexte:** Utilisation de GPT-4 (OpenAI) pour chatbot client

**Workflow:**

1. Créer élément `Application Component: "Intent Recognition Engine"`
2. Créer relation `uses → LLM: GPT-4 (OpenAI)`
3. Marquer GPT-4 comme `External`, vendor `OpenAI`, juridiction `US`
4. Scorer:
   - `CP_Concentration`: 95 (duopole OpenAI/Anthropic)
   - `CP_Substituabilite`: 85 (gap performance vs Mistral 7B)
   - `CP_Externalites`: 60 (fine-tuning data lock-in)
   - `CP_Asymetrie`: 90 (banque = 1/1M clients OpenAI)
   - `CP_Opacite`: 100 (closed model, boîte noire)
   - `CP_Extraterritorialite`: 100 (US, Cloud Act)
5. **Score Total = 88/100 → CRITIQUE**
6. **Mitigation:** Multi-model (Mistral 7B primary, GPT-4 fallback)

### Cas 3 : Payment Scheme (Visa/Mastercard vs EPI)

**Contexte:** Choix entre schemes internationaux et EPI souverain

**Workflow:**

1. Créer éléments pour Visa, Mastercard, EPI
2. Scorer chacun selon les 6 dimensions
3. Comparer:

| Dimension | Visa | Mastercard | EPI (hypothèse) |
|-----------|------|------------|-----------------|
| Concentration | 90 | 90 | 40 |
| Substituabilite | 85 | 85 | 60 |
| Externalites | 95 | 95 | 50 |
| Asymetrie | 90 | 90 | 40 |
| Opacite | 60 | 60 | 30 |
| Extraterritorialite | 95 | 95 | 20 |
| **TOTAL** | **86** | **86** | **40** |

4. **Décision:** Quota 40% EPI pour réduire dépendance Visa/MC

---

## 🛠️ Propriétés Étendues (Optionnelles)

Pour une analyse plus fine, ajouter ces propriétés:

### Substituabilité Détaillée
- `CP_Alternatives`: Liste alternatives viables
- `CP_Delai_Migration`: Estimation délai (ex: "18 mois")
- `CP_Cout_Migration`: Budget (ex: "€5M")

### Externalités Réseau
- `CP_Effet_Reseau`: Oui/Non/Partiel
- `CP_Standards`: "Ouvert" / "Fermé" / "Mixte"

### Asymétrie
- `CP_Dependance_Nous`: "Faible" / "Moyen" / "Fort"
- `CP_Dependance_Vendor`: "Faible" / "Moyen" / "Fort"

### Opacité
- `CP_Code_Type`: "Open Source" / "Closed" / "Open Weights"
- `CP_Doc_Quality`: "Excellente" / "Moyenne" / "Faible"
- `CP_Observability`: "Oui" / "Partielle" / "Non"

### Gouvernance
- `CP_Budget`: Montant mitigation (ex: "€500K")
- `CP_DRI`: Directly Responsible Individual
- `CP_Timeline`: "Q2 2025" / "Quick win" / "Strategic"
- `CP_Last_Review`: Date dernier audit
- `CP_Next_Review`: Date prochain audit
- `CP_SPOF`: "true"/"false" (détecté automatiquement)

---

## 📋 Workflow Complet

### Phase A : Vision (Preliminary)

```archimate
Driver: "Souveraineté numérique EU"
  └─influenced_by→ Vendor Cloud (AWS/Azure/GCP)
      • CP_Score_Total: 82/100 → CRITIQUE
      • Mitigation: Multi-cloud, Gaia-X
```

**Script:** Identifier acteurs externes influençant drivers critiques

### Phase B-C-D : Architecture (Business/Application/Technology)

```archimate
Business Service: "Paiement Instantané"
  └─served_by→ Business Actor: "Scheme EPI" (external)
      • CP_Score_Total: 75/100 → ÉLEVÉ
      • SPOF: OUI (pas d'alternative EU)
      • Mitigation: Quota 40% EPI obligatoire
```

**Scripts:**
1. `init_choke_point_properties.ajs` - Initialiser
2. Scorer manuellement les 6 dimensions
3. `calculate_choke_point_scores.ajs` - Calculer totaux
4. `dependency_analysis.ajs` - Détecter SPOF
5. `generate_choke_point_canvas.ajs` - Canvas détaillé

### Phase E : Opportunités (Scenarios)

**Pre-Mortem Analysis:** Pour chaque scenario ToT, identifier choke points = causes échec

```
Scenario: "Full Cloud Native (AWS)"
Pre-Mortem (2028): "Le projet a échoué. Pourquoi?"

Cause #1: Extraction rente AWS
  • Choke Point: Cloud/GPU oligopole (Score: 82)
  • Événement: GPU pricing × 3 en 2026
  • Mitigation manquée: Pas de hybrid cloud
  • Probabilité × Impact: €16M
```

**Script:** Comparer DHS par scenario

### Phase F-G : Migration & Gouvernance

**Quarterly Choke Point Review** (Q-Review):
- Fréquence: Trimestrielle
- Participants: Chief Architect, CISO, DPO, CTO, Procurement
- Agenda: Review Top 10, Deep dive CRITIQUES, Veille marché, ADR

**Script:** `generate_risk_register.ajs` → Dashboard Q-Review

### Phase H : Changement

**Risk Register Final:**

```
Top 10 Choke Points
DHS: 32/100 → CRITIQUE
Actions immédiates: 5 choke points CRITIQUES
Budget mitigation: €27.3M sur 18 mois
```

---

## 🎨 Visualisation

### Colorier les Vues

```
Exécuter: 04_Visualization/visualize_choke_points.ajs
```

**Résultat:**
- 🔴 Composants CRITIQUES en rouge
- 🟠 Composants ÉLEVÉS en orange
- 🟡 Composants MOYENS en jaune
- 🟢 Composants ACCEPTABLES en vert
- Bordure épaisse pour SPOF

**Exemple de vue:**

```
┌─────────────────────────┐
│ 🔴 GPT-4 (OpenAI)      │  ← CRITIQUE (88/100)
│    [CP: 88] [SPOF]     │  ← Score + SPOF indicator
└─────────────────────────┘
        ↑ serves
┌─────────────────────────┐
│ Intent Recognition      │
│ Engine                  │
└─────────────────────────┘
```

---

## 🔍 Analyse de Dépendances (SPOF Detection)

### Script: `dependency_analysis.ajs`

**Métriques calculées:**
- **Fan-in**: Nombre de composants qui dépendent du composant externe
- **Fan-out**: Nombre de dépendances du composant externe
- **Max Depth**: Profondeur maximale de l'arbre de dépendance
- **SPOF**: Détection si pas d'alternative viable
- **Impact Score**: 0-100 basé sur fan-in, depth, et SPOF

**Exemple de sortie:**

```
═══════════════════════════════════════════════════════════════════
RÉSULTATS D'ANALYSE
═══════════════════════════════════════════════════════════════════

1. GPT-4 (OpenAI)
   Vendor: OpenAI
   Fan-in (dépendants): 15
   Fan-out (dépendances): 2
   Profondeur max: 4
   SPOF: 🔴 OUI
   Impact Score: 92.5/100
   Dépendants critiques:
     • Onboarding Client
     • Support Client
     • Détection Fraude

🚨 ALERTE: 3 SPOF détecté(s)
   Action requise: Identifier alternatives ou créer redondance
```

---

## 📚 Exemples de Scores Réels

### AWS EC2 (GPU)

```yaml
CP_Vendor: AWS
CP_Juridiction: US
CP_Concentration: 88        # Oligopole AWS/Azure/GCP
CP_Substituabilite: 92      # 18 mois migration
CP_Externalites: 70         # Services AWS complémentaires
CP_Asymetrie: 85            # Leverage pricing unilatéral
CP_Opacite: 60              # Pricing opaque
CP_Extraterritorialite: 95  # Cloud Act applicable
─────────────────────────────
CP_Score_Total: 82/100 → CRITIQUE

Mitigation:
- Hybrid cloud: Gaia-X (Tier 1 PII) + GCP (Tier 2)
- GPU co-ownership: Consortium 10 banques (€25M pool)
- Failover drill trimestriel
```

### Apple Wallet

```yaml
CP_Vendor: Apple
CP_Juridiction: US
CP_Concentration: 95        # Duopole Apple/Google
CP_Substituabilite: 90      # Impossible sans perte UX
CP_Externalites: 100        # Effet réseau massif (iOS users)
CP_Asymetrie: 95            # Apple ne dépend pas de vous
CP_Opacite: 85              # API fermée, NDA
CP_Extraterritorialite: 100 # US jurisdiction
─────────────────────────────
CP_Score_Total: 94/100 → CRITIQUE

Mitigation:
- EUDI Wallet adoption urgente (EU sovereign alternative)
- Quota 50% EUDI dès disponibilité
- Parallel implementation (Apple + EUDI)
```

### PostgreSQL (Open Source)

```yaml
CP_Vendor: Community
CP_Juridiction: Global
CP_Concentration: 30        # Marché DB fragmenté
CP_Substituabilite: 40      # Migration SQL standard possible
CP_Externalites: 20         # Standards ouverts (SQL)
CP_Asymetrie: 30            # Pas de vendor unique
CP_Opacite: 10              # Open source, auditable
CP_Extraterritorialite: 10  # Global, pas de juridiction unique
─────────────────────────────
CP_Score_Total: 24/100 → ACCEPTABLE

Mitigation:
- Monitoring standard
- Backup strategy
```

---

## ⚠️ Alertes et Actions

### Seuils Critiques

| Condition | Alerte | Action |
|-----------|--------|--------|
| Score ≥ 85 | 🚨 EXISTENTIEL | Escalation COMEX immédiate |
| Score 80-84 | 🔴 CRITIQUE | Mitigation obligatoire (timeline < 6 mois) |
| Score 70-79 | 🔴 CRITIQUE | Plan B documenté + budget |
| Score 60-69 | 🟠 ÉLEVÉ | Surveillance renforcée |
| DHS < 50 | 🚨 ARCHITECTURE NON VIABLE | Refonte stratégique |
| 3+ SPOF | 🚨 FRAGILITÉ SYSTÉMIQUE | Architecture découplée urgente |

### Actions Automatiques

Le script `calculate_choke_point_scores.ajs` génère automatiquement:

1. **Si Score ≥ 80:**
   - Marquer propriété `CP_Action_Required` = `URGENT`
   - Recommander escalation COMEX

2. **Si SPOF détecté:**
   - Marquer `CP_SPOF` = `true`
   - Recommander multi-vendor ou abstraction layer

3. **Si DHS < 70:**
   - Alerter sur dashboard
   - Recommander Q-Review anticipée

---

## 🔄 Gouvernance Continue

### Processus Q-Review (Trimestriel)

**Participants:**
- Chief Architect (ownership)
- CISO (security)
- DPO (souveraineté/RGPD)
- CTO (faisabilité)
- Procurement (vendor relations)

**Agenda (2h):**

1. **Review Dashboard (15 min)**
   - Heat map mise à jour
   - Évolutions scores trimestre
   - Nouveaux choke points identifiés

2. **Deep Dive Top 3 Risques (45 min)**
   - Analyse détaillée
   - Mitigations proposées
   - Budget/timeline
   - Décision Go/No-Go

3. **Veille Marché (30 min)**
   - M&A impactant vendors
   - Nouvelles régulations
   - Émergence alternatives
   - Précédents industrie

4. **ADR & Actions (30 min)**
   - Rédaction ADR si décisions majeures
   - Assignment actions (DRI)
   - KPIs tracking

**Output:**
- Dashboard mis à jour (via `generate_risk_register.ajs`)
- ADRs (si nécessaire)
- Action log
- COMEX summary (si critique)

### KPIs à Suivre

| KPI | Formule | Seuil OK |
|-----|---------|----------|
| DHS | 100 - avg(scores) | ≥ 70 |
| Choke Points CRITIQUES | count(score ≥ 80) | ≤ 2 |
| SPOF | count(SPOF=true) | ≤ 3 |
| Budget mitigation | Σ(CP_Budget) | < budget projet × 0.5 |
| Coverage | Composantes scorées / Total externes | 100% |

---

## 🚨 Falsifiabilité

### Conditions d'Échec (Architecture Non Viable)

```
❌ Si DHS < 50 en 2026
   → Architecture non souveraine (capture imminente)
   → Action: Refonte stratégique obligatoire

❌ Si 3+ Choke Points score > 85
   → Risque existentiel (dépendances critiques multiples)
   → Action: Réduction urgente dépendances

❌ Si budget mitigation > 2× budget projet initial
   → ROI négatif (coût autonomie prohibitif)
   → Action: Revoir ambitions souveraineté
```

### Conditions de Succès

```
✅ Si DHS > 70 en 2027
   → Autonomie stratégique confirmée

✅ Si tous choke points CRITIQUES < 80 post-mitigation
   → Risques maîtrisés

✅ Si tests de réversibilité réussis (failover < 24h)
   → Mitigations opérationnelles
```

---

## 📖 Ressources

### Documentation
- [Méthodologie Choke Points (Prompt complet)](../METHODOLOGY_CHOKE_POINTS.md)
- [ArchiMate 3.2 Spec](https://pubs.opengroup.org/architecture/archimate3-doc/)
- [TOGAF 10.2 ADM](https://pubs.opengroup.org/togaf-standard/)

### Communauté
- [Archi Forum](https://forum.archimatetool.com/)
- [jArchi GitHub](https://github.com/archimatetool/archi-scripting-plugin)

---

## ✅ Checklist Complète

### Setup Initial
- [ ] Installer jArchi plugin dans Archi
- [ ] Créer modèle ArchiMate de l'architecture
- [ ] Exécuter `init_choke_point_properties.ajs`

### Identification Composants Externes
- [ ] Identifier tous vendors, SaaS, cloud providers
- [ ] Marquer `CP_Type` = `External`
- [ ] Définir `CP_Vendor` et `CP_Juridiction`

### Scoring (6 Dimensions)
- [ ] CP_Concentration (market share, HHI)
- [ ] CP_Substituabilite (délai, coût migration)
- [ ] CP_Externalites (standards, lock-in)
- [ ] CP_Asymetrie (leverage, dépendance mutuelle)
- [ ] CP_Opacite (open/closed, auditabilité)
- [ ] CP_Extraterritorialite (juridiction, Cloud Act)

### Analyse
- [ ] Exécuter `calculate_choke_point_scores.ajs`
- [ ] Exécuter `dependency_analysis.ajs` (SPOF)
- [ ] Exécuter `generate_choke_point_canvas.ajs` pour composants CRITIQUES

### Reporting
- [ ] Exécuter `generate_risk_register.ajs`
- [ ] Analyser Top 10 Choke Points
- [ ] Vérifier DHS (seuil: ≥ 70)
- [ ] Identifier actions immédiates

### Mitigation
- [ ] Pour chaque choke point CRITIQUE:
  - [ ] Définir stratégie mitigation (`CP_Mitigation`)
  - [ ] Estimer budget (`CP_Budget`)
  - [ ] Assigner DRI (`CP_DRI`)
  - [ ] Définir timeline (`CP_Timeline`)

### Visualisation
- [ ] Exécuter `visualize_choke_points.ajs`
- [ ] Vérifier colorisation vues (rouge = critique)
- [ ] Identifier SPOF visuellement (bordure épaisse)

### Gouvernance
- [ ] Planifier Q-Review (trimestrielle)
- [ ] Définir KPIs dashboard
- [ ] Assigner Chief Architect (ownership)
- [ ] Définir process escalation COMEX

---

## 🆘 Troubleshooting

### Problème: Scores non calculés

**Cause:** Propriétés non initialisées ou vides

**Solution:**
1. Vérifier que `init_choke_point_properties.ajs` a été exécuté
2. Vérifier que les propriétés CP_* existent
3. Vérifier que les scores sont bien numériques (pas de texte)

### Problème: Aucun SPOF détecté alors qu'il devrait y en avoir

**Cause:** Relations ArchiMate manquantes ou types incorrects

**Solution:**
1. Vérifier que les relations de dépendance existent (`serves`, `realizes`, `accesses`)
2. Exécuter `dependency_analysis.ajs` avec mode debug
3. Vérifier que `CP_Type` = `External` est bien défini

### Problème: DHS incohérent

**Cause:** Composants non scorés ou scores incorrects

**Solution:**
1. Lister tous composants externes: filtrer `CP_Type` = `External`
2. Vérifier que tous ont un `CP_Score_Total` > 0
3. Re-exécuter `calculate_choke_point_scores.ajs`

### Problème: Visualisation ne colore pas les vues

**Cause:** Script exécuté mais éléments non dans les vues

**Solution:**
1. Vérifier que les composants externes sont présents dans au moins une vue
2. Vérifier que `CP_Criticite` est défini
3. Re-exécuter `visualize_choke_points.ajs` avec `updateAll: true`

---

## 🎓 Formation & Best Practices

### Formation Recommandée

**Jour 1: Concepts (2h)**
- Qu'est-ce qu'un choke point ?
- Les 6 dimensions d'analyse
- Exemples concrets (AWS, OpenAI, Visa, etc.)

**Jour 2: Pratique ArchiMate (4h)**
- Modéliser l'architecture existante
- Identifier composants externes
- Scorer les 6 dimensions (workshop)

**Jour 3: Automatisation jArchi (2h)**
- Exécuter les scripts
- Générer Risk Register
- Planifier mitigations

### Best Practices

1. **Scorer de manière conservative**
   - En cas de doute, scorer plus haut (principe de précaution)
   - Valider avec experts métier et procurement

2. **Documenter les hypothèses**
   - Justifier chaque score dans `documentation` de l'élément
   - Exemple: "Score Concentration = 88 car AWS détient 40% PDM cloud EU (Gartner 2025)"

3. **Mettre à jour régulièrement**
   - Q-Review obligatoire
   - Veille M&A (acquisitions changent concentration)
   - Nouvelles alternatives (baisse substituabilité)

4. **Combiner avec autres analyses**
   - SWOT classique
   - Risk Register projet
   - Architecture Decision Records (ADR)

5. **Impliquer le COMEX**
   - DHS = KPI stratégique
   - Choke points CRITIQUES = escalation automatique
   - Budget mitigation = arbitrage COMEX

---

**Développé avec ❤️ pour architectes d'entreprise soucieux de souveraineté numérique**

*Version 1.0 - Compatible TOGAF 10.2, ArchiMate 3.2, jArchi 1.3+*
