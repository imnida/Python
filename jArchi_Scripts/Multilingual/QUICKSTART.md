# Guide de Démarrage Rapide - Multilinguisme ArchiMate
## 5 minutes pour des modèles multilingues

---

## 🚀 Démarrage en 4 Étapes

### Étape 1 : Initialiser (1 minute)

**Ouvrir Archi** → **Scripts** → `Multilingual/01_Setup/init_multilingual_properties.ajs`

**Configurer la langue par défaut** :
```javascript
var config = {
    defaultLanguage: "fr",  // ← Votre langue actuelle
};
```

**Exécuter** → ✅ Toutes les propriétés `ML_*` sont créées !

**Résultat Console** :
```
✅ Initialisation terminée !
📊 Objets traités:
   • Éléments initialisés: 44
   • Propriétés ajoutées: 1248
```

---

### Étape 2 : Exporter (30 secondes)

**Scripts** → `Multilingual/03_Import_Export/export_translations.ajs`

**Exécuter** → Fichier `translations_export.csv` créé dans le dossier du modèle

**Résultat** :
```
✅ Export réussi !
📁 Fichier: /path/to/model/translations_export.csv
   • Taille: 47.52 KB
   • Lignes: 103
```

---

### Étape 3 : Traduire (2 minutes)

**Ouvrir** `translations_export.csv` avec **Excel** ou **LibreOffice**

**Compléter les colonnes** :

| ML_Name_fr | ML_Name_en | ML_Name_de |
|------------|------------|------------|
| Service de Paiement | **Payment Service** | **Zahlungsservice** |
| Visa / Mastercard | Visa / Mastercard | Visa / Mastercard |

**Sauvegarder** le fichier (même nom, même emplacement)

---

### Étape 4 : Importer et Basculer (1 minute)

**Importer** : Scripts → `import_translations.ajs`

```
✅ Import terminé !
📊 Propriétés mises à jour: 408
```

**Basculer vers anglais** : Scripts → `switch_language.ajs`

```javascript
var config = {
    targetLanguage: "en"  // ← Changer ici
};
```

**Exécuter** → 🎉 **Tout le modèle est maintenant en anglais !**

```
✅ Basculement terminé !
🌐 Langue active: 🇬🇧 English
📊 Éléments mis à jour: 44
```

---

## 🔄 Workflow Quotidien

### Basculer vers français
```javascript
// switch_language.ajs
targetLanguage: "fr"
```

### Basculer vers allemand
```javascript
// switch_language.ajs
targetLanguage: "de"
```

### Vérifier la couverture
```javascript
// Exécuter: generate_multilingual_report.ajs
```

**Résultat** :
```
🇫🇷 Français (FR): Couverture globale: 100.0%
🇬🇧 English (EN): Couverture globale: 85.3%
🇩🇪 Deutsch (DE): Couverture globale: 42.2% ⚠️
```

---

## 📝 Exemples Rapides

### Exemple 1 : Traduire un élément spécifique

**Sélectionner** l'élément dans une vue

**Exécuter** `set_translations.ajs` :

```javascript
var config = {
    translations: {
        "API Gateway": {
            en: "API Gateway",
            de: "API-Gateway",
            es: "Puerta de Enlace API"
        }
    }
};
```

---

### Exemple 2 : Export JSON au lieu de CSV

```javascript
// export_translations.ajs
var config = {
    format: "json"  // ← Changer de "csv" à "json"
};
```

---

### Exemple 3 : Valider les propriétés

**Exécuter** `validate_multilingual_properties.ajs`

```
📊 Statistiques:
   • Objets vérifiés: 102
   • Erreurs trouvées: 0
   • Avertissements: 0

🎉 Aucune erreur détectée !
```

---

## 🎯 Cas d'Usage Fréquents

### Cas 1 : Présentation COMEX en français, Board en anglais

1. **Avant la présentation FR** :
   ```javascript
   switch_language.ajs → targetLanguage: "fr"
   ```
2. Exporter les vues en PNG
3. **Avant la présentation EN** :
   ```javascript
   switch_language.ajs → targetLanguage: "en"
   ```
4. Exporter les vues en PNG

**Résultat** : Même modèle, deux présentations !

---

### Cas 2 : Collaboration internationale

**Architecte FR** :
```javascript
switch_language.ajs → targetLanguage: "fr"
```

**Architecte DE** :
```javascript
switch_language.ajs → targetLanguage: "de"
```

