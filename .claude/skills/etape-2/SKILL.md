---
name: etape-2
description: Étape 2 - spécialise le harnais Vibe pour refactoriser un test Robot Framework à la fois (skill /refacto-test, sous-agents RF, validation par exécution du test, boucle bornée).
disable-model-invocation: true
argument-hint: "[consignes complémentaires]"
---

# Étape 2 — Refacto Robot Framework, test par test

Consignes complémentaires de l'utilisateur : $ARGUMENTS

## Prérequis
- `memoire/ETAT.md` indique l'étape 1 terminée. Recette de l'étape 1 non faite : le signaler et demander s'il faut continuer. La recette GLM (D-12) peut rester en attente : elle ne bloque pas l'étape 2.
- `projet-mistral-vibe/` contient le squelette de l'étape 1.

## Acquis de l'étape 1 à respecter (D-10 à D-12, `VIBE_FAITS_VERIFIES.md`)
- Unified Harness : sous-agents par `spawn` puis `wait`, pas de `task` ni d'`exit_plan_mode`. L'agent `plan` n'écrit rien : `/refacto-test` s'exécute dans `orchestrator` (`Shift+Tab` ou `vibe --agent orchestrator`).
- Un sous-agent ignore `active_model` et prend le modèle de l'agent qui le lance (GLM 5.3 `max` en D-12) : aucun modèle propre par sous-agent, et chaque itération déléguée coûte un appel GLM complet.
- Outils d'un sous-agent : `enabled_tools` parmi les outils natifs (`read_file`, `bash`, `edit`, `write_file`…) ; `grep` n'en fait pas partie.
- Prompts : base = traduction française de `cli.md` v2.26.0, puis section « Ajouts du harnais » (D-11). Les nouveaux prompts suivent le même modèle.
- `AGENTS.md` : fichiers modifiés uniquement par l'outil d'édition, refus définitif, arrêt si l'édition échoue. Cette dernière règle bloque une boucle de correction : à trancher en A1.
- Le modèle oublie `spawn` s'il n'est pas demandé explicitement : la skill nomme chaque `spawn` / `wait`. D-11 limite à une relecture par tâche : préciser la règle dans la boucle (une relecture par itération ou une seule finale).
- Bash : `default_timeout = 300` s et sortie tronquée à 16 000 octets (`vibe/core/tools/builtins/bash.py`). `log.html` est illisible pour l'agent ; `output.xml` dépasse vite la limite.
- Définir `allowlist` dans `[tools.bash]` remplace la liste par défaut (fusion superficielle) : reprendre les défauts (`cat`, `grep`, `ls`, `git status`…) en plus de `robot`.
- Pas d'`enabled_skills` : une liste blanche masquerait les skills fournies par Vibe (décision de l'étape 1).
- Hook `post_agent` (2.26.0) : `decision = "deny"` + `reason` réinjecté au modèle, 3 relances au plus par hook et par tour utilisateur. Stdin : `session_id`, `parent_session_id`, `transcript_path` (dossier), `cwd` = `workspace.cwd`.
- Coût de la session : `/status` (prix déclarés dans `[[models]]`).
- Environnement : `robot` (7.1) et les bibliothèques du dépôt cible doivent être installés dans le venv activé avant `vibe` (leçon pytest de l'étape 1) ; sinon `AGENTS.md` impose de signaler l'outil manquant.

## Lectures obligatoires
`memoire/*`, `projet-mistral-vibe/AGENTS.md`, `projet-mistral-vibe/.vibe/config.toml`, `projet-mistral-vibe/.vibe/agents/`, `projet-mistral-vibe/.vibe/prompts/orchestrator.md`, `reference/guide-harnais-vibe.md` (étapes 5 à 8).

## Flux cible dans Vibe
L'utilisateur tape `/refacto-test <fichier.robot>::<nom du test> <consignes>` :
1. **Analyse** (lecture seule) : localiser le test, ses keywords, ressources, variables, bibliothèques ; lire `historisation_refacto/INDEX.md` s'il existe (étape 3).
2. **Référence** : `robot --test "<nom>" --outputdir results/refacto/avant <fichier>`. Test rouge avant refacto : arrêt, compte rendu, question.
3. **Plan** : objectif, changements prévus, ce qui ne doit pas changer (assertions, données, keywords métier), critère de réussite ; soumis par `ask_user_question`. Aucune écriture avant accord.
4. **Refacto** : `spawn` du spécialiste `rf-refactorer` (Robot Framework 7.1 et Python des bibliothèques de mots-clés), puis `wait`. Écriture bornée aux `*.robot`, `*.resource` et, si validé en A1, aux bibliothèques Python du dépôt.
5. **Validation** : `robot --test "<nom>" --outputdir results/refacto/apres <fichier>` vert, puis `python3 .vibe/hooks/resume_resultat.py results/refacto/apres/output.xml` : statut, keyword en échec, message, fichier:ligne, en quelques lignes.
6. **Relecture** : `spawn` de `rf-reviewer`, puis `wait` : équivalence avant/après, syntaxe RF 7.1.
7. **Itération** : échec en 5 ou bloquant en 6 → nouveau `spawn` de `rf-refactorer` avec le résumé de `resume_resultat.py` et l'avis du relecteur, puis retour en 5, dans la limite du maximum validé.
8. **Arrêt et question** si : maximum d'itérations atteint ; incohérence flagrante (le test passe sans rien vérifier, assertion supprimée, statut différent pour une raison inexpliquée) ; logique métier insuffisante pour décider.
9. **Conclusion** : résumé (demande, changements, commandes et résultats, points ouverts). L'historisation sera branchée ici à l'étape 3.

## Phase A — Plan (mode plan, rien n'est écrit)

A1. Questions à l'utilisateur (une seule série, AskUserQuestion) :
- bibliothèques RF du dépôt cible (Browser, SeleniumLibrary, RequestsLibrary...) ;
- suite d'exemple disponible ? Sinon `robot-framework-expert` crée une petite suite témoin ;
- nombre maximal d'itérations (proposition : 3) ;
- critère de validation : `robot --test` vert (décision D-05), à confirmer avec ou sans `--dryrun` préalable ;
- périmètre de `rf-refactorer` : `*.robot` / `*.resource` seulement, ou aussi les bibliothèques Python du dépôt ;
- échec de l'outil d'édition dans la boucle : autoriser un nouvel essai après relecture du fichier, ou garder l'arrêt d'`AGENTS.md` ;
- relecture : à chaque itération ou une seule fois en fin de boucle (coût GLM `max`).

A2. Vérifier les faits utiles → `vibe-harness-expert` : arguments passés à une skill (`/refacto-test ...`) ; skill qui demande des `spawn` / `wait` ; `allowed-tools` ; limiter l'écriture d'un sous-agent à des chemins (`[tools.edit]` / `[tools.write_file]` dans le TOML d'un sous-agent, plafond `rust_agent_tool_ceiling`, `vibe/app_server/_runtime.py`) ; approbation d'une écriture demandée par un sous-agent (question posée à l'utilisateur ou refus) ; bash d'un sous-agent ; hooks déclenchés pour un sous-agent (`parent_session_id`). Déjà établi, ne pas revérifier : modèle des sous-agents (hérité), champs stdin et plafond de relances de `post_agent`.
→ vérif : statuts et URL, à reporter dans `VIBE_FAITS_VERIFIES.md`.

A3. Trancher le mécanisme de validation (présenter les deux options, recommander une) :
- (a) hook `post_agent` qui lit le dernier `results/refacto/apres/output.xml` et refuse la fin de tour si le test n'est pas PASS ou si un `*.robot`/`*.resource` a été modifié après ce fichier ;
- (b) hook `post_agent` qui lance lui-même `robot --test` (garantie plus forte, mais durée du test soumise au `timeout` du hook).
Recommandation par défaut : (a), le test étant lancé par l'agent et le hook vérifiant la preuve. Le délai de 300 s de bash rend (b) fragile. L'état de la refacto en cours (fichier, test, itération) est écrit par l'orchestrateur dans `.refacto/courant.json`, lu par le hook ; le hook ne fait rien en l'absence de ce fichier. Le plafond de 3 relances de `post_agent` doit rester cohérent avec le maximum d'itérations.

A4. Rédiger le plan et le soumettre (ExitPlanMode) : flux, fichiers ci-dessous, mécanisme retenu, coût estimé d'une refacto (sous-agents hérités du modèle de l'orchestrateur, D-12), réponses de A1.

Fichiers prévus :
```text
projet-mistral-vibe/
├── AGENTS.md                         # + section Robot Framework courte (renvoi aux skills), règle d'échec d'édition selon A1
├── .gitignore                        # + results/, .refacto/
├── README.md                         # + prérequis robot / bibliothèques dans le venv, recette
└── .vibe/
    ├── config.toml                   # + allowlist bash = défauts + robot (pas d'enabled_skills)
    ├── hooks.toml                    # + hook de validation
    ├── hooks/require_green_test.py
    ├── hooks/resume_resultat.py      # résumé court d'output.xml, partagé par l'agent et le hook
    ├── agents/rf-refactorer.toml     # subagent spécialiste RF 7.1 / Python, écriture bornée (A1, A2)
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

B3. Hook de validation → `python-expert` : `resume_resultat.py` (stdlib, `xml.etree` ; sortie bien en dessous de 16 000 octets ; tests pytest : PASS, FAIL avec message, fichier absent ou invalide) et `require_green_test.py` (réutilise la lecture de `resume_resultat.py`), avec ses tests pytest dans `tests_harnais/` : pas de refacto en cours → passe ; test PASS et postérieur aux éditions → passe ; test FAIL → refus ; édition postérieure au résultat → refus ; sous-agent (`parent_session_id`) → passe ; payload incomplet → passe.
→ vérif : tests verts, sortie copiée.

## Phase C — Vérification et clôture

C1. `harness-verifier` avec les critères ci-dessous ; corriger puis revérifier.

C2. Recette manuelle sous WSL (à exécuter par l'utilisateur), sur un banc `Test_Etape_2/` construit comme `Test_Etape_1/` (`preparer.sh`, venv avec `robotframework==7.1` et pytest) :
- `/refacto-test` apparaît dans l'autocomplétion ;
- `spawn` de `rf-refactorer` sans rappel explicite ; `resume_resultat.py` appelé après chaque exécution ;
- coût et durée d'une refacto relevés par `/status` ;
- sur la suite témoin : exécution de référence avant toute écriture, plan soumis, refacto, test vert, relecture `rf-reviewer` ;
- refus du hook si l'agent tente de conclure avec un test rouge ;
- `rf-refactorer` ne peut pas écrire hors de son périmètre (A1) ; pour tester une permission, préciser « je teste les permissions, appelle réellement l'outil » ;
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
