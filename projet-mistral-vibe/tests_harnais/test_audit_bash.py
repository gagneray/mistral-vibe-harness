"""Tests du hook .vibe/hooks/audit_bash.py."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parent.parent / ".vibe" / "hooks" / "audit_bash.py"

PAYLOAD_NORMAL = {
    "session_id": "s-1",
    "hook_event_name": "post_tool",
    "tool_name": "bash",
    "tool_call_id": "c-1",
    "tool_input": {"command": "ls -la"},
    "tool_status": "success",
    "duration_ms": 12,
}

# Charge utile réelle d'un appel shell sous Vibe 2.26.0 (_foreign_hooks.py).
PAYLOAD_2_26_0 = {
    "session_id": "s-2",
    "parent_session_id": None,
    "transcript_path": "/home/user/.vibe/logs/session/s-2",
    "cwd": "/home/user/test-etape-1",
    "hook_event_name": "post_tool",
    "tool_name": "file_system.bash",
    "tool_call_id": "c-2",
    "tool_input": {"command": "git status"},
    "tool_status": "failure",
    "tool_output": None,
    "tool_output_text": "",
    "tool_error": "exit code 128",
    "duration_ms": 0,
}


@pytest.fixture
def hook(tmp_path):
    """Copie le hook dans un faux dépôt et l'exécute depuis un autre dossier."""
    script = tmp_path / ".vibe" / "hooks" / "audit_bash.py"
    script.parent.mkdir(parents=True)
    shutil.copy(SOURCE, script)
    other_cwd = tmp_path / "ailleurs"
    other_cwd.mkdir()

    def run(stdin_data: str | bytes):
        if isinstance(stdin_data, str):
            stdin_data = stdin_data.encode("utf-8")
        result = subprocess.run(
            [sys.executable, str(script)],
            input=stdin_data,
            capture_output=True,
            cwd=other_cwd,
        )
        log = tmp_path / ".vibe" / "logs" / "bash.log"
        lines = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
        return result, lines

    return run


def test_payload_normal(hook):
    result, lines = hook(json.dumps(PAYLOAD_NORMAL))
    assert result.returncode == 0
    assert result.stdout == b""
    assert len(lines) == 1
    fields = lines[0].split("\t")
    assert fields[1:] == ["bash", "success", "ls -la"]


def test_payload_2_26_0(hook):
    result, lines = hook(json.dumps(PAYLOAD_2_26_0))
    assert result.returncode == 0
    assert result.stdout == b""
    assert len(lines) == 1
    assert lines[0].split("\t")[1:] == ["file_system.bash", "failure", "git status"]


@pytest.mark.parametrize("payload", [{}, {"tool_name": "bash", "tool_status": "failure"}])
def test_payload_incomplet(hook, payload):
    result, lines = hook(json.dumps(payload))
    assert result.returncode == 0
    assert result.stdout == b""
    assert len(lines) == 1
    assert lines[0].split("\t")[3] == "-"


def test_stdin_non_json(hook):
    result, lines = hook("pas du json")
    assert result.returncode == 0
    assert result.stdout == b""
    assert len(lines) == 1
    assert lines[0].split("\t")[1:] == ["-", "-", "-"]


def test_commande_multi_lignes(hook):
    payload = dict(PAYLOAD_NORMAL, tool_input={"command": "cd src\n\tgit status\r\necho fin"})
    result, lines = hook(json.dumps(payload))
    assert result.returncode == 0
    assert len(lines) == 1
    fields = lines[0].split("\t")
    assert len(fields) == 4
    assert "\n" not in fields[3] and "\r" not in fields[3]
    assert fields[3].startswith("cd src") and fields[3].endswith("echo fin")


def test_stdin_non_utf8(hook):
    result, lines = hook(b'\xff\xfe{"tool_name": "bash"}')
    assert result.returncode == 0
    assert result.stdout == b""
    assert len(lines) == 1
    assert lines[0].split("\t")[1:] == ["-", "-", "-"]
