---
name: refacto-test
description: Refactorise un seul test Robot Framework 7.1 - exécution de référence, plan validé, sous-agent rf-refactorer, test rejoué vert, relecture unique par rf-reviewer, 3 itérations au plus. Usage /refacto-test <fichier.robot>::<nom du test> <consignes>.
user-invocable: true
---
# Refacto d'un test Robot Framework

Lis la demande dans le message `/refacto-test …` qui précède ce texte : `<fichier.robot>::<nom du test>`, puis les consignes. Partie manquante ou ambiguë : pose la question par `ask_user_question` avant toute commande.

Agent requis : `orchestrator`. Si tu n'es pas l'orchestrateur, arrête-toi et demande de passer à `orchestrator` (`Shift+Tab`) puis de relancer la commande. Les invariants et conditions d'arrêt sont dans ton prompt (« Refacto Robot Framework ») ; ce fichier donne les commandes.

Notations : `<F>` fichier du test, `<T>` nom exact du test, `<n>` numéro d'itération (1 à 3).

## Commandes
Sélecteur `<S>` (pour `robot` seulement) : `<T>` entre guillemets simples, en remplaçant dans cet ordre `[` par `[[]`, `*` par `[*]`, `?` par `[?]` ; une apostrophe s'écrit `'\''`. Exemple : `Cas [1] avec *` donne `'Cas [[]1] avec [*]'`.

Cible `<C>` : `<F>`, sauf si un dossier parent de `<F>` contient un `__init__.robot` (`find . -name __init__.robot -not -path './.venv/*'`). Dans ce cas, `<C>` est le plus haut de ces dossiers, `<S>` devient `'*.<Suite>.<T échappé>'` (`<Suite>` dérivé du nom de fichier : `api_utilisateurs.robot` donne `Api Utilisateurs`), et le plan le mentionne.

Exécution (outil bash, délai 300 s, le maximum) puis résumé, `<D>` valant `avant` ou `apres` :
```bash
robot --test <S> --outputdir results/refacto/<D> <C>
python3 .vibe/hooks/resume_resultat.py results/refacto/<D>/output.xml --test '<T>'
```
- Le résumé prend `<T>` non échappé. Lance-le après chaque exécution : le code de retour ne suffit pas (un SKIP donne 0 ; 252 = aucun test sélectionné).
- Délai dépassé : le test dure plus de 300 s, il ne peut pas être validé ici : arrêt.

## Déroulé
1. **Analyse.** Lis `<F>` en entier, les `.resource` importés qui contiennent un keyword du test, les bibliothèques Python appelées (lecture seule), et `historisation_refacto/INDEX.md` s'il existe. Fixe `<C>` et `<S>`.
2. **Référence.** Exécution avec `<D>` = `avant`, puis résumé. Statut autre que PASS : arrêt sans rien écrire, compte rendu (résumé), question.
3. **Plan.** Écris-le dans `todo` et soumets-le par `ask_user_question` : objectif ; changements prévus (`fichier:ligne`) ; keywords partagés touchés ; invariants (nombre d'assertions, keywords de bibliothèque dans l'ordre, tags, setup / teardown, nom du test) ; critère (`<T>` PASS dans `results/refacto/apres`) ; cible `<C>` et pourquoi. Refusé ou amendé : corrige et redemande.
4. **État.** Après accord, `write_file` de `.refacto/courant.json` :
   ```json
   {"fichier": "<F>", "test": "<T>", "statut": "en_cours"}
   ```
5. **Refacto (itération `<n>`).** `spawn` avec `agentType = "rf-refactorer"`, `agentName = "rf-refactorer-<n>"`, `message` selon le gabarit ci-dessous ; puis `wait` (`agentName = "rf-refactorer-<n>"`, `timeoutMs = 600000`), rappelé tant que l'agent n'a pas fini. Lis ses quatre rubriques ; un « Doute » qui exige une décision ou un échec d'écriture : arrêt.
6. **Contrôle.** Exécution avec `<D>` = `apres`, puis résumé.
   - PASS, aucune relecture faite : étape 7. PASS après correction d'un Bloquant : étape 9.
   - FAIL : itération `<n>+1` (étape 5) avec ce résumé ; après la 3e : arrêt.
   - SKIP, INTROUVABLE, ERREUR, délai dépassé : arrêt.
7. **Relecture (une seule).** `spawn` avec `agentType = "rf-reviewer"`, `agentName = "rf-reviewer-1"`, `message` selon le gabarit ; puis `wait` (`agentName = "rf-reviewer-1"`, `timeoutMs = 600000`). Juge chaque point en le vérifiant dans le fichier : accepté ou rejeté, avec la raison.
8. **Bloquant accepté.** Itération `<n>+1` (étape 5) avec les Bloquants acceptés ; après la 3e : arrêt. Aucun Bloquant accepté : étape 9.
9. **Fin.** `write_file` de `.refacto/courant.json` :
   - test PASS dans `results/refacto/apres`, sans édition depuis : `{"fichier": "<F>", "test": "<T>", "statut": "terminee"}` ;
   - arrêt : `{"fichier": "<F>", "test": "<T>", "statut": "arretee", "motif": "<raison en une phrase>"}`.
   Puis la conclusion.

## Gabarit du message pour rf-refactorer
```text
Objectif : refactoriser le test « <T> » de <F> selon le plan validé. Itération <n>/3.
Consignes de l'utilisateur : <consignes, telles quelles>
Plan validé : <objectif, changements, critère>
Invariants : <nombre d'assertions, keywords de bibliothèque dans l'ordre, tags, setup / teardown, nom du test>
Périmètre : écrire uniquement <fichiers .robot / .resource du plan>. Bibliothèques Python, variables et données en lecture seule.
Dernier résultat : <sortie de resume_resultat, ou « référence PASS » à l'itération 1>
Avis du relecteur : <Bloquants acceptés, ou « sans objet »>
Avant d'écrire : lis .vibe/skills/rf-conventions/SKILL.md puis examples.md.
Retour attendu : Fichiers modifiés / Changements / Invariants préservés / Doutes.
```

## Gabarit du message pour rf-reviewer
```text
Objectif : relire en lecture seule la refacto du test « <T> » de <F>.
Plan validé : <objectif, changements, invariants, critère>
Retour de rf-refactorer : <ses quatre rubriques>
Résumé avant : <sortie de resume_resultat sur results/refacto/avant>
Résumé après : <sortie de resume_resultat sur results/refacto/apres>
Résultats complets : results/refacto/avant/output.xml et results/refacto/apres/output.xml.
Avant de relire : lis .vibe/skills/rf-conventions/SKILL.md puis examples.md.
Retour attendu : Bloquant / À corriger / Suggestion, chaque point « chemin:ligne — constat. Correction proposée. »
```

## Conditions d'arrêt
La liste est dans ton prompt (« Refacto Robot Framework », invariants). Arrêt avant l'étape 4 : rien n'est écrit. Arrêt après l'étape 4 : écris d'abord `arretee` avec le motif (étape 9), puis rends compte et pose la question.

## Conclusion
- Demande, cible `<C>`, nombre d'itérations.
- Changements (`fichier:ligne`, avant → après).
- Commandes lancées et résumés avant / après.
- Avis du relecteur : chaque point accepté ou rejeté, avec la raison.
- Points ouverts : « À corriger » et « Suggestion » acceptés, doutes, statut final (`terminee` ou `arretee` et motif).
- Coût et durée : à relever par `/status`.
- Historisation : branchée à l'étape 3.
