# Patterns GoF réincarnés pour l'ère des agents

## Cartographie GoF → Harness

| Pattern GoF | Manifestation dans le "Harness" | Rôle dans l'architecture agent |
|-------------|--------------------------------|--------------------------------|
| **Strategy** | `TOOL_HANDLERS` dispatch map | Permet au modèle de choisir dynamiquement quelle action exécuter parmi un registre d'outils interchangeables |
| **Chain of Responsibility** | Pipeline de permissions (`s03`) | Chaque règle de permission peut accepter, rejeter ou passer la main à la suivante |
| **Observer** | Hooks système (`s04`: `PreToolUse`, `PostToolUse`) | Permet d'injecter de la logique transversale (logging, audit, metrics) sans modifier la boucle principale |
| **Template Method** | `agent_loop()` immuable | Définit le squelette de l'exécution ; les variations viennent des outils et hooks injectés |
| **Facade** | Interface unifiée des outils | Masque la complexité des APIs externes (shell, navigateur, DB) derrière un contrat simple pour le LLM |
| **Proxy** | Sandbox / Permission wrapper | Contrôle l'accès aux ressources sensibles, ajoute une couche de sécurité avant l'exécution réelle |
| **Memento** | Système de mémoire (`s09`) + Context compaction (`s08`) | Capture et restaure l'état de la conversation ; compresse l'historique sans perdre l'essentiel |
| **Command** | `TodoWrite` + Task graph (`s05`, `s12`) | Encapsule une intention d'action dans un objet sérialisable, exécutable et persistable |
| **Mediator** | `MessageBus` des équipes d'agents (`s15`) | Centralise la communication entre sous-agents pour éviter le couplage direct |
| **Factory Method** | Skill loading dynamique (`s07`) | Instancie des "compétences" à la demande selon le contexte, sans les charger toutes au démarrage |

---

## Ce qui change par rapport aux GoF classiques

| Aspect | GoF traditionnel | Harness pour agent |
|--------|-----------------|-------------------|
| **Décideur** | Code déterministe | Modèle probabiliste (LLM) |
| **Interface** | Types statiques, signatures | Descriptions en langage naturel (JSON Schema + docstring) |
| **Erreur** | Exception → try/catch | Feedback dans le contexte → retry ou replanning |
| **État** | Objets en mémoire | Messages sérialisés + stockage externe |
| **Extension** | Héritage / Composition | Registration dynamique d'outils + hooks |

---

## Principe fondateur

> *"The model decides. The harness executes."*

C'est une reformulation moderne du **Principe d'inversion des dépendances** (SOLID-D) : les modules de haut niveau (le raisonnement du LLM) ne dépendent pas des modules de bas niveau (l'exécution des outils) — les deux dépendent d'abstractions (les descriptions d'outils en langage naturel).

```
LLM (haut niveau)
      ↕  [abstraction : tool descriptions / JSON Schema]
Harness (bas niveau)
```

Tu ne codes pas l'intelligence, tu codes **les interfaces par lesquelles l'intelligence agit sur le monde**.
