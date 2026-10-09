---
name: etape-1
description: Étape 1 - crée le squelette générique du harnais Mistral Vibe dans projet-mistral-vibe/ (AGENTS.md, .vibe/, orchestrateur, modèles par agent, hooks de base).
disable-model-invocation: true
argument-hint: "[consignes complémentaires]"
---

# Étape 1 — Squelette générique `projet-mistral-vibe/`

Consignes complémentaires de l'utilisateur : $ARGUMENTS

## Prérequis
- `memoire/ETAT.md` indique l'étape 0 terminée et l'étape 1 non commencée. Sinon : arrêter et demander.
- `projet-mistral-vibe/` n'existe pas, ou l'utilisateur confirme qu'il faut le reprendre.

## Lectures obligatoires
`memoire/DECISIONS.md`, `memoire/VIBE_FAITS_VERIFIES.md`, `reference/guide-harnais-vibe.md` (étapes 1 à 8 et recette), `reference/karpathy_method.md`.

## Phase A — Plan (mode plan, rien n'est écrit)

A1. Vérifier les faits utiles à l'étape → `vibe-harness-expert`.
Lui demander de confirmer en 2.26.0 (Unified Harness, D-10), avec source : clés de `config.toml` utilisées (`default_agent`, `active_model`, `compaction_model`, `[[models]]` et `thinking`, `enabled_skills`, `[tools.*]` avec `permission`/`allowlist`/`denylist`/`sensitive_patterns`), clés d'un fichier d'agent (`agent_type`, `active_model`, `system_prompt_id`, `enabled_tools`, `safety`), frontmatter de skill (`user-invocable`, `allowed-tools`, clé « explicit-only » ajoutée en 2.25.5), contrat des hooks (champs stdin, passage par un shell depuis 2.25.5), agent `plan`, outils réellement proposés au modèle (`exit_plan_mode`, `task` et `grep` ne le sont pas ; sous-agents par `spawn`/`wait`), `ask_user_question`, chargement d'`AGENTS.md`, nom du provider intégré.
→ vérif : chaque point a un statut et une URL ; `VIBE_FAITS_VERIFIES.md` sera mis à jour en phase C.

