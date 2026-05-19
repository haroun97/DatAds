resource "aws_sqs_queue" "ingest_dlq" {
  name                      = "${local.name_prefix}-ingest-dlq"
  message_retention_seconds = 1209600 # 14 days
  tags                      = local.common_tags
}

resource "aws_sqs_queue" "ingest_jobs" {
  name                       = "${local.name_prefix}-ingest-jobs"
  visibility_timeout_seconds = var.sqs_visibility_timeout_seconds
  message_retention_seconds  = 345600 # 4 days
  receive_wait_time_seconds  = 20

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.ingest_dlq.arn
    maxReceiveCount     = var.sqs_max_receive_count
  })

  tags = local.common_tags
}
