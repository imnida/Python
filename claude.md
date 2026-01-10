# Guide Claude - Projet jArchi Scripts

## 🎯 Contexte du Projet

Ce dépôt contient une collection complète de scripts jArchi pour l'automatisation d'ArchiMate, incluant:
- Systèmes de gestion multilingue
- Gestion d'identifiants uniques
- Analyse As-Is / To-Be
- Détection de Choke Points
- Framework Constitutional AI (TOGAF)
- Génération d'écosystème de paiement

## ✅ Bonnes Pratiques jArchi (IMPORTANT!)

### Création d'Éléments ArchiMate

**✅ CORRECT:**
```javascript
var element = model.createElement("business-actor", "Customer");
var app = model.createElement("application-component", "CRM System");
```

**❌ INCORRECT:**
```javascript
var element = model.createObject("business-actor", "Customer");  // NE PAS UTILISER
```

### Création de Relations

**✅ CORRECT:**
```javascript
// Signature: createRelationship(type, name, source, target)
var rel = model.createRelationship("serving-relationship", "", service, actor);
var rel2 = model.createRelationship("realization-relationship", "realizes", app, service);
```

### Itération sur Collections

**✅ CORRECT:**
```javascript
$("element").each(function(elem) {
    // Traiter elem
});

$("business-actor").each(function(actor) {
    console.log(actor.name);
});
```

**⚠️ Acceptable mais moins standard:**
```javascript
elements.forEach(function(elem) {
    // Fonctionne mais .each() est préféré
});
```

### Sélection d'Éléments

**✅ CORRECT:**
```javascript
var model = $("model").first();
var view = $(selection).filter("archimate-diagram-model").first();
var actors = $("business-actor");
```

### Gestion d'Erreurs

**✅ CORRECT:**
```javascript
try {
    // code
} catch (error) {
    console.log("❌ Erreur: " + error);
    // Le script se termine naturellement
}
```

**❌ INCORRECT:**
```javascript
java.lang.System.exit(1);  // Trop brutal, ne pas utiliser
```

### Import Java (Dialogues, I/O)

**✅ CORRECT:**
```javascript
var Files = Java.type("java.nio.file.Files");
var Paths = Java.type("java.nio.file.Paths");
var ListSelectionDialog = Java.type("org.eclipse.ui.dialogs.ListSelectionDialog");
```

### Console

**✅ CORRECT:**
```javascript
console.clear();
console.show();
console.log("Message");
```

## 📚 Code de Référence

