#!/usr/bin/env bash
# Export AWS CLI login-session credentials for tools that need static env vars (e.g. Terraform).
set -euo pipefail

if ! aws sts get-caller-identity &>/dev/null; then
  echo "AWS CLI is not authenticated. Run: aws login" >&2
  exit 1
fi

# Terraform does not support ~/.aws/login sessions; export temporary env credentials.
eval "$(aws configure export-credentials --format env)"

export PATH="${HOME}/.local/bin:${PATH}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/infrastructure/terraform"
exec terraform "$@"
