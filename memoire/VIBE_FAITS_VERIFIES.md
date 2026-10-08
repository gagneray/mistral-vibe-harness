# Faits Mistral Vibe vérifiés (cible 2.25.8)

Statuts : **Confirmé** (doc ou code 2.25.8) · **Précisé** (doc et code divergent, choix noté) · **À vérifier** (non documenté, test de recette prévu) · **Infirmé**.

Historique de validation :
- Le guide `reference/guide-harnais-vibe.md` a été validé contre la 2.25.2 le 2026-10-05.
- Les écarts 2.25.3 → 2.25.8 viennent du CHANGELOG lu le 2026-10-07.
- L'étape 1 (2026-10-07) a vérifié le code au tag **`v2.25.8`** (le nom `2.25.8` sans « v » renvoie 404).

Abréviations :
- **R** = `https://raw.githubusercontent.com/mistralai/mistral-vibe/v2.25.8/`
- **D** = `https://docs.mistral.ai/vibe/code/cli/`
- **CL** = R + `CHANGELOG.md`

Le **Unified Harness** est le nouveau moteur d'exécution, actif par défaut depuis 2.25.5 (`--legacy-harness` pour revenir à l'ancien).

## Configuration (`config.toml`)

| Fait | Statut | Détail | Source |
| --- | --- | --- | --- |
| `default_agent` | Précisé | Défaut `accept-edits`. Agents intégrés : `ask`, `plan`, `accept-edits`, `smart-approve`, `auto-approve`. Code : s'applique aussi en `-p` ; doc : ignoré en `-p`. Toujours passer `--agent`. | R`vibe/core/config/vibe_schema.py`, D`configuration-reference` |
| `active_model` | Précisé | Doit être un alias de `models` (sinon avertissement et retour au défaut). Alias intégrés : `mistral-medium-3.5` (name `mistral-vibe-cli-latest`, provider `mistral`, thinking `high`) et `local` (llamacpp). | R`vibe/core/config/vibe_schema.py` |
| `[[models]]` | Confirmé | `name` et `provider` requis ; `alias` = `name` par défaut ; `thinking` (défaut `off`), `temperature`, prix, `auto_compact_threshold`. Fusion par alias avec les défauts. Pas de `thinking_levels` ni de `max_context_length` (2.26.0+). | R`vibe/core/config/models.py` |
| Valeurs de `thinking` | Confirmé | `off`, `low`, `medium`, `high`, `max`. Vers l'API Mistral : `low` → `none` ; `medium`, `high` et `max` → `high`. | R`vibe/config_values.py`, R`vibe/core/llm/backend/mistral.py` |
| `compaction_model` | Précisé | Table `ModelConfig`, pas une chaîne. Même provider que le modèle actif, sinon erreur. | R`vibe/core/config/vibe_schema.py` |
| Provider intégré | Confirmé | `mistral` (clé `MISTRAL_API_KEY`) ; aussi `llamacpp`. | R`vibe/core/config/vibe_schema.py` |
| `enabled_skills` | Confirmé | Liste blanche (nom, glob, `re:`) ; masque aussi les skills fournies par Vibe. | R`vibe/core/skills/manager.py` |
| `[tools.<outil>]` | Précisé | `permission` vaut `always`, `ask` ou `never` (`never` absent de la doc). Clés `allowlist`, `denylist`, `sensitive_patterns` ; une clé inconnue est acceptée sans erreur. La doc écrit `allow`/`deny`. | R`vibe/core/tools/base.py` |
| Fusion des listes d'outil | Confirmé (nouveau) | Fusion superficielle : définir une liste **remplace** la liste par défaut. Défauts bash POSIX : allowlist `cd`, `echo`, `git diff`, `git log`, `git status`, `tree`, `whoami` + lecture seule POSIX ; denylist `gdb`, `pdb`, `passwd`, `nano`, `vim`, `vi`, `emacs`, `bash -i`, `sh -i`, `zsh -i`, `fish -i`, `dash -i`, `screen`, `tmux`. `edit` et `write_file` n'ont pas de liste par défaut, mais ont des `sensitive_patterns` par défaut (`.env*`). | R`vibe/core/tools/manager.py`, R`vibe/core/tools/builtins/bash.py`, R`…/edit.py`, R`…/write_file.py` |
| Listes de chemins (`edit`, `write_file`, `read_file`) | Confirmé (agent principal) | `fnmatch` sur le chemin absolu résolu ; la denylist l'emporte ; motifs `*/dossier/*`. Une allowlist qui correspond court-circuite la demande sur `.env`. | R`vibe/core/tools/utils.py` |
| Comparaison des préfixes bash | Confirmé | Sous-commande égale au préfixe ou commençant par « préfixe + espace » : `git push origin x --force` passe `git push --force`. | R`vibe/core/tools/builtins/bash.py` |
| Noms des outils | Confirmé | `edit`, `write_file`, `read_file`, `grep`, `bash`, `task`, `todo`, `skill`, `ask_user_question`, `exit_plan_mode`, `web_fetch`, `web_search`. | arborescence `vibe/core/tools/builtins` |
| Préséance admin > CLI > env > projet > utilisateur | Confirmé | — | Doc Configuration |
| Confiance du dossier, `--trust` | Confirmé | Sans confiance, la configuration projet est ignorée. | Doc Safety |

