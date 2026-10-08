#!/usr/bin/env bash
# Assemble un dépôt git de test : harnais (../projet-mistral-vibe) + projet_exemple.
# Usage (sous WSL) : bash preparer.sh [dossier_cible]   (défaut : ~/test-etape-1)
set -euo pipefail

ICI="$(cd "$(dirname "$0")" && pwd)"
HARNAIS="$ICI/../projet-mistral-vibe"
CIBLE="${1:-$HOME/test-etape-1}"

if [ -e "$CIBLE" ]; then
    echo "Existe déjà : $CIBLE (supprimez-le ou passez un autre chemin)" >&2
    exit 1
fi
mkdir -p "$CIBLE"

# Projet exemple
cp -r "$ICI/projet_exemple/src" "$ICI/projet_exemple/tests" "$CIBLE/"

# Harnais, sans les fichiers locaux
cp -r "$HARNAIS/.vibe" "$HARNAIS/tests_harnais" "$HARNAIS/.gitignore" "$CIBLE/"
rm -rf "$CIBLE/.vibe/logs"
find "$CIBLE" \( -name __pycache__ -o -name .pytest_cache \) -prune -exec rm -rf {} +

# AGENTS.md : la section « Projet » reçoit la description du projet exemple
awk -v f="$ICI/projet_exemple/PROJET.md" \
    '/^TODO : décrire le dépôt hôte/ { while ((getline l < f) > 0) print l; next } { print }' \
    "$HARNAIS/AGENTS.md" > "$CIBLE/AGENTS.md"

cd "$CIBLE"
git init -q
git add -A
git -c user.name="recette" -c user.email="recette@example.invalid" \
    commit -qm "État initial : harnais + projet exemple"

echo "Dépôt de test prêt : $CIBLE"
