---
name: etape-3
description: Étape 3 - ajoute au harnais Vibe l'historisation de chaque refacto (skill historiser-refacto, fichiers markdown numérotés dans historisation_refacto/ et INDEX).
disable-model-invocation: true
argument-hint: "[consignes complémentaires]"
---

# Étape 3 — Historisation des refactos

Consignes complémentaires de l'utilisateur : $ARGUMENTS

## But
L'expérimentation doit dire si la refacto assistée par Vibe vaut la peine. Chaque demande de refacto laisse donc une trace lisible dans l'ordre : demande, méthode, difficultés, résultat, améliorations. Ces traces servent aussi de contexte aux refactos suivantes et forment, en fin d'expérimentation, le livrable.

## Prérequis
- `memoire/ETAT.md` indique l'étape 2 terminée. Recette de l'étape 2 non faite : le signaler et demander s'il faut continuer.

## Lectures obligatoires
`memoire/*`, `projet-mistral-vibe/.vibe/skills/refacto-test/SKILL.md`, `projet-mistral-vibe/.vibe/prompts/orchestrator.md`, `projet-mistral-vibe/.vibe/config.toml`, `projet-mistral-vibe/.vibe/hooks.toml`.

## Conception attendue
- Skill Vibe `historiser-refacto` (`.vibe/skills/historiser-refacto/`), appelable en `/historiser-refacto` et appelée en dernière étape de `/refacto-test`.
- Pas de sous-agent `historien` : un sous-agent ne peut pas avoir son propre modèle, il prend celui de l'agent qui le lance (`vibe/app_server/_agent_types.py`, D-12). Un modèle léger est donc impossible : repli D-07b, l'orchestrateur remplit l'entrée lui-même avec l'outil d'écriture, après création du fichier par le script.
- Un fichier par demande : `historisation_refacto/NNNN_AAAA-MM-JJ_<test-slug>.md`, `NNNN` séquentiel.
- Numérotation et création par un script Python déterministe (`nouvelle_entree.py` dans le dossier de la skill) : calcule le numéro suivant, crée le fichier depuis le modèle, ajoute la ligne à l'INDEX, affiche le chemin créé.
- `historisation_refacto/INDEX.md` : tableau, une ligne par entrée (n°, date, test, résultat, lien).
- Modèle d'entrée (`modele.md` dans le dossier de la skill) :
  1. Demande : fichier, test, consignes, date, modèle effectif et niveau de `thinking` (GLM 5.3 ou Medium 3.5), version de Vibe et du harnais ;
  2. Méthode : étapes suivies, agents appelés (`spawn`), nombre d'itérations, commandes lancées, coût relevé par `/status` ;
  3. Difficultés : blocages, questions posées, hypothèses ;
  4. Résultat : statut avant/après, résumé du diff, durée approximative, verdict du relecteur ;
  5. Améliorations : pour le harnais, pour la consigne, pour le test.
- Contexte : en phase d'analyse, `/refacto-test` lit l'INDEX et la rubrique « Améliorations » des 3 dernières entrées.
- Option à trancher : hook `post_agent` qui refuse de conclure une refacto (`.refacto/courant.json` présent) sans nouvelle entrée d'historisation.
- `historisation_refacto/` est versionné (c'est le livrable), contrairement à `results/`.

## Phase A — Plan (mode plan, rien n'est écrit)

A1. Vérifier → `vibe-harness-expert` : skill qui exécute un script de son dossier (chemin, permission `bash`) ; ordre des hooks `post_agent` si deux hooks coexistent, et partage du plafond de 3 relances ; écriture dans `historisation_refacto/` non bloquée par les denylists de `[tools.edit]` / `[tools.write_file]`. Pas d'`enabled_skills` (décision de l'étape 1).
→ vérif : statuts et URL.

A2. Soumettre le plan (ExitPlanMode) : conception ci-dessus, choix sur le hook optionnel, modèle d'entrée complet, exemple d'entrée remplie.

## Phase B — Réalisation (après validation)

B1. Script et tests → `python-expert` : `nouvelle_entree.py` (stdlib ; slug ASCII ; dossier vide → 0001 ; INDEX créé s'il manque) ; tests pytest : dossier vide, numéros existants avec trou, nom de test avec espaces et accents, INDEX absent.
→ vérif : tests verts, sortie copiée.

B2. Intégration Vibe → `vibe-harness-expert` : `SKILL.md` (format strict et exemple), `modele.md`, hook optionnel si retenu, ajout de l'étape finale dans `refacto-test` et `orchestrator.md`, permission `bash` du script (allowlist = défauts + script, la liste remplaçant celle par défaut).
→ vérif : `tomllib` ; références croisées.

B3. Exemple d'entrée remplie (fictive, signalée comme telle) dans le dossier de la skill → orchestrateur, relu par `robot-framework-expert` pour la vraisemblance RF.

## Phase C — Vérification et clôture

C1. `harness-verifier` avec les critères ci-dessous ; corriger puis revérifier.

C2. Recette manuelle sous WSL :
- `/historiser-refacto` apparaît dans l'autocomplétion ;
- une refacto complète sur la suite témoin crée `0001_...md` et la ligne d'INDEX ;
- une deuxième refacto crée `0002_...md` et son analyse cite les améliorations de `0001` ;
- l'entrée est remplie avec des faits : commandes, résultats, modèle, coût `/status` ;
- hook optionnel : refus de conclure sans entrée.

C3. Mémoire : `ETAT.md` (harnais complet, expérimentation prête), `DECISIONS.md`, `VIBE_FAITS_VERIFIES.md`.

C4. Proposer un commit ; ne committer qu'avec accord.

## Critères d'acceptation
- Une entrée par refacto, numérotée sans collision, lisible dans l'ordre via l'INDEX.
- Les cinq rubriques présentes et remplies à partir de faits (commandes, résultats), pas de formules génériques.
- Historisation déclenchée en fin de `/refacto-test`, y compris quand la refacto s'arrête sur une question ou un échec.
- Script testé ; recette fournie ; mémoire à jour.
