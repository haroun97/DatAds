output "aws_region" {
  value = var.aws_region
}

output "sqs_queue_url" {
  description = "Main ingest job queue URL"
  value       = aws_sqs_queue.ingest_jobs.url
}

output "sqs_dlq_url" {
  description = "Dead-letter queue URL"
  value       = aws_sqs_queue.ingest_dlq.url
}

output "ecr_repository_url" {
  description = "Push worker image here before starting ECS tasks"
  value       = aws_ecr_repository.worker.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  value = aws_ecs_service.worker.name
}

output "cloudwatch_log_group" {
  value = aws_cloudwatch_log_group.worker.name
}

output "sns_alerts_topic_arn" {
  value = aws_sns_topic.alerts.arn
}

output "scheduler_facebook_arn" {
  value = aws_scheduler_schedule.facebook_ingest.arn
}
