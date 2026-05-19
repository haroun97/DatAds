#!/usr/bin/env bash
# Build worker image, push to ECR, and force ECS redeploy.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TF_DIR="$ROOT/infrastructure/terraform"
IMAGE_TAG="${IMAGE_TAG:-latest}"

cd "$TF_DIR"

if [[ ! -f terraform.tfstate ]]; then
  echo "Error: No terraform.tfstate. Run infrastructure deploy first:" >&2
  echo "  cd infrastructure/terraform && terraform apply" >&2
  exit 1
fi

_tf_output() {
  local value
  value="$(terraform output -raw "$1" 2>/dev/null)" || true
  if [[ -z "$value" ]] || [[ "$value" == *"Warning:"* ]] || [[ "$value" == *"No outputs found"* ]]; then
    echo "Error: Terraform output '$1' is missing. Run: terraform apply" >&2
    exit 1
  fi
  printf '%s' "$value"
}

ECR_URL="$(_tf_output ecr_repository_url)"
AWS_REGION="$(_tf_output aws_region)"
CLUSTER="$(_tf_output ecs_cluster_name)"
SERVICE="$(_tf_output ecs_service_name)"

echo "Logging in to ECR: $ECR_URL"
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "${ECR_URL%%/*}"

echo "Building worker image..."
docker build -f "$ROOT/Dockerfile.worker" -t "$ECR_URL:$IMAGE_TAG" "$ROOT"

echo "Pushing..."
docker push "$ECR_URL:$IMAGE_TAG"

echo "Forcing ECS deployment..."
aws ecs update-service \
  --cluster "$CLUSTER" \
  --service "$SERVICE" \
  --force-new-deployment \
  --region "$AWS_REGION" \
  --no-cli-pager

echo "Done. Tail logs: aws logs tail $(terraform output -raw cloudwatch_log_group) --follow --region $AWS_REGION"
