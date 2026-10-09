---
name: rf-conventions
description: Règles de refactorisation et de relecture d'un test Robot Framework 7.1 (syntaxe moderne VAR, IF, FOR, WHILE, TRY, RETURN ; formes dépréciées ; extraction de keywords dans un .resource ; invariants à préserver). À utiliser pour refactoriser, relire ou comparer avant/après un test d'un fichier .robot ou .resource.
user-invocable: false
---
# Conventions Robot Framework 7.1 pour la refacto

Référence : User Guide 7.1, https://robotframework.org/robotframework/7.1/RobotFrameworkUserGuide.html (sections citées entre parenthèses).
Avant d'écrire, lis [examples.md](examples.md) et reproduis sa structure, pas ses noms ni ses données.

## 1. Invariants (une refacto ne change pas ce que le test vérifie)
- **Assertions** : même nombre, même cible, même valeur attendue, même opérateur. Avec Browser, un `Get *` suivi d'un opérateur (`==`, `contains`, `should be`…) est une assertion : retirer l'opérateur la supprime.
- **Données** : mêmes valeurs littérales, variables, fichiers de données, sélecteurs, URL, identifiants.
- **Keywords métier** : mêmes keywords de bibliothèque appelés, dans le même ordre, avec les mêmes arguments. Un regroupement dans un keyword utilisateur est permis s'il conserve cette séquence.
- **Tags** : même ensemble de tags effectifs par test (`[Tags]` + `Test Tags` + tags hérités).
- **Setup / Teardown** : mêmes actions, mêmes niveaux (suite, test, keyword). Déplacer une action dans un `[Teardown]` change le comportement en cas d'échec : seulement si le plan validé le prévoit.
- **Comportement observable** : même statut attendu, même nom de test, mêmes effets de bord (fichiers, appels API, nettoyage).
- **Interdits** (bloquants) : supprimer ou affaiblir une assertion ; l'envelopper dans `Run Keyword And Ignore Error`, `Run Keyword And Return Status` ou `TRY/EXCEPT` sans la relancer ; ajouter `Skip`, `Pass Execution`, `robot:skip` ou `robot:exclude` ; élargir une tolérance, un `timeout` ou un `expected_status=any`.
- Besoin de modifier une bibliothèque Python, une donnée ou une assertion : ne le fais pas ; signale-le (orchestrateur : question à l'utilisateur ; sous-agent : rubrique « Doutes » de ton retour).

## 2. Syntaxe moderne à utiliser
| Forme ancienne | Forme RF 7.1 | Statut (section) |
| --- | --- | --- |
| `[Return]    ${x}` | `RETURN    ${x}` | déprécié en 7.0, avertissement à l'exécution (2.7.6) |
| `Return From Keyword (If)` | `RETURN` (dans un `IF` si conditionnel) | « effectivement déprécié » (2.7.6) |
| `${x}=    Set Variable    v` | `VAR    ${x}    v` | VAR recommandé depuis 7.0 (2.6.3, VAR syntax) |
| `Set Test/Suite/Global Variable` | `VAR    ${x}    v    scope=TEST/SUITE/GLOBAL` | idem (2.6.3) |
| `Create List` / `Create Dictionary` (valeurs fixes) | `VAR    @{l}    a    b` / `VAR    &{d}    k=v` | possible (2.6.3) |
| `Run Keyword If` / `Run Keyword Unless` | `IF / ELSE IF / ELSE / END` | IF recommandé (2.9.4) |
| `Set Variable If` | `IF` + `VAR` dans chaque branche | (2.6.3, 2.9.4) |
| `Exit For Loop (If)` / `Continue For Loop (If)` | `BREAK` / `CONTINUE` (dans un `IF`) | seront dépréciés (2.9.3) |
| `Run Keyword And Ignore Error` / `Run Keyword And Return Status` | `TRY / EXCEPT / ELSE / FINALLY / END` | syntaxe native recommandée (2.9.5) |
| `Repeat Keyword`, boucle manuelle | `FOR ... IN / IN RANGE / IN ENUMERATE / IN ZIP`, `WHILE` | (2.9.1, 2.9.2) |
| `Force Tags` | `Test Tags` | déprécié (2.2.5) |
| `Default Tags` | `[Tags]` sur chaque test concerné (ou `-tag` pour retirer) | déprécié (2.2.5) |
| `*** Setting ***` (singulier) | `*** Settings ***` | avertissement depuis 7.0 (2.1.2) |
| `:FOR` + lignes `\` | `FOR ... END` | retiré en 4.0 : erreur de syntaxe (2.9.1) |

Points d'attention :
- `VAR` crée une variable **locale** par défaut ; `Set Test Variable` la rendait visible aux keywords appelés. Utilise `scope=TEST` si un keyword appelé lit la variable.
- `TRY/EXCEPT` sans motif attrape toute erreur : n'emballe jamais une assertion. Préfère un motif (`EXCEPT    message`, `type=glob`) quand la forme ancienne filtrait.
- `IF` en ligne (`IF    cond    BREAK`) est valide pour un seul keyword ou une seule instruction.
- Les expressions de `IF`/`WHILE` sont évaluées en Python : `'${s}' == 'x'` ou `$s == 'x'` (6.7 Evaluating expressions).
- `WHILE` : garde la limite par défaut (`limit=10000`) ou fixe `limit=` ; jamais de boucle sans sortie.

## 3. Mise en forme
- Séparateur : 4 espaces (2.1.4, 2.1.6). Pas de tabulation. Continuation de ligne : `...`.
- Variables locales en minuscules `${total}`, variables de suite ou globales en majuscules `${URL}` (2.1.6). Casse des keywords : pas de convention forte, suis celle du fichier (Title Case le plus souvent).
- Un `=` dans un argument positionnel peut être lu comme argument nommé (`css=…`, `id=…`) si le keyword accepte des arguments nommés libres : ne déplace pas un tel argument et garde un éventuel échappement `\=` (2.2.2).
- Ne renomme pas un test : son nom sert de sélecteur (`robot --test`) et d'historique.
- Garde les commentaires existants ; n'en ajoute que pour expliquer une règle métier.

## 4. Extraction de keywords
- Extrais une séquence répétée ou un bloc nommable (connexion, création de données) en keyword utilisateur ; garde dans le test les assertions qui font son objet.
- Keyword utilisé par un seul fichier : section `*** Keywords ***` du même fichier. Partagé : un `.resource` existant, ou nouveau sous le dossier de ressources du dépôt (2.8.1).
- Import : `Resource    chemin/relatif.resource` ; le chemin est relatif au fichier qui importe (2.8.1). Un `.resource` n'a pas de section de tests et importe lui-même les bibliothèques qu'il utilise.
- Avant de créer un keyword, cherche (`grep -rn`) un keyword existant de même nom ou de même rôle : réutilise-le s'il fait exactement la même chose, sinon choisis un nom distinct.
- Ne modifie un keyword partagé que si le plan validé le prévoit (tous ses appelants sont affectés).
- Arguments explicites (`[Arguments]`), valeur rendue par `RETURN` ; pas de variable de suite lue en douce si on peut la passer en argument.
- `[Documentation]` d'une ligne sur tout keyword créé.

## 5. Setup, teardown, tags
- `[Setup]` / `[Teardown]` de test, `Suite Setup` / `Test Setup` / `Test Teardown` dans `*** Settings ***` (2.2.6, 2.4.6). `[Teardown]` s'exécute même si le test échoue.
- Plusieurs actions de setup : un keyword utilisateur dédié, pas `Run Keywords` si un keyword nommé est plus lisible (les deux sont valides).
- Tags : `Test Tags` dans les settings, `[Tags]` dans le test. Ne retire, n'ajoute ni ne renomme aucun tag (sélection en CI, rapports).

## 6. Vérification
- La validation est l'exécution réelle du test (`robot --test`), pas `--dryrun` : le dry run ne valide ni les variables ni le comportement (3.5.6).
- Résultat : statut du test dans `output.xml` ; avertissements de dépréciation dans `<errors>`.
