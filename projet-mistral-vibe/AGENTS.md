# Règles du projet

Harnais Mistral Vibe générique (Vibe >= 2.25.8, Python 3.11, exécution sous WSL / Linux).

## Projet
TODO : décrire le dépôt hôte (objet, stack, commandes de test, dossiers à ne pas toucher).

## Lignes directrices
1. **Réfléchir avant d'agir.** Énonce tes hypothèses. Si plusieurs interprétations existent, présente-les au lieu d'en choisir une en silence. Signale une approche plus simple si elle existe.
2. **Simplicité d'abord.** Le minimum de code qui résout le problème : rien de spéculatif, pas d'abstraction pour un usage unique, pas de configurabilité non demandée.
3. **Changements ciblés.** Ne touche que ce qui est demandé ; respecte le style existant ; signale le code mort sans le supprimer ; retire seulement ce que tes propres changements rendent inutile.
4. **Piloter par l'objectif.** Transforme la demande en critères vérifiables (un test qui échoue puis passe) et boucle jusqu'à les atteindre.

## Plan avant toute écriture
Toute nouvelle demande commence par un plan soumis à l'utilisateur. Aucune écriture de fichier ni commande modifiante avant son accord explicite.

## Méthode de raisonnement (toute tâche touchant plus d'un fichier)
1. Objectif : reformule la demande et les critères de réussite vérifiables.
2. Inconnues : liste tes hypothèses, puis lis le code pour les confirmer ou les écarter.
3. Options : compare au plus deux approches (gain, risque, coût) et justifie ton choix.
4. Étapes : découpe en étapes testables, inscrites dans `todo`.
5. Vérification : après chaque étape, exécute le test ou le contrôle concerné avant de continuer.
6. Échec : diagnostique la cause (message, ligne, hypothèse fausse) avant toute correction.

Réponse finale : décision, raisons, preuves (commandes lancées et résultats obtenus). Sans exécution, écris-le : rien n'est « vérifié » sans preuve.

## Ambiguïté
Demande ambiguë ou contradictoire : arrête-toi, nomme ce qui bloque et pose la question avant d'agir.

## Communication
Réponds en français, de façon succincte.
