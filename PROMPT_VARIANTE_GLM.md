Tu reprends le projet décrit dans `CLAUDE.md` : un harnais Mistral Vibe dans `projet-mistral-vibe/`. Tu es l'orchestrateur : tu planifies, délègues aux agents experts (`vibe-harness-expert`, `python-expert`, `harness-verifier`), intègres et vérifies. Commence en mode plan ; rien n'est écrit avant validation du plan ; ne committe jamais sans mon accord.

## Objectif

Adapter le harnais pour utiliser **GLM 5-3 (`name = "zai-glm-5-3"`) en effort de raisonnement maximal (`thinking = "max"`)** :
- au minimum pour l'agent `plan` (agent de démarrage) ;
- si c'est pertinent, aussi pour l'agent `orchestrator` ;
- trancher, faits à l'appui, ce qu'il advient des sous-agents (`reviewer`) et de la compaction.

C'est la variante prévue par `memoire/ETAT.md` (prochaine action 3) et la décision **D-12**, encore à prendre. GLM avait été écarté en D-07 (« tiers ») ; D-12 doit expliquer pourquoi on le réintroduit, et comment.

## Lis d'abord
- `CLAUDE.md` (versions de référence, règles de sources, rôle d'orchestrateur, style).
- `memoire/ETAT.md`, `memoire/DECISIONS.md` (D-07, D-07b, D-10, D-11), `memoire/VIBE_FAITS_VERIFIES.md` (sections « Configuration », « Agents et sous-agents », « Revérification 2.26.0 », « Recette 2026-10-09 »).
- Livrables : `projet-mistral-vibe/.vibe/config.toml`, `.vibe/agents/orchestrator.toml`, `.vibe/agents/reviewer.toml`, `projet-mistral-vibe/README.md`, `Test_Etape_1/README.md`, `Test_Etape_1/preparer.sh`.

## État au 2026-10-09
- Référence : **Mistral Vibe 2.26.0**, moteur **Unified Harness** (D-10). Code au tag `v2.26.0` : `https://raw.githubusercontent.com/mistralai/mistral-vibe/v2.26.0/` (le tag sans « v » renvoie 404).
- Modèles actuels (D-07b) :
  - `config.toml` : `active_model = "mistral-medium-3.5"` (alias intégré, `name = "mistral-vibe-cli-latest"`, provider `mistral`, `thinking = "high"`). C'est le modèle de l'agent `plan` et de toute session sans autre agent.
  - `orchestrator.toml` : `active_model = "mistral-medium-3.5"`. Le profil d'un agent principal applique son `active_model` quand on passe sur cet agent (`Shift+Tab` ou `--agent`).
  - Sous-agents (`reviewer`, lancé par `spawn` puis `wait`) : `active_model` **ignoré**. Vibe journalise « runs on the session's model instead » (`vibe/app_server/_agent_types.py`).
  - Compaction : `[compaction_model]` Mistral Small 4 (`mistral-small-latest`, `thinking = "off"`, provider `mistral`). **En 2.26.0, un `compaction_model` d'un autre provider que le modèle actif est ignoré sans message** (`_shares_active_provider`, `vibe/core/config/vibe_schema.py`).
- Valeurs de `thinking` : `off`, `low`, `medium`, `high`, `max`. Vers l'API Mistral, `medium`, `high` et `max` donnent tous `reasoning_effort = "high"` (`vibe/core/llm/backend/mistral.py`). Pour un autre provider, la traduction n'est **pas vérifiée**.
- 2.26.0 a ajouté `thinking_levels`, `max_context_length` et `[utility_models]`. Ils étaient écartés tant que la référence était 2.25.8 ; ils sont désormais utilisables s'ils servent.
- Recette du 2026-10-09 (Medium 3.5) : permissions, hook et `spawn`/`wait` fonctionnent. Relecture lente (environ 3 min), relecteur peu fiable, orchestrateur en boucle : corrigé dans les prompts (D-11), non revérifié.
- L'arbre de travail contient des changements **non committés** (D-10, D-11, traduction des prompts, tests restaurés) : ne pas committer, ne pas les écraser.
- Point en suspens, sans lien avec GLM : faut-il qu'`AGENTS.md` autorise un nouvel essai de l'outil d'édition après un échec, avant de s'arrêter ? Ne pas le traiter ici sauf si je le demande.

## Questions à me poser avant toute action (bloquantes)
1. **Fournisseur du modèle.** L'entrée de modèle est connue (donnée par l'utilisateur le 2026-10-09) :
   ```toml
   [[models]]
   name = "zai-glm-5-3"
   thinking = "max"
   ```
   Décidé : cette entrée se place dans la config projet `projet-mistral-vibe/.vibe/config.toml` (le harnais ne dépend d'aucune config utilisateur). Reste à obtenir : la valeur de `provider` de cette entrée et le bloc `[[providers]]` correspondant (URL de base, variable d'environnement de la clé, style d'API), ainsi que l'`alias` éventuel. Si le fournisseur n'est pas intégré à Vibe, son bloc `[[providers]]` va lui aussi dans la config projet, sans jamais la clé (variable d'environnement seulement). Vérifier que `name`, `thinking = "max"` et les clés ajoutées existent dans le schéma 2.26.0. Ne rien supposer d'autre.
2. **Périmètre** : GLM pour `plan` seul, ou pour `plan` et `orchestrator` ? Faut-il garder Medium 3.5 accessible comme repli ?
3. **Compaction** : un modèle GLM plus léger chez le même fournisseur, ou rien (Vibe utilise alors le modèle actif) ?
4. **Coût et durée** : un effort maximal sur chaque relecture est-il acceptable ?