A2. Revérifier la grille modèle / agent de `memoire/DECISIONS.md` (D-07) → `vibe-harness-expert`.
Modèles encore actifs (https://docs.mistral.ai/getting-started/models/models_overview/), IDs exacts, `active_model` dans un fichier d'agent et de sous-agent, valeur de `thinking` attendue (noms des niveaux non documentés : prévoir le relevé via `/thinking` en recette).
→ vérif : grille confirmée ou écarts listés.

A3. Rédiger le plan et le soumettre (ExitPlanMode). Il contient :
- l'arborescence cible ci-dessous ;
- la grille modèle / agent retenue et le repli si un sous-agent ne peut pas avoir son propre modèle ;
- les questions encore ouvertes (`memoire/ETAT.md`).

Arborescence cible (générique, aucun élément Robot Framework à ce stade) :
```text
projet-mistral-vibe/
├── AGENTS.md
├── README.md                    # installation WSL, import dans un dépôt RF, flux de travail
├── .gitignore                   # .vibe/logs/, .env, .env.*
├── .vibe/
│   ├── config.toml              # default_agent = "plan", [[models]], compaction_model, permissions
│   ├── hooks.toml
│   ├── hooks/audit_bash.py      # post_tool : trace les commandes dans .vibe/logs/bash.log
│   ├── agents/
│   │   ├── orchestrator.toml    # agent_type = "agent", modèle avec réflexion haute
│   │   └── reviewer.toml        # agent_type = "subagent", relecture générique
│   ├── prompts/
│   │   ├── orchestrator.md
│   │   └── reviewer.md
│   ├── skills/                  # vide à cette étape
│   └── logs/
└── tests_harnais/               # tests pytest des hooks
```

## Phase B — Réalisation (après validation)

B1. `AGENTS.md` → `vibe-harness-expert`.
Contenu : objet du dépôt (harnais générique, à compléter par le dépôt hôte), version min Vibe 2.26.0, Python 3.11, environnement WSL ; lignes directrices de `reference/karpathy_method.md` intégrées et complétées par :
- toute nouvelle demande commence par un plan soumis à validation, aucune écriture avant accord ;
- méthode de raisonnement (guide, étape 7.2) ;
- critères de réussite vérifiables et preuve par exécution ;
- arrêt et question en cas d'ambiguïté ;
- réponses en français, succinctes.
Court : les procédures longues iront dans des skills.
→ vérif : moins d'une page, aucune règle en double avec les prompts.

B2. `.vibe/config.toml` → `vibe-harness-expert`.
`default_agent = "plan"` ; presets `[[models]]` de la grille ; `active_model` global = preset de l'agent `plan` ; `compaction_model` ; `[tools.bash]` avec allowlist de lecture (`git status`, `git diff`, `git log`) et denylist (`git push --force`, `rm -rf`) ; `[tools.edit]` et `[tools.write_file]` avec `denylist = ["*/.vibe/*"]` ; `enabled_skills` laissé absent tant qu'il n'y a pas de skill.
→ vérif : `tomllib` charge le fichier.

B3. Orchestrateur et relecteur → `vibe-harness-expert`.
`orchestrator.toml` + `prompts/orchestrator.md` : méthode Comprendre → Planifier (`todo`) → Valider (`ask_user_question`) → Exécuter une étape à la fois → Déléguer la relecture à `reviewer` via `spawn` puis `wait` → Vérifier → Conclure. Le prompt part d'une copie du prompt système par défaut de Vibe 2.26.0 (`vibe/core/prompts/` du dépôt officiel), sections ajoutées à la fin.
`reviewer.toml` + `prompts/reviewer.md` : lecture seule, format de retour Bloquant / À corriger / Suggestion avec fichier:ligne et exemple complet.
→ vérif : chaque `system_prompt_id` a son fichier, chaque `active_model` existe dans `[[models]]`.

B4. Hook d'audit → `python-expert`.
`hooks.toml` (post_tool sur `bash`, commande `python3 .vibe/hooks/audit_bash.py`) et le script ; tests dans `tests_harnais/` (payload normal, payload incomplet).
→ vérif : tests verts, sortie copiée.

B5. `README.md` et `.gitignore` → orchestrateur (rédaction directe).
README : prérequis (WSL, `uv tool install mistral-vibe==2.26.0`, `vibe --setup`), import dans un dépôt RF (copier `AGENTS.md` et `.vibe/`, accepter la confiance), flux plan → validation → orchestrateur, lien vers la recette.

## Phase C — Vérification et clôture

C1. `harness-verifier` sur tous les livrables avec les critères d'acceptation ci-dessous. Corriger chaque « Non conforme » via l'agent concerné, puis revérifier.

C2. Produire la recette manuelle (à exécuter par l'utilisateur sous WSL), adaptée de la recette du guide :
- dialogue de confiance listant `AGENTS.md` et `.vibe/` ;
- « Quelles sont les règles de ce projet ? » cite `AGENTS.md` ;
- démarrage sur l'agent `plan` ; le plan est soumis avant toute écriture ;
- `vibe --agent orchestrator` : `todo` rempli, `ask_user_question` avant exécution, lancement de `reviewer` par `spawn` puis `wait` ;
- `/thinking` : relever les niveaux disponibles et vérifier ceux de `[[models]]` ;
- modèle effectif de `reviewer` lu dans son transcript (`/log`) ;
- écriture dans `.vibe/` refusée ; `git push --force` refusé ;
- `.vibe/logs/bash.log` rempli et absent de `git status`.

C3. Mettre à jour la mémoire :
- `ETAT.md` : étape 1 terminée (ou état exact), livrables, recette à faire, prochaine action ;
- `DECISIONS.md` : décisions prises (modèles, permissions, structure) ;
- `VIBE_FAITS_VERIFIES.md` : statuts mis à jour par A1, A2 et C1.

C4. Proposer un commit ; ne committer qu'avec accord.

## Critères d'acceptation
- Arborescence conforme au plan validé, chemins relatifs, aucun élément Robot Framework.
- Tous les `.toml` chargés par `tomllib` ; références croisées résolues.
- `AGENTS.md` intègre les lignes directrices et la règle « plan validé avant toute nouvelle demande ».
- Modèle et niveau de réflexion définis pour chaque agent, avec repli documenté.
- Tests pytest du hook verts.
- Recette manuelle fournie ; mémoire à jour.
