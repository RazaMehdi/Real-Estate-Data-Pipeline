output "source_bucket_name" {
  description = "Name of the source S3 bucket (upload CSVs here)"
  value       = aws_s3_bucket.source_bucket.id
}

output "processed_bucket_name" {
  description = "Name of the processed S3 bucket (transformed data)"
  value       = aws_s3_bucket.processed_bucket.id
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.etl_function.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.etl_function.arn
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for Lambda"
  value       = aws_cloudwatch_log_group.lambda_logs.name
}

output "instructions" {
  description = "How to use the pipeline"
  value = <<-EOT
    
    Pipeline deployed successfully!
    
    To trigger the pipeline:
    1. Upload CSV file to: ${aws_s3_bucket.source_bucket.id}
       aws s3 cp your_file.csv s3://${aws_s3_bucket.source_bucket.id}/
    
    2. Lambda will automatically:
       - Transform the data
       - Save to: ${aws_s3_bucket.processed_bucket.id}
       - Load to Snowflake
       - Load to Elasticsearch
    
    3. Check logs:
       aws logs tail ${aws_cloudwatch_log_group.lambda_logs.name} --follow
    
  EOT
}