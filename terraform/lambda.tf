# -----------------------------
# Lambda Deployment Setup
# -----------------------------

# Bucket to store Lambda deployment package
resource "aws_s3_bucket" "lambda_bucket" {
  bucket        = var.lambda_bucket_name
  force_destroy = true

  tags = {
    Project = var.project_name
  }
}

resource "aws_lambda_layer_version" "dependencies_layer" {
  filename            = "${path.module}/../custom_layer.zip"
  layer_name          = "${var.project_name}-dependencies"
  compatible_runtimes = ["python3.11"]
  source_code_hash    = filebase64sha256("${path.module}/../custom_layer.zip")

  description = "Custom dependencies layer for the Real Estate ETL pipeline"
}

# -----------------------------
# Lambda Function
# -----------------------------
resource "aws_lambda_function" "etl_function" {
  function_name    = "${var.project_name}-pipeline"
  role             = aws_iam_role.lambda_execution_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.11"
  filename         = "${path.module}/../lambda_package.zip"
  source_code_hash = filebase64sha256("${path.module}/../lambda_package.zip")
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory_size

  # Attach AWS Data Wrangler layer + custom dependencies
  layers = [
    aws_lambda_layer_version.dependencies_layer.arn
  ]

  ephemeral_storage {
    size = 4096
  }

  environment {
    variables = {
      SOURCE_BUCKET          = var.source_bucket_name
      PROCESSED_BUCKET       = var.processed_bucket_name
      SNOWFLAKE_USER         = var.snowflake_user
      SNOWFLAKE_PASSWORD     = var.snowflake_password
      SNOWFLAKE_ACCOUNT      = var.snowflake_account
      ELASTICSEARCH_URL      = var.elasticsearch_url
      ELASTICSEARCH_USER     = var.elasticsearch_user
      ELASTICSEARCH_PASSWORD = var.elasticsearch_password
    }
  }

  tags = {
    Project = var.project_name
  }
}

# -----------------------------
# Lambda Permission for S3 to invoke
# -----------------------------
resource "aws_lambda_permission" "allow_s3_invoke" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.etl_function.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.source_bucket.arn
}

# -----------------------------
# CloudWatch Log Group
# -----------------------------
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.etl_function.function_name}"
  retention_in_days = 7

  tags = {
    Project = var.project_name
  }
}
