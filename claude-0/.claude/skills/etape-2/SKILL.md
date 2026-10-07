---
name: etape-2
description: Étape 2 - spécialise le harnais Vibe pour refactoriser un test Robot Framework à la fois (skill /refacto-test, sous-agents RF, validation par exécution du test, boucle bornée).
disable-model-invocation: true
argument-hint: "[consignes complémentaires]"
---

# Étape 2 — Refacto Robot Framework, test par test

Consignes complémentaires de l'utilisateur : $ARGUMENTS

## Prérequis
- `memoire/ETAT.md` indique l'étape 1 terminée. Recette de l'étape 1 non faite : le signaler et demander s'il faut continuer.
- `projet-mistral-vibe/` contient le squelette de l'étape 1.

## Lectures obligatoires
`memoire/*`, `projet-mistral-vibe/AGENTS.md`, `projet-mistral-vibe/.vibe/config.toml`, `projet-mistral-vibe/.vibe/agents/`, `projet-mistral-vibe/.vibe/prompts/orchestrator.md`, `reference/guide-harnais-vibe.md` (étapes 5 à 8).

## Flux cible dans Vibe
L'utilisateur tape `/refacto-test <fichier.robot>::<nom du test> <consignes>` :
1. **Analyse** (lecture seule) : localiser le test, ses keywords, ressources, variables, bibliothèques ; lire `historisation_refacto/INDEX.md` s'il existe (étape 3).
2. **Référence** : `robot --test "<nom>" --outputdir results/refacto/avant <fichier>`. Test rouge avant refacto : arrêt, compte rendu, question.
3. **Plan** : objectif, changements prévus, ce qui ne doit pas changer (assertions, données, keywords métier), critère de réussite ; soumis par `ask_user_question`. Aucune écriture avant accord.
4. **Refacto** : délégation à `rf-refactorer` (écriture bornée aux `*.robot` et `*.resource`).
5. **Validation** : `robot --test "<nom>" --outputdir results/refacto/apres <fichier>` vert.
6. **Relecture** : délégation à `rf-reviewer` : équivalence avant/après, syntaxe RF 7.1.
7. **Itération** : échec en 5 ou bloquant en 6 → diagnostic puis retour en 4, dans la limite du maximum validé.
8. **Arrêt et question** si : maximum d'itérations atteint ; incohérence flagrante (le test passe sans rien vérifier, assertion supprimée, statut différent pour une raison inexpliquée) ; logique métier insuffisante pour décider.
9. **Conclusion** : résumé (demande, changements, commandes et résultats, points ouverts). L'historisation sera branchée ici à l'étape 3.

## Phase A — Plan (mode plan, rien n'est écrit)

A1. Questions à l'utilisateur (une seule série, AskUserQuestion) :
- bibliothèques RF du dépôt cible (Browser, SeleniumLibrary, RequestsLibrary...) ;
- suite d'exemple disponible ? Sinon `robot-framework-expert` crée une petite suite témoin ;
- nombre maximal d'itérations (proposition : 3) ;
- critère de validation : `robot --test` vert (décision D-05), à confirmer avec ou sans `--dryrun` préalable.

A2. Vérifier les faits utiles → `vibe-harness-expert` : arguments passés à une skill (`/refacto-test ...`), skill qui délègue via `task`, `allowed-tools`, hook `post_agent` (champs stdin, 3 relances max), hooks hérités par les sous-agents, `active_model` par sous-agent (résultat de la recette étape 1).
→ vérif : statuts et URL, à reporter dans `VIBE_FAITS_VERIFIES.md`.

A3. Trancher le mécanisme de validation (présenter les deux options, recommander une) :
- (a) hook `post_agent` qui lit le dernier `results/refacto/apres/output.xml` et refuse la fin de tour si le test n'est pas PASS ou si un `*.robot`/`*.resource` a été modifié après ce fichier ;
- (b) hook `post_agent` qui lance lui-même `robot --test` (garantie plus forte, mais durée du test soumise au `timeout` du hook).
Recommandation par défaut : (a), le test étant lancé par l'agent et le hook vérifiant la preuve. L'état de la refacto en cours (fichier, test, itération) est écrit par l'orchestrateur dans `.refacto/courant.json`, lu par le hook ; le hook ne fait rien en l'absence de ce fichier.

