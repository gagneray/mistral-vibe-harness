"""Tests de .vibe/hooks/resume_resultat.py (fonctions et CLI).

Fixture : fixtures/output_connexion.xml, produit par Robot Framework 7.1 sur une suite
BuiltIn (« Connexion Valide » PASS, « Connexion Refusee » FAIL dans un keyword imbriqué).
fixtures/output_doublon.xml : deux suites d'un dossier, chacune avec un test
« Connexion Valide » PASS (Robot Framework 7.1, chemins source neutralisés).
"""

import subprocess
import sys
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parent.parent / ".vibe" / "hooks"
SOURCE = HOOKS / "resume_resultat.py"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "output_connexion.xml"

sys.path.insert(0, str(HOOKS))
from resume_resultat import formater, resumer  # noqa: E402


def run_cli(*args: str, cwd: Path):
    result = subprocess.run([sys.executable, str(SOURCE), *args], capture_output=True, cwd=cwd)
    return result.returncode, result.stdout.decode("utf-8")


def test_pass():
    resume = resumer(FIXTURE, "Connexion Valide")
    assert resume["statut"] == "PASS"
    assert resume["ligne"] == "5"
    assert resume["fichier"].endswith("connexion.robot")
    assert resume["keyword"] is None


def test_fail_keyword_imbrique():
    resume = resumer(FIXTURE, "Connexion Refusee")
    assert resume["statut"] == "FAIL"
    assert resume["ligne"] == "8"
    assert resume["keyword"] == "Ouvrir Session > Verifier Mot De Passe > Should Be Equal"
    assert resume["message"] == "Mot de passe refusé pour l'utilisateur: mauvais != admin"


def test_nom_normalise():
    assert resumer(FIXTURE, "connexion_refusee")["statut"] == "FAIL"
    assert resumer(FIXTURE, "CONNEXION   VALIDE")["test"] == "Connexion Valide"


def test_doublon():
    resume = resumer(FIXTURE.with_name("output_doublon.xml"), "Connexion Valide")
    assert resume["statut"] == "PASS"
    assert resume["doublons"] == 2
    assert "Attention : 2 tests portent ce nom" in formater(resume)
    assert "doublons" not in resumer(FIXTURE, "Connexion Valide")
    assert "Attention" not in formater(resumer(FIXTURE, "Connexion Valide"))


def test_introuvable():
    resume = resumer(FIXTURE, "Test Inconnu")
    assert resume["statut"] == "INTROUVABLE"
    assert resume["test"] == "Test Inconnu"


def test_fichier_absent(tmp_path):
    resume = resumer(tmp_path / "absent.xml", "Connexion Valide")
    assert resume["statut"] == "ERREUR"
    assert "absent" in resume["message"]


@pytest.mark.parametrize("contenu", ["<robot><suite>", "pas du xml", "<autre/>"])
def test_xml_invalide(tmp_path, contenu):
    xml = tmp_path / "output.xml"
    xml.write_text(contenu, encoding="utf-8")
    assert resumer(xml, "Connexion Valide")["statut"] == "ERREUR"


def test_taille_formatee():
    long = "x" * 3000
    resume = {"statut": "FAIL", "test": long, "fichier": long, "ligne": "1",
              "keyword": long, "message": long}
    assert len(formater(resume).encode("utf-8")) < 2000
    assert len(formater(resumer(FIXTURE, "Connexion Refusee")).encode("utf-8")) < 2000


def test_cli_un_test(tmp_path):
    code, sortie = run_cli(str(FIXTURE), "--test", "Connexion Refusee", cwd=tmp_path)
    assert code == 0
    assert "(FAIL)" in sortie and "Should Be Equal" in sortie and "(PASS)" not in sortie


def test_cli_tous_les_tests(tmp_path):
    code, sortie = run_cli(str(FIXTURE), cwd=tmp_path)
    assert code == 0
    assert "Connexion Valide (PASS)" in sortie and "Connexion Refusee (FAIL)" in sortie


def test_cli_fichier_absent(tmp_path):
    code, sortie = run_cli("absent.xml", cwd=tmp_path)
    assert code == 0
    assert "(ERREUR)" in sortie


def test_cli_sans_argument(tmp_path):
    code, _ = run_cli(cwd=tmp_path)
    assert code != 0
