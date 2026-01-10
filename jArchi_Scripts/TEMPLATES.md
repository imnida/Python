# 📋 Templates de Scripts jArchi

Templates réutilisables pour créer vos propres scripts jArchi.

## Template 1 : Script de Base

```javascript
/*
 * [NOM DU SCRIPT]
 *
 * Description : [Ce que fait le script]
 * Auteur : [Votre nom]
 * Date : [Date]
 */

console.log("Début de l'exécution...");

// Obtenir le modèle actuel
var model = $("model").first();

if (!model) {
    console.log("❌ Aucun modèle trouvé. Veuillez ouvrir un modèle.");
} else {
    console.log("✓ Modèle : " + model.name);

    // === VOTRE CODE ICI ===

    console.log("✓ Script terminé avec succès !");
}
```

## Template 2 : Créateur d'Éléments avec Configuration

```javascript
/*
 * Créateur d'Éléments Configurables
 */

// ========== CONFIGURATION ==========
var config = {
    elements: [
        {type: "application-component", name: "Composant 1"},
        {type: "application-component", name: "Composant 2"},
        {type: "application-service", name: "Service 1"}
    ],
    properties: {
        "Status": "Active",
        "Owner": "IT Team",
        "Version": "1.0"
    }
};
// ===================================

console.log("Création de " + config.elements.length + " éléments...");

var model = $("model").first();
var created = [];

config.elements.forEach(function(elemConfig) {
    var elem = model.createObject(elemConfig.type, elemConfig.name);

    // Appliquer les propriétés
    for (var key in config.properties) {
        elem.prop(key, config.properties[key]);
    }

    created.push(elem);
    console.log("✓ " + elem.name);
});

console.log("\n✓ " + created.length + " éléments créés !");
```

## Template 3 : Générateur de Vue

```javascript
/*
 * Générateur de Vue Configurable
 */

// ========== CONFIGURATION ==========
var config = {
    viewName: "Ma Vue",
    layout: {
        startX: 50,
        startY: 50,
        spacing: 200,
        elementWidth: 150,
        elementHeight: 60
    },
    elements: [
        {type: "business-actor", name: "Utilisateur"},
        {type: "business-process", name: "Processus"},
        {type: "application-component", name: "Application"}
    ]
};
// ===================================

var model = $("model").first();
var view = model.createArchimateView(config.viewName);

var x = config.layout.startX;
var y = config.layout.startY;
var elements = [];

config.elements.forEach(function(elemConfig, index) {
    var elem = model.createObject(elemConfig.type, elemConfig.name);
    elements.push(elem);

    var posY = y + (index * (config.layout.elementHeight + config.layout.spacing));
    view.add(elem, x, posY, config.layout.elementWidth, config.layout.elementHeight);

    console.log("✓ Ajouté : " + elem.name);
});

// Créer des relations entre éléments adjacents
for (var i = 0; i < elements.length - 1; i++) {
    var rel = model.createRelationship("triggering-relationship", "",
        elements[i], elements[i + 1]);
    view.add(rel);
}

console.log("✓ Vue créée : " + view.name);
```

## Template 4 : Traitement en Masse

```javascript
/*
 * Traitement en Masse d'Éléments
 */

// ========== CONFIGURATION ==========
var config = {
    elementType: "application-component",  // Type d'élément à traiter
    action: "add-property",                // Action : "add-property", "rename", "color"
    property: {
        key: "Status",
        value: "Active"
    },
    filter: function(element) {
        // Filtrer les éléments (retourner true pour inclure)
        return element.name.indexOf("System") !== -1;
    }
};
// ===================================

var elements = $(config.elementType).filter(config.filter);
var processed = 0;

console.log("Traitement de " + elements.size() + " éléments...\n");

elements.each(function(elem) {
    switch(config.action) {
        case "add-property":
            elem.prop(config.property.key, config.property.value);
            console.log("✓ " + elem.name + " : propriété ajoutée");
            break;

        case "rename":
            elem.name = config.prefix + elem.name;
            console.log("✓ Renommé : " + elem.name);
            break;

        case "color":
            // Colorier dans toutes les vues
            $("view").each(function(view) {
                $(view).find(elem).each(function(viewElem) {
                    viewElem.fillColor = config.color;
                });
            });
            console.log("✓ " + elem.name + " : coloré");
            break;
    }
    processed++;
});

console.log("\n✓ " + processed + " éléments traités !");
```

