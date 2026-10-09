# Exemples de refacto Robot Framework 7.1

Trois exemples à imiter et un contre-exemple, tous sur la même structure : consigne, avant, après, changements, invariants vérifiés, à généraliser.
Reproduis la démarche et la structure, pas les noms, les sélecteurs ni les données : chez toi, ce sont ceux du test d'origine qui font foi.

## Exemple 1 — BuiltIn pur : formes dépréciées vers la syntaxe moderne (à imiter)

**Consigne** : « moderniser `Total Du Panier Avec Remise` en syntaxe RF 7 ».

**Avant** (`tests/panier.robot`)
```robotframework
*** Settings ***
Library        Collections
Force Tags     panier

*** Test Cases ***
Total Du Panier Avec Remise
    ${articles}=    Create List    10    25    5    FIN    99
    ${total}=    Calculer Total    ${articles}
    Should Be Equal As Integers    ${total}    40
    ${remise}=    Set Variable    0
    Run Keyword If    ${total} > 30    Set Test Variable    ${remise}    5
    Should Be Equal As Integers    ${remise}    5

*** Keywords ***
Calculer Total
    [Arguments]    ${articles}
    ${somme}=    Set Variable    ${0}
    FOR    ${prix}    IN    @{articles}
        Exit For Loop If    '${prix}' == 'FIN'
        ${somme}=    Evaluate    ${somme} + ${prix}
    END
    [Return]    ${somme}
```

**Après**
```robotframework
*** Settings ***
Library        Collections
Test Tags      panier

*** Test Cases ***
Total Du Panier Avec Remise
    VAR    @{articles}    10    25    5    FIN    99
    ${total}=    Calculer Total    ${articles}
    Should Be Equal As Integers    ${total}    40
    VAR    ${remise}    0
    IF    ${total} > 30
        VAR    ${remise}    5
    END
    Should Be Equal As Integers    ${remise}    5

*** Keywords ***
Calculer Total
    [Arguments]    ${articles}
    VAR    ${somme}    ${0}
    FOR    ${prix}    IN    @{articles}
        IF    '${prix}' == 'FIN'    BREAK
        ${somme}=    Evaluate    ${somme} + ${prix}
    END
    RETURN    ${somme}
```

