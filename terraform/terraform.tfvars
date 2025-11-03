# DO NOT COMMIT THIS FILE TO GIT!
aws_region      = "eu-north-1"
project_name    = "real-estate-etl"

source_bucket_name     = "real-estate-transactions-pipeline"      # Where you upload CSVs
processed_bucket_name  = "real-estate-transactions-pipeline-transformed-data" # Where transformed data goes


# Snowflake credentials
snowflake_user     = "RAZA"
snowflake_password = "SigninSnowflake@786"
snowflake_account  = "YSUNLYZ-HJ05342"

# Elasticsearch credentials
elasticsearch_url      = "https://my-deployment-29ddb0.es.eu-north-1.aws.elastic-cloud.com"
elasticsearch_user     = "elastic"
elasticsearch_password = "d01pgokTEjIiEVEVSGD55Seg"

# Lambda configuration
lambda_timeout      = 600
lambda_memory_size  = 2048

lambda_bucket_name = "real-estate-etl-lambda"