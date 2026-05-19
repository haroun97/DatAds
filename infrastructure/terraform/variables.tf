variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Prefix for resource names"
  type        = string
  default     = "datads"
}

variable "environment" {
  description = "Environment tag (e.g. dev, prod)"
  type        = string
  default     = "prod"
}

variable "database_url" {
  description = "PostgreSQL connection URL for workers (Render or RDS)"
  type        = string
  sensitive   = true
}

variable "api_base_url" {
  type    = string
  default = "https://datads-mock-ad-apis.happygrass-47d99234.germanywestcentral.azurecontainerapps.io"
}

variable "facebook_api_key" {
  type      = string
  sensitive = true
  default   = "facebook_test_key_123"
}

variable "google_token" {
  type      = string
  sensitive = true
  default   = "google_test_token_456"
}

variable "tiktok_token" {
  type      = string
  sensitive = true
  default   = "tiktok_test_token_789"
}

variable "sqs_visibility_timeout_seconds" {
  description = "Must exceed worst-case campaign ingest duration"
  type        = number
  default     = 900
}

variable "sqs_max_receive_count" {
  description = "Retries before message moves to DLQ"
  type        = number
  default     = 3
}

variable "facebook_schedule_expression" {
  type    = string
  default = "rate(1 hour)"
}

variable "google_schedule_expression" {
  type    = string
  default = "rate(2 hours)"
}

variable "tiktok_schedule_expression" {
  type    = string
  default = "rate(3 hours)"
}

variable "enable_google_schedule" {
  type    = bool
  default = false
}

variable "enable_tiktok_schedule" {
  type    = bool
  default = false
}

variable "lookback_days" {
  description = "Days of data each scheduled ingest fetches"
  type        = number
  default     = 30
}

variable "worker_cpu" {
  type    = number
  default = 256
}

variable "worker_memory" {
  type    = number
  default = 512
}

variable "worker_desired_count" {
  type    = number
  default = 1
}

variable "worker_image_tag" {
  description = "Docker image tag in ECR (build and push before apply)"
  type        = string
  default     = "latest"
}
