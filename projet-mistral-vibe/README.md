# Harnais Mistral Vibe

Harnais générique pour [Mistral Vibe](https://docs.mistral.ai/vibe/code) 2.25.8 : règles de projet (`AGENTS.md`), configuration, agents, prompts et hooks (`.vibe/`). Il est destiné à être copié à la racine d'un dépôt de tests Robot Framework ; tous ses chemins sont relatifs.

## Contenu

| Élément | Rôle |
| --- | --- |
| `AGENTS.md` | Règles du projet, ajoutées au prompt système de chaque session |
| `.vibe/config.toml` | Agent de démarrage `plan`, modèle, modèle de compaction, permissions |
| `.vibe/agents/orchestrator.toml` | Agent principal : planifie, fait valider, exécute, fait relire |
| `.vibe/agents/reviewer.toml` | Sous-agent de relecture, lecture seule |
| `.vibe/prompts/*.md` | Prompts système (copie du prompt par défaut de Vibe 2.25.8 + ajouts) |
| `.vibe/hooks.toml`, `.vibe/hooks/audit_bash.py` | Trace chaque commande shell dans `.vibe/logs/bash.log` |
| `.vibe/skills/` | Vide à ce stade |
| `tests_harnais/` | Tests pytest des hooks |

Modèles : toutes les sessions et tous les sous-agents tournent en Mistral Medium 3.5 (alias intégré `mistral-medium-3.5`, réflexion `high`). En 2.25.8, un sous-agent ignore son propre `active_model` et utilise le modèle de la session. La compaction utilise Mistral Small 4 sans réflexion.

## Prérequis (WSL / Linux)

```bash
uv tool install mistral-vibe==2.25.8
vibe --setup          # connexion navigateur ou clé API
vibe --version        # doit afficher 2.25.8
python3 --version     # 3.11 ou plus, utilisé par les hooks
```

## Importer le harnais dans un dépôt

1. Copier `AGENTS.md` et `.vibe/` à la racine du dépôt ; ajouter les entrées de `.gitignore` au `.gitignore` du dépôt.
2. Compléter la section « Projet » d'`AGENTS.md`.
3. Lancer `vibe` à la racine et accepter la confiance du dossier : sans elle, la configuration projet est ignorée.
4. Après toute modification du harnais en cours de session : `/reload`.

## Flux de travail

Lancer `vibe` depuis la racine du dépôt : la commande du hook est relative au répertoire courant de la session.

1. `vibe` démarre sur l'agent `plan` : il lit le code et rédige un plan, sans rien écrire.
2. Le plan est soumis par `exit_plan_mode`, qui propose quatre choix : « Yes, clear context and auto approve edits », « Yes, and auto approve edits » (ces deux-là basculent vers `accept-edits`, qui écrit sans orchestrateur), « Yes, and request approval for edits » (bascule vers `ask`), « No » (reste en plan pour corriger).
3. Pour exécuter avec délégation et relecture : répondre « No » en demandant d'attendre, puis `Shift+Tab` jusqu'à `orchestrator` (ou relancer `vibe --agent orchestrator`) et dire « exécute le plan approuvé ». L'orchestrateur remplit `todo`, demande validation par `ask_user_question`, exécute étape par étape et fait relire par `reviewer` avant de conclure.

En mode non interactif (`-p`), passer toujours `--agent` et `--trust` ; `ask_user_question` y est désactivé.

## Tests du hook

```bash
uv tool install pytest            # ou : python3 -m pip install pytest
python3 -m pytest tests_harnais -q
```

## Recette (à exécuter sous WSL)

Dans un dépôt git de test contenant le harnais. Noter le résultat de chaque point : il alimente `memoire/VIBE_FAITS_VERIFIES.md`.

- [ ] 1. `vibe` affiche le dialogue de confiance listant `AGENTS.md` et `.vibe/` ; accepter.
- [ ] 2. « Quelles sont les règles de ce projet ? » : la réponse cite `AGENTS.md`.
- [ ] 3. La session démarre sur l'agent `plan`. Demander une petite modification : un plan est proposé avant toute écriture ; une commande `bash` hors liste déclenche une demande ; `exit_plan_mode` propose les quatre choix ; `Shift+Tab` atteint bien `orchestrator`, qui voit le plan (ou demande l'accès à `~/.vibe/plans/`).
- [ ] 4. `vibe --agent orchestrator` sur une petite tâche : `todo` rempli, `ask_user_question` avant toute écriture, appel `task(agent="reviewer")` sans demande d'approbation, retour au format Bloquant / À corriger / Suggestion.
- [ ] 5. `/thinking` : relever les niveaux proposés et le niveau actif (attendu : `high`).
- [ ] 6. `/log` : relever le modèle effectif de l'orchestrateur et de `reviewer` (attendu : celui de la session), l'éventuel avertissement « runs on the session's model instead » et les outils réellement disponibles pour `reviewer` (`grep` compris ?) ; comparer le début du prompt système de la session avec `.vibe/prompts/orchestrator.md`.
- [ ] 7. « Modifie `.vibe/config.toml` » est refusé sans question ; « Lance `git push --force` » et « Lance `vim` » sont refusés sans question ; « Lance `git status` » et « Lance `ls` » s'exécutent sans question ; « Écris dans `.vibe/x` avec bash » déclenche une demande (refuser).
- [ ] 8. `.vibe/logs/bash.log` contient une ligne par commande, avec le `tool_name` exact (`bash` attendu, sinon ajuster `match` dans `hooks.toml`) ; `git status` ne l'affiche pas.
- [ ] 9. Lancer `vibe` depuis un sous-dossier du dépôt, exécuter une commande : échec probable du hook (`.vibe/hooks/audit_bash.py` introuvable depuis ce répertoire) ; noter le message affiché.
- [ ] 10. `/compact` fonctionne (modèle de compaction Small 4).
- [ ] 11. `python3 --version` (3.11) puis `python3 -m pytest tests_harnais -q` depuis la racine du harnais : tous verts (ils n'ont été joués que sous Python 3.13 / Windows).
