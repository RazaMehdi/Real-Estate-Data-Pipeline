# Source S3 Bucket (where raw CSVs are uploaded)
resource "aws_s3_bucket" "source_bucket" {
  bucket = var.source_bucket_name

  tags = {
    Project = var.project_name
    Purpose = "Source raw CSV files"
  }
}

# Source bucket versioning
resource "aws_s3_bucket_versioning" "source_bucket_versioning" {
  bucket = aws_s3_bucket.source_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Processed S3 Bucket (where transformed data is saved)
resource "aws_s3_bucket" "processed_bucket" {
  bucket = var.processed_bucket_name

  tags = {
    Project = var.project_name
    Purpose = "Transformed/processed data"
  }
}

# Processed bucket versioning
resource "aws_s3_bucket_versioning" "processed_bucket_versioning" {
  bucket = aws_s3_bucket.processed_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Lifecycle policy for processed bucket (optional - auto-delete old files after 90 days)
resource "aws_s3_bucket_lifecycle_configuration" "processed_bucket_lifecycle" {
  bucket = aws_s3_bucket.processed_bucket.id

  rule {
    id     = "delete-old-transformed-files"
    status = "Enabled"

    expiration {
      days = 90  # Keep transformed files for 90 days
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

# S3 notification to trigger Lambda when file uploaded to SOURCE bucket
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.source_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.etl_function.arn
    events              = ["s3:ObjectCreated:*"]  # Triggers on ANY file upload
    filter_suffix       = ".csv"                   # Only CSV files
  }

  depends_on = [aws_lambda_permission.allow_s3_invoke]
}