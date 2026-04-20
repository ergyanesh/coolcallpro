#!/usr/bin/env bash
# One-shot installer for the git pre-commit hook.
# Run this once per fresh clone of the repo.
#
# Usage:  bash scripts/install-hooks.sh

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

cp scripts/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "Installed: .git/hooks/pre-commit"
echo "Source:    scripts/pre-commit (version-controlled — edit this, then re-run the installer)"
