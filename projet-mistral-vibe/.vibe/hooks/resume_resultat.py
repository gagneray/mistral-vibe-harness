"""Résumé court d'un output.xml de Robot Framework 7.1, pour l'agent et les hooks.

Usage : python3 .vibe/hooks/resume_resultat.py <output.xml> [--test "<nom>"]
- avec --test : résume ce test ;
- sans --test : résume chaque test (au plus 20).

Résumé (dict) : statut (PASS, FAIL, SKIP, INTROUVABLE, ERREUR), test, fichier (source
de la suite), ligne (attribut line du test), keyword (chemin du keyword le plus profond
en échec, ex. « Ouvrir Session > Should Be Equal »), message (500 caractères au plus),
doublons (nombre de tests du même nom, présent seulement s'il y en a plusieurs).
Fichier absent ou XML invalide : statut ERREUR, code de sortie 0.
"""

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

MESSAGE_MAX = 500
SORTIE_MAX = 2000
TESTS_MAX = 20


def normaliser(nom: str) -> str:
    """Comme Robot Framework : casse, espaces et underscores ignorés."""
    return "".join(nom.split()).replace("_", "").lower()


def tronquer(texte: str, limite: int) -> str:
    return texte if len(texte) <= limite else texte[: limite - 3] + "..."


def statut_de(element: ET.Element) -> ET.Element | None:
    return element.find("status")


def chemin_echec(element: ET.Element) -> list[str]:
    """Descend dans les enfants en FAIL ; ne garde que les noms des éléments <kw>.

    Les structures de contrôle (for, iter, if, branch, try, while, group) sont traversées.
    """
    for enfant in element:
        if enfant.tag in ("status", "msg", "arg", "doc", "tag", "var", "timeout"):
            continue
        statut = statut_de(enfant)
        if statut is not None and statut.get("status") == "FAIL":
            suite = chemin_echec(enfant)
            if enfant.tag == "kw":
                return [enfant.get("name", "?")] + suite
            return suite
    return []


def lister_tests(suite: ET.Element, source: str = ""):
    """Renvoie (test, source de la suite) pour chaque test, dans l'ordre du fichier."""
    source = suite.get("source", source)
    for enfant in suite:
        if enfant.tag == "test":
            yield enfant, source
        elif enfant.tag == "suite":
            yield from lister_tests(enfant, source)


def resume_test(test: ET.Element, source: str) -> dict:
    statut = statut_de(test)
    valeur = statut.get("status", "ERREUR") if statut is not None else "ERREUR"
    message = (statut.text or "").strip() if statut is not None else ""
    chemin = chemin_echec(test) if valeur == "FAIL" else []
    return {
        "statut": valeur,
        "test": test.get("name", ""),
        "fichier": source or None,
        "ligne": test.get("line"),
        "keyword": " > ".join(chemin) or None,
        "message": tronquer(message, MESSAGE_MAX),
    }


def erreur(test: str | None, message: str) -> dict:
    return {"statut": "ERREUR", "test": test, "fichier": None, "ligne": None,
            "keyword": None, "message": tronquer(message, MESSAGE_MAX)}


def charger(chemin_xml) -> tuple[list, dict | None]:
    """Renvoie (liste des (test, source), None) ou ([], résumé ERREUR)."""
    chemin = Path(chemin_xml)
    if not chemin.is_file():
        return [], erreur(None, f"Fichier de résultat absent : {chemin}")
    try:
        racine = ET.parse(chemin).getroot()
    except ET.ParseError as exc:
        return [], erreur(None, f"XML invalide dans {chemin} : {exc}")
    except OSError as exc:
        return [], erreur(None, f"Lecture impossible de {chemin} : {exc}")
    if racine.tag != "robot":
        return [], erreur(None, f"{chemin} n'est pas un output.xml de Robot Framework.")
    tests = []
    for suite in racine.findall("suite"):
        tests.extend(lister_tests(suite))
    return tests, None


def resumer(chemin_xml, test: str | None = None) -> dict:
    """Résume le test demandé ; sans nom, le premier test du fichier.

    Correspondance : égalité exacte, sinon nom normalisé. Plusieurs correspondances :
    la première en échec est retenue (pour ne pas masquer un FAIL), sinon la première,
    et le champ « doublons » donne leur nombre.
    """
    tests, err = charger(chemin_xml)
    if err:
        err["test"] = test
        return err
    if test is None:
        candidats = tests[:1]
    else:
        candidats = [t for t in tests if t[0].get("name") == test]
        if not candidats:
            cible = normaliser(test)
            candidats = [t for t in tests if normaliser(t[0].get("name", "")) == cible]
    if not candidats:
        return {"statut": "INTROUVABLE", "test": test, "fichier": None, "ligne": None,
                "keyword": None,
                "message": f"Aucun test de ce nom dans {chemin_xml}." if test
                else f"Aucun test dans {chemin_xml}."}
    resumes = [resume_test(t, source) for t, source in candidats]
    retenu = next((r for r in resumes if r["statut"] != "PASS"), resumes[0])
    if len(resumes) > 1:
        retenu["doublons"] = len(resumes)
    return retenu


def resumer_tous(chemin_xml, limite: int = TESTS_MAX) -> tuple[list[dict], int]:
    """Renvoie (résumés des premiers tests, nombre total de tests)."""
    tests, err = charger(chemin_xml)
    if err:
        return [err], 0
    return [resume_test(t, source) for t, source in tests[:limite]], len(tests)


def formater(resume: dict) -> str:
    """Quelques lignes lisibles, moins de 2 000 octets en UTF-8."""
    lignes = [f"Test : {resume.get('test') or '-'} ({resume.get('statut')})"]
    if resume.get("doublons"):
        lignes.append(f"Attention : {resume['doublons']} tests portent ce nom")
    if resume.get("fichier"):
        ligne = f":{resume['ligne']}" if resume.get("ligne") else ""
        lignes.append(f"Fichier : {resume['fichier']}{ligne}")
    if resume.get("keyword"):
        lignes.append(f"Keyword en échec : {resume['keyword']}")
    if resume.get("message"):
        lignes.append(f"Message : {resume['message']}")
    texte = "\n".join(lignes)
    octets = texte.encode("utf-8")
    if len(octets) >= SORTIE_MAX:
        texte = octets[: SORTIE_MAX - 4].decode("utf-8", errors="ignore") + "..."
    return texte


def main() -> int:
    parser = argparse.ArgumentParser(description="Résume un output.xml de Robot Framework.")
    parser.add_argument("output_xml")
    parser.add_argument("--test", help="nom du test à résumer")
    args = parser.parse_args()

    if args.test is not None:
        texte = formater(resumer(args.output_xml, args.test))
    else:
        resumes, total = resumer_tous(args.output_xml)
        texte = "\n\n".join(formater(r) for r in resumes)
        if total > len(resumes):
            texte += f"\n\n... {total - len(resumes)} autre(s) test(s) non affiché(s)."
    # Octets UTF-8 : la sortie ne dépend pas de l'encodage de la console.
    sys.stdout.buffer.write((texte + "\n").encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
