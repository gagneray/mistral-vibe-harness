# Harnais Mistral Vibe : résumé de l'étape 1

Date : 7 octobre 2026. Statut : étape 1 réalisée et vérifiée sur documents ; essai réel dans Vibe (recette) encore à faire.

Ce document a deux niveaux de lecture :
- **Partie 1, pour tous** : ce qui a été fait et pourquoi, sans jargon.
- **Partie 2, pour les développeurs** : comment c'est construit, pour un lecteur qui ne connaît ni les assistants de code IA ni Mistral Vibe.

---

## Partie 1 — Pour tous

### De quoi parle-t-on ?

**Mistral Vibe** est un assistant de programmation fonctionnant avec une intelligence artificielle de l'entreprise française Mistral AI. On lui écrit en langage courant (« corrige ce test », « explique ce fichier ») et il lit les fichiers, propose des modifications, lance des commandes sur l'ordinateur.

Laissé à lui-même, un tel assistant peut aller trop vite, modifier ce qu'on ne lui a pas demandé ou affirmer qu'un travail est fini sans l'avoir vérifié. Un **harnais** est l'ensemble des fichiers qui encadrent son comportement. On peut le comparer à l'accueil d'un nouveau collaborateur :

| Élément du harnais | Équivalent dans une équipe |
| --- | --- |
| Règles du projet | Le règlement intérieur, lu chaque matin |
| Agents spécialisés | Des fiches de poste : un chef de projet, un relecteur |
| Permissions | Les badges d'accès : certaines portes restent fermées |
| Journal automatique | Le registre des entrées et sorties |
| Recette | La visite de contrôle avant mise en service |

### À quoi servira ce harnais ?

L'objectif final est d'aider à **remettre au propre des tests automatisés** écrits avec l'outil Robot Framework, un test à la fois, sans en changer le comportement. Le projet avance en trois étapes :

1. **Étape 1 (celle-ci)** : construire le socle générique, valable pour n'importe quel projet.
2. **Étape 2** : ajouter le savoir-faire propre aux tests Robot Framework.
3. **Étape 3** : garder une trace de chaque remise au propre pour mesurer si la méthode fonctionne.

### Ce qui a été fait à l'étape 1

- **Un règlement** : l'assistant doit toujours présenter un plan et attendre l'accord avant de modifier quoi que ce soit. Il doit prouver ce qu'il affirme en lançant les vérifications, et s'arrêter pour poser une question quand la demande est ambiguë.
- **Deux rôles** :
  - un **chef de projet**, qui planifie, fait valider, avance étape par étape ;
  - un **relecteur**, qui n'a le droit que de lire et qui donne un avis critique avant toute conclusion.
- **Des interdits** : l'assistant ne peut pas modifier ses propres règles, ni lancer certaines commandes dangereuses (effacement massif de fichiers, écrasement forcé de l'historique partagé).
- **Un journal** : chaque commande lancée par l'assistant est notée automatiquement, avec l'heure et le résultat.
- **Un mode d'emploi** et une **liste de 11 contrôles** à effectuer pour la mise en service.

### Comment le travail a été mené

Le harnais a été construit avec un autre assistant IA (Claude Code), organisé comme une petite équipe : un coordinateur et des « experts » (configuration de Vibe, programmation Python, contrôle qualité). Les règles suivies :

1. **Plan d'abord** : rien n'a été écrit avant validation du plan par le responsable du projet.
2. **Sources officielles uniquement** : chaque affirmation sur Vibe a été vérifiée dans sa documentation ou directement dans son code source, pour la version exacte utilisée (2.25.8).
3. **Contrôle indépendant** : un vérificateur qui n'a pas participé à l'écriture a relu l'ensemble. Il a relevé 5 défauts, qui ont été corrigés puis revérifiés.

### Ce que les vérifications ont appris

Trois découvertes ont changé le plan initial :

