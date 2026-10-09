# Décisions

Format : identifiant, date, décision, justification, source. Statut « Proposée » = à confirmer à l'étape indiquée.

## D-01 — Organisation de l'outillage (2026-10-07, validée)
`claude-0/` contient `CLAUDE.md`, `.claude/`, `memoire/`, `reference/` ; il est déplacé à la racine d'un espace de travail avant l'étape 1. `projet-mistral-vibe/` est créé par `/etape-1` à cette racine.
Justification : Claude Code ne lit `.claude/` et `CLAUDE.md` qu'à la racine de la session.

## D-02 — Une session par étape, état dans `memoire/` (2026-10-07, validée)
Chaque étape démarre dans un contexte neuf ; `CLAUDE.md` importe `memoire/ETAT.md` ; chaque étape met à jour les trois fichiers de mémoire en clôture.

## D-03 — Mode plan par défaut (2026-10-07, validée)
Claude Code : `permissions.defaultMode = "plan"`. Vibe : `default_agent = "plan"` et validation par `ask_user_question` dans le prompt de l'orchestrateur.
Justification : exigence « toute nouvelle demande passe par un plan à valider ». Le modèle Vibe ne peut pas entrer seul dans l'agent `plan` (guide, 5.3) : l'orchestrateur impose donc aussi la validation.

## D-04 — Quatre agents Claude Code, orchestration dans la session principale (2026-10-07, validée)
`vibe-harness-expert`, `python-expert`, `robot-framework-expert`, `harness-verifier` (lecture seule). Les agents ne délèguent pas entre eux.

## D-05 — Critère de validation d'une refacto (2026-10-07, validée)
`robot --test "<nom>"` exécuté et vert. Exécution de référence avant refacto.

## D-06 — Environnement d'exécution (2026-10-07, validée)
Vibe et `robot` sous WSL/Linux ; hooks en `python3`, stdlib Python 3.11 ; chemins relatifs (harnais importé plus tard dans le dépôt de tests RF).

## D-07 — Modèles Mistral par agent Vibe (2026-10-07, proposée, révisée par D-07b ; GLM réintroduit par D-12)

Modèles actifs au 2026-10-07 :

| Modèle | ID | Contexte | Profil | $/M entrée / sortie |
| --- | --- | --- | --- | --- |
| Mistral Medium 3.5 | `mistral-medium-latest` | 256k | Recommandé par la doc Vibe, agentique et code | 1,5 / 7,5 |
| Mistral Small 4 | `mistral-small-latest` | 256k | Instruct + raisonnement + code, rapide | 0,15 / 0,6 |
| Mistral Large 3 | `mistral-large-latest` | n.c. | Tâches complexes, non orienté agent | 0,5 / 1,5 |
| Codestral | `codestral-latest` | n.c. | Complétion de code (FIM), non agentique | 0,3 / 0,9 |

Écartés : Devstral 2, Devstral Small 2, Magistral (retirés, remplacés par Medium 3.5 / Small 4) ; Large 4 (absent de la liste Vibe) ; GLM (tiers).

| Agent Vibe | Modèle | `thinking` | Raison |
| --- | --- | --- | --- |
| `plan` (intégré), `orchestrator` | Medium 3.5 | haut | Analyse, plan, décisions d'arrêt |
| `rf-refactorer` | Medium 3.5 | moyen | Qualité du code ; plan validé en amont |
| `reviewer`, `rf-reviewer` | Medium 3.5 | moyen | Un relecteur plus faible que l'auteur rate des erreurs |
| `historien` | Small 4 | off | Mise en forme d'un résumé fourni, coût divisé par 10 |
| `compaction_model` | Small 4 | off | Résumés de contexte |

Mise en œuvre : presets `[[models]]` (alias `medium-think`, `medium`, `small`) dans `.vibe/config.toml`, référencés par `active_model` dans chaque agent.
Conséquence : une skill tourne avec le modèle de l'agent courant ; l'historisation passe donc par un sous-agent `historien`.
Repli : si un sous-agent n'applique pas son propre `active_model`, tout en Medium 3.5 et la skill d'historisation écrit directement.
Sources : https://docs.mistral.ai/getting-started/models/models_overview/ · https://docs.mistral.ai/inference/pricing · https://docs.mistral.ai/vibe/code/cli/configuration-reference · https://docs.mistral.ai/vibe/code/cli/agents

## D-07b — Grille modèle / agent révisée (2026-10-07, validée, étape 1 ; `plan` et `orchestrator` remplacés par D-12)
| Agent | Modèle | `thinking` | Mécanisme |
| --- | --- | --- | --- |
| `plan`, session par défaut | Medium 3.5 (alias intégré `mistral-medium-3.5` = `mistral-vibe-cli-latest`) | high | `active_model` global |
| `orchestrator` | Medium 3.5 | high | `active_model` dans le fichier d'agent |
| Tout sous-agent (`reviewer`, futurs `rf-*`, `historien`) | Modèle de la session | high | Aucune clé : ignorée en 2.25.8 |
| compaction | Small 4 (`mistral-small-latest`) | off | Table `[compaction_model]`, provider `mistral` |