## Template 5 : Rapport Personnalisé

```javascript
/*
 * Générateur de Rapport Personnalisé
 */

// ========== CONFIGURATION ==========
var config = {
    reportTitle: "Mon Rapport",
    sections: [
        {name: "Composants Applicatifs", type: "application-component"},
        {name: "Services Applicatifs", type: "application-service"},
        {name: "Nœuds Technologiques", type: "node"}
    ],
    showProperties: ["Status", "Owner", "Version"],
    showRelationships: true
};
// ===================================

console.log("=" .repeat(60));
console.log(config.reportTitle.toUpperCase());
console.log("=" .repeat(60));

config.sections.forEach(function(section) {
    var elements = $(section.type);

    console.log("\n" + section.name.toUpperCase());
    console.log("-" .repeat(60));
    console.log("Total : " + elements.size());

    elements.each(function(elem) {
        console.log("\n• " + elem.name);

        // Propriétés
        config.showProperties.forEach(function(propKey) {
            var value = elem.prop(propKey);
            if (value) {
                console.log("  " + propKey + ": " + value);
            }
        });

        // Relations
        if (config.showRelationships) {
            var inRels = $(elem).inRels().size();
            var outRels = $(elem).outRels().size();
            console.log("  Relations : " + inRels + " entrantes, " + outRels + " sortantes");
        }
    });
});

console.log("\n" + "=" .repeat(60));
console.log("✓ Rapport généré !");
```

## Template 6 : Import de Données

```javascript
/*
 * Import de Données depuis Structure
 */

// ========== DONNÉES À IMPORTER ==========
var dataToImport = {
    applications: [
        {
            name: "CRM System",
            type: "application-component",
            properties: {
                "Status": "Active",
                "Owner": "Sales Team"
            },
            services: ["Customer Management", "Sales Tracking"]
        },
        {
            name: "ERP System",
            type: "application-component",
            properties: {
                "Status": "Active",
                "Owner": "Finance Team"
            },
            services: ["Financial Reporting", "Inventory Management"]
        }
    ]
};
// =========================================

var model = $("model").first();
var imported = {elements: 0, services: 0, relationships: 0};

console.log("Import en cours...\n");

dataToImport.applications.forEach(function(appData) {
    // Créer l'application
    var app = model.createObject(appData.type, appData.name);

    // Propriétés
    for (var key in appData.properties) {
        app.prop(key, appData.properties[key]);
    }
    imported.elements++;
    console.log("✓ Application : " + app.name);

    // Créer les services
    appData.services.forEach(function(serviceName) {
        var service = model.createObject("application-service", serviceName);
        var rel = model.createRelationship("realization-relationship", "", app, service);

        imported.services++;
        imported.relationships++;
        console.log("  ✓ Service : " + serviceName);
    });
});

console.log("\n" + "=".repeat(60));
console.log("✓ Import terminé !");
console.log("  Applications : " + imported.elements);
console.log("  Services : " + imported.services);
console.log("  Relations : " + imported.relationships);
```

## Template 7 : Validation Personnalisée

