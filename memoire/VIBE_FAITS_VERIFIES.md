# Faits Mistral Vibe vérifiés (cible 2.26.0, Unified Harness ; D-10)

Les tableaux thématiques ont été établis sur 2.25.8 et corrigés pour 2.26.0 là où ils divergent ; la section « Revérification 2.26.0 » fait foi en cas de doute.

Statuts : **Confirmé** (doc ou code 2.25.8 / 2.26.0) · **Précisé** (doc et code divergent, choix noté) · **À vérifier** (non documenté, test de recette prévu) · **Infirmé**.

Historique de validation :
- Le guide `reference/guide-harnais-vibe.md` a été validé contre la 2.25.2 le 2026-10-05.
- Les écarts 2.25.3 → 2.25.8 viennent du CHANGELOG lu le 2026-10-07.
- L'étape 1 (2026-10-07) a vérifié le code au tag **`v2.25.8`** (le nom `2.25.8` sans « v » renvoie 404).

Abréviations :
- **R** = `https://raw.githubusercontent.com/mistralai/mistral-vibe/v2.25.8/`
- **R26** = `https://raw.githubusercontent.com/mistralai/mistral-vibe/v2.26.0/`
- **H** = R26 + `harness/runtimes/python/python/mistralai_vibe_local_harness/vibe/`
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
| Noms des outils | Précisé (2.26.0) | Clés de config : noms historiques (`bash`, `edit`, `write_file`, `read_file`…). Noms vus par le modèle sous le Unified Harness : `file_system.bash`, `file_system.search_replace`, `file_system.write_file`, `file_system.read_file`, `process.*`, sous-agents `spawn`/`wait`/`list`… ; `task`, `exit_plan_mode`, `grep` non proposés (ancien moteur seulement). | R`vibe/core/tools/builtins`, R26`vibe/app_server/_unified_permissions.py` |
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
| `task` | **Infirmé (Unified)** | Ancien moteur seulement. Sous le Unified Harness : `spawn` (`agentName` unique, `message`, `agentType`), non bloquant, puis `wait` (`agentName`, `timeoutMs` entier ≥ 1, requis). `[tools.task] allowlist` sans effet ; tous les `agent_type = "subagent"` à fichier source sont proposés, `explore` exclu. | R26`harness/core/src/core/features/subagents/tools.rs`, R26`vibe/app_server/_agent_types.py` |
| Agent `plan` | Précisé | `edit` et `write_file` en `never` sauf dans le dossier des plans ; `bash` en demande (la doc dit « read-only »). | R`vibe/core/agents/models.py` |
| `exit_plan_mode` | **Infirmé (Unified)** | Jamais proposé au modèle sous le Unified Harness (2.25.8 et 2.26.0). Ancien moteur seulement : uniquement dans l'agent `plan`, en interactif. Choix : « Yes, clear context and auto approve edits », « Yes, and auto approve edits » (→ `accept-edits`), « Yes, and request approval for edits » (→ `ask`), « No ». | R`vibe/core/tools/builtins/exit_plan_mode.py` |
| Le modèle ne peut pas entrer seul dans l'agent `plan` | Confirmé | — | Doc Agents |
| Sous-agents : pas de question, retour texte seul | Confirmé | — | Doc Agents |
| `-p` : outils interactifs désactivés | Confirmé | — | Doc Agents |
| Fichier de plan sous `~/.vibe/plans/` | Précisé | `PLANS_DIR`, accessible en lecture et en écriture par l'agent `plan`. | R`vibe/core/agents/models.py` |
| `AGENTS.md` | Confirmé | `~/.vibe/AGENTS.md` plus ceux trouvés jusqu'à la racine de confiance ; ceux des sous-dossiers sont injectés à la lecture d'un fichier. | R`vibe/core/system_prompt.py`, CL 2.25.3, 2.25.8 |
| Sous-agents de `.vibe/agents` lançables, agent invalide signalé | Confirmé | — | CL 2.25.8 |
| Accès de `reviewer` à `grep` sous le Unified Harness | **Infirmé** | Plafond d'outils d'un sous-agent calculé sur les outils natifs : `grep` ignoré sans message. Recherche via bash. | R26`vibe/app_server/_runtime.py` |

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
| `tool_name` vu par le hook (`bash` ou `file_system.bash`) | Confirmé (code 2.26.0) | `tool_name = "file_system.bash"` sur stdin ; `match` comparé à `file_system.bash`, `bash`, `file_system_bash` : `match = "bash"` fonctionne. `process.start` non capté. À confirmer en recette (point 8). | H`_foreign_hooks.py`, H`_hook_matcher.py` |
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
| `orchestrator` : pas d'appel `task(reviewer)` | Expliqué : `task` non proposé sous le Unified Harness ; relecture par `spawn`/`wait` (D-10) | Recette 1, point 4 |
| `/log` affiche seulement le dossier de session | Explorer ses fichiers | Recette 1, point 6 |

