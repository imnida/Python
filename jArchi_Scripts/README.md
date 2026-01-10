# jArchi Scripts Collection

Une collection complète de scripts jArchi pour automatiser la création et la gestion de modèles ArchiMate.

## 📋 Table des Matières

- [Introduction](#introduction)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Structure du Projet](#structure-du-projet)
- [Guide d'Utilisation](#guide-dutilisation)
- [Catalogue de Scripts](#catalogue-de-scripts)
- [Exemples](#exemples)
- [Bonnes Pratiques](#bonnes-pratiques)
- [Ressources](#ressources)

## 🎯 Introduction

**jArchi** est un plugin de scripting pour Archi qui permet d'automatiser la création, la modification et l'analyse de modèles ArchiMate en utilisant JavaScript.

Cette collection fournit des scripts prêts à l'emploi pour :
- ✅ Créer rapidement des éléments et des vues
- ✅ Générer des architectures complètes (microservices, layered, etc.)
- ✅ Effectuer des opérations en masse (renommage, propriétés, etc.)
- ✅ Générer des rapports et analyses
- ✅ Importer/Exporter des données
- ✅ Valider et nettoyer les modèles

## 📦 Prérequis

1. **Archi** - Télécharger depuis [https://www.archimatetool.com](https://www.archimatetool.com)
2. **jArchi Plugin** - Installer depuis le menu Archi :
   - `Help` → `Manage Plug-ins...` → Rechercher "jArchi"
   - Ou télécharger depuis [https://github.com/archimatetool/archi-scripting-plugin](https://github.com/archimatetool/archi-scripting-plugin)

## 🚀 Installation

1. Cloner ou télécharger ce repository
2. Dans Archi, ouvrir le panneau Scripts : `Scripts` → `Scripts Manager`
3. Configurer le dossier de scripts :
   - Cliquer sur l'icône d'engrenage
   - Pointer vers le dossier `jArchi_Scripts`
4. Les scripts apparaîtront automatiquement dans le panneau

## 📁 Structure du Projet

```
jArchi_Scripts/
├── 01_Basic_Operations/      # Scripts de base pour démarrer
│   ├── create_elements.ajs
│   ├── create_relationships.ajs
│   └── create_view.ajs
│
├── 02_Model_Generation/       # Génération de modèles complets
│   ├── generate_application_landscape.ajs
│   ├── generate_layered_view.ajs
│   └── generate_microservices.ajs
│
├── 03_Bulk_Operations/        # Opérations en masse
│   ├── bulk_rename_elements.ajs
│   ├── bulk_set_properties.ajs
│   ├── bulk_delete_unused.ajs
│   └── bulk_color_by_property.ajs
│
├── 04_Reporting/              # Rapports et analyses
│   ├── generate_model_report.ajs
│   ├── export_to_csv.ajs
│   ├── find_dependencies.ajs
│   └── view_usage_report.ajs
│
├── 05_Import_Export/          # Import/Export de données
│   ├── import_from_csv.ajs
│   └── export_to_json.ajs
│
├── 06_Utilities/              # Utilitaires
│   ├── validate_model.ajs
│   ├── find_and_replace.ajs
│   └── backup_model.ajs
│
├── examples/                  # Exemples simples
│   ├── hello_jarchi.ajs
│   └── quick_diagram.ajs
│
└── README.md                  # Ce fichier
```

## 📖 Guide d'Utilisation

### Exécuter un Script

1. Ouvrir un modèle Archi ou créer un nouveau modèle
2. Ouvrir le panneau Scripts (`Scripts` → `Scripts Manager`)
3. Double-cliquer sur le script souhaité
4. Consulter les résultats dans la console

### Modifier un Script

Tous les scripts sont configurables. Cherchez la section `Configuration` au début du script :

```javascript
// Configuration
var config = {
    elementType: "application-component",
    prefix: "NEW_",
    // ... autres options
};
```

## 📚 Catalogue de Scripts

### 01_Basic_Operations

#### `create_elements.ajs`
Crée des exemples d'éléments pour toutes les couches ArchiMate (Business, Application, Technology, Motivation, etc.).

**Utilisation :** Idéal pour apprendre la syntaxe ou peupler rapidement un modèle de test.

#### `create_relationships.ajs`
Démontre comment créer différents types de relations ArchiMate (composition, aggregation, assignment, realization, etc.).

#### `create_view.ajs`
Crée une vue avec éléments positionnés automatiquement.

### 02_Model_Generation

#### `generate_application_landscape.ajs`
Génère un paysage applicatif complet avec :
- Composants applicatifs
- Services applicatifs
- Objets de données
- Relations entre applications

**Personnalisation :** Modifier le tableau `applications` pour définir votre propre landscape.

#### `generate_layered_view.ajs`
Crée une architecture en couches (Business → Application → Technology) avec relations inter-couches.

#### `generate_microservices.ajs`
Génère une architecture microservices avec :
- API Gateway
- Service Registry
- Message Broker
- Microservices avec leurs bases de données

### 03_Bulk_Operations

#### `bulk_rename_elements.ajs`
Renomme des éléments en masse selon différents modes :
- Ajouter un préfixe/suffixe
- Rechercher et remplacer
- Appliquer des conventions de nommage

**Configuration :**
```javascript
var config = {
    mode: "prefix",  // "prefix", "suffix", "replace", "convention"
    prefix: "NEW_",
    applyTo: "application-component"
};
```

#### `bulk_set_properties.ajs`
Définit des propriétés sur plusieurs éléments simultanément (Status, Owner, Lifecycle, etc.).

#### `bulk_delete_unused.ajs`
Nettoie le modèle en supprimant :
- Éléments sans relations
- Éléments non utilisés dans les vues
- Relations orphelines ou dupliquées

#### `bulk_color_by_property.ajs`
Colore automatiquement les éléments dans les vues selon leurs propriétés (Status, Criticality, etc.).

### 04_Reporting

#### `generate_model_report.ajs`
Génère un rapport complet avec :
- Statistiques d'éléments par type
- Distribution par couche
- Statistiques de relations
- Métriques de santé du modèle

#### `export_to_csv.ajs`
Exporte les éléments vers CSV pour analyse dans Excel.

#### `find_dependencies.ajs`
Analyse les dépendances d'un élément :
- Dépendances directes
- Dépendants (qui dépend de cet élément)
- Dépendances transitives
- Score d'impact

#### `view_usage_report.ajs`
Rapport sur l'utilisation des vues :
- Éléments les plus/moins utilisés
- Éléments non présents dans les vues
- Couverture du modèle

### 05_Import_Export

#### `import_from_csv.ajs`
Importe des éléments depuis des données CSV.

**Format CSV :**
```csv
Name,Type,Documentation,Status,Owner
CRM System,application-component,Customer management,Active,IT
```

#### `export_to_json.ajs`
Exporte le modèle complet en JSON (éléments, relations, vues).

### 06_Utilities

#### `validate_model.ajs`
Valide le modèle et détecte :
- Éléments sans nom
- Relations invalides
- Violations de conventions de nommage
- Documentation manquante
- Éléments orphelins
- Noms dupliqués

#### `find_and_replace.ajs`
Recherche et remplace du texte dans :
- Noms d'éléments
- Documentation
- Valeurs de propriétés

#### `backup_model.ajs`
Crée une sauvegarde textuelle des métadonnées du modèle.

## 💡 Exemples

### Exemple 1 : Créer un Diagramme Simple

```javascript
var model = $("model").first();
var view = model.createArchimateView("My View");

var app = model.createObject("application-component", "My App");
var service = model.createObject("application-service", "My Service");
var rel = model.createRelationship("realization-relationship", "", app, service);

view.add(app, 50, 50, 120, 55);
view.add(service, 50, 150, 120, 55);
view.add(rel);
```

### Exemple 2 : Lister Tous les Composants Applicatifs

```javascript
$("application-component").each(function(app) {
    console.log(app.name + " - " + app.prop("Status"));
});
```

### Exemple 3 : Trouver les Éléments Sans Relations

```javascript
$("element").each(function(elem) {
    var totalRels = $(elem).inRels().size() + $(elem).outRels().size();
    if (totalRels === 0) {
        console.log("No relationships: " + elem.name);
    }
});
```

## 🎨 Bonnes Pratiques

### 1. Conventions de Nommage
- Utiliser des noms descriptifs et cohérents
- Éviter les acronymes non documentés
- Utiliser Title Case pour les éléments

### 2. Organisation du Modèle
- Grouper les éléments liés dans les mêmes vues
- Utiliser des propriétés pour catégoriser
- Documenter les décisions d'architecture

### 3. Propriétés Recommandées
- **Status** : Active, Deprecated, Planned, Retired
- **Owner** : Équipe ou personne responsable
- **Lifecycle** : Development, Production, Legacy
- **Criticality** : High, Medium, Low
- **Version** : Numéro de version

### 4. Gestion des Vues
- Limiter à 15-20 éléments par vue pour la lisibilité
- Créer des vues par domaine ou par couche
- Utiliser des couleurs de manière cohérente

### 5. Scripts
- Toujours tester sur une copie du modèle
- Commenter les modifications importantes
- Versionner vos scripts personnalisés

## 🔧 API jArchi - Référence Rapide

### Sélection d'Éléments
```javascript
$("model").first()                    // Le modèle actuel
$("element")                          // Tous les éléments
$("application-component")            // Par type
$("element").filter(function(e) {     // Avec filtre
    return e.name.indexOf("CRM") !== -1;
})
```

### Création
```javascript
model.createObject(type, name)
model.createRelationship(type, name, source, target)
model.createArchimateView(name)
```

### Types d'Éléments Courants
- `business-actor`, `business-role`, `business-process`, `business-service`
- `application-component`, `application-service`, `application-interface`
- `node`, `device`, `system-software`, `artifact`
- `data-object`

### Types de Relations
- `composition-relationship`
- `aggregation-relationship`
- `assignment-relationship`
- `realization-relationship`
- `serving-relationship`
- `access-relationship`
- `flow-relationship`
- `triggering-relationship`

### Propriétés
```javascript
element.name                          // Nom
element.documentation                 // Documentation
element.prop("key", "value")          // Définir propriété
element.prop("key")                   // Lire propriété
element.prop()                        // Toutes les propriétés
```

### Relations
```javascript
$(element).inRels()                   // Relations entrantes
$(element).outRels()                  // Relations sortantes
$(element).rels()                     // Toutes les relations
```

### Vues
```javascript
view.add(element, x, y, width, height)
view.add(relationship)
$(view).find("element")
```

## 📚 Ressources

### Documentation Officielle
- [Archi](https://www.archimatetool.com/)
- [jArchi Wiki](https://github.com/archimatetool/archi-scripting-plugin/wiki)
- [ArchiMate Specification](https://pubs.opengroup.org/architecture/archimate3-doc/)

### Communauté
- [Archi Forum](https://forum.archimatetool.com/)
- [jArchi GitHub](https://github.com/archimatetool/archi-scripting-plugin)

### Tutoriels
- [jArchi Collection Scripts](https://github.com/archimatetool/archi-scripting-plugin/tree/master/com.archimatetool.script/src/com/archimatetool/script/dom)

## 🤝 Contribution

N'hésitez pas à :
- Proposer de nouveaux scripts
- Signaler des bugs
- Améliorer la documentation
- Partager vos cas d'usage

## 📝 Licence

Ces scripts sont fournis à titre d'exemple et peuvent être librement modifiés et distribués.

## ✨ Auteur

Scripts créés pour faciliter l'automatisation de modèles ArchiMate avec jArchi.

---

**Bon scripting avec jArchi ! 🚀**