- **Un seul « cerveau » pour toute l'équipe.** On voulait donner au relecteur une IA différente, moins chère, pour certaines tâches. Dans cette version de Vibe, c'est impossible : tous les rôles utilisent le même modèle. Ce n'est pas un problème de qualité ; cela supprime seulement une piste d'économie.
- **Les interdits remplaçaient ceux d'origine.** En ajoutant nos propres interdits, on effaçait sans le savoir ceux que Vibe prévoit par défaut. Le défaut a été repéré par le vérificateur et corrigé : les deux listes sont maintenant réunies.
- **Une copie infidèle.** Le texte de base donné aux rôles devait être une copie exacte de celui de Vibe ; la première copie avait été légèrement reformulée par l'outil de lecture. Elle a été refaite à partir du fichier original, et l'identité est maintenant prouvée.

### Ce qui reste à faire

- **La recette** : le harnais n'a encore jamais été lancé dans Vibe. Le responsable doit dérouler les 11 contrôles sur un poste Linux (WSL) et noter les résultats.
- Puis l'**étape 2**.

---

## Partie 2 — Pour les développeurs

### Vocabulaire

| Terme | Définition |
| --- | --- |
| **Modèle (LLM)** | Le moteur d'IA qui génère les réponses. Ici Mistral Medium 3.5, appelé par API. |
| **Agent** | Une configuration de session : prompt système, outils accessibles, modèle, permissions. On choisit l'agent au lancement (`vibe --agent <nom>`). |
| **Sous-agent** | Un agent que le modèle lance lui-même pour une tâche délimitée (outil `task`). Il part d'un contexte vierge, ne voit pas la conversation, ne peut pas poser de question et rend un texte. |
| **Prompt système** | Le texte d'instructions envoyé au modèle avant tout message de l'utilisateur. Il définit son rôle et sa méthode. |
| **Outil (tool)** | Une action que le modèle peut demander : lire un fichier (`read_file`), éditer (`edit`), lancer une commande shell (`bash`), déléguer (`task`), poser une question (`ask_user_question`), tenir une liste de tâches (`todo`). Vibe exécute l'action, éventuellement après approbation humaine. |
| **Permission** | Pour chaque outil : `always` (sans demander), `ask` (demander), `never`. Affinée par des listes d'autorisation (`allowlist`) et d'interdiction (`denylist`). |
| **Hook** | Un script que Vibe exécute automatiquement à un moment donné (avant ou après un outil, en fin de tour), quoi que décide le modèle. C'est le seul mécanisme déterministe. |
| **Skill** | Une procédure écrite en Markdown que le modèle charge à la demande ou que l'utilisateur déclenche par `/nom`. Aucune à cette étape. |
| **Réflexion (thinking)** | Le modèle « raisonne » avant de répondre, ce qui coûte du temps et des jetons. Niveau réglable par modèle. |
| **Compaction** | Quand la conversation devient trop longue, Vibe la résume avec un modèle (ici un modèle plus petit et moins cher). |
| **Dossier de confiance** | Vibe ignore la configuration d'un projet tant que l'utilisateur n'a pas accepté de lui faire confiance. |

### Architecture

Tout le harnais tient dans des fichiers texte versionnés, copiés à la racine du dépôt à outiller. Les chemins sont relatifs.

```text
projet-mistral-vibe/
├── AGENTS.md                    # règles du projet, injectées dans chaque session
├── README.md                    # installation, flux de travail, recette
├── .gitignore                   # journaux et secrets exclus de git
├── .vibe/
│   ├── config.toml              # agent de démarrage, modèles, permissions
│   ├── agents/
│   │   ├── orchestrator.toml    # agent principal
│   │   └── reviewer.toml        # sous-agent de relecture
│   ├── prompts/
│   │   ├── orchestrator.md      # prompt système de l'orchestrateur
│   │   └── reviewer.md          # prompt système du relecteur
│   ├── hooks.toml               # déclaration du hook d'audit
│   ├── hooks/audit_bash.py      # script du hook
│   └── skills/                  # vide (étape 2)
└── tests_harnais/
    └── test_audit_bash.py       # tests automatisés du hook
```