## Revérification 2.26.0 (code au tag `v2.26.0`, 2026-10-08)

| Fait | Statut | Détail | Source |
| --- | --- | --- | --- |
| Moteur par défaut | Confirmé | Toujours le Unified Harness ; erreur explicite s'il manque. `--legacy-harness` : « temporary escape hatch ». | R26`CHANGELOG.md`, R26`vibe/cli/entrypoint.py` |
| Changements 2.26.0 utiles | Confirmé | Hooks : `session_id`, `transcript_path`, `parent_session_id` transmis ; `tool_input` avec les noms d'arguments historiques ; agent `plan` réécrit son plan ; `compaction_model` d'un autre provider ignoré (plus d'erreur) ; ajouts `thinking_levels`, `max_context_length`, `[utility_models]` (non utilisés). | R26`CHANGELOG.md` |
| Listes `allowlist` / `denylist` sous Unified | Confirmé | Chaque appel passe par `tool.resolve_permission(args)` de l'outil historique ; `always` abaissé en `ask` pour appliquer les règles. | R26`vibe/app_server/_unified_permissions.py`, R26`vibe/app_server/_runtime.py` |
| `*/.vibe/*` couvre `~/.vibe/plans/` | Confirmé | `PLANS_DIR = VIBE_HOME/"plans"` ; section `tools` fusionnée en profondeur entre couches ; denylist prioritaire : l'agent `plan` ne pouvait pas écrire son plan. Corrigé (D-10). | R26`vibe/core/paths/_vibe_home.py`, R26`vibe/core/agents/models.py`, R26`vibe/core/tools/utils.py` |
| Défauts bash POSIX | Confirmé | Identiques à 2.25.8 ; en plus `denylist_standalone` et `sensitive_patterns = ["sudo"]` par défaut (non redéfinis : actifs). Fusion superficielle. | R26`vibe/core/tools/builtins/bash.py`, R26`vibe/core/tools/manager.py` |
| Agent `plan` | Confirmé | `edit`/`write_file` en `never` sauf `~/.vibe/plans/*` ; `bash` en `ask` (d'où le contournement observé) ; `ask_user_question` disponible. | R26`vibe/core/agents/models.py` |
| Champs stdin des hooks | Précisé | `transcript_path` = dossier de session (`""` possible) ; `duration_ms` toujours 0 ; `cancelled` jamais émis. cwd du hook = `workspace.cwd`. | H`_foreign_hooks.py` |
| Permission de `spawn` | À vérifier | Outil fourni hors `RUST_BUILTIN_TOOL_SOURCES` : probablement `ask`. | R26`vibe/app_server/_runtime.py`, recette 1, point 4 |
| `system_prompt_id` | Précisé | Défaut `cli` ; une couche d'expérimentation GrowthBook peut fixer `cli_2026-07_v2` ou `cli_2026-08_v3` pour les agents sans prompt propre (`plan`) ; nos agents gardent le leur. | R26`vibe/core/config/layers/growthbook.py` |
| `cli.md` 2.26.0 = 2.25.8 | Confirmé | `diff` vide (curl des deux fichiers bruts, 136 lignes). | R26`vibe/core/prompts/cli.md` |
| `active_model` d'un sous-agent | Confirmé | Toujours ignoré (« runs on the session's model instead »). | R26`vibe/app_server/_agent_types.py` |
| Doc officielle | Divergente | Pages Agents et Hooks décrivent encore `task`, `enabled_tools = ["grep", …]`, `tool_name = "bash"`. Code retenu. | https://docs.mistral.ai/vibe/code/cli/agents · https://docs.mistral.ai/vibe/code/cli/hooks |

## Recette 2026-10-09 (Vibe 2.26.0, WSL, Medium 3.5, harnais D-10)

| Point | Observation | Conséquence |
| --- | --- | --- |
| 0, 11 | Python 3.11, 11 tests verts dans `~/test-etape-1` | Hook et tests validés sous 3.11 |
| 1 | Pas de dialogue (dossier déjà approuvé) ; confiance prouvée par le démarrage sur `plan` et l'accès à `orchestrator`. Le modèle a inventé une variable `VIBE_TRUST_MODE` | Ne pas croire le modèle sur Vibe lui-même |
| 2 | `AGENTS.md` cité, section « Refus et vérification » comprise | Confirmé |
| 3 | Plan correct, aucun contournement par bash, renvoi vers `orchestrator`. Plan écrit par `unified_harness_scratchpad` dans `<session>/scratchpad/` (approbation `always` venant de la config), pas dans `~/.vibe/plans/` (absent) | Le correctif de denylist (D-10) est sans effet sur le plan, mais sans danger |
| 4 | Orchestrateur : édition et pytest réels (5 verts) ; pas de `todo` visible, pas d'`ask_user_question`, **pas de `spawn`** | Consigne du prompt non suivie (D-11) |
| 4 bis | Appel explicite : `spawn` (« Started reviewer-1 ») puis `wait` fonctionnent, format Bloquant / À corriger / Suggestion respecté, environ 3 min par relecture. Relecteur peu fiable (avis contradictoires sur les lignes vides, lignes fausses) ; orchestrateur en boucle (4 relecteurs), corrections par `sed -i` / `git checkout` après échec de `search_replace` (« old_str and new_str must differ ») | Correctifs D-11 |
| 5 | `/thinking` = `high` | Confirmé |
| 6 | Session : `CURRENT`, `chunks/`, `generations/`, `journal/`, `meta.json`, `scratchpad/`. Modèles : `mistral-medium-3.5` / `mistral-vibe-cli-latest`, `mistral-small-latest`. Outils exposés en plus : `web_search`, `connector_web_search`, `news_search`, `finance_search`, `weather_search`, `open_url`, `search_tool_functions`, `cron`. Ni « Ajouts du harnais » ni `spawn` trouvés par `grep` (texte non stocké en clair) | Contrôle du prompt par `grep` non concluant ; outils web à décider |
| 7a | Édition de `.vibe/config.toml` : « Tool execution denied by approval policy », sans question | Denylist `[tools.edit]` appliquée à `file_system.search_replace` : confirmé |
| 7b | « Command denied: 'git push --force' matches denylist pattern » ; idem `vim` | Confirmé |
| 7c | `git status`, `ls src` sans question | Confirmé |
| 7d | `echo test > .vibe/x` : demande d'approbation, refus → « denied by approval callback » | Confirmé |
| 7e | `write_file` sur `.vibe/x` : demande d'approbation | Limite connue, acceptée |
| 7 (tous) | Sans consigne explicite, le modèle refuse de lui-même (règles d'`AGENTS.md`, section Projet) sans appeler l'outil | Pour tester une permission, exiger l'appel de l'outil |
| 8 | `bash.log` : `file_system.bash` en 2e colonne, `success` / `failure` ; `python3 << EOF` refusé (« not allowed as a standalone command », `denylist_standalone`) tracé en `failure` | `match = "bash"` et `tool_name` confirmés |
| Bash dans `ask` | `sed -i` soumis à approbation | Pas de trou de permission |
| Non faits | Capture du stdin d'un hook, point 9 (sous-dossier), point 10 (`/compact`), bonus (bash du relecteur) | Restent « À vérifier » |

## GLM 5.3 et modèles (code au tag `v2.26.0` et doc Mistral, 2026-10-09 ; D-12)

H = R26`harness/runtimes/python/python/mistralai_vibe_local_harness/vibe/`.

| Fait | Statut | Détail | Source |
| --- | --- | --- | --- |
| GLM 5.3 chez Mistral | Confirmé (doc) | « third-party open weight text model from Z.ai, hosted by Mistral » ; ID `zai-glm-5-3` ; texte seul ; contexte 1M, sortie 128k ; appels de fonction ; 1,4 / 0,14 (cache) / 4,4 USD par M tokens | https://docs.mistral.ai/models/zai-glm-5-3 |
| Effort de raisonnement GLM | Confirmé (doc) | `reasoning_effort` accepte `low`, `high`, `max`, pas `none` | https://docs.mistral.ai/capabilities/reasoning |
| Providers intégrés | Confirmé | `mistral` et `llamacpp` seulement ; GLM sur `mistral` : aucun `[[providers]]` | R26`vibe/core/config/vibe_schema.py` (`DEFAULT_PROVIDERS`) |
| Schéma `[[models]]` | Confirmé | `name`, `provider`, `alias` (= `name` par défaut), `display_name`, `temperature` (0.2), prix, `thinking`, `thinking_levels`, `supports_images` (False), `max_context_length`, `auto_compact_threshold` ; dictionnaire indexé par alias, fusion profonde avec les modèles intégrés | R26`vibe/core/config/models.py`, R26`vibe/core/config/vibe_schema.py` |
| Traduction de `thinking` | Confirmé | `low`→`none`, `medium`/`high`/`max`→`high`, `off` = non envoyé. Sous Unified, adaptateur H`adapters/mistral.py` (choisi si backend `mistral`) ; même table que le backend historique | H`adapters/mistral.py`, H`_completion.py`, R26`vibe/core/llm/backend/mistral.py` |
| Raisonnement renvoyé | Confirmé (code) | Chunks `thinking` lus en flux et hors flux, rejoués dans l'historique avec `tool_calls` ; rien ne dépend du nom de modèle. Compatibilité réelle avec GLM : à recetter | H`adapters/mistral.py` |
| Modèle d'un sous-agent | Confirmé (Python), à recetter | Modèle actif de l'agent parent au moment du `spawn` (`create_child` copie le `config_orchestrator` du parent) ; `SpawnInput` sans champ modèle. L'avertissement dit « session's model » : écart sans effet ici (parent et session sur GLM), à trancher en recette (modèle du `reviewer`) | R26`vibe/app_server/_runtime.py`, R26`vibe/app_server/_agent_types.py` |
| Changement d'agent | Confirmé (couches), à recetter | Ordre : défauts < GrowthBook < utilisateur < projet < env < session < profil d'agent < admin ; le profil l'emporte sur le modèle fixé par le premier message | R26`vibe/core/config/default_orchestrator.py`, R26`vibe/app_server/_session_model.py` |
| `/model` | Confirmé | Écrit `active_model` dans la config utilisateur `~/.vibe/config.toml` et dans la surcharge de session ; surclassé par un profil d'agent ; pas une procédure de repli | R26`vibe/app_server/_config_write.py`, R26`vibe/core/config/default_orchestrator.py`, R26`README.md` |
| Compaction | Confirmé | `compaction_model` gardé si même provider que le modèle actif : Small 4 reste utilisé avec GLM | R26`vibe/core/config/vibe_schema.py` |
| Image avec GLM | Confirmé | Modèle sans images : `vision_model` s'il est défini (pas le cas), sinon premier modèle du même provider avec images (Medium 3.5), qui décrit l'image en texte | R26`vibe/core/config/vibe_schema.py` (`get_vision_fallback_model`), appelé par R26`vibe/app_server/_vision.py` |
| `routed_*`, `allowed_models` | Confirmé | Sans effet ici (`active_model` fixé, liste vide) | R26`vibe/core/config/vibe_schema.py` |
