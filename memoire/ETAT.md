# État d'avancement

Dernière mise à jour : 2026-10-09 (étape 2 réalisée, D-14 ; recettes GLM et étape 2 à faire).

| Étape | Commande | Statut | Livrables |
| --- | --- | --- | --- |
| 0. Outillage Claude Code | — | Terminée | `CLAUDE.md`, `.claude/`, `memoire/`, `reference/` |
| 1. Squelette générique | `/etape-1` | Recette WSL 2026-10-09 jugée suffisante (points 0-8) ; correctifs D-11 appliqués | `projet-mistral-vibe/` (AGENTS.md, README.md, .gitignore, .vibe/, tests_harnais/), `Test_Etape_1/` |
| 2. Refacto Robot Framework | `/etape-2` | Réalisée 2026-10-09, vérifiée (harness-verifier), recette WSL à faire | skills `refacto-test` et `rf-conventions`, sous-agents `rf-refactorer` / `rf-reviewer`, hooks `require_green_test.py`, `guard_subagent_write.py`, `resume_resultat.py`, `Test_Etape_2/README.md` |
| 3. Historisation | `/etape-3` | À faire | skill `historiser-refacto`, `historisation_refacto/` |

## Livrables de l'étape 1 (référence Vibe 2.26.0, D-10)
- `AGENTS.md` : lignes directrices, plan validé avant toute écriture, agent `plan` sans écriture, fichiers modifiés uniquement par l'outil d'édition (jamais par le shell), refus définitif, outil de vérification manquant signalé, méthode de raisonnement, preuve par exécution.
- `.vibe/config.toml` : `default_agent = "plan"`, `active_model = "glm-5-3"` + `[[models]]` GLM 5.3 (D-12 ; avant : `mistral-medium-3.5`), `[compaction_model]` Small 4, denylist bash (défauts + ajouts), fichiers du harnais protégés en écriture (le plan de l'agent `plan` va dans le scratchpad de session).
- `.vibe/agents/orchestrator.toml` (`active_model = "glm-5-3"`), `reviewer.toml` (`enabled_tools = ["read_file", "bash"]`) ; `.vibe/prompts/` = traduction française de `cli.md` v2.26.0 (D-11) + « Ajouts du harnais » (relecture unique par `spawn`/`wait`, points jugés, corrections non bloquantes après accord).
- `.vibe/hooks.toml` + `hooks/audit_bash.py` ; `tests_harnais/test_audit_bash.py` (suivi depuis 920b754) : 7 tests verts (Python 3.13 Windows, revérifié le 2026-10-09).
- `Test_Etape_1/` : `projet_exemple/tests/` recréé (4 tests + `conftest.py`) ; `preparer.sh` → 11 tests verts.
- `README.md` et `Test_Etape_1/README.md` : venv avec pytest activé avant `vibe`, recette 2.26.0 (points 1-11, 7a bis, 7e, bonus).

## Livrables de l'étape 2 (D-14)
- `/refacto-test <fichier.robot>::<test> <consignes>` dans `orchestrator` : référence `results/refacto/avant`, plan par `ask_user_question`, `.refacto/courant.json`, `spawn`/`wait` de `rf-refactorer-<n>` (3 au plus), validation `results/refacto/apres` + `resume_resultat.py`, relecture unique `rf-reviewer-1`, fin `terminee` / `arretee`.
- Hooks : `require-green-test` (`post_agent`), `guard-subagent-write` (`pre_tool`, strict) ; 50 tests pytest verts (Python 3.13 Windows, venv avec RF 7.1 ; fixtures `output.xml` générées par RF 7.1).
- `AGENTS.md` : un nouvel essai après échec d'édition ; section Robot Framework. `config.toml` : allowlist bash = 44 défauts + `robot` + `resume_resultat.py`.

## Prochaine action
1. Commit des étapes 1 (D-11, D-12) et 2 (D-14), avec accord.
2. Recette ciblée GLM (`Test_Etape_1/README.md`), puis recette étape 2 (`Test_Etape_2/README.md`) sur le dépôt cible.
3. Reporter les points « À vérifier » (approbation dans un sous-agent, permission de `spawn`, `post_agent` d'un enfant, `tool_input` réel de `search_replace`, bash des sous-agents) dans `VIBE_FAITS_VERIFIES.md`.
4. Puis `/etape-3` dans une session neuve.

## Recette du 2026-10-08 (Vibe 2.26.0, harnais avant correctifs)
- OK : confiance, règles d'`AGENTS.md`, `/thinking` = high, `todo`, écriture par l'outil d'édition avec approbation dans `orchestrator`.
- Écarts expliqués par D-10 : pas d'`exit_plan_mode` ni de `task` sous le Unified Harness ; contournement par bash dans `plan` (bash en `ask`) ; vérification factice (pytest absent, tests du banc manquants).

## Questions ouvertes
- Outils web exposés par Vibe (`web_search`, `news_search`, `finance_search`, `weather_search`, `open_url`…) : les désactiver pour les agents du harnais ?
- Le modèle oublie `spawn` sans demande explicite : à revérifier après D-11.
- Champs stdin réels des hooks (`session_id`, `transcript_path` dossier, `duration_ms`) : utile à l'étape 3 (point 8).
- Hook depuis un sous-dossier : `workspace.cwd` = dossier de lancement ? si gênant, `git rev-parse --show-toplevel` (point 9).
- Prompt de l'agent `plan` : `cli` ou variante `cli_2026-*` (GrowthBook) (point 6).
- Bash dans le sous-agent `reviewer` (bonus).
- Signatures Browser / Selenium / Requests des exemples `rf-conventions` : validées seulement contre des bibliothèques simulées (recette).
- `robot` sans demande dans l'agent `plan` aussi : acceptable ? (exécute réellement le test).
