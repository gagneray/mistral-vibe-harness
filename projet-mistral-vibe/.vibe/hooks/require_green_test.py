"""Hook post_agent Vibe 2.26.0 : pas de fin de tour avec un test refactorisé non vert.

État lu : .refacto/courant.json = {"fichier", "test", "statut"} (écrit par l'orchestrateur).
Laisse passer (stdout vide) : payload invalide, session de sous-agent (parent_session_id
renseigné), état absent ou illisible, statut « arretee » ou inconnu.
Statut « en_cours » ou « terminee » : refuse ({"decision": "deny", "reason": ...}) si
results/refacto/apres/output.xml est absent, si plusieurs tests y portent le nom demandé
(nom ambigu, condition d'arrêt de la skill), si le test n'y est pas PASS, ou si un
.robot / .resource du dépôt a été modifié après ce fichier :
- « en_cours » : toute modification postérieure à output.xml compte ;
- « terminee » : seules comptent les modifications entre output.xml et l'écriture de
  courant.json ; une édition postérieure à « terminee » n'est plus contrôlée.
Sort toujours en code 0 ; Vibe réinjecte le motif au modèle (3 relances au plus).
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from resume_resultat import formater, resumer  # noqa: E402

ETAT = Path(".refacto") / "courant.json"
SORTIE_APRES = Path("results") / "refacto" / "apres"
DOSSIERS_EXCLUS = {"results", ".venv", ".git", ".vibe", "node_modules"}
STATUTS_CONTROLES = {"en_cours", "terminee"}


def read_payload() -> dict:
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def racine_depot(payload: dict) -> Path:
    cwd = payload.get("cwd")
    if isinstance(cwd, str) and cwd.strip() and Path(cwd).is_dir():
        return Path(cwd)
    return Path.cwd()


def fichier_rf_plus_recent(racine: Path, reference: float,
                           limite: float | None = None) -> Path | None:
    """Premier .robot ou .resource modifié après la référence (et au plus à la limite)."""
    for dossier, sous_dossiers, fichiers in os.walk(racine):
        sous_dossiers[:] = [d for d in sous_dossiers if d not in DOSSIERS_EXCLUS]
        for nom in fichiers:
            if nom.lower().endswith((".robot", ".resource")):
                chemin = Path(dossier) / nom
                try:
                    mtime = chemin.stat().st_mtime
                    if mtime > reference and (limite is None or mtime <= limite):
                        return chemin.relative_to(racine)
                except OSError:
                    continue
    return None


def consigne() -> str:
    return (
        "Relance la commande de validation de la skill `refacto-test` (sortie "
        f"{SORTIE_APRES.as_posix()}), puis `resume_resultat.py` ; si l'arrêt est justifié, "
        f"passe le statut de {ETAT.as_posix()} à « arretee » avec un motif."
    )


def verifier(racine: Path, etat: dict, limite: float | None = None) -> str | None:
    """Renvoie le motif de refus, ou None si le test est vert et à jour."""
    test = etat.get("test")
    if not isinstance(test, str) or not test.strip():
        return f"{ETAT.as_posix()} n'indique pas le test refactorisé (champ « test »)."
    output = racine / SORTIE_APRES / "output.xml"
    if not output.is_file():
        return f"Aucun résultat d'exécution après refacto : {(SORTIE_APRES / 'output.xml').as_posix()} est absent."
    resume = resumer(output, test)
    if resume.get("doublons"):
        return (f"Nom ambigu : {resume['doublons']} tests s'appellent « {test} » "
                f"(condition d'arrêt de la skill).\n{formater(resume)}")
    if resume["statut"] != "PASS":
        return f"Le test « {test} » n'est pas PASS après refacto.\n{formater(resume)}"
    recent = fichier_rf_plus_recent(racine, output.stat().st_mtime, limite)
    if recent:
        return (f"{recent.as_posix()} a été modifié après la dernière exécution du test ; "
                f"le résultat n'est plus à jour.\n{formater(resume)}")
    return None


def main() -> None:
    payload = read_payload()
    parent = payload.get("parent_session_id")
    if parent is not None and str(parent).strip():
        return
    racine = racine_depot(payload)
    chemin_etat = racine / ETAT
    if not chemin_etat.is_file():
        return
    try:
        etat = json.loads(chemin_etat.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        print(f"require_green_test: {ETAT.as_posix()} illisible ({error}), contrôle ignoré",
              file=sys.stderr)
        return
    if not isinstance(etat, dict):
        print(f"require_green_test: {ETAT.as_posix()} n'est pas un objet JSON, contrôle ignoré",
              file=sys.stderr)
        return
    statut = etat.get("statut")
    if statut not in STATUTS_CONTROLES:
        if statut != "arretee":
            print(f"require_green_test: statut inconnu {statut!r}, contrôle ignoré",
                  file=sys.stderr)
        return
    limite = chemin_etat.stat().st_mtime if statut == "terminee" else None
    motif = verifier(racine, etat, limite)
    if motif:
        reason = f"{motif}\n{consigne()}"
        print(json.dumps({"decision": "deny", "reason": reason}))


if __name__ == "__main__":
    main()
    sys.exit(0)