Justification :
- un sous-agent ignore `active_model` sous le Unified Harness (`vibe/app_server/_agent_types.py`) ;
- `active_model` doit être un alias existant ;
- vers l'API Mistral, `medium`, `high` et `max` donnent tous `reasoning_effort = "high"` (`vibe/core/llm/backend/mistral.py`) : pas de niveau intermédiaire réel ;
- aucun `[[models]]` ajouté : l'alias intégré suffit.

Conséquence : repli D-07 appliqué. Pour l'étape 3, la skill d'historisation écrit directement, sans sous-agent `historien` sur Small 4.
Sources : https://raw.githubusercontent.com/mistralai/mistral-vibe/v2.25.8/vibe/core/config/vibe_schema.py · …/v2.25.8/vibe/config_values.py · …/v2.25.8/vibe/core/llm/backend/mistral.py · …/v2.25.8/vibe/app_server/_agent_types.py · https://docs.mistral.ai/models/mistral-medium-3-5-26-04 · https://docs.mistral.ai/models/mistral-small-4-0-26-03

## D-08 — Permissions du harnais générique (2026-10-07, validée, étape 1 ; révisée par D-10)
- `[tools.bash]` : pas d'`allowlist` (les défauts couvrent `git status/diff/log`, `ls`, `cat`…). La `denylist` reprend les 14 défauts POSIX de `bash.py`, plus `git push --force`, `git push -f`, `rm -rf` et `rm -fr`.
- `[tools.edit]` et `[tools.write_file]` : `denylist = ["*/.vibe/*"]`.
- Pas de `sensitive_patterns`.
- `reviewer` : lecture seule par `enabled_tools = ["read_file", "grep", "bash"]`, sans `[tools.*]`.
- `orchestrator` : `[tools.task] allowlist = ["explore", "reviewer"]`.

Justification :
- définir une liste d'outil remplace la liste par défaut (fusion superficielle, `vibe/core/tools/manager.py`) : il faut donc reprendre les défauts, et un `sensitive_patterns` remplacerait les motifs `.env*` ;
- un sous-agent perd les `allowlist` / `denylist` de ses `[tools.*]` (`vibe/app_server/_runtime.py`).

Limite : la comparaison se fait par préfixe, la protection est donc partielle (`git push origin x --force` passe).

## D-09 — Structure et prompts (2026-10-07, validée, étape 1 ; flux révisé par D-10, copie remplacée par une traduction en D-11)
- Prompts = copie exacte (vérifiée par `diff`) de `vibe/core/prompts/cli.md` au tag v2.25.8, suivie d'une section « Ajouts du harnais ». Une copie via WebFetch n'est pas fiable (texte reformulé) : toujours copier depuis le fichier brut avec `curl`.
- Règles transverses dans `AGENTS.md`, méthode d'orchestration et format de relecture dans les prompts, sans doublon.
- Hook d'audit : chemin du log calculé depuis `__file__`, stdin lu en octets UTF-8, toujours `exit 0`. La commande `python3 .vibe/hooks/audit_bash.py` suppose que `vibe` est lancé à la racine.
- Flux : agent `plan`, puis `exit_plan_mode`, répondre « No », puis `Shift+Tab` vers `orchestrator`. Les choix « Yes … auto approve » basculent vers `accept-edits` sans orchestrateur.

## D-10 — Référence Vibe 2.26.0, Unified Harness (2026-10-08, validée)
Décision : la version de référence passe de 2.25.8 à 2.26.0, version installée sous WSL. Le moteur visé est le Unified Harness ; `--legacy-harness` reste un repli documenté, non retenu.

