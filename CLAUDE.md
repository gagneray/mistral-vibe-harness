# Construction d'un harnais Mistral Vibe pour la refacto Robot Framework

## Mission

Construire, dans `projet-mistral-vibe/`, un harnais Mistral Vibe (`AGENTS.md` + `.vibe/`) qui :
1. fournit une base générique (étape 1) ;
2. refactorise un test Robot Framework à la fois, avec plan validé, sous-agents spécialisés et validation par exécution du test (étape 2) ;
3. historise chaque refacto dans `historisation_refacto/` pour évaluer la méthode (étape 3).

Le harnais sera ensuite importé à la racine d'un dépôt de tests Robot Framework : tous ses chemins sont relatifs.

Une étape = une session neuve, lancée par `/etape-1`, `/etape-2`, `/etape-3`. L'état entre sessions vit dans `memoire/`.

## Versions de référence

| Outil | Version | Source officielle |
| --- | --- | --- |
| Mistral Vibe | 2.26.0 (Unified Harness) | https://docs.mistral.ai/vibe/code · https://github.com/mistralai/mistral-vibe (README, CHANGELOG, code au tag `v2.26.0`) |
| Robot Framework | 7.1 | https://robotframework.org/robotframework/7.1/RobotFrameworkUserGuide.html |
| Python | 3.11 | https://docs.python.org/3.11/ |
| Modèles Mistral | — | https://docs.mistral.ai/getting-started/models/models_overview/ |

Règles :
- Toute affirmation sur Vibe, RF ou Python s'appuie sur ces sources ; citer l'URL dans `memoire/VIBE_FAITS_VERIFIES.md` ou `memoire/DECISIONS.md`.
- Doc et code divergent : le noter, retenir le comportement du code 2.26.0 et prévoir un test de recette.
- Recherche hors de ces sources (WebSearch, sites tiers) : la demander à l'utilisateur en justifiant le besoin.
- N'utiliser aucune fonctionnalité postérieure à 2.26.0 (décision D-10 : référence passée de 2.25.8 à 2.26.0 le 2026-10-08).

## Environnement d'exécution

- Vibe et `robot` tournent sous **WSL / Linux** ; les hooks sont appelés en `python3`, chemins POSIX.
- Cette session Claude Code peut tourner sous Windows : ne pas lancer Vibe soi-même ; produire une recette que l'utilisateur exécute sous WSL.
- Python des hooks : bibliothèque standard 3.11 uniquement (`json`, `tomllib`, `xml.etree`, `pathlib`, `subprocess`).

## Rôle de cette session : orchestrateur

La session principale planifie, délègue, intègre et vérifie. Toute délégation part d'ici : les agents experts ne délèguent pas entre eux (traçabilité, contexte maîtrisé).

| Agent | Quand l'appeler |
| --- | --- |
| `vibe-harness-expert` | `AGENTS.md`, `config.toml`, agents TOML, prompts, skills, hooks.toml, permissions, modèles |
| `python-expert` | Scripts de hooks et utilitaires Python, leurs tests pytest |
| `robot-framework-expert` | Syntaxe RF 7.1, règles de refacto, CLI `robot`, suite témoin, prompts des agents Vibe RF |
| `harness-verifier` | Avant de conclure une étape : contrôle indépendant, lecture seule |

Chaque délégation transmet : objectif, fichiers à lire et à produire, contraintes, critères d'acceptation, format de retour. L'agent part d'un contexte vierge.

## Méthode de travail

- Suivre `reference/karpathy_method.md` : hypothèses explicites, simplicité, changements ciblés, critères vérifiables.
- Chaque étape commence en mode plan ; rien n'est écrit avant validation du plan.
- Une question bloquante se pose avant d'agir, pas après.
- Ne jamais committer sans accord explicite.

## Références locales

- `reference/guide-harnais-vibe.md` : guide de mise en place (réf. 2.25.2 et ancien moteur, écarts connus dans `memoire/VIBE_FAITS_VERIFIES.md`).
- `reference/karpathy_method.md` : lignes directrices à intégrer à l'`AGENTS.md` du harnais.

## Mémoire entre sessions

Lire en début de session : `memoire/DECISIONS.md` et `memoire/VIBE_FAITS_VERIFIES.md` (l'état est importé ci-dessous).
En fin d'étape, mettre à jour les trois fichiers :
- `ETAT.md` : avancement, livrables, prochaine action, questions ouvertes ;
- `DECISIONS.md` : décision, justification, source, date ;
- `VIBE_FAITS_VERIFIES.md` : faits confirmés ou infirmés en recette.

@memoire/ETAT.md

## Style

Français, didactique, succinct. Pas d'emoji, pas de remplissage, pas de sur-ingénierie.
