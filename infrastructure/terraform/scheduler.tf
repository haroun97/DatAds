resource "aws_scheduler_schedule" "facebook_ingest" {
  name       = "${local.name_prefix}-facebook-ingest"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = var.facebook_schedule_expression
  schedule_expression_timezone = "UTC"

  target {
    arn      = aws_sqs_queue.ingest_jobs.arn
    role_arn = aws_iam_role.scheduler.arn

    input = jsonencode({
      job_type      = "ingest_platform"
      platform      = "facebook"
      lookback_days = var.lookback_days
    })
  }
}

resource "aws_scheduler_schedule" "google_ingest" {
  count = var.enable_google_schedule ? 1 : 0

  name       = "${local.name_prefix}-google-ingest"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = var.google_schedule_expression
  schedule_expression_timezone = "UTC"

  target {
    arn      = aws_sqs_queue.ingest_jobs.arn
    role_arn = aws_iam_role.scheduler.arn

    input = jsonencode({
      job_type      = "ingest_platform"
      platform      = "google"
      lookback_days = var.lookback_days
    })
  }
}

resource "aws_scheduler_schedule" "tiktok_ingest" {
  count = var.enable_tiktok_schedule ? 1 : 0

  name       = "${local.name_prefix}-tiktok-ingest"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = var.tiktok_schedule_expression
  schedule_expression_timezone = "UTC"

  target {
    arn      = aws_sqs_queue.ingest_jobs.arn
    role_arn = aws_iam_role.scheduler.arn

    input = jsonencode({
      job_type      = "ingest_platform"
      platform      = "tiktok"
      lookback_days = var.lookback_days
    })
  }
}