### Déroulement d'une demande

```text
Utilisateur ── vibe ──> agent "plan" (lecture seule)
                          │ lit le code, rédige un plan
                          ▼
                    exit_plan_mode : l'utilisateur valide ou fait corriger
                          │
                          ▼ (Shift+Tab ou vibe --agent orchestrator)
                    agent "orchestrator"
                          │ 1. comprend   2. plan dans todo
                          │ 3. ask_user_question : accord explicite
                          │ 4. exécute une étape à la fois, avec contrôle
                          │ 5. task(agent="reviewer") ──> sous-agent "reviewer"
                          │                                 lit le diff, rend
                          │                                 Bloquant / À corriger / Suggestion
                          │ 6. vérifie (tests)   7. conclut
                          ▼
            hook audit-bash : chaque commande shell est tracée dans .vibe/logs/bash.log
```

Pourquoi deux validations ? L'agent `plan` est fourni par Vibe et ne peut rien écrire, mais le modèle ne peut pas y entrer seul. L'orchestrateur, lui, peut écrire : son prompt impose donc de faire valider son plan par `ask_user_question` avant d'agir.

### Les fichiers en détail

**`AGENTS.md`** (31 lignes). Vibe l'ajoute au prompt système de chaque session. Il contient :
- quatre lignes directrices (réfléchir avant d'agir, simplicité, changements ciblés, critères vérifiables) ;
- la règle « plan validé avant toute écriture » ;
- une méthode de raisonnement en six points (objectif, inconnues, options, étapes, vérification, diagnostic d'échec) ;
- l'obligation de preuve par exécution ;
- l'arrêt sur ambiguïté ;
- les réponses en français.

**`.vibe/config.toml`** :

```toml
default_agent = "plan"                # démarrage en mode plan
active_model  = "mistral-medium-3.5"  # alias intégré à Vibe, réflexion "high"

[compaction_model]                    # résumés de contexte : modèle petit, sans réflexion
name = "mistral-small-latest"
provider = "mistral"
thinking = "off"

[tools.bash]                          # commandes refusées sans demande
denylist = ["gdb", "pdb", "passwd", "nano", "vim", ..., "git push --force", "git push -f", "rm -rf", "rm -fr"]

[tools.edit]                          # le harnais ne peut pas se modifier lui-même
denylist = ["*/.vibe/*"]
```

(Extrait simplifié.)

**Agents** : un fichier TOML par agent, nommé comme l'agent.
- `orchestrator.toml` : `agent_type = "agent"`, prompt `orchestrator`, droit de déléguer sans demande à `explore` (sous-agent d'exploration fourni par Vibe) et à `reviewer`.
- `reviewer.toml` : `agent_type = "subagent"`, outils limités à `read_file`, `grep` et `bash`. Il n'a aucun outil d'écriture, c'est ce qui garantit la lecture seule.

**Prompts** : chacun est une copie exacte du prompt système par défaut de Vibe 2.25.8 (`vibe/core/prompts/cli.md`), suivie d'une section « Ajouts du harnais ». Pourquoi une copie ? Définir un prompt pour un agent *remplace* entièrement celui de Vibe, y compris les consignes d'usage des outils ; on repart donc de l'original pour ne rien perdre. Le relecteur reçoit un format de réponse strict, illustré par un exemple complet : comme il ne peut pas poser de question, l'exemple lui sert de contrat.

**Hook d'audit** :
- Contrat : après chaque appel de l'outil `bash`, Vibe lance `python3 .vibe/hooks/audit_bash.py` et lui envoie sur l'entrée standard un JSON décrivant l'appel (`tool_name`, `tool_input.command`, `tool_status`…). Si le script ne renvoie rien et sort avec le code 0, Vibe continue normalement.
- Le script ajoute une ligne `horodatage  outil  statut  commande` à `.vibe/logs/bash.log`.
- Il est écrit pour ne jamais gêner la session : entrée illisible ou champs manquants sont tolérés, et il sort toujours en succès.
- Six tests pytest couvrent les cas normal, incomplet, non JSON, non UTF-8 et multi-lignes.

### Garde-fous : quatre couches

| Couche | Mécanisme | Dans ce harnais |
| --- | --- | --- |
| Outils disponibles | `enabled_tools` | Le relecteur n'a pas d'outil d'écriture |
| Permission par outil | `always` / `ask` / `never` | Délégation au relecteur sans demande ; le reste suit les défauts de Vibe |
| Listes | `allowlist` / `denylist` | Commandes dangereuses refusées ; `.vibe/` protégé en écriture |
| Hook | Script exécuté à chaque appel | Audit des commandes (pas de blocage à ce stade) |

**Limite assumée** : les listes comparent le début des commandes. `git push --force` est bloqué, mais `git push origin main --force` passe ; seul un hook pourrait analyser la commande complète.

### Modèles retenus

| Rôle | Modèle | Réflexion |
| --- | --- | --- |
| `plan`, `orchestrator` | Mistral Medium 3.5 | haute |
| `reviewer` (et tout futur sous-agent) | Celui de la session, imposé par Vibe 2.25.8 | haute |
| Compaction | Mistral Small 4 | aucune |

Pourquoi aucun réglage plus fin ? Le code de Vibe 2.25.8 montre que :
- un sous-agent ignore le modèle qu'on lui assigne ;
- les niveaux de réflexion « moyen », « haut » et « max » envoient la même valeur à l'API Mistral.

Déclarer des réglages sans effet aurait donné une fausse impression de contrôle.

### Méthode de vérification

- **Version figée.** Toutes les vérifications portent sur Vibe 2.25.8 : documentation officielle, et code source au tag `v2.25.8` quand la documentation est muette ou contredite par le code. Dans ce cas, c'est le code qui fait foi.
- **Chargement des fichiers.** Les fichiers TOML sont chargés avec `tomllib`, la bibliothèque standard Python.
- **Copie des prompts.** Elle est contrôlée par `diff` contre le fichier original téléchargé.
- **Tests du hook.** Ils ont été joués avec pytest (6 réussis, sous Python 3.13 / Windows ; à rejouer en 3.11 sous WSL).
- **Contrôle indépendant.** Un agent vérificateur en lecture seule a contrôlé chaque critère d'acceptation, avec preuve (fichier et ligne, commande et sortie, URL). Il a trouvé 5 non-conformités, toutes corrigées puis revérifiées.

Les faits vérifiés et les décisions, avec leurs sources, sont consignés dans `memoire/VIBE_FAITS_VERIFIES.md` et `memoire/DECISIONS.md` (décisions D-07b, D-08, D-09).

### Points ouverts, tranchés par la recette

| Question | Pourquoi elle compte |
| --- | --- |
| Le hook voit-il l'outil sous le nom `bash` ? | Depuis la 2.25.5, Vibe exécute les sessions avec un nouveau moteur interne, le « Unified Harness ». Il nomme l'outil `file_system.bash` en interne ; si c'est ce nom qui arrive au hook, le filtre ne se déclenche pas. |
| Le hook fonctionne-t-il si `vibe` est lancé depuis un sous-dossier ? | La commande du hook est relative au répertoire courant : échec probable. Il faudra alors toujours lancer depuis la racine, ou rendre la commande absolue. |
| Le relecteur a-t-il accès à `grep` ? | Sous le Unified Harness, cet outil pourrait ne pas être transmis aux sous-agents. |
| Le prompt de base est-il bien celui utilisé par la version installée ? | D'autres variantes du prompt existent dans le code. |

### Utilisation

```bash
uv tool install mistral-vibe==2.25.8   # installation (Linux / WSL)
vibe --setup                           # authentification
# copier AGENTS.md et .vibe/ à la racine du dépôt, puis :
vibe                                   # accepter la confiance du dossier
```

Le détail de l'installation, du flux de travail et des 11 contrôles de recette se trouve dans `projet-mistral-vibe/README.md`.