**Changements** : `Force Tags` → `Test Tags` ; `Create List` et `Set Variable` → `VAR` ; `Run Keyword If` + `Set Test Variable` → bloc `IF` + `VAR` (la variable n'est lue que dans le test : la portée locale suffit) ; `Exit For Loop If` → `IF … BREAK` ; `[Return]` → `RETURN`.

**Invariants vérifiés** : 2 assertions identiques (`40`, `5`) ; données identiques (y compris `FIN` et `99`, qui testent l'arrêt de boucle) ; tag `panier` toujours appliqué ; import `Collections` conservé même s'il paraît inutile ; nom du test inchangé.

**À généraliser** : remplacer chaque forme dépréciée par son équivalent exact, une à une, sans toucher aux valeurs ; vérifier la portée de chaque `Set * Variable` avant de la convertir en `VAR`.

## Exemple 2 — Browser : extraction de keywords dans un .resource (à imiter)

**Consigne** : « extraire la connexion de `Connexion Valide Affiche Le Tableau De Bord` pour la réutiliser ».

**Avant** (`tests/connexion.robot`)
```robotframework
*** Settings ***
Library    Browser

*** Test Cases ***
Connexion Valide Affiche Le Tableau De Bord
    [Tags]    smoke    connexion
    New Browser    chromium    headless=True
    New Page    ${URL}/login
    Fill Text    id=username    ${UTILISATEUR}
    Fill Text    id=password    ${MOT_DE_PASSE}
    Click    css=button[type="submit"]
    Get Text    h1    ==    Tableau de bord
    Get Url    contains    /dashboard
    Close Browser
```

**Après** (`tests/connexion.robot`)
```robotframework
*** Settings ***
Library     Browser
Resource    ../resources/connexion.resource

*** Test Cases ***
Connexion Valide Affiche Le Tableau De Bord
    [Tags]    smoke    connexion
    Ouvrir La Page De Connexion    ${URL}
    Se Connecter    ${UTILISATEUR}    ${MOT_DE_PASSE}
    Get Text    h1    ==    Tableau de bord
    Get Url    contains    /dashboard
    Close Browser
```

**Après** (`resources/connexion.resource`, nouveau ; aucun keyword de même nom trouvé par `grep -rn`)
```robotframework
*** Settings ***
Documentation    Keywords de connexion partagés (Browser).
Library          Browser

*** Keywords ***
Ouvrir La Page De Connexion
    [Documentation]    Ouvre un navigateur et la page de connexion.
    [Arguments]    ${url}
    New Browser    chromium    headless=True
    New Page    ${url}/login

Se Connecter
    [Documentation]    Saisit les identifiants et valide le formulaire.
    [Arguments]    ${utilisateur}    ${mot_de_passe}
    Fill Text    id=username    ${utilisateur}
    Fill Text    id=password    ${mot_de_passe}
    Click    css=button[type="submit"]
```

**Changements** : 5 appels Browser regroupés en 2 keywords utilisateur avec arguments explicites ; import `Resource` relatif au fichier de test.

**Invariants vérifiés** : même séquence d'appels Browser, mêmes arguments et sélecteurs ; les 2 assertions (`Get Text … ==`, `Get Url … contains`) restent dans le test, opérateur compris ; tags `smoke` et `connexion` inchangés ; `Close Browser` reste en fin de test (le passer en `[Teardown]` changerait le comportement en cas d'échec : à proposer dans le plan, pas à décider seul).

**À généraliser** : extraire les étapes de préparation, laisser dans le test ce qu'il vérifie ; chercher un keyword existant avant d'en créer un.

## Exemple 3 — RequestsLibrary : nettoyage toléré et variables (à imiter)

**Consigne** : « remplacer les Run Keyword dans `Creer Un Utilisateur Renvoie 201` ».

**Avant** (`tests/api_utilisateurs.robot`)
```robotframework
*** Settings ***
Library        RequestsLibrary
Library        Collections
Suite Setup    Create Session    api    ${API_URL}

*** Test Cases ***
Creer Un Utilisateur Renvoie 201
    [Tags]    api
    ${corps}=    Create Dictionary    nom=Durand    role=admin
    ${reponse}=    POST On Session    api    /users    json=${corps}    expected_status=201
    Should Be Equal As Strings    ${reponse.json()}[nom]    Durand
    Dictionary Should Contain Key    ${reponse.json()}    id
    ${id}=    Set Variable    ${reponse.json()}[id]
    ${statut}    ${message}=    Run Keyword And Ignore Error    DELETE On Session    api    /users/${id}
    Run Keyword If    '${statut}' == 'FAIL'    Log    Nettoyage impossible : ${message}    WARN
```

**Après**
```robotframework
*** Settings ***
Library        RequestsLibrary
Library        Collections
Suite Setup    Create Session    api    ${API_URL}

*** Test Cases ***
Creer Un Utilisateur Renvoie 201
    [Tags]    api
    VAR    &{corps}    nom=Durand    role=admin
    ${reponse}=    POST On Session    api    /users    json=${corps}    expected_status=201
    Should Be Equal As Strings    ${reponse.json()}[nom]    Durand
    Dictionary Should Contain Key    ${reponse.json()}    id
    VAR    ${id}    ${reponse.json()}[id]
    TRY
        DELETE On Session    api    /users/${id}
    EXCEPT    AS    ${message}
        Log    Nettoyage impossible : ${message}    WARN
    END
```

**Changements** : `Create Dictionary` et `Set Variable` → `VAR` ; `Run Keyword And Ignore Error` + `Run Keyword If` → `TRY/EXCEPT AS`.

**Invariants vérifiés** : `expected_status=201` conservé (c'est une assertion) ; 2 assertions sur le corps conservées ; même corps JSON ; le `DELETE` était toléré avant et l'est toujours (le `TRY` n'entoure que le nettoyage, jamais une assertion) ; `Suite Setup` et tag `api` inchangés.

**À généraliser** : un `TRY/EXCEPT` ne remplace qu'un échec déjà toléré dans la version d'origine ; tout argument `expected_status`, `msg`, `timeout` d'un keyword de bibliothèque se conserve tel quel.

## Contre-exemple — SeleniumLibrary : test qui passe sans rien vérifier (à ne pas reproduire)

**Consigne** : « rendre `Recherche Affiche Des Resultats` moins fragile ».

**Avant** (`tests/recherche.robot`)
```robotframework
*** Test Cases ***
Recherche Affiche Des Resultats
    [Tags]    recherche
    Open Browser    ${URL}    chrome
    Input Text    name=q    robot framework
    Click Button    id=rechercher
    Wait Until Element Is Visible    css=.resultats    timeout=10s
    Element Should Contain    css=.resultats li    Robot Framework
    [Teardown]    Close Browser
```

**Après (FAUX)**
```robotframework
*** Test Cases ***
Recherche Affiche Des Resultats
    [Tags]    recherche
    Open Browser    ${URL}    chrome
    Input Text    name=q    robot framework
    Click Button    id=rechercher
    ${visible}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    css=.resultats    timeout=10s
    IF    ${visible}
        TRY
            Element Should Contain    css=.resultats li    Robot Framework
        EXCEPT
            Log    Résultat inattendu
        END
    END
    [Teardown]    Close Browser
```

**Changements** : l'attente est convertie en booléen, l'assertion est conditionnée puis avalée par un `EXCEPT` sans motif.

**Invariants violés** : sans résultat, ou avec un mauvais résultat, le test passe : les deux vérifications ont disparu. La syntaxe est valide et le test est vert : seul le contrôle des invariants le détecte. Verdict de relecture : **Bloquant**.

**À généraliser** : « moins fragile » ne signifie jamais « vérifie moins ». Si la consigne ne peut être tenue qu'en affaiblissant une assertion (timeout plus long, attente conditionnelle, erreur ignorée), arrête-toi et pose la question.
