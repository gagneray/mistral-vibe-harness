"""Hook post_tool Vibe 2.26.0 : trace chaque commande shell dans .vibe/logs/bash.log.

Une ligne par appel : horodatage, outil, statut, commande (séparés par des tabulations).
Champs lus sur stdin : tool_name (« file_system.bash » depuis 2.26.0, « bash » avant),
tool_status (success/failure), tool_input.command. Les autres champs sont ignorés.
N'écrit rien sur stdout et sort toujours en code 0 : le hook ne bloque jamais.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent.parent / "logs" / "bash.log"


def read_payload() -> dict:
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def one_line(text: str) -> str:
    return " ".join(text.replace("\t", " ").splitlines())


def main() -> None:
    payload = read_payload()
    tool_input = payload.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None

    fields = [
        datetime.now().isoformat(timespec="seconds"),
        str(payload.get("tool_name") or "-"),
        str(payload.get("tool_status") or "-"),
        one_line(str(command)) if command else "-",
    ]
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as log:
            log.write("\t".join(fields) + "\n")
    except OSError as error:
        print(f"audit_bash: écriture impossible ({error})", file=sys.stderr)


if __name__ == "__main__":
    main()
    sys.exit(0)