Conséquences sur le harnais :
- `[tools.edit]` / `[tools.write_file]` : la denylist `*/.vibe/*` est remplacée par les sous-dossiers et fichiers du harnais (`*/.vibe/agents/*`, `prompts`, `hooks`, `skills`, `logs`, `config.toml`, `hooks.toml`). L'ancien motif couvrait `~/.vibe/plans/` et empêchait l'agent `plan` d'écrire son plan.
- `[tools.bash]` inchangé : clés historiques appliquées à `file_system.bash` ; défauts POSIX identiques à 2.25.8.
- `[tools.task]` supprimé (sans effet). La relecture passe par l'outil natif `spawn` (`agentType = "reviewer"`) puis `wait`.
- `reviewer` : `enabled_tools = ["read_file", "bash"]` (`grep` n'est pas un outil natif) ; recherche via `grep`/`find` en bash.
- Flux (remplace celui de D-09) : agent `plan` → plan en texte → `Shift+Tab` vers `orchestrator` → `ask_user_question` → exécution → `spawn`/`wait` de `reviewer`. `exit_plan_mode` n'est pas proposé au modèle.
- `default_agent = "plan"` conservé (lecture seule matérielle de l'édition).
- `AGENTS.md` : un refus est définitif (pas de contournement par le shell) ; un outil de vérification manquant est signalé, jamais remplacé.
- `python3 -m pytest` reste soumis à approbation (pas d'allowlist bash, choix utilisateur : simplicité).
- Prompts : `cli.md` v2.26.0 identique octet par octet à v2.25.8 (diff du 2026-10-08) : copie conservée (remplacée par une traduction en D-11).

Justification : recette du 2026-10-08 jouée sur 2.26.0 ; trois écarts (`exit_plan_mode`, `task`, `grep`) viennent du Unified Harness, déjà par défaut en 2.25.8 : les fiches 2.25.8 correspondantes ne valaient que pour l'ancien moteur.
Sources : https://raw.githubusercontent.com/mistralai/mistral-vibe/v2.26.0/CHANGELOG.md · …/v2.26.0/vibe/app_server/_unified_permissions.py · …/v2.26.0/vibe/app_server/_runtime.py · …/v2.26.0/vibe/app_server/_agent_types.py · …/v2.26.0/vibe/core/agents/models.py · …/v2.26.0/vibe/core/tools/utils.py · …/v2.26.0/harness/core/src/core/features/subagents/tools.rs

## D-11 — Prompts en français et correctifs de recette (2026-10-09, validée)
- La partie de base des prompts `orchestrator.md` et `reviewer.md` devient une traduction française fidèle de `cli.md` v2.26.0 (au lieu de la copie exacte de D-09). Coût : à reprendre à la main si Vibe modifie `cli.md`.
- L'agent `plan` garde le prompt intégré de Vibe (anglais) : pas de `.vibe/prompts/cli.md` projet (simplicité ; une expérimentation GrowthBook peut lui imposer une variante `cli_2026-*`).
- Correctifs issus de la recette du 2026-10-09 :
  - orchestrateur : une seule relecture par tâche ; chaque point jugé ; « À corriger » / « Suggestion » appliqués seulement après `ask_user_question` ; au plus une nouvelle relecture, après correction d'un Bloquant ;
  - relecteur : constat vérifié dans le fichier (ligne exacte), rien de contraire aux conventions du langage ;
  - `AGENTS.md` : un fichier ne se modifie que par l'outil d'édition ou d'écriture, jamais par le shell ; si l'outil échoue, s'arrêter et signaler.
- Pas de changement de permissions : les modifications par `sed -i` étaient soumises à approbation (7d confirmé).
Justification : recette du 2026-10-09 (`VIBE_FAITS_VERIFIES.md`, section « Recette 2026-10-09 ») ; demande utilisateur (instructions en français).

## D-12 — Variante GLM 5.3 pour `plan` et `orchestrator` (2026-10-09, validée, recette à faire)
| Agent | Modèle | `thinking` | Mécanisme |
| --- | --- | --- | --- |
| `plan` (démarrage) | `glm-5-3` (`zai-glm-5-3`, provider `mistral`) | `max` (l'API reçoit `high`) | `active_model` de `config.toml` + `[[models]]` projet |
| `orchestrator` | `glm-5-3` | `max` | `active_model` d'`orchestrator.toml` |
| `reviewer` | hérité : GLM | `max` | modèle actif de l'agent parent au `spawn` |
| Compaction | Small 4, inchangé | `off` | `[compaction_model]`, même provider |
| Repli | `mistral-medium-3.5` (alias intégré) | `high` | remettre `active_model` dans les deux fichiers, session neuve |

- Pourquoi GLM revient : D-07 l'écartait comme « tiers ». Ce motif tombe, car Mistral l'héberge sur sa propre API (même clé `MISTRAL_API_KEY`, même backend, aucun `[[providers]]`). Demande de l'utilisateur.
- `thinking = "max"` est gardé à la demande de l'utilisateur. En 2.26.0, `max` envoie `reasoning_effort = "high"` : le `max` de GLM n'est pas atteignable sans modifier Vibe. Commentaire dans la config.
- Pas de `thinking_levels` (choix de l'utilisateur : minimum de clés). Risque documenté dans le README : `/thinking low` envoie `none`, que GLM refuse.
- Prix renseignés (1,4 / 4,4 / 0,14 USD par M tokens) pour mesurer le coût. Pas de `max_context_length` : il relèverait le seuil de compaction vers 1M.
- `reviewer` en effort maximal sur chaque relecture : coût et durée acceptés par l'utilisateur. Inévitable, car le sous-agent hérite du modèle du parent.
- Repli : ne pas passer par `/model`, qui écrit dans `~/.vibe/config.toml` et que le profil d'`orchestrator` surclasse.
Sources : https://docs.mistral.ai/models/zai-glm-5-3 · https://docs.mistral.ai/capabilities/reasoning · https://raw.githubusercontent.com/mistralai/mistral-vibe/v2.26.0/vibe/core/config/models.py · …/v2.26.0/vibe/core/config/vibe_schema.py · …/v2.26.0/harness/runtimes/python/python/mistralai_vibe_local_harness/vibe/adapters/mistral.py · …/v2.26.0/vibe/app_server/_runtime.py · …/v2.26.0/vibe/app_server/_config_write.py · …/v2.26.0/vibe/core/config/default_orchestrator.py
