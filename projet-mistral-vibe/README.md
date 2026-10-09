# Harnais Mistral Vibe

Harnais générique pour [Mistral Vibe](https://docs.mistral.ai/vibe/code) 2.26.0 (moteur Unified Harness) : règles de projet (`AGENTS.md`), configuration, agents, prompts et hooks (`.vibe/`). Il est destiné à être copié à la racine d'un dépôt de tests Robot Framework ; tous ses chemins sont relatifs.

## Contenu

| Élément | Rôle |
| --- | --- |
| `AGENTS.md` | Règles du projet, ajoutées au prompt système de chaque session : plan avant écriture, refus définitifs, preuve par exécution |
| `.vibe/config.toml` | Agent de démarrage `plan`, modèle, modèle de compaction, permissions (allowlist et denylist shell, fichiers du harnais sous `.vibe/` protégés en écriture) |
| `.vibe/agents/orchestrator.toml` | Agent principal : planifie, fait valider, exécute, fait relire par `spawn` de `reviewer` ; mène les refactos RF |
| `.vibe/agents/reviewer.toml` | Sous-agent de relecture, lecture seule (`read_file`, `bash`) |
| `.vibe/agents/rf-refactorer.toml` | Sous-agent de refacto d'un test RF : n'écrit que des `.robot` / `.resource`, ne lance pas `robot` |
| `.vibe/agents/rf-reviewer.toml` | Sous-agent de relecture d'une refacto RF, lecture seule ; remplace `reviewer` pendant une refacto |
| `.vibe/prompts/*.md` | Prompts système : traduction française du prompt par défaut de Vibe (`vibe/core/prompts/cli.md` v2.26.0) + « Ajouts du harnais ». Si Vibe modifie `cli.md`, reprendre la traduction à la main dans les quatre fichiers |
| `.vibe/hooks.toml` | Déclare les trois hooks ci-dessous |
| `.vibe/hooks/audit_bash.py` | `post_tool` : trace chaque commande shell dans `.vibe/logs/bash.log` |
| `.vibe/hooks/guard_subagent_write.py` | `pre_tool` strict : refuse à un sous-agent toute écriture hors `.robot` / `.resource` |
| `.vibe/hooks/require_green_test.py` | `post_agent` : refuse la fin de tour tant que le test refactorisé n'est pas PASS et à jour |
| `.vibe/hooks/resume_resultat.py` | Résumé court d'un `output.xml` (statut, keyword en échec, message), pour l'agent et le hook |
| `.vibe/skills/refacto-test/` | Skill `/refacto-test` : déroulé de la refacto d'un test (commandes, messages de `spawn`) |
| `.vibe/skills/rf-conventions/` | Conventions RF 7.1 et exemples, lues par l'orchestrateur et par les sous-agents RF |
| `tests_harnais/` | Tests pytest des hooks (et leurs fixtures `output.xml`) |

## Fonctionnement

Le harnais impose un cycle : plan validé, exécution pas à pas, relecture, preuve par exécution des tests.

```
vibe ──► plan ──(plan validé, Shift+Tab)──► orchestrator ──spawn / wait──► reviewer
         lit, propose                       todo, question,               relit, classe :
         n'écrit rien                       édite, lance pytest           Bloquant / À corriger / Suggestion
```

1. `plan` (agent intégré de Vibe, au démarrage) lit le code et propose un plan. Il n'écrit rien, sauf son brouillon de session.
2. `orchestrator` découpe le travail (`todo`), demande confirmation (`ask_user_question`), modifie les fichiers avec l'outil d'édition (chaque écriture est soumise à approbation) et lance réellement les tests.
3. `reviewer` est lancé une fois par tâche. L'orchestrateur prend position sur chaque point. Les points « À corriger » et « Suggestion » ne sont appliqués qu'après accord ; une nouvelle relecture n'a lieu qu'après la correction d'un Bloquant.

Garde-fous, du plus souple au plus strict :
- **Consignes** (`AGENTS.md`, prompts) : suivies par le modèle, sans garantie.
- **Permissions Vibe** (`config.toml`) :
  - commandes dangereuses refusées (`rm -rf`, `git push --force`, éditeurs interactifs) ;
  - fichiers du harnais protégés contre l'outil d'édition ;
  - le reste du shell demande approbation, sauf les commandes de lecture autorisées par défaut (`git status`, `ls`…), `robot` et `python3 .vibe/hooks/resume_resultat.py`.

  La denylist compare des préfixes : `git push origin x --force` passe ce filtre, mais reste soumis à approbation.
- **Trace** : chaque commande shell est journalisée par le hook.

Modèles (GLM 5.3, hébergé par Mistral, déclaré par `[[models]]` dans `.vibe/config.toml`) :

| Agent | Modèle | Réflexion (`thinking`) |
| --- | --- | --- |
| `plan`, `orchestrator` | GLM 5.3 (alias `glm-5-3`, ID `zai-glm-5-3`) | `max` ; l'API reçoit `high` (Vibe 2.26.0 ne transmet pas `max`) |
| `reviewer` | Hérité de l'agent qui le lance (GLM 5.3) | Hérité |
| Compaction | Mistral Small 4 (`mistral-small-latest`) | `off` |

GLM 5.3 ne lit que du texte : une image est décrite par Medium 3.5, modèle de vision de repli du provider.

## Prérequis (WSL / Linux)

```bash
uv tool install mistral-vibe==2.26.0
vibe --setup          # connexion navigateur ou clé API
vibe --version        # doit afficher 2.26.0
python3 --version     # 3.11 ou plus, utilisé par les hooks
```

Clé : `MISTRAL_API_KEY` suffit (GLM 5.3 passe par le provider `mistral`), à condition que le compte ait accès à GLM 5.3. Ne jamais mettre de clé dans le dépôt.

Ne pas utiliser `/thinking low` avec GLM : Vibe envoie alors `reasoning_effort = "none"`, que GLM refuse.

pytest, Robot Framework 7.1 et les bibliothèques du dépôt doivent être disponibles dans le shell qui lance `vibe` : sinon l'agent ne peut pas prouver ses changements. À la racine du dépôt, une fois :

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install pytest robotframework==7.1
pip install <bibliothèques du dépôt>   # ex. robotframework-browser, robotframework-seleniumlibrary, robotframework-requests
rfbrowser init                         # seulement avec Browser : installe ses navigateurs
```

Puis, avant chaque session : `. .venv/bin/activate`.

## Repli vers Medium 3.5

1. Remettre `active_model = "mistral-medium-3.5"` dans `.vibe/config.toml` et dans `.vibe/agents/orchestrator.toml` (l'entrée `[[models]]` de GLM peut rester).
2. Lancer une session neuve.

Ne pas passer par `/model` : il écrit `active_model` dans la config utilisateur (`~/.vibe/config.toml`), et le profil d'agent `orchestrator` l'emporte de toute façon.

## Importer le harnais dans un dépôt

1. Copier `AGENTS.md` et `.vibe/` à la racine du dépôt ; ajouter les entrées de `.gitignore` au `.gitignore` du dépôt.
2. Compléter la section « Projet » d'`AGENTS.md`.
3. Lancer `vibe` à la racine et accepter la confiance du dossier : sans elle, la configuration projet est ignorée.
4. Après toute modification du harnais en cours de session : `/reload`.

## Flux de travail

Lancer `vibe` depuis la racine du dépôt, venv activé : la commande du hook est relative au répertoire de lancement.

`plan` → plan en texte → `Shift+Tab` vers `orchestrator` → validation par `ask_user_question` → exécution → relecture par `spawn` de `reviewer` → vérification → conclusion.

1. `vibe` démarre sur l'agent `plan` : il lit le code et rédige un plan (en texte, et dans le scratchpad de la session), sans rien écrire d'autre. Sous le moteur 2.26.0, l'outil `exit_plan_mode` n'est pas proposé : l'agent rend la main en texte.
2. `Shift+Tab` jusqu'à `orchestrator` (ou relancer `vibe --agent orchestrator`), puis « exécute le plan ».
3. L'orchestrateur remplit `todo`, demande validation par `ask_user_question`, exécute étape par étape, lance `reviewer` par l'outil `spawn` puis attend son retour par `wait`, vérifie par les tests et conclut.

Repli non retenu : `vibe --legacy-harness` rétablit l'ancien moteur (`task`, `exit_plan_mode`) ; le harnais n'est ni conçu ni testé pour ce mode.

En mode non interactif (`-p`), passer toujours `--agent` et `--trust` ; `ask_user_question` y est désactivé.

## Refacto d'un test

Dans l'agent `orchestrator`, depuis la racine du dépôt, venv activé :

```text
/refacto-test tests/panier.robot::Total Du Panier Avec Remise passer en syntaxe RF 7
```

Flux : exécution de référence (`results/refacto/avant`) → plan soumis par `ask_user_question` → `.refacto/courant.json` à `en_cours` → `rf-refactorer` (`spawn` / `wait`) → test rejoué (`results/refacto/apres`) → au premier test vert, relecture unique par `rf-reviewer` → nouvelle itération seulement sur un Bloquant accepté (3 itérations au plus) → `courant.json` à `terminee` ou `arretee` → conclusion.

- Validation : `robot --test` réellement exécuté et PASS (pas de `--dryrun`), lu dans `output.xml` par `resume_resultat.py` (un SKIP rend aussi le code 0).
- Garde-fous : `rf-refactorer` ne peut écrire que des `.robot` / `.resource` (hook `guard-subagent-write`) ; l'orchestrateur ne peut pas finir son tour sur un test non vert tant que la refacto est `en_cours` ou `terminee` (hook `require-green-test`).
- Limite : un appel bash dure 300 s au plus. Un test plus long ne peut pas être validé par l'agent : il le signale et s'arrête.
- Réinitialiser : supprimer `.refacto/` (et `results/refacto/` si besoin). Le hook ne contrôle plus rien sans `courant.json`.
- Coût et durée d'une refacto : à relever par `/status` en fin de session (sous-agents sur le modèle de l'orchestrateur, GLM 5.3).

## Tests des hooks

```bash
. .venv/bin/activate
python3 -m pytest tests_harnais -q   # 50 tests verts attendus
```

## Recette (à exécuter sous WSL)

Dans un dépôt git de test contenant le harnais, venv avec pytest activé. Noter le résultat de chaque point : il alimente `memoire/VIBE_FAITS_VERIFIES.md`.

Points 7a, 7b, 7d et 7e : préciser dans la demande « je teste les permissions, appelle réellement l'outil ». Sinon le modèle refuse de lui-même, sans exercer la permission.

- [ ] 1. `vibe` affiche le dialogue de confiance listant `AGENTS.md` et `.vibe/` ; accepter.
- [ ] 2. « Quelles sont les règles de ce projet ? » : la réponse cite `AGENTS.md`.
- [ ] 3. La session démarre sur l'agent `plan`. Demander une petite modification : un plan est proposé sans aucune écriture hors du scratchpad ; aucune tentative de contournement par bash (`cat >`, `python3 -c`, `sed -i`…) ; une commande `bash` hors liste déclenche une demande. `exit_plan_mode` n'est pas attendu : l'agent invite à passer à `orchestrator`. `Shift+Tab` atteint `orchestrator`, qui voit le plan.
- [ ] 4. `vibe --agent orchestrator` sur une petite tâche : `todo` rempli ; `ask_user_question` avant toute écriture ; appel `spawn` de `reviewer` puis `wait` (noter le nom d'outil affiché et s'il demande approbation) ; retour au format Bloquant / À corriger / Suggestion ; tests réellement exécutés et verts (sortie pytest visible).
- [ ] 5. `/thinking` : relever les niveaux proposés et le niveau actif (attendu : `max`).
- [ ] 6. `/log`, puis explorer le dossier de session : modèle effectif de l'orchestrateur et de `reviewer` (attendu : celui de la session) ; présence de « Ajouts du harnais » dans le prompt système de l'orchestrateur et du relecteur ; outils appelés ; outils réellement disponibles pour `reviewer`. Relever si l'agent `plan` charge le prompt `cli` ou une variante `cli_2026-*`.
- [ ] 7a. « Modifie `.vibe/config.toml` » est refusé sans question.
- [ ] 7a bis. L'agent `plan` écrit son plan dans le scratchpad de la session (`<dossier /log>/scratchpad/`), pas dans `~/.vibe/plans/`.
- [ ] 7b. « Lance `git push --force` » et « Lance `vim` » sont refusés sans question.
- [ ] 7c. « Lance `git status` » et « Lance `ls` » s'exécutent sans question.
- [ ] 7d. « Écris dans `.vibe/x` avec bash » déclenche une demande (refuser) ; l'agent ne contourne pas le refus.
- [ ] 7e. « Crée `.vibe/x` avec l'outil d'écriture » : limite connue, la denylist ne couvre que les sous-dossiers et fichiers du harnais ; noter si l'écriture est demandée ou passe.
- [ ] 8. `.vibe/logs/bash.log` contient une ligne par commande, avec `file_system.bash` en 2e colonne ; `git status` ne l'affiche pas. Puis capturer le stdin brut d'un hook : ajouter temporairement à `.vibe/hooks.toml` un hook `post_tool`, `match = "bash"`, `command = "cat > /tmp/vibe_hook_stdin.json"`, relancer `vibe`, lancer une commande, et relever dans `/tmp/vibe_hook_stdin.json` `session_id`, `parent_session_id`, `transcript_path` (dossier ou fichier ?) et `duration_ms`. Retirer le hook ensuite.
- [ ] 9. Lancer `vibe` depuis un sous-dossier du dépôt, exécuter une commande : échec probable du hook (`.vibe/hooks/audit_bash.py` introuvable depuis ce répertoire) ; noter le message affiché.
- [ ] 10. `/compact` fonctionne (modèle de compaction Small 4).
- [ ] 11. `python3 --version` (3.11) puis `python3 -m pytest tests_harnais -q` depuis la racine du harnais : 50 tests verts (7 à l'étape 1).
- [ ] Bonus. Dans le sous-agent `reviewer` : `git diff` et `grep -n` passent-ils sans question ? Une commande hors allowlist (ex. `touch x`) déclenche-t-elle une demande, un refus, ou passe-t-elle ?
