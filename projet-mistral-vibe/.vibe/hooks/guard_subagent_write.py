"""Hook pre_tool Vibe 2.26.0 : un sous-agent n'écrit que des fichiers .robot ou .resource.

Déclaré avec match = "re:edit|write_file" et strict = true.
Laisse passer (stdout vide) : payload invalide (un hook strict ne doit pas planter),
session principale (parent_session_id vide ou absent), tool_input.file_path terminé par
.robot ou .resource (casse ignorée).
Sinon, refuse : {"decision": "deny", "reason": ...}. Sort toujours en code 0.
"""

import json
import sys

EXTENSIONS_AUTORISEES = (".robot", ".resource")


def read_payload() -> dict | None:
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def main() -> None:
    payload = read_payload()
    if payload is None:
        return
    parent = payload.get("parent_session_id")
    if parent is None or not str(parent).strip():
        return
    tool_input = payload.get("tool_input")
    chemin = tool_input.get("file_path") if isinstance(tool_input, dict) else None
    if isinstance(chemin, str) and chemin.strip().lower().endswith(EXTENSIONS_AUTORISEES):
        return
    reason = (f"rf-refactorer n'écrit que des fichiers .robot ou .resource : {chemin or '(chemin absent)'}. "
              "Signale le besoin à l'orchestrateur.")
    print(json.dumps({"decision": "deny", "reason": reason}))


if __name__ == "__main__":
    main()
    sys.exit(0)