## Agents et sous-agents

| Fait | Statut | Détail | Source |
| --- | --- | --- | --- |
| Clés d'un fichier d'agent | Confirmé | Lues directement : `display_name`, `description`, `safety` (`safe`, `neutral`, `destructive`, `smart`, `yolo`), `agent_type` (défaut `agent`). Le reste forme une surcharge de config. Nom de l'agent = nom du fichier. | R`vibe/core/agents/models.py` |
| `active_model` d'un agent principal | Confirmé | Appliqué au changement de profil. | R`vibe/core/agents/manager.py` |
| `active_model` d'un sous-agent | **Infirmé** | Ignoré sous le Unified Harness ; avertissement « runs on the session's model instead ». | R`vibe/app_server/_agent_types.py` |
| `[tools.*]` d'un sous-agent | Précisé (nouveau) | Seul le niveau allow / ask / deny est gardé : les listes sont perdues et `always` + liste devient `ask`. Restreindre par `enabled_tools`. | R`vibe/app_server/_runtime.py` |
| `description` d'un sous-agent | Confirmé | Obligatoire, sinon l'agent est rejeté ; une clé `instructions` l'emporte sur `system_prompt_id`. | R`vibe/app_server/_agent_types.py` |
| Emplacements | Confirmé | Agents : `.vibe/agents` du projet de confiance, puis `~/.vibe/agents`. Prompts : `.vibe/prompts`, puis `~/.vibe/prompts`, puis intégrés. | R`vibe/core/agents/registry.py`, R`vibe/core/prompts/__init__.py` |
| `system_prompt_id` | Confirmé | Remplace tout le prompt système ; défaut `cli` (`vibe/core/prompts/cli.md`, 136 lignes, `$current_date`) ; respecté sous le Unified Harness (2.25.8). | R`vibe/core/prompts/cli.md`, CL 2.25.8 |
| Prompt réellement utilisé par le Unified Harness | À vérifier | Variantes `cli_2026-07_v2.md`, `cli_2026-08_v3.md` présentes ; comparer avec `/log`. | Recette 1, point 6 |
| `task` | Confirmé | Arguments `task` et `agent` (défaut `explore`). Cible un `subagent` seulement, sans imbrication. Permission `ask`, `allowlist` par défaut `["explore"]` (comparée au nom d'agent). | R`vibe/core/tools/builtins/task.py` |
| Agent `plan` | Précisé | `edit` et `write_file` en `never` sauf dans le dossier des plans ; `bash` en demande (la doc dit « read-only »). | R`vibe/core/agents/models.py` |
| `exit_plan_mode` | Confirmé | Uniquement dans l'agent `plan`, en interactif. Choix : « Yes, clear context and auto approve edits », « Yes, and auto approve edits » (→ `accept-edits`), « Yes, and request approval for edits » (→ `ask`), « No ». | R`vibe/core/tools/builtins/exit_plan_mode.py` |
| Le modèle ne peut pas entrer seul dans l'agent `plan` | Confirmé | — | Doc Agents |
| Sous-agents : pas de question, retour texte seul | Confirmé | — | Doc Agents |
| `-p` : outils interactifs désactivés | Confirmé | — | Doc Agents |
| Fichier de plan sous `~/.vibe/plans/` | Précisé | `PLANS_DIR`, accessible en lecture et en écriture par l'agent `plan`. | R`vibe/core/agents/models.py` |
| `AGENTS.md` | Confirmé | `~/.vibe/AGENTS.md` plus ceux trouvés jusqu'à la racine de confiance ; ceux des sous-dossiers sont injectés à la lecture d'un fichier. | R`vibe/core/system_prompt.py`, CL 2.25.3, 2.25.8 |
| Sous-agents de `.vibe/agents` lançables, agent invalide signalé | Confirmé | — | CL 2.25.8 |
| Accès de `reviewer` à `grep` sous le Unified Harness | À vérifier | `grep` absent de `RUST_BUILTIN_TOOL_SOURCES`. | R`vibe/app_server/_runtime.py`, recette 1, point 6 |

## Skills

| Fait | Statut | Détail | Source |
| --- | --- | --- | --- |
| `user-invocable` | Précisé | `true` par défaut dans le code. | R`vibe/core/skills/models.py` |
| Clé « explicit-only » | Confirmé | `disable-model-invocation: true` (absente de la doc). | R`vibe/core/skills/models.py`, CL 2.25.5 |
| `allowed-tools` | À vérifier | Code : « pre-approved tools (experimental) » ; doc : restriction. Application non trouvée. | R`vibe/core/skills/models.py`, D`skills`, recette étape 2 |
| Hooks sur l'outil `skill` | Confirmé | — | CL 2.25.5 |

## Hooks

| Fait | Statut | Détail | Source |
| --- | --- | --- | --- |
| Fichier, clés | Confirmé | `.vibe/hooks.toml` puis `~/.vibe/hooks.toml`. Clés `name`, `type` (`pre_tool`/`post_tool`/`post_agent`), `command` requis ; `match` (glob ou `re:`, interdit sur `post_agent`), `timeout` (60 s), `strict`, `description`. | R`vibe/core/hooks/models.py` |
| Champs stdin `post_tool` | Confirmé (modèle) | `session_id`, `transcript_path`, `cwd`, `parent_session_id`, `hook_event_name`, `tool_name`, `tool_call_id`, `tool_input`, `tool_status`, `tool_output`, `tool_output_text`, `tool_error`, `duration_ms`. | R`vibe/core/hooks/models.py` |
| Champs réellement transmis sous le Unified Harness | À vérifier | CL 2.26.0 : `session_id`, `transcript_path`, `parent_session_id` transmis « à nouveau ». Lire avec `.get()`. | CL 2.26.0 |
| `tool_name` vu par le hook (`bash` ou `file_system.bash`) | À vérifier | Le Unified Harness nomme l'outil `file_system.bash` en interne. | R`vibe/app_server/_unified_permissions.py`, recette 1, point 8 |
| Réponse | Confirmé | `exit 0` et stdout vide = rien ; JSON `decision`/`reason`/`system_message`/`hook_specific_output.additional_context` ; code non nul ou délai dépassé = échec du hook (refus si `strict`). `post_agent` relance au plus 3 fois. | D`hooks` |
| Shell et répertoire | Confirmé (legacy) | `create_subprocess_shell`, cwd = répertoire de la session. Une commande relative échoue depuis un sous-dossier. | R`vibe/core/hooks/executor.py`, CL 2.25.5, recette 1, point 9 |
| Hooks dans les sous-agents | Confirmé | — | CL 2.25.5 |
| `match` sur l'outil réellement appelé | Confirmé | — | CL 2.25.5 |
| Hook basé sur le texte du transcript | À vérifier | Format interne non documenté. | — |

## Divers hérités

| Fait | Statut | Détail | Source |
| --- | --- | --- | --- |
| Allowlists de chemins relatifs | Précisé | 2.25.8 : un chemin relatif n'autorise plus un fichier sur simple suffixe commun. | CL 2.25.8 |
| Contournement des listes shell | Précisé | Syntaxes de contournement soumises à approbation. | CL 2.25.4 |
| Agent par défaut renommé `ask` | Précisé | — | CL 2.24.1 |

## Modèles Mistral (au 2026-10-07)

| Modèle | ID épinglé | Statut | Contexte | Source |
| --- | --- | --- | --- | --- |
| Medium 3.5 | `mistral-medium-3-5` (Vibe : `mistral-vibe-cli-latest`) | GA, raisonnement | 256k | https://docs.mistral.ai/models/mistral-medium-3-5-26-04 |
| Small 4 | `mistral-small-2603` / `mistral-small-latest` | GA, raisonnement | 256k | https://docs.mistral.ai/models/mistral-small-4-0-26-03 |
| Large 3 | `mistral-large-2512` | GA | 256k | https://docs.mistral.ai/models/mistral-large-3-25-12 |
| Codestral | `codestral-2508` | GA | 128k | https://docs.mistral.ai/models/codestral-25-08 |

- **Devstral 2 et Magistral :** retirés le 2026-07-31 (https://docs.mistral.ai/getting-started/models/models_overview/).
- **Raisonnement côté API :** les modèles Mistral n'acceptent que `reasoning_effort` `high` ou `none` (https://docs.mistral.ai/capabilities/reasoning).
- **Comportement de `thinking = "off"` :** ce que reçoit l'API n'est pas vérifié ; à contrôler par `/compact` puis `/log`.

## Recette 2026-10-08 (Vibe 2.26.0, WSL) — observations, pas des faits 2.25.8

| Observation | Conséquence | Source |
| --- | --- | --- |
| Outils nommés `file_system.bash`, `file_system.search_replace` dans les demandes d'approbation | `[tools.bash]`, `[tools.edit]`, `[tools.write_file]` et `match = "bash"` peut-être inopérants : à tester (points 7, 8) | Recette 1, points 3-4 |
| Étape « Searched for relevant tools » avant certains appels | Outils chargés à la demande ; `exit_plan_mode` peut-être différé | Recette 1, point 3 |
| Agent `plan` : plan soumis en texte libre, sans `exit_plan_mode` | Sortie fiable du mode plan : `Shift+Tab` | Recette 1, point 3 |
| Agent `plan` : édition refusée sans question (« denied by approval policy ») | Conforme au code 2.25.8 (`never` hors dossier des plans) | Recette 1, point 3 |
| Le modèle contourne un refus d'édition par bash (`python3 -c`, `cat >` + `cp`) ; bash reste soumis à approbation | Règle à ajouter à `AGENTS.md` | Recette 1, points 3-4 |
| Bash : demande d'approbation motivée (« outside workdir », « redirection ») | Contournement détecté par Vibe | Recette 1, point 3 |
| `orchestrator` : pas d'appel `task(reviewer)` | À diagnostiquer (prompt, permission `task`) | Recette 1, point 4 |
| `/log` affiche seulement le dossier de session | Explorer ses fichiers | Recette 1, point 6 |
