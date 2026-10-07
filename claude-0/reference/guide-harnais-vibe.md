# Harnais Mistral Vibe : mise en place pas à pas

Oct 5, 2026 · @Gaëtan

## Vue d'ensemble

Le harnais tient en un `AGENTS.md` à la racine et un dossier `.vibe/` versionné ; tout ce qui est personnel (clés, préférences, autorisations accordées) reste dans `~/.vibe/`. Ce guide prend l'exemple d'une API avec une base PostgreSQL, à adapter à votre stack. Version de référence : Vibe CLI 2.25.2.

```text
mon-projet/
├── AGENTS.md                      # instructions projet (équivalent CLAUDE.md)
├── .gitignore                     # + entrées Vibe (étape 3)
└── .vibe/
    ├── config.toml                # modèle, agent par défaut, permissions, MCP
    ├── hooks.toml                 # hooks pre_tool / post_tool / post_agent
    ├── hooks/                     # scripts appelés par les hooks
    │   ├── guard_db.py
    │   ├── lint_after_edit.py
    │   └── require_review.py
    ├── agents/                    # profils TOML
    │   ├── orchestrator.toml      # agent_type = "agent"
    │   ├── code-reviewer.toml     # agent_type = "subagent"
    │   └── test-writer.toml       # agent_type = "subagent"
    ├── prompts/                   # prompts système référencés par system_prompt_id
    │   ├── orchestrator.md
    │   ├── code-reviewer.md
    │   └── test-writer.md
    ├── skills/                    # skills Agent Skills (SKILL.md)
    │   ├── review/SKILL.md
    │   ├── db-query/SKILL.md
    │   └── api-conventions/
    │       ├── SKILL.md
    │       └── examples.md        # exemples few-shot
    ├── tasks/                     # prompts de tâche versionnés (convention, non lu par Vibe)
    │   └── add-endpoint.md
    └── logs/                      # journaux écrits par vos hooks (ignorés par git)
```

| Fichier | Lu par Vibe | Commité | Rôle |
| --- | --- | --- | --- |
| `AGENTS.md` | Oui, dossier de confiance | Oui | Contexte et règles du projet, ajoutés au prompt système |
| `.vibe/config.toml` | Oui, dossier de confiance | Oui | Réglages d'équipe, superposés à `~/.vibe/config.toml` |
| `.vibe/hooks.toml` + `hooks/` | Oui | Oui | Garde-fous et automatismes |
| `.vibe/agents/*.toml` | Oui | Oui | Orchestrateur et sous-agents |
| `.vibe/prompts/*.md` | Oui (via `system_prompt_id`) | Oui | Prompts système des agents |
| `.vibe/skills/*/SKILL.md` | Oui | Oui | Savoir-faire et commandes `/nom` |
| `.vibe/tasks/*.md` | Non | Oui | Prompts de tâche réutilisables en CLI |
| `.vibe/logs/` | Non | Non | Traces d'audit des hooks |
| `~/.vibe/` | Oui | Jamais | Clés, config perso, sessions, plans, autorisations « toujours » |

## Étape 1 — Mise en place

Deux fichiers suffisent pour démarrer : `AGENTS.md` et `.vibe/config.toml`. Le reste s'ajoute au fil des étapes.

### 1.1 Installer et s'authentifier (une fois par poste)

```bash
curl -LsSf https://mistral.ai/vibe/install.sh | bash   # ou : uv tool install mistral-vibe
vibe --setup        # connexion navigateur (défaut avec un compte Mistral) ou clé API
                    # identifiants hors projet : ~/.vibe/.env ou trousseau OS selon la version
vibe --version
```

### 1.2 Créer le squelette dans le dépôt

```bash
cd mon-projet
git switch -c chore/vibe-harness
mkdir -p .vibe/{agents,prompts,skills,hooks,tasks,logs}
touch AGENTS.md .vibe/config.toml .vibe/hooks.toml
```

### 1.3 `AGENTS.md` : le contexte projet

Court et factuel : Vibe l'ajoute à chaque session. Les procédures longues vont dans des skills.

```markdown
# Projet : orders-api

## Stack
- Python 3.12, FastAPI, SQLAlchemy 2, PostgreSQL 16
- Tests : pytest (`make test`), lint : ruff (`make lint`)

## Carte du code
- `app/api/` routes HTTP · `app/domain/` logique métier · `app/db/` modèles et requêtes
- `migrations/` Alembic : ne jamais modifier une migration déjà fusionnée

## Règles
- Jamais d'accès direct à la base de production ; uniquement `DATABASE_URL` local.
- Toute modification de code s'accompagne d'un test.
- Avant de conclure : `make lint` puis `make test` doivent passer.

## Façon de travailler
- Tâche non triviale : propose d'abord un plan (agent `plan`).
- Délègue la relecture au sous-agent `code-reviewer`.
```

Pour une règle propre à un sous-dossier (par exemple `migrations/`), ajoutez un `AGENTS.md` dans ce dossier : Vibe le découvre quand il y lit des fichiers.

### 1.4 `.vibe/config.toml` : la base d'équipe

```toml
# Agent au lancement interactif : default (renommé "ask" en 2.24.1) | plan | accept-edits
# | auto-approve | nom d'un agent perso de .vibe/agents/. Ignoré en mode -p.
default_agent = "plan"

# Modèle partagé par l'équipe (ID de modèle ou alias d'un [[models]])
active_model = "mistral-medium-latest"

# Liste blanche de skills : si non vide, SEULES ces skills se chargent
# (y compris les skills fournies par Vibe : ajoutez-les si vous les utilisez)
enabled_skills = ["review", "db-query", "api-conventions"]
```

Les permissions (étape 2), le serveur MCP et les modèles à réflexion (étape 7) viendront compléter ce fichier.

### 1.5 Premier lancement

```bash
vibe
```

Vibe détecte `AGENTS.md` et `.vibe/`, liste les risques et propose de faire confiance à la racine git. Acceptez : sans cela, toute la configuration projet est ignorée. Le choix est mémorisé dans `~/.vibe/trusted_folders.toml`. Après chaque modification du harnais en cours de session, tapez `/reload`.