**Architecte EN** :
```javascript
switch_language.ajs → targetLanguage: "en"
```

**Chacun travaille dans sa langue, un seul modèle partagé !**

---

### Cas 3 : Ajout d'éléments après initialisation

1. **Créer** de nouveaux éléments (dans votre langue)
2. **Ré-exécuter** `init_multilingual_properties.ajs`
3. **Exporter** → Traduire → Importer

**Les nouveaux éléments sont automatiquement initialisés !**

---

## ⚡ Commandes Essentielles

| Action | Script | Config Clé |
|--------|--------|------------|
| **Initialiser** | `init_multilingual_properties.ajs` | `defaultLanguage: "fr"` |
| **Basculer EN** | `switch_language.ajs` | `targetLanguage: "en"` |
| **Basculer FR** | `switch_language.ajs` | `targetLanguage: "fr"` |
| **Basculer DE** | `switch_language.ajs` | `targetLanguage: "de"` |
| **Exporter CSV** | `export_translations.ajs` | `format: "csv"` |
| **Exporter JSON** | `export_translations.ajs` | `format: "json"` |
| **Importer** | `import_translations.ajs` | `inputFile: "..."` |
| **Vérifier** | `generate_multilingual_report.ajs` | - |
| **Valider** | `validate_multilingual_properties.ajs` | - |

---

## 🌐 Langues Disponibles

| Code | Langue | Flag |
|------|--------|------|
| `fr` | Français | 🇫🇷 |
| `en` | English | 🇬🇧 |
| `de` | Deutsch | 🇩🇪 |
| `es` | Español | 🇪🇸 |
| `it` | Italiano | 🇮🇹 |
| `pt` | Português | 🇵🇹 |
| `nl` | Nederlands | 🇳🇱 |
| `zh` | 中文 | 🇨🇳 |
| `ja` | 日本語 | 🇯🇵 |
| `ar` | العربية | 🇸🇦 |

---

## ❓ FAQ Express

**Q : Mes traductions sont-elles sauvegardées ?**
✅ OUI, dans le fichier `.archimate` (propriétés `ML_*`)

**Q : Puis-je ajouter d'autres langues ?**
✅ OUI, modifier `supportedLanguages` dans `init_multilingual_properties.ajs`

**Q : Que se passe-t-il si une traduction manque ?**
ℹ️ Fallback vers la langue par défaut (configurable)

**Q : Puis-je utiliser Google Translate ?**
✅ OUI, exporter CSV → traduire avec API → importer

**Q : Le multilinguisme ralentit-il Archi ?**
✅ NON, impact minimal (<10% au chargement)

---

## 🆘 Problèmes Courants

### "ML_Default_Language manquant"
→ Exécuter `init_multilingual_properties.ajs`

### "Traductions vides après import"
→ Vérifier que le CSV a bien les colonnes `ML_Name_en`, etc.

### "Caractères spéciaux corrompus dans Excel"
→ Ouvrir le CSV en spécifiant UTF-8 lors de l'import

### "La langue ne change pas"
→ Vérifier qu'il y a des traductions : `generate_multilingual_report.ajs`

---

## 📚 Documentation Complète

Pour aller plus loin : **`README_MULTILINGUAL.md`**

Contient :
- Architecture détaillée du système
- Format des propriétés ML_*
- Workflows avancés
- Intégration Constitutional AI
- Cas d'usage complets
- Troubleshooting exhaustif

---

## ✅ Checklist de Démarrage

- [ ] Modèle ArchiMate ouvert dans Archi
- [ ] Scripts jArchi installés (dossier `Multilingual/`)
- [ ] Langue par défaut configurée (`defaultLanguage`)
- [ ] `init_multilingual_properties.ajs` exécuté
- [ ] Export réalisé (`export_translations.ajs`)
- [ ] Fichier CSV traduit (Excel/LibreOffice)
- [ ] Import réalisé (`import_translations.ajs`)
- [ ] Premier basculement testé (`switch_language.ajs`)
- [ ] Rapport de couverture vérifié (`generate_multilingual_report.ajs`)

---

**Prêt à commencer ?** 🚀

1. **Ouvrir** Archi
2. **Scripts** → `init_multilingual_properties.ajs`
3. **Exécuter**
4. **Suivre** les 4 étapes ci-dessus

**Bonne architecture multilingue !** 🌐

---

**Version** : 1.0 | **Date** : 2026-01-10 | **Constitutional AI Framework**