A4. Rédiger le plan et le soumettre (ExitPlanMode) : flux, fichiers ci-dessous, mécanisme retenu, grille modèle des nouveaux agents (décision D-07), réponses de A1.

Fichiers prévus :
```text
projet-mistral-vibe/
├── AGENTS.md                         # + section Robot Framework courte (renvoi aux skills)
├── .gitignore                        # + results/, .refacto/
└── .vibe/
    ├── config.toml                   # + allowlist robot, enabled_skills, presets éventuels
    ├── hooks.toml                    # + hook de validation
    ├── hooks/require_green_test.py
    ├── agents/rf-refactorer.toml     # subagent, écriture *.robot / *.resource seulement
    ├── agents/rf-reviewer.toml       # subagent, lecture seule
    ├── prompts/rf-refactorer.md
    ├── prompts/rf-reviewer.md        # format de retour strict + exemple complet
    ├── prompts/orchestrator.md       # + section refacto (étapes 1 à 9 ci-dessus)
    └── skills/
        ├── refacto-test/SKILL.md     # user-invocable, point d'entrée
        └── rf-conventions/
            ├── SKILL.md              # connaissance, chargée par description
            └── examples.md           # 2 à 4 exemples RF 7.1 + 1 contre-exemple
```

## Phase B — Réalisation (après validation)

B1. Contenu Robot Framework → `robot-framework-expert` : `rf-conventions` (règles et few-shot RF 7.1), texte métier des prompts `rf-refactorer` et `rf-reviewer` (critères d'équivalence), suite témoin si besoin (un test à refactoriser contenant des formes dépréciées, et passant).
→ vérif : `robot --dryrun` sur la suite témoin si `robot` est disponible, sinon à reporter en recette.

B2. Intégration Vibe → `vibe-harness-expert` : agents TOML, prompts (contenu B1 intégré), skill `refacto-test`, mises à jour de `config.toml`, `AGENTS.md`, `orchestrator.md`, `hooks.toml`, `.gitignore`.
→ vérif : `tomllib` charge les fichiers ; références croisées résolues.

B3. Hook de validation → `python-expert` : `require_green_test.py` (stdlib, `xml.etree` pour `output.xml`) et tests pytest dans `tests_harnais/` : pas de refacto en cours → passe ; test PASS et postérieur aux éditions → passe ; test FAIL → refus ; édition postérieure au résultat → refus ; sous-agent (`parent_session_id`) → passe ; payload incomplet → passe.
→ vérif : tests verts, sortie copiée.

## Phase C — Vérification et clôture

C1. `harness-verifier` avec les critères ci-dessous ; corriger puis revérifier.

C2. Recette manuelle sous WSL (à exécuter par l'utilisateur) :
- `/refacto-test` apparaît dans l'autocomplétion ;
- sur la suite témoin : exécution de référence avant toute écriture, plan soumis, refacto, test vert, relecture `rf-reviewer` ;
- refus du hook si l'agent tente de conclure avec un test rouge ;
- `rf-refactorer` ne peut pas écrire hors `*.robot` / `*.resource` ;
- cas d'arrêt : consigne volontairement contradictoire → question posée ;
- modèle effectif des sous-agents lu via `/log`.

C3. Mémoire : `ETAT.md`, `DECISIONS.md` (mécanisme de validation, itérations max, librairies), `VIBE_FAITS_VERIFIES.md`.

C4. Proposer un commit ; ne committer qu'avec accord.

## Critères d'acceptation
- Flux 1 à 9 décrit dans `refacto-test` et `orchestrator.md`, sans doublon avec `AGENTS.md`.
- Aucune écriture possible avant validation du plan dans Vibe (agent `plan` ou `ask_user_question`).
- Test lancé avant et après ; conclusion impossible avec un test rouge (hook testé).
- Boucle bornée ; conditions d'arrêt explicites.
- Écritures de `rf-refactorer` bornées ; `rf-reviewer` en lecture seule avec format de retour exemplifié.
- Syntaxe RF 7.1 conforme au User Guide ; tests pytest verts ; recette fournie ; mémoire à jour.