Documentation officielle : [Install and setup](https://docs.mistral.ai/vibe/code/cli/install-setup) · [API keys and profiles](https://docs.mistral.ai/vibe/code/cli/api-keys-profiles) · [Configuration](https://docs.mistral.ai/vibe/code/cli/configuration) · [Configuration reference](https://docs.mistral.ai/vibe/code/cli/configuration-reference) · [Agents, section AGENTS.md](https://docs.mistral.ai/vibe/code/cli/agents) · [Trusted folders](https://docs.mistral.ai/vibe/code/safety-approvals-permissions) · [Commandes (`/reload`)](https://docs.mistral.ai/vibe/code/cli/commands-shortcuts).

## Étape 2 — Commandes autorisées ou interdites, accès aux fichiers

Vibe n'a pas de règles `allow / ask / deny` à la Claude Code : on combine quatre couches, de la plus simple à la plus fine. Une règle `denylist` refuse sans demander ; tout ce qui n'est ni autorisé ni interdit est demandé.

| Couche | Où | Granularité | Exemple base de données |
| --- | --- | --- | --- |
| 1. Outils actifs | `enabled_tools` / `disabled_tools` | Outil entier | Retirer `web_fetch` |
| 2. Permission par outil | `[tools.<outil>] permission` | `always` ou `ask` | Shell toujours demandé |
| 3. Listes du shell et des fichiers | `allowlist`, `denylist`, `sensitive_patterns` | Préfixe de commande, glob de chemin | Interdire `dropdb`, protéger `migrations/` |
| 4. Hook `pre_tool` | `.vibe/hooks.toml` | Tout ce qu'un script peut analyser | Refuser `DROP TABLE` dans une requête |

### 2.1 Shell : autoriser les commandes sûres, interdire les dangereuses

```toml
# .vibe/config.toml
[tools.bash]
permission = "ask"
# Préfixes exécutés sans demande (s'ajoutent aux défauts : ls, cat, grep, git status, git diff…)
allowlist = ["make test", "make lint", "pytest", "ruff check", "alembic current", "alembic history"]
# Préfixes refusés sans demande
denylist = ["dropdb", "createdb", "pg_restore", "alembic downgrade", "docker compose down -v", "git push --force"]
# Toujours demander, même si l'utilisateur a approuvé « pour la session »
sensitive_patterns = ["sudo", "psql", "alembic upgrade"]
```

Comment Vibe applique ces listes (lu dans le code source de l'outil `bash`) :

- La commande est découpée en sous-commandes (`&&`, `|`, `;`…) ; **chaque** sous-commande est comparée aux listes.
- Une règle correspond si la sous-commande est égale au préfixe ou commence par « préfixe + espace » : `git push --force` bloque `git push --force origin main`, pas `git push -f`.
- Un `denylist` gagne toujours ; le refus est renvoyé au modèle avec le motif.
- Par défaut sont déjà interdits les éditeurs et shells interactifs (`vim`, `nano`, `bash -i`, `tmux`…) et `python` ou `bash` lancés seuls.

**Point vérifié — nom des clés.** La [Configuration reference](https://docs.mistral.ai/vibe/code/cli/configuration-reference) et la page [Safety](https://docs.mistral.ai/vibe/code/safety-approvals-permissions) écrivent `allow` / `deny`. Le code de la 2.25 ([`base.py`](https://raw.githubusercontent.com/mistralai/mistral-vibe/main/vibe/core/tools/base.py)) ne définit que `allowlist`, `denylist` et `sensitive_patterns`, et accepte les clés inconnues sans erreur : une clé mal nommée se charge donc sans message mais reste probablement sans effet. Ce guide utilise `allowlist` / `denylist` ; validez avec les tests `dropdb` et `make test` de la recette, quelle que soit la clé retenue.

### 2.2 Base de données : filtrer le contenu des requêtes

Un préfixe ne voit pas l'intérieur d'un `psql -c "…"`. Un hook `pre_tool` lit la commande complète avant l'invite d'approbation :

```toml
# .vibe/hooks.toml
[[hooks]]
name = "guard-db"
type = "pre_tool"
match = "bash"
command = "python3 .vibe/hooks/guard_db.py"
strict = true          # un crash du script vaut refus
description = "Interdit la prod et les requêtes destructrices."
```

```python
# .vibe/hooks/guard_db.py
import json, re, sys

payload = json.load(sys.stdin)
cmd = payload.get("tool_input", {}).get("command", "")

DB_CLIENTS = re.compile(r"\b(psql|pgcli|alembic|sqlalchemy)\b")
PROD = re.compile(r"(prod|production)[\w.-]*\.(internal|example\.com)", re.I)
DESTRUCTIVE = re.compile(r"\b(DROP|TRUNCATE|DELETE\s+FROM|ALTER\s+TABLE|UPDATE\s+\w+\s+SET)\b", re.I)

def deny(reason):
    print(json.dumps({"decision": "deny", "reason": reason}))
    sys.exit(0)

if PROD.search(cmd):
    deny("Accès à une base de production interdit. Utilise DATABASE_URL local.")
if DB_CLIENTS.search(cmd) and DESTRUCTIVE.search(cmd):
    deny("Requête destructrice interdite. Propose une migration Alembic à relire.")
# stdout vide = laisser passer vers l'approbation normale
```

Alternative plus sûre que le shell : un serveur MCP qui n'exécute que des transactions en lecture seule, avec approbation à chaque requête. N'utilisez pas `@modelcontextprotocol/server-postgres`, souvent cité dans les tutoriels : il est [déprécié sur npm](https://www.npmjs.com/package/@modelcontextprotocol/server-postgres) et n'est plus maintenu. [Postgres MCP Pro](https://github.com/crystaldba/postgres-mcp) (`postgres-mcp`) propose un mode `restricted` limité aux transactions en lecture seule.

```toml
[[mcp_servers]]
name = "db"
transport = "stdio"
command = "uvx"
args = ["postgres-mcp", "--access-mode=restricted"]   # lecture seule
env = { "DATABASE_URI" = "postgresql://localhost:5432/orders_dev" }   # base locale, sans mot de passe commité

# Outils exposés sous la forme {serveur}_{outil}
[tools.db_execute_sql]
permission = "ask"

[tools.db_list_objects]
permission = "always"

[tools.db_get_object_details]
permission = "always"
```

### 2.3 Fichiers : zones d'écriture et fichiers protégés

Les outils `read_file`, `edit` et `write_file` acceptent eux aussi `allowlist` / `denylist`, comparés par glob au **chemin absolu** du fichier : commencez donc vos motifs par `*/`.

```toml
[tools.read_file]
denylist = ["*/secrets/*", "*.pem", "*.key"]

[tools.edit]
permission = "ask"
allowlist = ["*/app/*", "*/tests/*"]                         # édition sans demande
denylist = ["*/migrations/versions/*", "*/.vibe/*", "*/.github/workflows/*"]

[tools.write_file]
allowlist = ["*/app/*", "*/tests/*"]
denylist = ["*/migrations/versions/*", "*/.vibe/*"]
```

Ce qui s'applique sans configuration :

- Les fichiers `.env`, `.env.*` et `.envrc` déclenchent toujours une demande (`sensitive_patterns` par défaut).
- Lire, écrire ou lancer une commande **hors du répertoire de travail** déclenche une demande, quel que soit l'agent. Pour ouvrir un autre dépôt : `vibe --add-dir ../shared-lib`.
- `write_file` ne fait que créer : il refuse d'écraser un fichier existant ; toute modification passe par `edit`.

Protégez `.vibe/` en écriture : sinon l'agent pourrait modifier ses propres garde-fous. Avec `auto-approve` ou `--yolo`, ne comptez que sur les hooks, et seulement dans un conteneur jetable.

Documentation officielle : [Safety, approvals, and permissions](https://docs.mistral.ai/vibe/code/safety-approvals-permissions) · [Configuration reference, `[tools.<outil>]`](https://docs.mistral.ai/vibe/code/cli/configuration-reference) · [Hooks](https://docs.mistral.ai/vibe/code/cli/hooks) · [MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers). Comportements lus dans le code source (non décrits dans la doc) : [découpage et préfixes du shell](https://raw.githubusercontent.com/mistralai/mistral-vibe/main/vibe/core/tools/builtins/bash.py), [globs de chemins et fichiers sensibles](https://raw.githubusercontent.com/mistralai/mistral-vibe/main/vibe/core/tools/utils.py).

## Étape 3 — Versionner le harnais et travailler en équipe

La règle est simple : tout ce qui est dans le dépôt est partagé et relu en PR, tout ce qui est personnel vit dans `~/.vibe/`. Vibe n'a pas d'équivalent à `settings.local.json` : il n'y a donc presque rien à ignorer dans `.vibe/`.

### 3.1 Commitable ou local

| Élément | Emplacement | Statut git | Pourquoi |
| --- | --- | --- | --- |
| Contexte projet | `AGENTS.md` (+ sous-dossiers) | Commité | Mêmes règles pour toute l'équipe |
| Réglages, permissions, MCP | `.vibe/config.toml` | Commité | Garde-fous identiques pour tous |
| Agents, prompts, skills | `.vibe/agents/`, `prompts/`, `skills/` | Commités | Comportement reproductible |
| Hooks et scripts | `.vibe/hooks.toml`, `.vibe/hooks/` | Commités (scripts exécutables) | Contrôles automatiques partagés |
| Prompts de tâche | `.vibe/tasks/` | Commités | Réutilisables en CLI et en CI |
| Traces des hooks | `.vibe/logs/` | Ignoré | Propre à chaque poste |
| Clé API | Trousseau OS ou `~/.vibe/.env` | Hors dépôt | Secret |
| Préférences perso (thème, modèle favori) | `~/.vibe/config.toml` | Hors dépôt | Couche utilisateur, recouverte par le projet |
| Style perso, skills perso | `~/.vibe/AGENTS.md`, `~/.vibe/skills/` | Hors dépôt | Chargés dans tous vos projets |
| Confiance, autorisations « toujours » | `~/.vibe/trusted_folders.toml`, config utilisateur | Hors dépôt | Choix individuels |
| Sessions, plans, worktrees | `~/.vibe/logs/`, `~/.vibe/plans/`, `~/.vibe/worktrees/` | Hors dépôt | État de travail |

### 3.2 `.gitignore`

```gitignore
# Vibe : traces locales écrites par nos hooks
.vibe/logs/

# Secrets (Vibe demande avant de les lire, mais ils ne doivent jamais être commités)
.env
.env.*
!.env.example
```

N'ignorez surtout pas `.vibe/` en entier : vous perdriez tout le harnais partagé.

### 3.3 Surcharges personnelles sur un seul projet

Faute de fichier local dédié, trois options, de la plus légère à la plus durable :

1. **Session** : `/config`, puis `Tab` pour choisir la cible « session » ; ou des options de lancement (`vibe --agent accept-edits`).
2. **Variables d'environnement** `VIBE_*` chargées par un outil comme direnv, dans un `.envrc` ignoré par git.
3. **Couche utilisateur** `~/.vibe/config.toml`, si le réglage vous convient partout.

Attention : `/config` peut aussi écrire dans `.vibe/config.toml` (cible « projet »). La cible par défaut est l'utilisateur depuis la 2.25.0, mais relisez tout diff sur ce fichier avant de commiter.

### 3.4 Règles d'équipe

- Faire relire toute modification de `AGENTS.md` et `.vibe/` en PR, idéalement par un propriétaire désigné (`CODEOWNERS`) : ces fichiers changent ce que l'agent a le droit de faire.
- Documenter la version minimale de Vibe dans `AGENTS.md` ou le README ; les formats évoluent vite (hooks renommés en 2.21.0).
- En CI, la confiance n'est jamais demandée : passer `--trust` explicitement.
- Équipe mixte Claude Code + Vibe : gardez un `CLAUDE.md` contenant seulement `@AGENTS.md`, et partagez les skills dans `.agents/skills/` (lu nativement par Vibe).

Documentation officielle : [Configuration — emplacements, `VIBE_HOME`, préséance des couches](https://docs.mistral.ai/vibe/code/cli/configuration) · [Trusted folders et `--trust`](https://docs.mistral.ai/vibe/code/safety-approvals-permissions) · [API keys and profiles](https://docs.mistral.ai/vibe/code/cli/api-keys-profiles). La cible de `/config` (utilisateur / session / projet) et la couche de variables `VIBE_*` sont décrites dans le [CHANGELOG](https://github.com/mistralai/mistral-vibe/blob/main/CHANGELOG.md) (2.14.0, 2.25.0), pas encore dans la doc.

## Étape 4 — Prompt principal : versionné ou en CLI

Distinguez le prompt **système** (comment l'agent travaille, stable, versionné) du prompt de **tâche** (ce qu'il doit faire maintenant, versionné s'il est réutilisé, sinon tapé en CLI).

| Besoin | Mécanisme Vibe | Versionné |
| --- | --- | --- |
| Ajouter des règles au comportement par défaut | `AGENTS.md` | Oui |
| Remplacer tout le prompt système | `.vibe/prompts/<id>.md` + `system_prompt_id` (global ou par agent) | Oui |
| Personnaliser le résumé de compaction | `.vibe/prompts/<id>.md` + `compaction_prompt_id` | Oui |
| Tâche récurrente en interactif | Skill `user-invocable` (`/add-endpoint refunds`) | Oui |
| Tâche récurrente en CLI ou CI | Fichier `.vibe/tasks/*.md` passé à `vibe` | Oui |
| Tâche ponctuelle | `vibe "…"` ou saisie dans la session | Non |

### 4.1 Prompt système versionné

```toml
# .vibe/config.toml  (s'applique à tous les agents qui ne définissent pas le leur)
system_prompt_id = "main"            # -> .vibe/prompts/main.md
compaction_prompt_id = "compact"     # -> .vibe/prompts/compact.md
```

`system_prompt_id` **remplace** le prompt par défaut, y compris les consignes d'usage des outils. Partez d'une copie du prompt fourni dans le dépôt (`vibe/core/prompts/`) et ajoutez vos sections ; si vous voulez seulement ajouter des règles, restez sur `AGENTS.md`.

**Précision.** La doc [Agents](https://docs.mistral.ai/vibe/code/cli/agents) indique que `system_prompt_id` pointe vers `~/.vibe/prompts/` ; le [README](https://github.com/mistralai/mistral-vibe#custom-system-prompts) ajoute que `.vibe/prompts/` du projet est aussi lu et l'emporte à nom égal. `compaction_prompt_id` n'est documenté que dans ce README. Si votre version ignore le prompt projet, copiez-le dans `~/.vibe/prompts/`.

### 4.2 Prompt de tâche versionné

```markdown
<!-- .vibe/tasks/add-endpoint.md -->
Ajoute l'endpoint REST `${ENDPOINT}` dans `app/api/`.

Contraintes :
- Respecte la skill `api-conventions`.
- Écris les tests dans `tests/api/` avant le code.
- Termine par `make lint` et `make test`, puis fais relire par `code-reviewer`.

Rends un résumé : fichiers modifiés, tests ajoutés, points ouverts.
```

### 4.3 Appels en ligne de commande

```bash
# Interactif, avec un premier message
vibe --agent orchestrator "$(ENDPOINT=refunds envsubst < .vibe/tasks/add-endpoint.md)"

# Non interactif (script, CI) : toujours fixer agent, confiance et budget
vibe -p "$(ENDPOINT=refunds envsubst < .vibe/tasks/add-endpoint.md)" \
     --agent orchestrator --trust --max-turns 40 --output json > run.json

# Analyse en lecture seule
vibe -p "Liste les endpoints sans test" --agent plan --trust --output text

# Reprendre plus tard la même conversation
vibe -c
```

En mode `-p`, les outils interactifs (dont `ask_user_question`) sont désactivés : la tâche doit être autosuffisante. **Point vérifié** : selon la doc ([Agents](https://docs.mistral.ai/vibe/code/cli/agents), [Configuration](https://docs.mistral.ai/vibe/code/cli/configuration)), `-p` sans `--agent` ignore `default_agent` et retombe sur `auto-approve`, alors que le CHANGELOG 2.11.1 annonce l'inverse. Passez donc toujours `--agent` explicitement.

Documentation officielle : [Work with the CLI — mode programmatique et reprise](https://docs.mistral.ai/vibe/code/cli/work-with-cli) · [Agents](https://docs.mistral.ai/vibe/code/cli/agents).

## Étape 5 — Orchestrateur, mode plan et sous-agents

L'orchestrateur est un agent principal (`agent_type = "agent"`) dont le prompt planifie et délègue via l'outil `task` ; les sous-agents (`agent_type = "subagent"`) ne sont appelables que par le modèle. Le mode plan, lui, est un agent à part que **vous** activez.

&#91;embedded content: qui déclenche quoi · orchestrateur, 3 sous-agents, 1 skill, 1 hook\]

L'orchestrateur choisit librement entre `explore` et `test-writer` ; la relecture par `code-reviewer` est garantie soit par vous (`/review`), soit par le hook qui refuse de conclure sans elle.

### 5.1 Déclarer les sous-agents

```toml
# .vibe/agents/code-reviewer.toml
agent_type = "subagent"
display_name = "Code reviewer"
description = "Relit le diff courant : bugs, sécurité, tests manquants. À appeler après toute modification de code."
safety = "safe"
system_prompt_id = "code-reviewer"
enabled_tools = ["read_file", "grep", "bash"]

[tools.bash]
allowlist = ["git diff", "git log", "make lint"]
```

```toml
# .vibe/agents/test-writer.toml
agent_type = "subagent"
display_name = "Test writer"
description = "Écrit ou complète les tests pytest d'un module donné, puis les exécute."
safety = "neutral"
system_prompt_id = "test-writer"
enabled_tools = ["read_file", "grep", "edit", "write_file", "bash"]

# N'écrit et ne modifie que des tests : les deux outils d'écriture sont bornés
[tools.write_file]
allowlist = ["*/tests/*"]
denylist = ["*/app/*", "*/migrations/*"]

[tools.edit]
allowlist = ["*/tests/*"]
denylist = ["*/app/*", "*/migrations/*"]

[tools.bash]
allowlist = ["pytest", "make test"]
```

Le sous-agent ne voit pas la conversation et ne peut pas poser de question : son prompt système (`.vibe/prompts/code-reviewer.md`) doit fixer un **format de retour** strict, par exemple « Bloquant / À corriger / Suggestion, avec fichier:ligne ».

### 5.2 Déclarer l'orchestrateur

```toml
# .vibe/agents/orchestrator.toml
agent_type = "agent"
display_name = "Orchestrateur"
description = "Planifie, délègue, intègre et vérifie."
safety = "neutral"
system_prompt_id = "orchestrator"

[tools.task]
permission = "always"     # déléguer sans demander

[tools.edit]
permission = "ask"        # garder la main sur les écritures
```

Extrait de `.vibe/prompts/orchestrator.md` (à ajouter à une copie du prompt par défaut, voir étape 4) :

```markdown
## Méthode
1. Comprendre : explore avec `task(agent="explore")` si le périmètre dépasse 3 fichiers.
2. Planifier : écris un plan numéroté dans `todo`, puis demande validation avec `ask_user_question`.
3. Exécuter : une étape à la fois ; coche `todo` après chaque étape.
4. Déléguer :
   - tests d'un module -> `task(agent="test-writer")`
   - relecture finale -> `task(agent="code-reviewer")`, toujours, avant de conclure
5. Transmettre au sous-agent : objectif, fichiers concernés, contraintes, format de réponse attendu.
6. Conclure : résumé, fichiers modifiés, retours du reviewer traités ou non.
```

Lancement : `vibe --agent orchestrator`, ou `default_agent = "orchestrator"` dans `.vibe/config.toml`.

### 5.3 Activer le mode plan

1. Lancez `vibe --agent plan` (ou `Shift+Tab` jusqu'à « plan »).
2. Décrivez la tâche ; l'agent lit le code avec les outils de lecture auto-approuvés, écritures et commandes bloquées (doc [Agents](https://docs.mistral.ai/vibe/code/cli/agents)).
3. Il rédige un plan ; `Ctrl+G` ouvre « le plan courant » dans votre éditeur (doc [Commands and shortcuts](https://docs.mistral.ai/vibe/code/cli/commands-shortcuts)). Le fichier est rangé sous `~/.vibe/plans/` : détail observé par un outil tiers, non documenté officiellement.
4. Il appelle `exit_plan_mode` (outil cité dans le CHANGELOG, pas dans la doc) : vous approuvez, ce qui bascule vers `accept-edits` avec option de vider le contexte, ou vous demandez des corrections.
5. Pour exécuter avec délégation, passez à l'orchestrateur par `Shift+Tab` et dites « exécute le plan approuvé ».

Le modèle ne peut pas entrer seul dans l'agent `plan`. Pour un plan systématique sans changer d'agent, c'est le prompt de l'orchestrateur (étape 2 de sa méthode) qui l'impose.

### 5.4 Appel déterminé par l'orchestrateur ou déterministe

| Mode | Mécanisme | Garantie |
| --- | --- | --- |
| Décidé par l'orchestrateur | `description` des sous-agents + règles de délégation dans son prompt | Le modèle choisit ; fiable si les descriptions sont nettes |
| Déterministe à la demande | Skill `/review` qui n'autorise que l'outil `task` (étape 6) | Vous déclenchez, le seul geste possible est la délégation |
| Déterministe systématique | Hook `post_agent` qui refuse la fin de tour tant que `code-reviewer` n'a pas tourné (étape 6) | Relance automatique, 3 fois au plus |
| Déterministe hors modèle | Script enchaînant `vibe -p --agent plan` puis `vibe -p --agent orchestrator` | L'ordre est fixé par le script |

Documentation officielle : [Agents — agents perso, sous-agents, `agent_type`](https://docs.mistral.ai/vibe/code/cli/agents) · [Configuration reference — clés des fichiers d'agent](https://docs.mistral.ai/vibe/code/cli/configuration-reference) · [README — Subagents and Task Delegation, `ask_user_question`](https://github.com/mistralai/mistral-vibe#subagents-and-task-delegation). Les sous-agents ne peuvent pas poser de questions et renvoient un texte seul (doc Agents) ; les hooks hérités par les sous-agents sont décrits dans la doc [Hooks](https://docs.mistral.ai/vibe/code/cli/hooks).

## Étape 6 — Créer et appeler skills et hooks

Une skill apporte du savoir-faire que le modèle charge ou que vous tapez en `/nom` ; un hook est un script que Vibe exécute quoi que décide le modèle. Mettez dans les hooks ce qui doit être garanti, dans les skills ce qui doit être bien fait.

### 6.1 Skill déterministe : `/review`

```markdown
<!-- .vibe/skills/review/SKILL.md -->
---
name: review
description: Lance la relecture du diff courant par le sous-agent code-reviewer.
user-invocable: true
allowed-tools:
  - task
---
Appelle exactement une fois `task(agent="code-reviewer", task=...)` avec :
- l'objectif : relire `git diff HEAD` (et la consigne éventuelle tapée après /review) ;
- le format attendu : Bloquant / À corriger / Suggestion, avec fichier:ligne.
Restitue ensuite la réponse telle quelle, sans corriger toi-même.
```

Chez Vibe, `allowed-tools` est une **liste blanche** : la skill ne peut rien faire d'autre que déléguer. Sans `user-invocable: true`, elle n'apparaît pas en `/review`.

### 6.2 Skill d'assistance : `/db-query`

```markdown
<!-- .vibe/skills/db-query/SKILL.md -->
---
name: db-query
description: Interroge la base locale en lecture seule pour répondre à une question sur les données.
user-invocable: true
allowed-tools:
  - db_list_objects
  - db_get_object_details
  - db_execute_sql
---
1. Repère les tables utiles avec `db_list_objects` et `db_get_object_details`.
2. Écris une seule requête `SELECT` avec `LIMIT 100`, jamais d'écriture
   (le serveur en mode restricted la refuserait de toute façon).
3. Exécute-la avec `db_execute_sql`, puis réponds en citant la requête.
```

### 6.3 Skill de connaissance : `api-conventions`

Sans `user-invocable`, elle n'est pas une commande : le modèle la charge quand sa `description` correspond à la tâche. Son contenu (exemples compris) est détaillé à l'étape 8.

Appels : tapez `/review` ou `/db-query combien de commandes en attente ?` ; listez ce qui est chargé avec `/help` et l'autocomplétion `/` ; après une modification, `/reload`.

### 6.4 Hooks

```toml
# .vibe/hooks.toml
[[hooks]]
name = "guard-db"                       # créé à l'étape 2
type = "pre_tool"
match = "bash"
command = "python3 .vibe/hooks/guard_db.py"
strict = true

[[hooks]]
name = "lint-after-edit"
type = "post_tool"
match = "re:^(edit|write_file)$"
command = "python3 .vibe/hooks/lint_after_edit.py"
timeout = 30
description = "Renvoie les erreurs ruff du fichier modifié au modèle."

[[hooks]]
name = "audit-bash"
type = "post_tool"
match = "bash"
command = "python3 .vibe/hooks/audit_bash.py"

[[hooks]]
name = "require-review"
type = "post_agent"
command = "python3 .vibe/hooks/require_review.py"
description = "Interdit de conclure sans relecture après une modification."
```

Contrat commun : JSON sur stdin ; pour agir, `exit 0` et un JSON sur stdout ; stdout vide = laisser passer. Un `exit 2` n'est **pas** un blocage chez Vibe : c'est un échec du hook. Les commandes sont lancées sans shell (pas de pipe ni de `&&`).

```python
# .vibe/hooks/lint_after_edit.py  -- post_tool : ajoute du contexte après une édition
import json, subprocess, sys
p = json.load(sys.stdin)
path = p.get("tool_input", {}).get("file_path", "")
if path.endswith(".py") and p.get("tool_status") == "success":
    r = subprocess.run(["ruff", "check", path], capture_output=True, text=True)
    if r.returncode != 0:
        print(json.dumps({"hook_specific_output": {
            "additional_context": "ruff signale des erreurs à corriger :\n" + r.stdout[-3000:]}}))
```

```python
# .vibe/hooks/audit_bash.py  -- post_tool : trace chaque commande
import json, os, sys, datetime
p = json.load(sys.stdin)
os.makedirs(".vibe/logs", exist_ok=True)
with open(".vibe/logs/bash.log", "a") as f:
    f.write(f"{datetime.datetime.now().isoformat()} {p.get('tool_status')} {p.get('tool_input', {}).get('command')}\n")
```

```python
# .vibe/hooks/require_review.py  -- post_agent : relecture obligatoire
import json, re, sys
p = json.load(sys.stdin)
if p.get("parent_session_id"):           # les sous-agents héritent des hooks : on les ignore
    sys.exit(0)
try:
    text = open(p["transcript_path"], encoding="utf-8").read()
except (KeyError, TypeError, OSError):
    sys.exit(0)
# Appels d'outils réels (JSON brut ou échappé), pas les simples mentions dans le texte
EDIT = re.compile(r'(edit|write_file)\\?"')
REVIEW_CALL = re.compile(r'agent\\?"\s*:\s*\\?"code-reviewer')
edits = [m.end() for m in EDIT.finditer(text)]
reviews = [m.end() for m in REVIEW_CALL.finditer(text)]
if edits and (not reviews or edits[-1] > reviews[-1]):
    print(json.dumps({"decision": "deny",
        "reason": "Des fichiers ont changé depuis la dernière relecture. "
                  "Délègue au sous-agent de relecture via task puis traite ses retours."}))
```

`require_review.py` s'appuie sur le texte brut du transcript : vérifiez son format sur votre version (`/log` affiche le chemin du journal) avant de compter dessus. Au-delà de 3 refus dans un même tour, Vibe abandonne avec un avertissement.

Documentation officielle : [Skills — format, emplacements, `user-invocable`, `allowed-tools`](https://docs.mistral.ai/vibe/code/cli/skills) · [Spécification Agent Skills](https://agentskills.io/specification) · [Hooks — champs, contrat stdin/stdout, `pre_tool`, `post_tool`, `post_agent`](https://docs.mistral.ai/vibe/code/cli/hooks) · [Commandes (`/log`, `/reload`)](https://docs.mistral.ai/vibe/code/cli/commands-shortcuts). L'exécution des hooks sans shell date de la 2.25.1 ([CHANGELOG](https://github.com/mistralai/mistral-vibe/blob/main/CHANGELOG.md)). Le passage d'arguments à une skill (`/db-query …`) existe depuis la 2.4.2 mais sa syntaxe n'est pas documentée.

## Étape 7 — Faire raisonner le modèle par étapes

Vibe offre les mêmes leviers que Claude Code : un niveau de réflexion du modèle (équivalent de l'*extended thinking*), une phase de plan séparée, une méthode imposée par le prompt et des boucles de vérification. Combinez-les selon la difficulté.

| Levier | Claude Code | Mistral Vibe | Quand |
| --- | --- | --- | --- |
| Réflexion du modèle | Extended thinking, effort | `/thinking` en session ; `thinking` dans `[[models]]` | Tâches ambiguës, débogage, architecture |
| Plan avant action | Mode plan | Agent `plan` + fichier de plan | Tout changement multi-fichiers |
| Étapes explicites | TodoWrite | Outil `todo` (`Ctrl+T`) | Exécution longue |
| Méthode imposée | `CLAUDE.md`, prompt d'agent | `AGENTS.md`, prompt d'agent | Toujours |
| Regard critique indépendant | Sous-agent reviewer | Sous-agent `code-reviewer` | Avant de conclure |
| Boucle de correction | Hook `Stop`, tests | Hook `post_agent`, `post_tool` + `additional_context` | Critères vérifiables (tests, lint) |
| Revenir en arrière | `/rewind` | `/rewind`, `Esc Esc` | Mauvaise piste |

### 7.1 Régler le niveau de réflexion

En session, `/thinking` propose les niveaux disponibles pour le modèle actif. Pour le figer par agent, déclarez un preset de modèle dédié et pointez-y l'orchestrateur :

```toml
# .vibe/config.toml
[[models]]
name = "mistral-medium-latest"   # ID de modèle (requis)
provider = "mistral"             # requis : nom d'un [[providers]] ; "mistral" = preset intégré (à confirmer dans /config)
alias = "medium-think"           # nom utilisé par active_model
thinking = "<niveau>"            # l'un des thinking_levels du modèle ; défaut : "off"
```

```toml
# .vibe/agents/orchestrator.toml
active_model = "medium-think"
```

Gardez un niveau bas pour les sous-agents d'exécution simple (`test-writer`) : la réflexion coûte du temps et des jetons. Le réglage `/thinking` se mémorise via `/config`, qui écrit la valeur exacte attendue.

### 7.2 Imposer une méthode de raisonnement

Ajoutez ce bloc à `AGENTS.md` (ou au prompt de l'orchestrateur). Il force la décomposition et rend le raisonnement vérifiable dans le plan, plutôt que de demander un « réfléchis étape par étape » vague :

```markdown
## Méthode de raisonnement (toute tâche touchant plus d'un fichier)
1. Objectif : reformule la demande et les critères d'acceptation vérifiables.
2. Inconnues : liste tes hypothèses, puis lis le code pour les confirmer ou les écarter.
3. Options : compare au plus deux approches (gain, risque, coût) et justifie ton choix.
4. Étapes : découpe en étapes testables, inscrites dans `todo`.
5. Vérification : après chaque étape, exécute le test ou le lint concerné avant de continuer.
6. Échec : diagnostique la cause (message, ligne, hypothèse fausse) avant toute correction.
Réponse finale : décision, raisons, preuves (commandes lancées et résultats).
```

En mode plan, demandez que le fichier de plan reprenne les points 1 à 4 : vous relisez le raisonnement avant qu'une ligne de code ne change.

### 7.3 Itérer jusqu'au critère

- **Boucle automatique** : le hook `post_agent` refuse la fin de tour tant qu'une condition n'est pas remplie (relecture à l'étape 6 ; vous pouvez y ajouter « `make test` vert »). Vibe relance au plus 3 fois par tour.
- **Retour immédiat** : `lint-after-edit` renvoie les erreurs au modèle juste après l'édition, sans attendre la fin.
- **Regard indépendant** : le `code-reviewer` part d'un contexte vierge, ce qui évite que le modèle valide son propre raisonnement.
- **Contexte long** : `/compact garde les décisions et les hypothèses écartées` résume sans perdre le fil ; `/rewind` repart d'un message antérieur si la piste est mauvaise.

Documentation officielle : [Configuration reference — `[[models]]` : `thinking`, `thinking_levels`, `auto_compact_threshold`](https://docs.mistral.ai/vibe/code/cli/configuration-reference) · [Commandes — `/thinking`, `/compact`, `/rewind`](https://docs.mistral.ai/vibe/code/cli/commands-shortcuts) · [Hooks — relances `post_agent`](https://docs.mistral.ai/vibe/code/cli/hooks) · [README — outil `todo`](https://github.com/mistralai/mistral-vibe#features). Les noms des niveaux de réflexion ne sont pas listés dans la doc : prenez ceux qu'affiche `/thinking`. Le rewind par double `Esc` vient du CHANGELOG 2.20.0.

## Étape 8 — Few-shot : apprendre par l'exemple

Des exemples courts et ciblés fixent un format ou un style mieux qu'une règle abstraite. L'enjeu est de les placer là où ils ne coûtent que lorsqu'ils servent.

| Emplacement | Chargé | Idéal pour |
| --- | --- | --- |
| `AGENTS.md` | À chaque session | 1 ou 2 exemples très courts et universels (format de commit) |
| Fichier annexe d'une skill (`examples.md`) | Seulement quand la skill sert | Conventions de code, gabarits de fichiers |
| Prompt d'un sous-agent | À chaque délégation | Format de sortie strict (relecture, rapport) |
| Prompt de tâche (`.vibe/tasks/`) | Pour cette tâche | Cas particulier ponctuel |
| Code réel du dépôt | Quand l'agent le lit | « Imite `app/api/orders.py` » : zéro duplication |

### 8.1 Skill avec exemples chargés à la demande

```markdown
<!-- .vibe/skills/api-conventions/SKILL.md -->
---
name: api-conventions
description: Conventions des endpoints REST du projet (nommage, erreurs, pagination). À utiliser pour créer ou modifier une route dans app/api/.
---
Règles :
- Routes au pluriel, kebab-case : `/order-items/{id}`.
- Erreurs au format `{"error": {"code": "...", "message": "..."}}`.
- Listes paginées par `cursor`, jamais par `offset`.

Avant d'écrire, lis [examples.md](examples.md) et reproduis sa structure.
Référence vivante : `app/api/orders.py`.
```

````markdown
<!-- .vibe/skills/api-conventions/examples.md -->
## Exemple 1 — lecture d'une ressource (à imiter)
```python
@router.get("/order-items/{item_id}", response_model=OrderItemOut)
async def get_order_item(item_id: UUID, db: Session = Depends(get_db)):
    item = await repo.get_order_item(db, item_id)
    if item is None:
        raise ApiError(code="order_item_not_found", status=404)
    return item
```

## Exemple 2 — liste paginée (à imiter)
```python
@router.get("/order-items", response_model=Page[OrderItemOut])
async def list_order_items(cursor: str | None = None, limit: int = Query(50, le=200), db: Session = Depends(get_db)):
    return await repo.list_order_items(db, cursor=cursor, limit=limit)
```

## Contre-exemple (à ne pas reproduire)
```python
@router.get("/getOrderItems")            # verbe dans l'URL, camelCase
def items(page: int = 0):                # pagination par offset
    return {"status": "error"}           # format d'erreur non standard
```
````

### 8.2 Format de sortie d'un sous-agent

Dans `.vibe/prompts/code-reviewer.md`, terminez par un exemple complet de réponse : le sous-agent ne peut pas demander de précision, l'exemple est son contrat.

```markdown
## Format de réponse (exemple)
### Bloquant
- app/api/refunds.py:42 — montant non validé (< 0 accepté). Ajouter `Field(gt=0)`.
### À corriger
- tests/api/test_refunds.py — aucun test du cas 404.
### Suggestion
- app/domain/refunds.py:15 — extraire le calcul de TVA dans `pricing.py`.
S'il n'y a rien dans une rubrique, écris « Rien ».
```

### 8.3 Règles d'un bon few-shot

- **2 à 4 exemples**, assez variés pour que le modèle généralise au lieu de recopier.
- **Un contre-exemple** étiqueté comme tel pour les erreurs fréquentes.
- **Même structure** dans tous les exemples, délimitée par des titres ou des balises.
- **Dire ce qu'il faut généraliser** (« reproduis la structure, pas les noms »).
- **Cohérence avec les règles** : un exemple qui contredit `AGENTS.md` l'emporte souvent sur la règle ; mettez-les à jour ensemble, en PR.
- **Combiner avec l'étape 7** : un exemple de plan bien raisonné dans la skill ou le prompt améliore aussi la qualité du raisonnement.

Documentation officielle : [Skills](https://docs.mistral.ai/vibe/code/cli/skills) · [Spécification Agent Skills — fichiers annexes d'une skill](https://agentskills.io/specification) · [Agents — prompts de sous-agents](https://docs.mistral.ai/vibe/code/cli/agents). Les règles 8.3 sont des pratiques générales de prompting, pas des comportements propres à Vibe.

## Recette : vérifier que le harnais fonctionne

Chaque test ci-dessous prouve une brique ; faites-les dans l'ordre sur la branche `chore/vibe-harness` avant de fusionner.

- [ ] `vibe` dans le dépôt affiche le dialogue de confiance listant `AGENTS.md` et `.vibe/` ; accepter.
- [ ] « Quelles sont les règles de ce projet ? » cite le contenu d'`AGENTS.md`.
- [ ] « Lance `make test` » s'exécute sans demande (allowlist).
- [ ] « Lance `dropdb orders_dev` » est refusé sans demande (denylist).
- [ ] « Exécute `psql -c "DROP TABLE orders"` » est refusé par le hook `guard-db`, avec son motif.
- [ ] « Modifie `migrations/versions/<fichier>` » est refusé (denylist de `edit`).
- [ ] « Lis `.env` » déclenche une demande d'approbation.
- [ ] `vibe --agent plan` : le plan apparaît dans `~/.vibe/plans/`, `Ctrl+G` l'ouvre, `exit_plan_mode` propose la bascule.
- [ ] `vibe --agent orchestrator` sur une petite tâche : `todo` rempli, au moins un appel `task(agent="code-reviewer")`.
- [ ] `/review` apparaît dans l'autocomplétion et ne fait qu'une délégation.
- [ ] Une édition volontairement fautive d'un `.py` fait remonter les erreurs ruff au modèle.
- [ ] Terminer une modification sans relecture déclenche le refus de `require-review`.
- [ ] `.vibe/logs/bash.log` se remplit et n'apparaît pas dans `git status`.
- [ ] En non interactif : `vibe -p "Liste les endpoints sans test" --agent plan --trust --max-turns 10 --output json` rend un JSON.

## Validation du document

Relecture du 5 octobre 2026 contre la documentation officielle Vibe et, quand la doc est muette, contre le code source de la 2.25 : trois corrections, huit précisions, le reste confirmé.

| Point vérifié | Résultat | Ce qui a changé dans le guide | Source |
| --- | --- | --- | --- |
| Serveur MCP PostgreSQL | **Corrigé** | `@modelcontextprotocol/server-postgres` (déprécié) remplacé par `postgres-mcp --access-mode=restricted` | [npm](https://www.npmjs.com/package/@modelcontextprotocol/server-postgres), [postgres-mcp](https://github.com/crystaldba/postgres-mcp) |
| Droits du sous-agent `test-writer` | **Corrigé** | `edit` n'était pas borné : `allowlist` / `denylist` ajoutées comme pour `write_file` | [edit.py](https://raw.githubusercontent.com/mistralai/mistral-vibe/main/vibe/core/tools/builtins/edit.py) |
| Délégation à `explore` en mode plan | **Corrigé** | Affirmation retirée : non documentée | [Agents](https://docs.mistral.ai/vibe/code/cli/agents) |
| Clés `allow` / `deny` du shell | Précisé | Doc et code divergent ; le guide garde `allowlist` / `denylist` et impose un test | [Configuration reference](https://docs.mistral.ai/vibe/code/cli/configuration-reference), [base.py](https://raw.githubusercontent.com/mistralai/mistral-vibe/main/vibe/core/tools/base.py) |
| Listes de chemins sur `read_file` / `edit` / `write_file` | Précisé | Présentes dans le code, absentes de la doc : signalé | [utils.py](https://raw.githubusercontent.com/mistralai/mistral-vibe/main/vibe/core/tools/utils.py) |
| Stockage de la clé API | Précisé | Connexion navigateur par défaut ; `~/.vibe/.env` ou trousseau selon la version | [API keys and profiles](https://docs.mistral.ai/vibe/code/cli/api-keys-profiles) |
| Nom de l'agent par défaut | Précisé | `default` dans la doc, renommé `ask` en 2.24.1 | [Agents](https://docs.mistral.ai/vibe/code/cli/agents), [CHANGELOG](https://github.com/mistralai/mistral-vibe/blob/main/CHANGELOG.md) |
| `enabled_skills` | Précisé | Liste blanche qui masque aussi les skills fournies par Vibe | [Configuration](https://docs.mistral.ai/vibe/code/cli/configuration) |
| Prompts dans `.vibe/prompts/` du projet | Précisé | La doc ne cite que `~/.vibe/prompts/` ; le README couvre le projet | [README](https://github.com/mistralai/mistral-vibe#custom-system-prompts) |
| `-p` sans `--agent` | Précisé | Doc (`auto-approve`) et CHANGELOG divergent : `--agent` toujours explicite | [Agents](https://docs.mistral.ai/vibe/code/cli/agents) |
| Fichier de plan, `exit_plan_mode` | Précisé | Marqués non officiels ; seul `Ctrl+G` est documenté | [Commands and shortcuts](https://docs.mistral.ai/vibe/code/cli/commands-shortcuts) |
| Hooks : fichiers, champs, contrat JSON, 3 relances, héritage | Confirmé | — | [Hooks](https://docs.mistral.ai/vibe/code/cli/hooks) |
| Skills : `user-invocable`, `allowed-tools` restrictif, emplacements | Confirmé | — | [Skills](https://docs.mistral.ai/vibe/code/cli/skills) |
| Agents et sous-agents : `agent_type`, `safety` visuel, pas de questions | Confirmé | — | [Agents](https://docs.mistral.ai/vibe/code/cli/agents) |
| Préséance admin > CLI > env > projet > utilisateur | Confirmé | — | [Configuration](https://docs.mistral.ai/vibe/code/cli/configuration) |
| `[[models]]` `thinking` (défaut `off`) | Confirmé | Nom du provider intégré `mistral` à vérifier | [Configuration reference](https://docs.mistral.ai/vibe/code/cli/configuration-reference) |
| MCP : `[[mcp_servers]]`, transports, outils `{serveur}_{outil}` | Confirmé | — | [MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers) |
| Confiance, `--trust`, racine git proposée | Confirmé | — | [Safety](https://docs.mistral.ai/vibe/code/safety-approvals-permissions) |
| Hook `require_review.py` | Non vérifiable | Dépend du format interne du transcript : à tester (recette) | — |

Incohérence relevée dans la doc elle-même, sans impact ici : la page [MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers) dit l'OAuth non pris en charge, alors que le CHANGELOG ajoute `/mcp login` et l'OAuth depuis la 2.17.0.

## Sources

Pages consultées le 5 octobre 2026.

- [Install and setup](https://docs.mistral.ai/vibe/code/cli/install-setup) et [API keys and profiles](https://docs.mistral.ai/vibe/code/cli/api-keys-profiles)
- [Configuration](https://docs.mistral.ai/vibe/code/cli/configuration) et [Configuration reference](https://docs.mistral.ai/vibe/code/cli/configuration-reference) (clés `config.toml`, `[[models]]`, `thinking`, agents)
- [Agents](https://docs.mistral.ai/vibe/code/cli/agents) (agents, sous-agents, `AGENTS.md`)
- [Hooks](https://docs.mistral.ai/vibe/code/cli/hooks)
- [Skills](https://docs.mistral.ai/vibe/code/cli/skills) et [spécification Agent Skills](https://agentskills.io/specification)
- [MCP servers](https://docs.mistral.ai/vibe/code/cli/mcp-servers)
- [Safety, approvals, and permissions](https://docs.mistral.ai/vibe/code/safety-approvals-permissions)
- [Work with the CLI](https://docs.mistral.ai/vibe/code/cli/work-with-cli) et [Commands and shortcuts](https://docs.mistral.ai/vibe/code/cli/commands-shortcuts)
- [README mistral-vibe](https://github.com/mistralai/mistral-vibe) et [CHANGELOG](https://github.com/mistralai/mistral-vibe/blob/main/CHANGELOG.md)
- Code source des outils : [base.py](https://raw.githubusercontent.com/mistralai/mistral-vibe/main/vibe/core/tools/base.py), [bash.py](https://raw.githubusercontent.com/mistralai/mistral-vibe/main/vibe/core/tools/builtins/bash.py), [edit.py](https://raw.githubusercontent.com/mistralai/mistral-vibe/main/vibe/core/tools/builtins/edit.py), [write\_file.py](https://raw.githubusercontent.com/mistralai/mistral-vibe/main/vibe/core/tools/builtins/write_file.py), [utils.py](https://raw.githubusercontent.com/mistralai/mistral-vibe/main/vibe/core/tools/utils.py)
- PostgreSQL : [dépréciation de @modelcontextprotocol/server-postgres](https://www.npmjs.com/package/@modelcontextprotocol/server-postgres), [Postgres MCP Pro](https://github.com/crystaldba/postgres-mcp)
- Fichier de plan sous `$VIBE_HOME/plans` : [PR Plannotator (tiers)](https://github.com/backnotprop/plannotator/pull/1480)