Le script `AuditModel.ajs` (fourni par l'utilisateur) est la référence absolue pour les bonnes pratiques. Il démontre:
- Utilisation correcte de `createElement()`
- Création de folders avec `createFolder()`
- Création de vues avec `createArchimateView()`
- Patterns d'itération avec `.each()`
- Gestion des relations
- Dialogues utilisateur avec `window.promptSelection()`
- Expressions régulières pour validation

## 🔧 Structure du Projet

```
jArchi_Scripts/
├── 01_Basic_Operations/          # Scripts de base (éléments, vues, relations)
├── 02_Model_Generation/          # Générateurs de modèles (microservices, etc.)
├── 03_Bulk_Operations/           # Opérations en masse
├── 04_Reporting/                 # Génération de rapports
├── 05_Import_Export/             # Import/Export CSV/JSON
├── 06_Utilities/                 # Utilitaires (validation, backup)
├── AsIs_ToBe/                    # Gestion états architecturaux
├── Choke_Points/                 # Détection et analyse des choke points
├── Constitutional_AI/            # Framework TOGAF/ArchiMate
├── ID_Management/                # Génération d'identifiants uniques
├── Multilingual/                 # Système multilingue complet
├── Payment_Ecosystem/            # Modèle d'écosystème de paiement
└── examples/                     # Exemples simples
```

## 🐛 Erreurs Corrigées (2026-01-10)

### Commit: "Fix jArchi scripts: use correct jArchi API methods"

**Problèmes identifiés et corrigés:**
1. ✅ Remplacement de `model.createObject()` → `model.createElement()` (10 fichiers)
2. ✅ Suppression de `java.lang.System.exit(1)` en faveur d'une terminaison naturelle
3. ✅ Tous les scripts alignés avec les bonnes pratiques jArchi

**Fichiers modifiés:**
- `01_Basic_Operations/` (create_elements, create_view, create_relationships)
- `02_Model_Generation/` (generate_microservices, generate_layered_view, generate_application_landscape)
- `05_Import_Export/import_from_csv.ajs`
- `Multilingual/01_Setup/init_multilingual_properties.ajs`
- `Payment_Ecosystem/generate_payment_ecosystem.ajs`
- `examples/quick_diagram.ajs`

## 🎨 Conventions de Code

### Logging avec Emojis
```javascript
function log(level, message) {
    var prefix = {
        "INFO": "ℹ️  ",
        "SUCCESS": "✅ ",
        "WARNING": "⚠️  ",
        "ERROR": "❌ "
    }[level] || "";
    console.log(prefix + message);
}
```

### Configuration Centralisée
```javascript
var config = {
    // Toujours documenter les options
    overwriteExisting: false,
    validateUniqueness: true,
    verboseLogging: false
};
```

### Statistiques de Traitement
```javascript
var stats = {
    elementsProcessed: 0,
    idsGenerated: 0,
    errors: 0
};
```

## 📖 Documentation des Scripts

Chaque script doit avoir un en-tête clair:
```javascript
/*
 * Nom du Script
 *
 * Description : Description courte
 * Auteur : [Auteur]
 * Date : YYYY-MM-DD
 * Version : X.Y
 *
 * Fonctionnalités :
 *   - Liste des fonctionnalités
 *
 * Usage :
 *   - Instructions d'utilisation
 */
```

## 🔗 Intégrations

### Constitutional AI Framework
Les scripts marqués avec "Constitutional AI" suivent les principes:
- **Traçabilité**: Chaque élément technique doit être traçable à la couche Motivation
- **Falsifiabilité**: Conditions de test et validation explicites
- **Choke Points**: Identification des dépendances critiques

### Propriétés Standards
- `ID_Business`, `ID_Technical`, `ID_Original` (ID Management)
- `ML_Name_{lang}`, `ML_Description_{lang}` (Multilingual)
- `State`, `State_Transition_Date`, `Migration_Risk` (As-Is/To-Be)
- `CP_*` (Choke Points: Concentration, Substituabilité, etc.)

## 🚀 Workflow Recommandé

1. **Initialisation**: Exécuter les scripts `01_Setup/init_*.ajs`
2. **Analyse**: Utiliser les scripts `02_Analysis/`
3. **Visualisation**: Scripts `03_Visualization/` ou `04_Visualization/`
4. **Reporting**: Générer les rapports avec `04_Reporting/`

## ⚠️ Points d'Attention

1. **Ne jamais** utiliser `createObject()` - toujours `createElement()`
2. **Toujours** vérifier que le modèle existe avant manipulation
3. **Préférer** `.each()` à `.forEach()` pour les collections jArchi
4. **Utiliser** `.first()` après les sélections jQuery-like
5. **Éviter** les imports Java inutiles - jArchi fournit la plupart des APIs nécessaires

## 📝 Notes pour Claude

- Le code de référence (`AuditModel.ajs`) est **toujours** la source de vérité
- En cas de doute sur une API jArchi, se référer à ce fichier
- Les scripts doivent être **autonomes** et **bien documentés**
- Privilégier la **clarté** à la **concision**
- Les messages console doivent être **informatifs** et utiliser des emojis pour la lisibilité

---

**Dernière mise à jour**: 2026-01-10
**Statut**: ✅ Tous les scripts fonctionnels et conformes aux bonnes pratiques
