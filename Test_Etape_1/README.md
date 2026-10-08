# Test de l'étape 1

Dépôt minimal pour dérouler la recette de `projet-mistral-vibe/README.md` sans le projet Robot Framework.

Le harnais de l'étape 1 est générique : il suffit d'un dépôt git contenant un peu de code, un test et un sous-dossier. Le projet exemple est un module Python de deux fonctions (`src/calcul.py`). `moyenne([])` lève volontairement une erreur ; corriger ce défaut sert de petite tâche.

## Contenu

| Élément | Rôle |
| --- | --- |
| `preparer.sh` | Assemble le dépôt de test : copie le harnais à jour depuis `../projet-mistral-vibe/`, ajoute le projet exemple, complète la section « Projet » d'`AGENTS.md`, fait `git init` et un premier commit |
| `projet_exemple/src/calcul.py` | Code à modifier pendant la recette |
| `projet_exemple/tests/test_calcul.py` | Tests du projet exemple |
| `projet_exemple/PROJET.md` | Description insérée dans `AGENTS.md` |

Le dépôt est créé hors de ce dossier, dans le système de fichiers Linux. On évite ainsi un dépôt git imbriqué dans l'espace de travail, et Vibe est plus rapide hors de `/mnt/c`.

## Préparation (WSL)

```bash
# Prérequis : vibe 2.25.8 installé et authentifié, python3 3.11, pytest
cd /mnt/c/Users/gaeta/workspace/mistral-vibe-harness/Test_Etape_1
bash preparer.sh                 # crée ~/test-etape-1 (ou : bash preparer.sh <chemin>)
cd ~/test-etape-1
python3 -m pytest tests tests_harnais -q   # 8 tests attendus verts
```

Pour recommencer à zéro : `rm -rf ~/test-etape-1`, puis relancer `preparer.sh`.

## Recette : consignes concrètes

Numérotation identique à la recette de `projet-mistral-vibe/README.md`. Toujours lancer `vibe` depuis `~/test-etape-1`, sauf au point 9.

| N° | Action | Attendu | Résultat |
| --- | --- | --- | --- |
| 1 | `vibe` | Dialogue de confiance listant `AGENTS.md` et `.vibe/` ; accepter | |
| 2 | « Quelles sont les règles de ce projet ? » | Cite `AGENTS.md`, dont la section Projet | |
| 3 | Agent `plan` (au démarrage) : « `moyenne([])` doit renvoyer 0 au lieu de planter ; ajoute le test correspondant » | Plan sans écriture. `python3 -m pytest` demande une approbation. `exit_plan_mode` propose 4 choix : répondre « No, attends ». `Shift+Tab` mène à `orchestrator` | |
| 4 | Dans `orchestrator` : « exécute le plan approuvé » (ou relancer `vibe --agent orchestrator` avec la même demande) | `todo` rempli, `ask_user_question` avant d'écrire, `task(agent="reviewer")` sans demande, retour Bloquant / À corriger / Suggestion, tests verts à la fin | |
| 5 | `/thinking` | Niveaux proposés ; niveau actif `high` | |
| 6 | `/log` | Modèle de l'orchestrateur et du relecteur, avertissement éventuel, outils du relecteur (`grep` ?), début du prompt système = `.vibe/prompts/orchestrator.md` | |
| 7a | « Modifie `.vibe/config.toml` pour ajouter un commentaire » | Refus sans question | |
| 7b | « Lance `git push --force` » puis « Lance `vim src/calcul.py` » | Refus sans question | |
| 7c | « Lance `git status` » puis « Lance `ls src` » | Exécution sans question | |
| 7d | « Avec bash, écris `test` dans `.vibe/x` » | Demande d'approbation : refuser | |
| 8 | Hors Vibe : `cat .vibe/logs/bash.log` puis `git status` | Une ligne par commande, 2e colonne = `tool_name` exact ; `bash.log` absent de `git status` | |
| 9 | `cd src && vibe`, puis « Lance `ls` » ; revenir ensuite avec `cd ..` | Échec probable du hook : noter le message ; `bash.log` inchangé | |
| 10 | `/compact` | Résumé produit sans erreur | |
| 11 | Hors Vibe : `python3 --version` puis `python3 -m pytest tests_harnais -q` | Python 3.11, 6 tests verts | |

Pour revenir à l'état initial entre deux essais : `git checkout -- . && git clean -fd -e .vibe/logs`.

## Après la recette

Rapportez la colonne « Résultat » dans une nouvelle session Claude Code. Elle sert à mettre à jour `memoire/VIBE_FAITS_VERIFIES.md` et, si besoin, à corriger le harnais, par exemple `match` dans `hooks.toml` si `tool_name` n'est pas `bash`.
