"""Tests du hook .vibe/hooks/guard_subagent_write.py."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parent.parent / ".vibe" / "hooks" / "guard_subagent_write.py"


def payload(file_path=None, parent="s-parent", tool_name="file_system.search_replace"):
    tool_input = {"file_path": file_path, "content": "..."} if file_path else {"content": "..."}
    return {
        "session_id": "s-enfant",
        "parent_session_id": parent,
        "transcript_path": "/home/user/.vibe/logs/session/s-enfant",
        "cwd": "/home/user/depot",
        "hook_event_name": "pre_tool",
        "tool_name": tool_name,
        "tool_input": tool_input,
    }


def run(stdin_data, cwd: Path):
    if not isinstance(stdin_data, bytes):
        stdin_data = json.dumps(stdin_data).encode("utf-8")
    result = subprocess.run([sys.executable, str(SOURCE)], input=stdin_data,
                            capture_output=True, cwd=cwd)
    assert result.returncode == 0
    return json.loads(result.stdout) if result.stdout.strip() else None


@pytest.mark.parametrize("parent", [None, ""])
def test_orchestrateur_passe(tmp_path, parent):
    assert run(payload("src/outil.py", parent=parent), tmp_path) is None


def test_orchestrateur_sans_champ_parent(tmp_path):
    data = payload("src/outil.py")
    del data["parent_session_id"]
    assert run(data, tmp_path) is None


@pytest.mark.parametrize("chemin", ["tests/connexion.robot", "resources/Commun.RESOURCE"])
def test_sous_agent_fichier_rf_passe(tmp_path, chemin):
    assert run(payload(chemin, tool_name="file_system.write_file"), tmp_path) is None


@pytest.mark.parametrize("chemin", ["libs/outil.py", "notes.txt"])
def test_sous_agent_autre_fichier_refuse(tmp_path, chemin):
    sortie = run(payload(chemin), tmp_path)
    assert sortie["decision"] == "deny"
    assert chemin in sortie["reason"] and "orchestrateur" in sortie["reason"]


def test_sous_agent_chemin_absent_refuse(tmp_path):
    assert run(payload(None), tmp_path)["decision"] == "deny"


@pytest.mark.parametrize("stdin_data", [b"pas du json", b"\xff\xfe{}", b"[1, 2]"])
def test_payload_invalide_passe(tmp_path, stdin_data):
    assert run(stdin_data, tmp_path) is None
