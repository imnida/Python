# 🚀 Guide de Démarrage Rapide - jArchi

## 5 Minutes pour Commencer

### Étape 1 : Installation (2 min)

1. **Télécharger Archi**
   - Aller sur [archimatetool.com](https://www.archimatetool.com)
   - Télécharger et installer Archi

2. **Installer le plugin jArchi**
   - Dans Archi : `Help` → `Manage Plug-ins...`
   - Rechercher "jArchi" et installer
   - Redémarrer Archi

3. **Configurer les scripts**
   - Dans Archi : `Scripts` → `Scripts Manager`
   - Cliquer sur l'icône d'engrenage ⚙️
   - Pointer vers le dossier `jArchi_Scripts` de ce projet

### Étape 2 : Premier Script (1 min)

1. Créer un nouveau modèle Archi
2. Ouvrir `Scripts Manager`
3. Double-cliquer sur `examples/hello_jarchi.ajs`
4. Voir le résultat dans la console !

### Étape 3 : Créer Votre Premier Diagramme (2 min)

Exécuter le script `examples/quick_diagram.ajs` pour créer automatiquement une architecture 3-tiers complète !

## 🎯 Cas d'Usage Fréquents

### Générer un Paysage Applicatif

```javascript
// Exécuter : 02_Model_Generation/generate_application_landscape.ajs
```

Ce script crée automatiquement :
- ✅ Plusieurs applications
- ✅ Leurs services
- ✅ Les objets de données
- ✅ Les relations entre applications
- ✅ Une vue complète

**Personnalisation :** Éditer le tableau `applications` dans le script.

### Créer une Architecture Microservices

```javascript
// Exécuter : 02_Model_Generation/generate_microservices.ajs
```

Génère :
- ✅ API Gateway
- ✅ Service Registry
- ✅ Message Broker
- ✅ Microservices avec leurs BD

### Nettoyer un Modèle

```javascript
// Exécuter : 03_Bulk_Operations/bulk_delete_unused.ajs
```

Supprime automatiquement :
- ✅ Éléments sans relations
- ✅ Éléments non utilisés dans les vues
- ✅ Relations orphelines
- ✅ Relations dupliquées

### Générer un Rapport

```javascript
// Exécuter : 04_Reporting/generate_model_report.ajs
```

Affiche :
- ✅ Statistiques complètes du modèle
- ✅ Distribution par couche
- ✅ Métriques de santé
- ✅ Utilisation des propriétés

### Valider le Modèle

```javascript
// Exécuter : 06_Utilities/validate_model.ajs
```

Détecte :
- ✅ Erreurs de modélisation
- ✅ Violations de conventions
- ✅ Documentation manquante
- ✅ Noms dupliqués

## 💡 Snippets Utiles

### Créer un Élément

```javascript
var model = $("model").first();
var app = model.createObject("application-component", "Mon Application");
app.documentation = "Description de l'application";
app.prop("Status", "Active");
app.prop("Owner", "Équipe IT");
```

### Créer une Relation

```javascript
var source = $("application-component").first();
var target = $("application-service").first();
var rel = model.createRelationship("realization-relationship", "", source, target);
```

### Lister des Éléments

```javascript
// Tous les composants applicatifs
$("application-component").each(function(app) {
    console.log(app.name);
});

// Avec filtre
$("application-component").filter(function(app) {
    return app.prop("Status") === "Active";
}).each(function(app) {
    console.log("Active: " + app.name);
});
```

### Modifier des Propriétés en Masse

```javascript
$("application-component").each(function(app) {
    app.prop("Lifecycle", "Production");
    app.prop("Reviewed", "2026-01");
});
```

### Créer une Vue

```javascript
var model = $("model").first();
var view = model.createArchimateView("Ma Vue");

var app = model.createObject("application-component", "App");
var service = model.createObject("application-service", "Service");

// Ajouter à la vue avec position
view.add(app, 50, 50, 150, 60);
view.add(service, 250, 50, 150, 60);

// Créer et ajouter une relation
var rel = model.createRelationship("realization-relationship", "", app, service);
view.add(rel);
```

### Colorer des Éléments

```javascript
// Dans une vue, colorer selon une propriété
$("view").first().find("element").each(function(viewElement) {
    var elem = viewElement.concept;
    var status = elem.prop("Status");

    if (status === "Active") {
        viewElement.fillColor = "#90EE90"; // Vert
    } else if (status === "Deprecated") {
        viewElement.fillColor = "#FFB6C1"; // Rouge
    }
});
```

### Trouver des Dépendances

```javascript
var element = $("application-component").filter(function(e) {
    return e.name === "CRM System";
}).first();

console.log("Dépendances de " + element.name + ":");
$(element).outRels().each(function(rel) {
    console.log("  → " + rel.target.name + " (" + rel.type + ")");
});

console.log("\nDépendants de " + element.name + ":");
$(element).inRels().each(function(rel) {
    console.log("  ← " + rel.source.name + " (" + rel.type + ")");
});
```

## 📊 Types d'Éléments ArchiMate

### Couche Business
- `business-actor` - Acteur métier
- `business-role` - Rôle métier
- `business-process` - Processus métier
- `business-function` - Fonction métier
- `business-service` - Service métier

### Couche Application
- `application-component` - Composant applicatif
- `application-service` - Service applicatif
- `application-interface` - Interface applicative
- `data-object` - Objet de données

### Couche Technologie
- `node` - Nœud (serveur)
- `device` - Équipement
- `system-software` - Logiciel système
- `artifact` - Artefact
- `technology-service` - Service technique

### Motivation
- `stakeholder` - Partie prenante
- `driver` - Facteur d'influence
- `goal` - Objectif
- `requirement` - Exigence

## 🔗 Types de Relations

- `composition-relationship` - Composition (fait partie de)
- `aggregation-relationship` - Agrégation (groupe)
- `assignment-relationship` - Affectation (assigné à)
- `realization-relationship` - Réalisation (implémente)
- `serving-relationship` - Service (sert)
- `access-relationship` - Accès (accède à)
- `flow-relationship` - Flux (transfère à)
- `triggering-relationship` - Déclenchement (déclenche)
- `influence-relationship` - Influence

## 🎨 Conseils Pro

### 1. Tester sur une Copie
Avant d'exécuter des scripts de modification, toujours sauvegarder le modèle ou travailler sur une copie.

### 2. Utiliser la Console
La console (`Window` → `Console`) affiche les résultats et les erreurs.

### 3. Incrémenter Progressivement
Commencer par de petits scripts et augmenter la complexité progressivement.

### 4. Documenter les Changements
Ajouter des commentaires dans les scripts pour expliquer la logique.

### 5. Versionner les Scripts
Utiliser Git pour versionner vos scripts personnalisés.

## 🚨 Résolution de Problèmes

### Le script ne s'exécute pas
- Vérifier qu'un modèle est ouvert
- Vérifier la syntaxe JavaScript
- Consulter la console pour les erreurs

### Éléments non créés
- Vérifier que le type d'élément est correct
- Utiliser les types exacts (tirets, pas de camelCase)

### Relations invalides
- Vérifier que les éléments source et cible existent
- Vérifier la compatibilité des types de relation

## 📚 Aller Plus Loin

1. **Personnaliser les scripts** - Adapter les scripts à vos besoins
2. **Combiner les scripts** - Créer des workflows complexes
3. **Intégration** - Intégrer avec d'autres outils via CSV/JSON
4. **Automatisation** - Programmer des tâches récurrentes

## 🆘 Besoin d'Aide ?

- Consulter le [README.md](README.md) complet
- Visiter le [Wiki jArchi](https://github.com/archimatetool/archi-scripting-plugin/wiki)
- Poser des questions sur le [Forum Archi](https://forum.archimatetool.com/)

---

**Prêt à automatiser vos modèles ArchiMate ! 🎉**