## Sources
- Vibe : code au tag `v2.26.0`, CHANGELOG, https://docs.mistral.ai/vibe/code. Le code prime sur la doc.
- GLM : **j'autorise la consultation de la documentation officielle du fournisseur de GLM** (modèle, API compatible OpenAI ou non, paramètres de raisonnement, appels d'outils). Toute autre source tierce : me la demander.
- Citer chaque URL dans `memoire/VIBE_FAITS_VERIFIES.md` ou `memoire/DECISIONS.md`.

## Faits à établir (délégation à `vibe-harness-expert`, en lecture seule d'abord)
Dans le code Vibe 2.26.0, avec fichier et URL :
1. **Fournisseurs** : schéma de `[[providers]]` (clés exactes : nom, URL de base, variable de clé, style d'API, backend), backends disponibles (`vibe/core/llm/backend/`), et façon de déclarer un fournisseur compatible OpenAI.
2. **Modèles** : schéma de `[[models]]` (`name`, `provider`, `alias`, `thinking`, `temperature`, prix, `auto_compact_threshold`, `thinking_levels`, `max_context_length`), règles de fusion avec les alias intégrés.
3. **Effort de raisonnement** : comment `thinking = "max"` est traduit pour un fournisseur non Mistral (paramètre envoyé, valeur, ou rien). Rôle de `thinking_levels`. Croiser avec la doc GLM : quel paramètre active le raisonnement maximal, et Vibe sait-il l'envoyer ? Sinon, quel est le meilleur équivalent sans modifier Vibe ?
4. **Réponses de raisonnement** : Vibe gère-t-il le champ de raisonnement renvoyé par GLM (par exemple `reasoning_content`) sans erreur ni perte, y compris pendant les appels d'outils ?
5. **Appels d'outils** : le Unified Harness (outils `file_system.*`, `spawn`, `wait`, `ask_user_question`, `todo`) fonctionne-t-il avec ce backend ? Contraintes connues (schémas JSON, appels parallèles) ?
6. **Modèle des sous-agents** : que veut dire précisément « session's model » ? Le modèle actif de l'agent principal au moment du `spawn` (orchestrateur), ou celui du démarrage de la session (`plan`) ? Mon hypothèse : les sous-agents utilisent le modèle de l'orchestrateur. À confirmer ou infirmer dans `_agent_types.py`, `_runtime.py` et `harness/`.
7. **Compaction** : `[compaction_model]` sur le fournisseur GLM (même provider) ; comportement exact quand il est ignoré.
8. **Changement de modèle** : existe-t-il une commande ou une option CLI pour basculer entre GLM et Medium 3.5 sans éditer les fichiers (utile pour le repli) ?

## Décisions à proposer (dans le plan, avec justification)
- Grille modèle / agent : `plan`, `orchestrator`, `reviewer` (déterminé par le fait 6), compaction, chacun avec son niveau de `thinking`.
- Pertinence de l'effort maximal pour `reviewer` : bénéfice attendu (moins d'erreurs de relecture, constatées en recette) contre coût et durée. Si le sous-agent hérite forcément du modèle de l'orchestrateur, dire ce que cela impose.
- Repli Mistral : garder un alias `mistral-medium-3.5` utilisable, et dire comment revenir en arrière.
- Simplicité : le minimum de clés ; pas de configurabilité non demandée.

## Livrables attendus
- `projet-mistral-vibe/.vibe/config.toml` : fournisseur et modèle GLM, `active_model` (agent `plan`), compaction ; commentaires sourcés.
- `projet-mistral-vibe/.vibe/agents/orchestrator.toml` : `active_model` selon la décision.
- `projet-mistral-vibe/README.md` : prérequis (clé API GLM, variable d'environnement, jamais commitée), tableau des modèles, repli, recette ciblée.
- `Test_Etape_1/README.md` : prérequis (clé GLM) et recette ciblée.
- `memoire/DECISIONS.md` (D-12), `memoire/VIBE_FAITS_VERIFIES.md` (faits GLM et fournisseur), `memoire/ETAT.md`.
- Contrôle `harness-verifier` (référence 2.26.0) avant de conclure.

## Recette ciblée (je l'exécute sous WSL, tu me guides pas à pas)
Vibe ne se lance pas depuis cette session Windows. Banc : `bash Test_Etape_1/preparer.sh` → `~/test-etape-1`, venv avec pytest activé avant `vibe`. Remise à zéro : `git checkout -- . && git clean -fd -e .vibe/logs -e .venv`.
1. Démarrage : modèle effectif de `plan` (`/log`, dossier de session), niveau de `/thinking`, absence d'erreur d'API.
2. Point 3 : plan correct, aucune écriture, aucun contournement par bash.
3. Point 4 : `orchestrator` → `todo`, `ask_user_question`, édition, pytest réel, **un seul** `spawn`/`wait` de `reviewer`, points jugés, pas de boucle, aucune modification par le shell (vérifie aussi D-11).
4. Modèle réellement utilisé par `reviewer` (fait 6) et durée de la relecture.
5. Point 7d : refus d'approbation respecté, sans contournement.
6. Point 10 : `/compact` (modèle de compaction réellement utilisé).
7. Repli : retour à Medium 3.5 selon la procédure du README.

Pour tester une permission, préciser au modèle : « je teste les permissions, appelle réellement l'outil » ; sinon il refuse de lui-même sans exercer l'outil (constat du 2026-10-09).

## Critères d'acceptation
- Chaque clé de configuration existe en 2.26.0 (source citée) ; aucun secret dans le dépôt.
- La grille modèle / agent est justifiée par des faits du code, pas par des suppositions ; tout point non vérifiable a un test de recette.
- `harness-verifier` : aucun point Bloquant.
- Mémoire à jour (D-12, faits, état), sans commit.

## Style
Français, didactique, succinct. Pas d'emoji, pas de remplissage, pas de sur-ingénierie.
