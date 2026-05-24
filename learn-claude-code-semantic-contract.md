# Le contrat sémantique : nouvelle discipline du développement LLM-native

## Le renversement du "Client" GoF

| Aspect | GoF Classique | Harness LLM |
|--------|--------------|-------------|
| **Client** | Code déterministe | LLM probabiliste |
| **Contrat** | Signature de méthode (types) | JSON Schema + docstring (sémantique) |
| **Validation** | Compile-time / type checker | Runtime / cohérence sémantique |
| **Documentation** | Commentaire pour humains | Spécification exécutable |
| **Erreur d'usage** | `TypeError` → rejet immédiat | Hallucination → dérive silencieuse |

> *"Le contrat n'est plus dans la signature, il est dans la sémantique."*

---

## Loi fondamentale : *"Un outil mal documenté est un outil cassé"*

```python
# ❌ Fonctionnel mais inutilisable par un LLM
def save_architecture_element(name, type, properties):
    """Save an element."""  # Trop vague : quel type ? quelles propriétés ?
    ...

# ✅ LLM-ready
def save_architecture_element(
    name: str,
    type: Literal["Application", "Data", "Business"],
    properties: dict
):
    """
    Persist a new ArchiMate element in the EA360 model.

    USE WHEN: The user wants to create a structured architecture component
    after validation of its relationships and compliance with TOGAF metamodel.

    NEVER USE FOR: Temporary notes, informal diagrams, or elements without
    clear stakeholder value.

    Args:
        name: Human-readable identifier (must be unique within its layer)
        type: ArchiMate layer category — affects validation rules
        properties: Dict containing mandatory fields per type:
            - Application: { "interfaces": [], "technology": str }
            - Data: { "sensitivity": "public|internal|confidential", "owner": str }
            - Business: { "process_owner": str, "kpi": Optional[str] }

    Returns:
        dict: { "id": str, "status": "created|updated", "warnings": List[str] }
    """
```

La docstring devient du **code fonctionnel**. Le LLM la "compile" en décision d'usage.

---

## Approche Schema-First + Doc-First

```yaml
# tools/architecture/create_element.yaml
name: create_architecture_element
description: |
  Create a validated ArchiMate element within the EA360 metamodel.
  Enforces TOGAF 10 compliance and data sovereignty rules.
parameters:
  type: object
  properties:
    element_type:
      type: string
      enum: [BusinessProcess, ApplicationComponent, DataObject]
      description: |
        The ArchiMate 3.2 concept. Determines which validation rules
        and required properties apply.
required: [name, element_type]
```

Cette spécification devient **la source de vérité unique**, générant :
- Le code Python (via template)
- La documentation utilisateur
- Le prompt system pour le LLM
- Les tests de validation

---

## Vers le "Prompt-Compatible Engineering"

```
Code = Logique d'exécution
     + Contrat sémantique (schema)
     + Guide d'intention (docstring)
     + Garde-fous contextuels (examples, anti-patterns)
```

C'est du **Design by Contract**, mais où le "client" qui lit le contrat est un modèle statistique, pas un compilateur.

---

## Gate de qualité : `tool_readiness_score`

Inverser la perspective : au lieu de seulement *vérifier la sortie du LLM*, valider en amont la **consommabilité des outils par le LLM**.

Critères d'évaluation :
- Clarté sémantique de la docstring (exemples, anti-patterns, préconditions)
- Exhaustivité du JSON Schema (types, enums, descriptions de champs)
- Alignement avec le vocabulaire domaine (TOGAF, ArchiMate)
- Présence de sections USE WHEN / NEVER USE

**Règle** : un outil avec un score < 0.7 n'est pas exposé à l'agent — forçant une refactorisation *avant* l'intégration.

Voir `tool_readiness_score.py` pour l'implémentation.
