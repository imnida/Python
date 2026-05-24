# Analyse du dépôt : `learn-claude-code`

## Objectif principal

Ce dépôt GitHub (**62.3k ⭐ / 10.2k 🍴**) est un **tutoriel d'ingénierie de "harness" pour agents IA**, basé sur l'architecture de Claude Code.

> **Philosophie clé** : *"L'agency vient du modèle. Le harness donne à l'agency un endroit où atterrir."*

Autrement dit : vous ne codez pas l'intelligence, vous construisez **l'environnement opérationnel** dans lequel un modèle (LLM) peut percevoir, raisonner et agir.

---

## Architecture du "Harness"

```
Harness = Outils + Connaissances + Observation + Interfaces d'action + Permissions
```

| Composant | Rôle |
|-----------|------|
| **Tools** | File I/O, shell, réseau, base de données, navigateur |
| **Knowledge** | Docs produit, specs API, guides de style |
| **Observation** | Git diff, logs d'erreur, état du navigateur |
| **Action** | Commandes CLI, appels API, interactions UI |
| **Permissions** | Sandbox, workflows d'approbation, limites de confiance |

---

## Structure pédagogique : 20 leçons progressives

Chaque chapitre ajoute **un seul mécanisme** au-dessus d'une boucle agent immuable :

```python
def agent_loop(messages):
    while True:
        response = client.messages.create(model=MODEL, messages=messages, tools=TOOLS)
        if response.stop_reason != "tool_use":
            return  # Le modèle a terminé
        # Exécuter les outils demandés et boucler
```

### Parcours d'apprentissage

| Phase | Chapitres | Objectif |
|-------|-----------|----------|
| **Fondations** | s01-s04 | Boucle agent, outils, permissions, hooks |
| **Travail complexe** | s05-s08 | Planification, sous-agents, compaction de contexte |
| **Mémoire & résilience** | s09-s11 | Système de mémoire, prompts dynamiques, recovery |
| **Tâches longues** | s12-s14 | Task graph, background jobs, scheduler cron |
| **Multi-agents** | s15-s18 | Équipes, protocoles, autonomie, isolation worktree |
| **Extension** | s19-s20 | Plugins MCP, intégration complète |

---

## Démarrage rapide

```bash
git clone https://github.com/shareAI-lab/learn-claude-code
cd learn-claude-code
pip install -r requirements.txt
cp .env.example .env  # Configurer ANTHROPIC_API_KEY

# Commencer par la base
python s01_agent_loop/code.py

# Ou tester un chapitre avancé
python s08_context_compact/code.py
python s20_comprehensive/code.py
```

---

## Points clés

1. **Modulariser la boucle d'agent** : séparer clairement la logique de décision (LLM) des mécanismes d'exécution (harness)
2. **Implémenter un système de permissions** : utile pour la souveraineté numérique et la propagation de confiance
3. **Gestion du contexte** : les stratégies de compaction (s08) sont pertinentes pour les LLM locaux à fenêtre limitée
4. **Task graph persistant** (s12) : aligné avec le cycle de vie des éléments d'architecture
5. **Hooks extensibles** (s04) : pour intégrer un framework d'analyse critique modulaire

> **Note** : Le dépôt cible l'API Anthropic, mais les patterns sont transférables à `llama-cpp-python` ou tout autre backend LLM local.

---

## Ressources complémentaires

- **Dépôt source** : [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code)
- **Kode Agent CLI** : `npm i -g @shareai-lab/kode` — CLI open-source inspirée
- **Kode Agent SDK** : pour embarquer ces capacités dans des applications
- **claw0** : tutoriel sœur pour des assistants "always-on" (heartbeat + cron + canaux IM)