```javascript
/*
 * Validation Personnalisée du Modèle
 */

// ========== RÈGLES DE VALIDATION ==========
var validationRules = [
    {
        name: "Applications doivent avoir un propriétaire",
        check: function(elem) {
            return elem.type === "application-component" && !elem.prop("Owner");
        },
        severity: "WARNING"
    },
    {
        name: "Éléments critiques doivent être documentés",
        check: function(elem) {
            return elem.prop("Criticality") === "High" &&
                   (!elem.documentation || elem.documentation.trim() === "");
        },
        severity: "ERROR"
    },
    {
        name: "Applications actives doivent avoir au moins un service",
        check: function(elem) {
            if (elem.type === "application-component" && elem.prop("Status") === "Active") {
                return $(elem).outRels("realization-relationship").size() === 0;
            }
            return false;
        },
        severity: "WARNING"
    }
];
// ===========================================

var issues = [];

console.log("Validation du modèle...\n");

$("element").each(function(elem) {
    validationRules.forEach(function(rule) {
        if (rule.check(elem)) {
            issues.push({
                severity: rule.severity,
                rule: rule.name,
                element: elem.name
            });
        }
    });
});

// Afficher les résultats
console.log("=" .repeat(60));
console.log("RÉSULTATS DE VALIDATION");
console.log("=" .repeat(60));

if (issues.length === 0) {
    console.log("\n✅ Aucun problème détecté !");
} else {
    var errors = issues.filter(function(i) { return i.severity === "ERROR"; });
    var warnings = issues.filter(function(i) { return i.severity === "WARNING"; });

    if (errors.length > 0) {
        console.log("\n❌ ERREURS (" + errors.length + ") :");
        errors.forEach(function(e) {
            console.log("  • " + e.element + " : " + e.rule);
        });
    }

    if (warnings.length > 0) {
        console.log("\n⚠️  AVERTISSEMENTS (" + warnings.length + ") :");
        warnings.forEach(function(w) {
            console.log("  • " + w.element + " : " + w.rule);
        });
    }
}

console.log("\n" + "=" .repeat(60));
```

## Template 8 : Export Personnalisé

```javascript
/*
 * Export de Données au Format Personnalisé
 */

// ========== CONFIGURATION ==========
var config = {
    elementType: "application-component",
    format: "markdown",  // "markdown", "csv", "json"
    includeProperties: ["Status", "Owner", "Version"],
    includeRelationships: true
};
// ===================================

var elements = $(config.elementType);
var output = "";

if (config.format === "markdown") {
    output = "# " + config.elementType + " Report\n\n";

    elements.each(function(elem) {
        output += "## " + elem.name + "\n\n";
        output += "**Type:** " + elem.type + "\n\n";

        if (elem.documentation) {
            output += "**Description:** " + elem.documentation + "\n\n";
        }

        output += "**Properties:**\n";
        config.includeProperties.forEach(function(prop) {
            var value = elem.prop(prop) || "N/A";
            output += "- " + prop + ": " + value + "\n";
        });

        if (config.includeRelationships) {
            output += "\n**Relationships:**\n";
            $(elem).outRels().each(function(rel) {
                output += "- → " + rel.target.name + " (" + rel.type + ")\n";
            });
        }

        output += "\n---\n\n";
    });

} else if (config.format === "csv") {
    output = "Name,Type," + config.includeProperties.join(",") + "\n";

    elements.each(function(elem) {
        var row = '"' + elem.name + '","' + elem.type + '"';
        config.includeProperties.forEach(function(prop) {
            var value = elem.prop(prop) || "";
            row += ',"' + value + '"';
        });
        output += row + "\n";
    });
}

console.log("=" .repeat(60));
console.log("EXPORT - " + config.format.toUpperCase());
console.log("=" .repeat(60));
console.log(output);
console.log("=" .repeat(60));
console.log("\n✓ " + elements.size() + " éléments exportés");
```

## 💡 Conseils d'Utilisation des Templates

1. **Copier le template** qui correspond à votre besoin
2. **Modifier la section CONFIGURATION** selon vos besoins
3. **Tester sur une copie** de votre modèle
4. **Ajuster et itérer** selon les résultats
5. **Sauvegarder votre script** pour réutilisation

## 🔗 Combinaison de Templates

Vous pouvez combiner plusieurs templates pour créer des workflows complexes :

```javascript
// 1. Import de données
// 2. Création de vues
// 3. Validation
// 4. Export de rapport
```

---

**Personnalisez ces templates pour créer vos propres automatisations ! 🎨**
