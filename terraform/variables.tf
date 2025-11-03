variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-north-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "real-estate-etl"
}

variable "source_bucket_name" {
  description = "S3 bucket for raw CSV files (source)"
  type        = string
}

variable "processed_bucket_name" {
  description = "S3 bucket for transformed data (output)"
  type        = string
}

variable "snowflake_user" {
  description = "Snowflake username"
  type        = string
  sensitive   = true
}

variable "snowflake_password" {
  description = "Snowflake password"
  type        = string
  sensitive   = true
}

variable "snowflake_account" {
  description = "Snowflake account identifier"
  type        = string
}

variable "elasticsearch_url" {
  description = "Elasticsearch cluster URL"
  type        = string
}

variable "elasticsearch_user" {
  description = "Elasticsearch username"
  type        = string
  sensitive   = true
}

variable "elasticsearch_password" {
  description = "Elasticsearch password"
  type        = string
  sensitive   = true
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 600
}

variable "lambda_memory_size" {
  description = "Lambda function memory in MB"
  type        = number
  default     = 2048
}

variable "lambda_bucket_name" {
  description = "S3 bucket name where Lambda deployment package (ZIP) is stored"
  type        = string
}