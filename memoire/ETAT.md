# État d'avancement

Dernière mise à jour : 2026-10-08 (recette étape 1 en cours).

| Étape | Commande | Statut | Livrables |
| --- | --- | --- | --- |
| 0. Outillage Claude Code | — | Terminée | `CLAUDE.md`, `.claude/`, `memoire/`, `reference/` |
| 1. Squelette générique | `/etape-1` | Construite ; recette WSL en cours (points 1-5 faits, écarts relevés) | `projet-mistral-vibe/` (AGENTS.md, README.md, .gitignore, .vibe/, tests_harnais/) |
| 2. Refacto Robot Framework | `/etape-2` | À faire | skill `refacto-test`, sous-agents RF, hook de validation |
| 3. Historisation | `/etape-3` | À faire | skill `historiser-refacto`, `historisation_refacto/` |

## Livrables de l'étape 1
- `AGENTS.md` : lignes directrices, plan validé avant toute écriture, méthode de raisonnement, preuve par exécution.
- `.vibe/config.toml` : `default_agent = "plan"`, `active_model = "mistral-medium-3.5"`, `[compaction_model]` Small 4, denylist bash (défauts + ajouts), `.vibe/` protégé en écriture.
- `.vibe/agents/orchestrator.toml`, `reviewer.toml` ; `.vibe/prompts/` = `cli.md` v2.25.8 (copie exacte) + « Ajouts du harnais ».
- `.vibe/hooks.toml` + `hooks/audit_bash.py` ; `tests_harnais/test_audit_bash.py` : 6 tests verts (Python 3.13 Windows).
- `README.md` : installation, import, flux, recette en 11 points.
- Vérification `harness-verifier` : 5 non-conformités corrigées puis revérifiées.

## Prochaine action
1. Nouvelle session avec `PROMPT_REPRISE_ETAPE_1.md` (racine) : trancher la version (2.25.8 ou 2.26.0), finir la recette (points 6 à 11), corriger le harnais.
2. Puis lancer `/etape-2` dans une session neuve.

## Recette du 2026-10-08 (Vibe 2.26.0 installé, référence 2.25.8)
- OK : confiance, règles d'`AGENTS.md`, `/thinking` = high, `todo`, écriture par l'outil d'édition avec approbation dans `orchestrator`.
- Écarts : pas d'`exit_plan_mode` (question en texte libre) ; l'agent `plan` contourne ses refus d'écriture par bash ; pas de `task(reviewer)` ; vérification factice quand pytest manque.
- Détail et correctifs envisagés : `PROMPT_REPRISE_ETAPE_1.md`, `VIBE_FAITS_VERIFIES.md` (section « Recette 2026-10-08 »).

## Recettes manuelles en attente
- Étape 1 : `projet-mistral-vibe/README.md`, section « Recette » (11 points).

## Questions ouvertes
- **Version de référence** : 2.25.8 (CLAUDE.md) ou 2.26.0 (installée par l'utilisateur) ? Bloquant pour la suite de la recette.
- Nom de l'outil shell vu par les hooks sous le nouveau moteur (`bash` ou `file_system.bash`) : recette 1, point 8.
- Hook introuvable si `vibe` est lancé depuis un sous-dossier : recette 1, point 9 ; si gênant, passer par `git rev-parse --show-toplevel` (shell disponible depuis 2.25.5).
- Outils réellement disponibles pour `reviewer` (`grep`) sous le nouveau moteur : recette 1, point 6.
- Prompt système du nouveau moteur = `cli.md` ? recette 1, point 6.
- Contenu réel du stdin des hooks (`session_id`, `transcript_path`) : recette 1, utile à l'étape 3.
- Effet réel d'`allowed-tools` dans une skill (restriction ou pré-approbation) : étape 2.
- Bibliothèques RF du dépôt cible et existence d'une suite d'exemple (étape 2).
- Nombre maximal d'itérations de refacto (étape 2).
