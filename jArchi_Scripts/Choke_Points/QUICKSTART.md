# ⚡ Quick Start - Choke Points en 10 Minutes

## 1️⃣ Initialiser (1 min)

```
Exécuter: 01_Setup/init_choke_point_properties.ajs
```

✅ Ajoute les propriétés CP_* à tous vos composants

## 2️⃣ Marquer les Externes (2 min)

Pour chaque vendor/SaaS/cloud dans votre modèle:

1. Sélectionner l'élément
2. Propriétés → Ajouter:
   - `CP_Type` = `External`
   - `CP_Vendor` = nom vendor (ex: `AWS`)
   - `CP_Juridiction` = `US` ou `EU` ou `Other`

## 3️⃣ Scorer les 6 Dimensions (5 min)

Pour chaque composant externe, évaluer **0 à 100**:

| Dimension | Question Clé | Exemple Haut (>80) |
|-----------|--------------|---------------------|
| **Concentration** | Part de marché vendor? | Monopole/Duopole |
| **Substituabilité** | Délai migration? | >18 mois |
| **Externalités** | Lock-in propriétaire? | Effet réseau fort |
| **Asymétrie** | Leverage négociation? | Vous dépendez, pas lui |
| **Opacité** | Auditable? | Boîte noire |
| **Extraterritorialité** | Juridiction? | US (Cloud Act) |

**Exemples rapides:**
- **AWS EC2**: 88, 92, 70, 85, 60, 95 → **82/100 CRITIQUE**
- **PostgreSQL**: 30, 40, 20, 30, 10, 10 → **24/100 ACCEPTABLE**
- **OpenAI GPT-4**: 95, 85, 60, 90, 100, 100 → **88/100 CRITIQUE**

## 4️⃣ Calculer (30 sec)

```
Exécuter: 02_Analysis/calculate_choke_point_scores.ajs
```

✅ Calcule scores totaux et criticité (CRITIQUE/ELEVE/MOYEN/ACCEPTABLE)

## 5️⃣ Analyser (30 sec)

```
Exécuter: 03_Reporting/generate_risk_register.ajs
```

✅ Génère le Risk Register complet

## 6️⃣ Visualiser (30 sec)

```
Exécuter: 04_Visualization/visualize_choke_points.ajs
```

✅ Colore les vues:
- 🔴 Rouge = CRITIQUE (≥80)
- 🟠 Orange = ÉLEVÉ (60-79)
- 🟡 Jaune = MOYEN (40-59)
- 🟢 Vert = ACCEPTABLE (<40)

---

## 📊 Interpréter les Résultats

### Dependency Health Score (DHS)

```
DHS = 100 - (Score Moyen Choke Points)
```

- **DHS ≥ 70**: ✅ OK (autonomie acceptable)
- **DHS 50-69**: ⚠️ ATTENTION (surveillance renforcée)
- **DHS < 50**: 🚨 ALERTE (architecture non souveraine)

### Actions Immédiates

| Si... | Alors... |
|-------|----------|
| Score ≥ 85 | 🚨 Escalation COMEX immédiate |
| Score 80-84 | 🔴 Mitigation obligatoire (< 6 mois) |
| DHS < 50 | 🚨 Refonte stratégique requise |
| 3+ SPOF | 🔴 Architecture découplée urgente |

---

## 🎯 Exemple Complet : AWS Cloud

### Avant

```archimate
Application Component: "Banking App"
  └─runs_on→ Node: "AWS EC2" (vendor unknown)
```

### Après Scoring

```archimate
Node: "AWS EC2"
  CP_Type: External
  CP_Vendor: AWS
  CP_Juridiction: US

  CP_Concentration: 88      # Oligopole
  CP_Substituabilite: 92    # 18 mois migration
  CP_Externalites: 70       # Services complémentaires
  CP_Asymetrie: 85          # Leverage faible
  CP_Opacite: 60            # Pricing opaque
  CP_Extraterritorialite: 95 # Cloud Act

  → CP_Score_Total: 82/100
  → CP_Criticite: CRITIQUE 🔴
```

### Mitigation

```
CP_Mitigation: "Hybrid cloud: Gaia-X (Tier 1 PII) + GCP (Tier 2)"
CP_Budget: "€5M"
CP_DRI: "Infrastructure Lead"
CP_Timeline: "Q4 2025"
```

---

## 🔄 Workflow Récurrent

**Mensuel:**
- Mettre à jour scores si évolution marché

**Trimestriel (Q-Review):**
1. Re-générer Risk Register
2. Analyser Top 10 Choke Points
3. Vérifier DHS (seuil: ≥70)
4. Valider mitigations en cours
5. Escalader COMEX si nouveaux CRITIQUES

**Annuel:**
- Audit complet de tous les scores
- Validation par procurement + CISO
- Mise à jour stratégie souveraineté

---

## 📚 Aller Plus Loin

- 📖 Guide complet: [README_CHOKE_POINTS.md](README_CHOKE_POINTS.md)
- 🎯 Méthodologie détaillée: Voir prompt original
- 🛠️ Scripts avancés: `dependency_analysis.ajs`, `generate_choke_point_canvas.ajs`

---

**🚀 Prêt à détecter vos choke points en 10 minutes !**
