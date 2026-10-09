"""Tests du hook .vibe/hooks/require_green_test.py.

Chaque test monte un faux dépôt dans tmp_path : hooks copiés dans .vibe/hooks/, suite
tests/connexion.robot, état .refacto/courant.json et results/refacto/apres/output.xml
(fixture réelle Robot Framework 7.1).
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parent.parent / ".vibe" / "hooks"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "output_connexion.xml"
FIXTURE_DOUBLON = FIXTURE.with_name("output_doublon.xml")

PAYLOAD = {
    "session_id": "s-1",
    "parent_session_id": None,
    "transcript_path": "/home/user/.vibe/logs/session/s-1",
    "cwd": "",
    "hook_event_name": "post_agent",
}


@pytest.fixture
def depot(tmp_path):
    hooks = tmp_path / ".vibe" / "hooks"
    hooks.mkdir(parents=True)
    for nom in ("require_green_test.py", "resume_resultat.py"):
        shutil.copy(HOOKS / nom, hooks / nom)
    robot = tmp_path / "tests" / "connexion.robot"
    robot.parent.mkdir()
    robot.write_text("*** Test Cases ***\n", encoding="utf-8")
    return tmp_path


def ecrire_etat(depot: Path, statut="en_cours", test="Connexion Valide"):
    etat = depot / ".refacto" / "courant.json"
    etat.parent.mkdir(exist_ok=True)
    etat.write_text(json.dumps({"fichier": "tests/connexion.robot", "test": test,
                                "statut": statut}), encoding="utf-8")


def poser_output(depot: Path, decalage_robot: int = -100, decalage_etat: int | None = None,
                 fixture: Path = FIXTURE):
    """Copie la fixture ; décale le mtime du .robot (et de l'état) par rapport à output.xml."""
    output = depot / "results" / "refacto" / "apres" / "output.xml"
    output.parent.mkdir(parents=True)
    shutil.copy(fixture, output)
    reference = output.stat().st_mtime
    robot = depot / "tests" / "connexion.robot"
    os.utime(robot, (reference + decalage_robot, reference + decalage_robot))
    if decalage_etat is not None:
        etat = depot / ".refacto" / "courant.json"
        os.utime(etat, (reference + decalage_etat, reference + decalage_etat))


def run(depot: Path, stdin_data=PAYLOAD, cwd: Path | None = None):
    if not isinstance(stdin_data, bytes):
        stdin_data = json.dumps(stdin_data).encode("utf-8")
    result = subprocess.run([sys.executable, str(depot / ".vibe" / "hooks" / "require_green_test.py")],
                            input=stdin_data, capture_output=True, cwd=cwd or depot)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout) if result.stdout.strip() else None


def test_sans_etat_passe(depot):
    assert run(depot) is None


def test_arretee_passe(depot):
    ecrire_etat(depot, statut="arretee")
    assert run(depot) is None


def test_sous_agent_passe(depot):
    ecrire_etat(depot)
    assert run(depot, dict(PAYLOAD, parent_session_id="s-parent")) is None


@pytest.mark.parametrize("stdin_data", [b"pas du json", b"\xff\xfe", b"[]", json.dumps({})])
def test_payload_invalide_ou_incomplet_passe(depot, stdin_data):
    data = stdin_data.encode("utf-8") if isinstance(stdin_data, str) else stdin_data
    assert run(depot, data) is None


def test_etat_invalide_passe(depot):
    (depot / ".refacto").mkdir()
    (depot / ".refacto" / "courant.json").write_text("{pas du json", encoding="utf-8")
    assert run(depot) is None


@pytest.mark.parametrize("statut", ["en_cours", "terminee"])
def test_pass_a_jour_passe(depot, statut):
    ecrire_etat(depot, statut=statut)
    poser_output(depot)
    assert run(depot) is None


def test_fail_refuse(depot):
    ecrire_etat(depot, test="Connexion Refusee")
    poser_output(depot)
    sortie = run(depot)
    assert sortie["decision"] == "deny"
    assert "Should Be Equal" in sortie["reason"]
    assert "refacto-test" in sortie["reason"] and "results/refacto/apres" in sortie["reason"]
    assert "resume_resultat.py" in sortie["reason"]
    assert "robot --test" not in sortie["reason"]
    assert "arretee" in sortie["reason"]


def test_output_absent_refuse(depot):
    ecrire_etat(depot, statut="terminee")
    sortie = run(depot)
    assert sortie["decision"] == "deny"
    assert "output.xml est absent" in sortie["reason"]


def test_robot_modifie_apres_output_refuse(depot):
    ecrire_etat(depot)
    poser_output(depot, decalage_robot=+100)
    sortie = run(depot)
    assert sortie["decision"] == "deny"
    assert "tests/connexion.robot" in sortie["reason"]


def test_champ_cwd_du_payload(depot, tmp_path_factory):
    ecrire_etat(depot, test="Connexion Refusee")
    poser_output(depot)
    ailleurs = tmp_path_factory.mktemp("ailleurs")
    sortie = run(depot, dict(PAYLOAD, cwd=str(depot)), cwd=ailleurs)
    assert sortie["decision"] == "deny"


def test_terminee_edition_apres_etat_passe(depot):
    ecrire_etat(depot, statut="terminee")
    poser_output(depot, decalage_robot=+100, decalage_etat=+50)
    assert run(depot) is None


def test_terminee_edition_avant_etat_refuse(depot):
    ecrire_etat(depot, statut="terminee")
    poser_output(depot, decalage_robot=+50, decalage_etat=+100)
    sortie = run(depot)
    assert sortie["decision"] == "deny"
    assert "tests/connexion.robot" in sortie["reason"]


def test_en_cours_edition_apres_etat_refuse(depot):
    ecrire_etat(depot)
    poser_output(depot, decalage_robot=+100, decalage_etat=+50)
    assert run(depot)["decision"] == "deny"


def test_doublon_refuse(depot):
    ecrire_etat(depot, statut="terminee")
    poser_output(depot, decalage_etat=+50, fixture=FIXTURE_DOUBLON)
    sortie = run(depot)
    assert sortie["decision"] == "deny"
    assert "Nom ambigu" in sortie["reason"]
    assert "Attention : 2 tests portent ce nom" in sortie["reason"]
