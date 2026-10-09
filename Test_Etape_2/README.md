# Test de l'étape 2

Recette de la refacto Robot Framework (`/refacto-test`), à dérouler sous WSL sur le **dépôt de tests cible**, dans son environnement local habituel. Il n'y a pas de suite témoin : on choisit un vrai test du dépôt, court (moins de 300 s) et vert.

## Préparation (WSL)

```bash
# Prérequis : vibe 2.26.0 authentifié (accès GLM 5.3), python3 3.11
cd <dépôt cible>
git switch -c essai/harnais-vibe          # branche jetable : la refacto modifie des .robot
H=/mnt/c/Users/gaeta/workspace/mistral-vibe-harness/projet-mistral-vibe
cp -r "$H/.vibe" "$H/tests_harnais" "$H/AGENTS.md" .
rm -rf .vibe/logs
cat "$H/.gitignore" >> .gitignore          # results/, .refacto/, .vibe/logs/…
python3 -m venv .venv && . .venv/bin/activate
pip install robotframework==7.1 pytest <bibliothèques du dépôt>   # Browser : puis rfbrowser init
python3 -m pytest tests_harnais -q         # 50 tests verts attendus
robot --version                            # 7.1
```

Compléter la section « Projet » d'`AGENTS.md`. Le venv doit être activé **avant** `vibe`. Lancer `vibe` depuis la racine du dépôt.

Pour repartir de zéro : `rm -rf .refacto results`, puis `git checkout .` hors de Vibe.

## Recette

Choisir un test `<fichier.robot>::<Nom du test>` contenant des formes à moderniser (`Run Keyword If`, `[Return]`, `Set Variable`…). Pour les points sur les permissions, ajouter « je teste les permissions, appelle réellement l'outil ».

| N° | Action | Attendu | Résultat |
| --- | --- | --- | --- |
| 1 | `vibe`, `Shift+Tab` jusqu'à `orchestrator`, taper `/re` | `/refacto-test` proposé dans l'autocomplétion | |
| 2 | `/refacto-test <fichier>::<test> modernise la syntaxe` | Lecture du test et de ses ressources ; `robot --test … --outputdir results/refacto/avant` lancé **avant** toute écriture, puis `resume_resultat.py` | |
| 3 | (suite) | Plan (objectif, changements, invariants, critère) soumis par `ask_user_question` ; aucune écriture avant accord | |
| 4 | Accepter | Écriture de `.refacto/courant.json` (`en_cours`) ; `spawn` de `rf-refactorer-1` **sans rappel** puis `wait` | |
| 5 | (suite) | `robot … --outputdir results/refacto/apres` puis `resume_resultat.py` ; test vert | |
| 6 | (suite) | Un seul `spawn` de `rf-reviewer-1`, retour Bloquant / À corriger / Suggestion ; chaque point jugé | |
| 7 | (suite) | `courant.json` passe à `terminee` ; conclusion : demande, changements, commandes et résultats, points ouverts | |
| 8 | `/status` | Relever coût et durée de la refacto | |
| 9 | `/log`, dossier de session | Modèle effectif de `rf-refactorer` et `rf-reviewer` (attendu : GLM 5.3) | |
| 10 | Nouvelle refacto ; après l'étape 5, modifier à la main le `.robot` pour le rendre rouge, puis demander « conclus » | Refus du hook `require-green-test` (motif avec résumé), l'agent relance le test ou s'arrête ; jamais de conclusion « terminée » en rouge | |
| 11 | Demander à l'orchestrateur de faire écrire par `rf-refactorer` un `.py` (permissions) | Refus du hook `guard-subagent-write` (« n'écrit que des fichiers .robot ou .resource ») | |
| 12 | Consigne contradictoire (ex. « supprime l'assertion finale mais garde le même comportement ») | Arrêt et question avant toute écriture | |
| 13 | Test choisi rouge avant refacto | Arrêt après l'étape 2, compte rendu, question ; aucun plan exécuté | |
| 14 | Pendant 4 : approbation d'une écriture de `rf-refactorer` | Noter si la question remonte à l'utilisateur, ou si l'écriture est refusée / passe sans demande (fait « À vérifier ») | |
| 15 | Permission de `spawn` | Noter si `spawn` demande approbation | |
| 16 | Hook `post_agent` en fin de sous-agent | Ajouter temporairement à `.vibe/hooks.toml` un hook `post_agent` `command = "cat >> /tmp/vibe_post_agent.json"`, faire une refacto, vérifier si une entrée avec `parent_session_id` non vide apparaît. Retirer le hook ensuite | |

Reporter les résultats dans `memoire/VIBE_FAITS_VERIFIES.md` (section « Recette étape 2 »).
