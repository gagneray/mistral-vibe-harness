# Faits Mistral Vibe vérifiés (cible 2.25.8)

Statuts : **Confirmé** (doc ou code 2.25.8) · **Précisé** (doc et code divergent, choix noté) · **À vérifier** (non documenté, test de recette prévu) · **Infirmé**.
Le guide `reference/guide-harnais-vibe.md` a été validé contre la 2.25.2 le 2026-10-05 ; les écarts 2.25.3 → 2.25.8 viennent du CHANGELOG lu le 2026-10-07.

## Écarts entre le guide (2.25.2) et la 2.25.8

| Fait | Statut | Détail | Source |
| --- | --- | --- | --- |
| Hooks exécutés via un shell | Précisé | Sans shell en 2.25.1–2.25.4 ; depuis 2.25.5, pipes, `&&`, redirections, globs et `$VAR` repassent par le shell. Préférer une commande simple `python3 <script>`. | CHANGELOG 2.25.1, 2.25.5 |
| Hooks dans les sous-agents | Confirmé | 2.25.5 : les hooks tournent dans les sous-agents (filtrer via `parent_session_id` si besoin). | CHANGELOG 2.25.5 |
| Hooks sur l'outil `skill` | Confirmé | 2.25.5 : `pre_tool` / `post_tool` s'appliquent aussi à `skill`. | CHANGELOG 2.25.5 |
| `match` d'un hook | Confirmé | 2.25.5 : correspond à l'outil réellement appelé, `edit` et outils MCP compris. | CHANGELOG 2.25.5 |
| Champs `session_id`, `transcript_path`, `parent_session_id` sur stdin | À vérifier | Le CHANGELOG 2.26.0 indique qu'ils sont « à nouveau » transmis sous le Unified Harness : possiblement absents en 2.25.8. Le hook doit tolérer leur absence. | CHANGELOG 2.26.0 |
| Skills « explicit-only » | À vérifier | 2.25.5 : invocation `/nom` seule possible ; clé de frontmatter non nommée dans le CHANGELOG. | CHANGELOG 2.25.5, doc Skills |
| Sous-agents de `.vibe/agents` | Confirmé | 2.25.8 : de nouveau lançables sous le Unified Harness. | CHANGELOG 2.25.8 |
| `system_prompt_id` d'un agent | Confirmé | 2.25.8 : respecté sous le Unified Harness. | CHANGELOG 2.25.8 |
| Fichier d'agent invalide | Confirmé | 2.25.8 : signalé au lieu de disparaître. | CHANGELOG 2.25.8 |
| `AGENTS.md` racine et sous-dossiers | Confirmé | 2.25.3 et 2.25.8 : chargés dans le prompt système, sous-dossiers à la lecture d'un fichier. | CHANGELOG 2.25.3, 2.25.8 |
| Allowlists de chemins relatifs | Précisé | 2.25.8 : un chemin relatif n'autorise plus un fichier sur simple suffixe commun. Garder des motifs `*/dossier/*`. | CHANGELOG 2.25.8 |
| Contournement des listes shell | Précisé | 2.25.4 : syntaxes de contournement soumises à approbation (CVE-2026-87984 à 87988). | CHANGELOG 2.25.4 |
| Unified Harness | Confirmé | Par défaut depuis 2.25.5 (`--legacy-harness` pour revenir). | CHANGELOG 2.25.5 |
| `thinking_levels` dans `[[models]]` | Infirmé pour 2.25.8 | Accepté seulement à partir de 2.26.0 : ne pas l'utiliser. | CHANGELOG 2.26.0 |

## Points hérités du guide (validation 2026-10-05)

| Fait | Statut | Détail |
| --- | --- | --- |
| Clés des listes outils | Précisé | Doc : `allow`/`deny` ; code : `allowlist`/`denylist`/`sensitive_patterns`, clés inconnues ignorées sans erreur. Retenir `allowlist`/`denylist`, tester en recette. |
| Listes de chemins sur `read_file` / `edit` / `write_file` | Précisé | Dans le code, absentes de la doc ; comparées par glob au chemin absolu (`*/` en tête). |
| Agent par défaut | Précisé | `default` dans la doc, renommé `ask` en 2.24.1. |
| `enabled_skills` | Précisé | Liste blanche : masque aussi les skills fournies par Vibe. |
| Prompts dans `.vibe/prompts/` | Précisé | README : lus et prioritaires à nom égal ; la doc ne cite que `~/.vibe/prompts/`. |
| `system_prompt_id` | Confirmé | Remplace tout le prompt système par défaut. |
| `-p` sans `--agent` | Précisé | Doc et CHANGELOG divergent : toujours passer `--agent`. Outils interactifs désactivés en `-p`. |
| Fichier de plan, `exit_plan_mode` | À vérifier | Seul `Ctrl+G` est documenté ; plan sous `~/.vibe/plans/` (source tierce). |
| Le modèle ne peut pas entrer seul dans l'agent `plan` | Confirmé | Doc Agents. |
| Sous-agents : pas de question, retour texte seul | Confirmé | Doc Agents. |
| Contrat des hooks | Confirmé | JSON stdin ; agir = `exit 0` + JSON stdout (`decision`/`reason` ou `hook_specific_output.additional_context`) ; stdout vide = laisser passer ; `exit 2` = échec du hook ; `post_agent` relance au plus 3 fois par tour. |
| Skills : `user-invocable`, `allowed-tools` restrictif | Confirmé | Doc Skills. |
| Préséance admin > CLI > env > projet > utilisateur | Confirmé | Doc Configuration. |
| Confiance du dossier, `--trust` | Confirmé | Sans confiance, la configuration projet est ignorée. |
| Hook basé sur le texte du transcript | À vérifier | Format interne non documenté. |

## Modèles

| Fait | Statut | Détail | Source |
| --- | --- | --- | --- |
| `active_model` dans un fichier d'agent | Confirmé | Surcharge le modèle global pour cet agent. | Doc Configuration reference, Agents |
| `active_model` appliqué à un sous-agent | À vérifier | Non précisé par la doc ; vérifier via `/log`. | — |
| Clés `[[models]]` | Confirmé | `name`, `provider` (requis), `alias`, `temperature`, `thinking` (défaut `off`), prix, `auto_compact_threshold`. | Doc Configuration reference |
| Noms des niveaux de `thinking` | À vérifier | Cinq niveaux intégrés, non nommés dans la doc ; relever via `/thinking`. | Doc Configuration reference |
| Provider intégré `mistral` | À vérifier | Nom à confirmer dans `/config`. | — |
| `compaction_model` | Confirmé | Clé de premier niveau. | Doc Configuration reference |
| Devstral, Magistral retirés | Confirmé | Remplacés par Medium 3.5 et Small 4. | docs.mistral.ai models overview |
| ID épinglé de Medium 3.5 | À vérifier | Doc : `mistral-medium-3-5` ; un exemple du README écrit `mistral-medium-3.5`. Utiliser `mistral-medium-latest`. | Models overview, README |
