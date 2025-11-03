# Real Estate Transactions ETL Pipeline

Automated serverless data pipeline that processes real estate transaction data from CSV files, applies transformations, and loads into Snowflake (data warehouse) and Elasticsearch (search engine) for analytics and querying.

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Data Transformations](#data-transformations)
- [Usage](#usage)
- [Monitoring](#monitoring)
- [Testing](#testing)
- [Challenges & Solutions](#challenges--solutions)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)

---

## 🎯 Overview

This project implements an **event-driven ETL pipeline** that automatically processes real estate transaction data when CSV files are uploaded to AWS S3. The pipeline performs data quality checks, applies business logic transformations, and loads the cleansed data into both a data warehouse (Snowflake) and a search engine (Elasticsearch) for different analytical use cases.

**Key Highlights:**
- ⚡ **Event-driven**: Automatically triggers on file upload (no manual intervention)
- 🔄 **Serverless**: Uses AWS Lambda (no server management)
- 📊 **Dual storage**: Snowflake for SQL analytics, Elasticsearch for full-text search
- 🛡️ **Infrastructure as Code**: Terraform for reproducible deployments
- 🧪 **Tested**: Local testing framework before production deployment

---

## 🏗️ Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW                                  │
└─────────────────────────────────────────────────────────────────────┘

  CSV File Upload
       ↓
┌──────────────────┐
│  S3 Source       │  ← Manual upload or automated drop
│  Bucket          │     (real-estate-transactions-pipeline)
└────────┬─────────┘
         │
         │ S3 Event Notification (ObjectCreated)
         ↓
┌──────────────────┐
│  AWS Lambda      │  ← Serverless compute
│  Function        │     • Reads CSV from S3
│                  │     • Applies 8 transformations
│  + Lambda Layer  │     • Validates data
│  (Dependencies)  │     • Loads to targets
└────────┬─────────┘
         │
         ├──────────────────┬──────────────────┐
         ↓                  ↓                  ↓
┌─────────────────┐  ┌─────────────┐  ┌──────────────┐
│ S3 Processed    │  │ Snowflake   │  │ Elasticsearch│
│ Bucket          │  │ Data        │  │ Search       │
│                 │  │ Warehouse   │  │ Engine       │
│ • Backup        │  │             │  │              │
│ • Audit trail   │  │ • SQL       │  │ • Full-text  │
│ • Versioned     │  │ • Analytics │  │ • Geo search │
└─────────────────┘  └─────────────┘  └──────────────┘
```

### Component Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                      AWS Lambda Function                        │
│  Name: RealEstatePipelineLambda                                │
│  Runtime: Python 3.11 | Memory: 3008 MB | Timeout: 10 min     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Lambda Code (15 KB)                                     │  │
│  │  ├─ lambda_function.py  (orchestration)                  │  │
│  │  └─ transform.py        (transformation logic)           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          ↓ imports                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Lambda Layer: real-estate-dependencies (~150 MB)        │  │
│  │  ├─ pandas              (data manipulation)              │  │
│  │  ├─ snowflake-connector (warehouse connection)           │  │
│  │  ├─ elasticsearch       (search engine connection)       │  │
│  │  ├─ pyarrow             (efficient data formats)         │  │
│  │  ├─ python-slugify      (ID generation)                  │  │
│  │  └─ nameparser          (name parsing)                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

- **Automated Processing**: Event-driven architecture eliminates manual intervention
- **Data Quality**: Filters unnecessary columns, handles missing values, standardizes formats
- **Scalable**: Processes files up to 500 MB, can be extended for larger datasets
- **Idempotent**: Safe to reprocess same file (unique transaction IDs prevent duplicates)
- **Monitored**: CloudWatch logs for debugging and audit trails
- **Versioned**: S3 versioning for both source and processed data
- **Multi-target Loading**: Simultaneous loading to Snowflake and Elasticsearch
- **Cost-Effective**: Serverless architecture (pay only for execution time)

---

## 🛠️ Tech Stack

### Cloud Infrastructure
- **AWS S3**: Object storage for raw and processed data
- **AWS Lambda**: Serverless compute for ETL processing
- **AWS IAM**: Security and access management
- **AWS CloudWatch**: Logging and monitoring

### Data Platforms
- **Snowflake**: Cloud data warehouse for SQL analytics
  - Database: `REAL_ESTATE_DB`
  - Schema: `TRANSACTIONS`
  - Warehouse: `ETL_WH` (X-Small)
- **Elasticsearch**: Distributed search and analytics engine
  - Index: `real_estate_transactions`
  - Cluster: Elastic Cloud (14-day trial)

### Development Tools
- **Python 3.11**: Primary programming language
- **Docker**: For building Lambda deployment packages
- **Terraform**: Infrastructure as Code (optional deployment method)
- **Git**: Version control

### Python Libraries
- `pandas==2.0.3`: Data manipulation and transformation
- `snowflake-connector-python[pandas]==3.0.4`: Snowflake integration
- `elasticsearch==8.9.0`: Elasticsearch client
- `python-slugify==8.0.1`: URL-friendly ID generation
- `nameparser==1.1.2`: Human name parsing
- `pyarrow>=10.0.0`: Columnar data format support

---

## 📁 Project Structure
```
real-estate-pipeline/
├── README.md                          # This file
├── PROJECT_DOCUMENTATION.pdf          # Detailed documentation
├── .gitignore                         # Git ignore rules
│
├── lambda/                            # Lambda function code
│   ├── lambda_function.py             # Main handler & orchestration
│   ├── transform.py                   # Transformation logic (8 operations)
│   ├── requirements.txt               # Python dependencies
│   ├── build_with_layer.sh            # Build script for deployment package
│   └── lambda_code.zip                # Deployment artifact (generated)
│
├── tests/                             # Local testing
│   ├── test_snowflake.py              # Snowflake connection test
│   ├── test_elasticsearch.py          # Elasticsearch connection test
│   └── test_pipeline.py               # End-to-end pipeline test
│
├── terraform/                         # Infrastructure as Code (optional)
│   ├── main.tf                        # Terraform configuration
│   ├── variables.tf                   # Input variables
│   ├── s3.tf                          # S3 bucket resources
│   ├── lambda.tf                      # Lambda function resources
│   ├── iam.tf                         # IAM roles and policies
│   ├── outputs.tf                     # Output values
│   └── terraform.tfvars.example       # Example configuration
│
├── sample_data/                       # Test data
│   └── transactions_data.csv          # Sample real estate data
│
├── sql/                               # Database scripts
│   └── snowflake_setup.sql            # Snowflake table DDL
│
├── docs/                              # Additional documentation
│   ├── architecture_diagram.png       # Visual architecture
│   └── transformation_logic.md        # Detailed transformation docs
│
└── .env.example                       # Environment variables template
```

---

## 📋 Prerequisites

### Accounts Required
- **AWS Account** (Free tier eligible)
  - S3 bucket creation
  - Lambda function deployment
  - IAM role management

- **Snowflake Account** (30-day trial, $400 credit)
  - Standard edition
  - AWS cloud provider (same region as Lambda)

- **Elasticsearch Account** (14-day trial)
  - Elastic Cloud deployment
  - Or AWS OpenSearch Service

### Local Development
- **Python 3.11+**
- **Docker** (for building Lambda packages)
- **AWS CLI** (configured with credentials)
- **Git**

---

## 🚀 Setup Instructions

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/real-estate-pipeline.git
cd real-estate-pipeline
```

### Step 2: Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r lambda/requirements.txt
```

### Step 3: Configure Credentials

Create `.env` file (don't commit this):
```bash
# Snowflake
SNOWFLAKE_USER=your-email@example.com
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=abc12345.us-east-1.aws

# Elasticsearch
ELASTICSEARCH_URL=https://your-cluster.es.io:9243
ELASTICSEARCH_USER=elastic
ELASTICSEARCH_PASSWORD=your_password

# AWS (for local testing)
AWS_REGION=us-east-1
S3_SOURCE_BUCKET=real-estate-transactions-pipeline
S3_PROCESSED_BUCKET=real-estate-transactions-pipeline-transformed-data
```

### Step 4: Set Up Snowflake
```sql
-- Create warehouse
CREATE WAREHOUSE ETL_WH
  WITH WAREHOUSE_SIZE = 'X-SMALL'
  AUTO_SUSPEND = 300
  AUTO_RESUME = TRUE;

-- Create database and schema
CREATE DATABASE REAL_ESTATE_DB;
CREATE SCHEMA REAL_ESTATE_DB.TRANSACTIONS;

-- Create table (see sql/snowflake_setup.sql for full DDL)
USE SCHEMA REAL_ESTATE_DB.TRANSACTIONS;
-- Run the DDL from sql/snowflake_setup.sql
```

### Step 5: Set Up Elasticsearch
```bash
# Create index via Kibana Dev Tools or API
curl -X PUT "https://your-cluster:9243/real_estate_transactions" \
  -u elastic:your_password \
  -H 'Content-Type: application/json' \
  -d '{
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 1
    }
  }'
```

### Step 6: Test Locally
```bash
# Test Snowflake connection
python tests/test_snowflake.py

# Test Elasticsearch connection
python tests/test_elasticsearch.py

# Test full pipeline (processes first 10 rows)
python tests/test_pipeline.py
```

### Step 7: Build Lambda Package
```bash
cd lambda

# Build function code and dependencies layer
./build_with_layer.sh

# This creates:
# - lambda_code.zip (your code, ~15 KB)
# - dependencies_layer.zip (libraries, ~150 MB)
```

### Step 8: Deploy to AWS

#### Option A: Manual Deployment (Console)

**8.1: Create IAM Role**
- Go to IAM → Roles → Create role
- Service: Lambda
- Attach policies:
  - `AWSLambdaBasicExecutionRole`
  - `AmazonS3ReadOnlyAccess`
  - Create inline policy for S3 write to processed bucket
- Name: `RealEstateLambdaRole`

**8.2: Create S3 Buckets**
- Source: `real-estate-transactions-pipeline`
- Processed: `real-estate-transactions-pipeline-transformed-data`
- Enable versioning on both

**8.3: Upload Layer to S3**
```bash
aws s3 cp dependencies_layer.zip s3://real-estate-transactions-pipeline/lambda/
```

**8.4: Create Lambda Layer**
- Lambda Console → Layers → Create layer
- Name: `real-estate-dependencies`
- Upload from S3: `s3://real-estate-transactions-pipeline/lambda/dependencies_layer.zip`
- Runtime: Python 3.11
- Architecture: x86_64

**8.5: Create Lambda Function**
- Function name: `RealEstatePipelineLambda`
- Runtime: Python 3.11
- Execution role: `RealEstateLambdaRole`
- Upload code: `lambda_code.zip`
- Add layer: `real-estate-dependencies:1`
- Memory: 3008 MB
- Timeout: 10 minutes
- Environment variables: (Add all from .env)

**8.6: Add S3 Trigger**
- Trigger: S3
- Bucket: `real-estate-transactions-pipeline`
- Event: All object create events
- Suffix: `.csv`

#### Option B: Terraform Deployment
```bash
cd terraform

# Initialize Terraform
terraform init

# Review plan
terraform plan

# Deploy
terraform apply
```

---

## 🔄 Data Transformations

The pipeline applies **8 data transformations**:

### 1. Column Filtering & Renaming
- **Input**: 317 columns (including 284 unnamed columns)
- **Output**: 33 required columns with standardized names
- **Example**: `propertyStatus` → `status`, `numberOfBeds` → `bedrooms`

### 2. Status Standardization
- **Purpose**: Normalize property status values
- **Mapping**:
  - `"Active Under Contract"` → `"Pending"`
  - `"New"` → `"Active"`
  - `"Closed"` → `"Sold"`

### 3. Name Parsing
- **Input**: `presentedBy` (e.g., "John Michael Smith")
- **Output**: 
  - `presented_by_first_name`: "John"
  - `presented_by_middle_name`: "Michael"
  - `presented_by_last_name`: "Smith"
- **Library**: `nameparser` (handles edge cases like "Jr.", "Sr.", hyphens)

### 4. Open House JSON Parsing
- **Input**: JSON string in `openHouse` column
```json
  {"startTime": "2024-01-15 10:00", "company": "ABC Realty", "contactName": "Jane Doe"}
```
- **Output**:
  - `oh_startTime`: "2024-01-15 10:00"
  - `oh_company`: "ABC Realty"
  - `oh_contactName`: "Jane Doe"
- **Original column dropped** after extraction

### 5. Full Address Generation
- **Input**: Separate address components
- **Output**: `full_address` = "123 Main St, Apt 4B, Austin, TX, 78701"
- **Logic**: Concatenates non-null values with proper formatting

### 6. Email Splitting
- **Input**: `email` = "agent1@example.com,agent2@example.com"
- **Output**:
  - `email_1`: "agent1@example.com"
  - `email_2`: "agent2@example.com"
- **Handles**: Single email or missing values

### 7. Transaction ID Generation
- **Input**: Multiple columns (mls, address, city, state, zip)
- **Output**: `id` = "mls12345-123-main-st-austin-tx-78701"
- **Purpose**: Unique identifier for deduplication
- **Library**: `python-slugify` (creates URL-safe IDs)

### 8. Phone Number Cleaning
- **Input**: `realtorMobile` = "(512) 555-1234" or "512-555-1234"
- **Output**: `presented_by_mobile` = "5125551234" (10 digits only)
- **Logic**: Strips non-numeric characters, limits to 10 digits

### Summary Statistics
- **Input**: 100,012 rows × 317 columns
- **Output**: 100,012 rows × 42 columns
- **Processing time**: ~30 seconds (varies by file size)
- **Memory usage**: ~1.5 GB peak

---

## 📖 Usage

### Manual File Upload
```bash
# Upload CSV to trigger pipeline
aws s3 cp your_file.csv s3://real-estate-transactions-pipeline/

# Pipeline automatically:
# 1. Transforms data
# 2. Saves to processed bucket
# 3. Loads to Snowflake
# 4. Loads to Elasticsearch
```

### Query Data

**Snowflake (SQL Analytics):**
```sql
-- Total transactions
SELECT COUNT(*) FROM REAL_ESTATE_DB.TRANSACTIONS.TRANSACTIONS;

-- Average price by city
SELECT CITY, AVG(PRICE) as avg_price, COUNT(*) as count
FROM REAL_ESTATE_DB.TRANSACTIONS.TRANSACTIONS
GROUP BY CITY
ORDER BY avg_price DESC;

-- Properties by status
SELECT STATUS, COUNT(*) as count
FROM REAL_ESTATE_DB.TRANSACTIONS.TRANSACTIONS
GROUP BY STATUS;
```

**Elasticsearch (Search & Filter):**
```bash
# Total documents
curl -u elastic:password \
  "https://your-cluster:9243/real_estate_transactions/_count"

# Search by city
curl -u elastic:password \
  "https://your-cluster:9243/real_estate_transactions/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "match": {
        "city": "Austin"
      }
    }
  }'

# Filter by price range
curl -u elastic:password \
  "https://your-cluster:9243/real_estate_transactions/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "range": {
        "price": {
          "gte": 300000,
          "lte": 500000
        }
      }
    }
  }'
```

---

## 📊 Monitoring

### CloudWatch Logs
```bash
# Real-time logs
aws logs tail /aws/lambda/RealEstatePipelineLambda --follow

# Filter errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/RealEstatePipelineLambda \
  --filter-pattern "ERROR"
```

### Metrics to Monitor
- **Lambda Invocations**: Number of files processed
- **Duration**: Processing time per file
- **Errors**: Failed executions
- **Throttles**: Concurrent execution limits hit
- **Memory Usage**: Peak memory consumption
- **Snowflake Warehouse**: Credit usage
- **S3 Storage**: Bucket size growth

### Success Indicators
✅ CloudWatch logs show: `✅ Snowflake: X rows loaded`  
✅ CloudWatch logs show: `✅ Elasticsearch: X documents indexed`  
✅ Processed file appears in S3 processed bucket  
✅ Row count in Snowflake matches CSV row count  
✅ Document count in Elasticsearch matches CSV row count  

---

## 🧪 Testing

### Unit Tests (Local)
```bash
# Test transformation logic
python tests/test_transform.py

# Test Snowflake connection
python tests/test_snowflake.py

# Test Elasticsearch connection
python tests/test_elasticsearch.py
```

### Integration Test (End-to-End)
```bash
# Process sample data locally
python tests/test_pipeline.py

# Expected output:
# ✅ Loaded 100012 rows
# ✅ Transformed: 42 columns
# ✅ Snowflake: 10 rows loaded (test mode)
# ✅ Elasticsearch: 10 documents indexed (test mode)
```

### Production Test
```bash
# Upload test file
aws s3 cp sample_data/transactions_data.csv \
  s3://real-estate-transactions-pipeline/test_$(date +%s).csv

# Monitor execution
aws logs tail /aws/lambda/RealEstatePipelineLambda --follow

# Verify in Snowflake
SELECT COUNT(*) FROM REAL_ESTATE_DB.TRANSACTIONS.TRANSACTIONS;

# Verify in Elasticsearch
curl -u elastic:password \
  "https://your-cluster:9243/real_estate_transactions/_count"
```

---

## 🚧 Challenges & Solutions

### Challenge 1: Lambda Package Size Limits
**Problem**: Dependencies (pandas, snowflake, pyarrow) exceed Lambda's 250 MB uncompressed limit.

**Solution**: Implemented Lambda Layers architecture
- Separated code (15 KB) from dependencies (150 MB)
- Layers can be reused across multiple functions
- Faster deployments (only update code when logic changes)

### Challenge 2: Large CSV Processing
**Problem**: Files with 100K+ rows consuming excessive memory.

**Solution**: 
- Increased Lambda memory to 3008 MB
- Used pandas `low_memory=False` parameter
- Filtered unnecessary columns early in pipeline (317 → 33 columns)
- Configured Lambda ephemeral storage to 2048 MB

### Challenge 3: Snowflake Connection Overhead
**Problem**: Each Lambda invocation creates new warehouse connection (slow and expensive).

**Solution**:
- Used X-Small warehouse with 5-minute auto-suspend
- Batch inserts using `write_pandas()` for efficiency
- Connection pooling considered for future enhancement

### Challenge 4: Handling Messy Data
**Problem**: CSV contains 284 unnamed columns, inconsistent naming, missing values.

**Solution**:
- Implemented column filtering (drop all `Unnamed: X` columns)
- Whitelist approach: Only keep 33 specified columns
- Null handling in transformation logic
- Data validation before loading

### Challenge 5: Idempotency
**Problem**: Same file uploaded twice would create duplicate records.

**Solution**:
- Generate unique `id` field from address + MLS number
- Snowflake table uses `id` as primary key
- Duplicate inserts fail gracefully (or can implement MERGE)
- Elasticsearch uses `id` as document ID (upsert behavior)

---

## 🔮 Future Enhancements

### Short-Term (1-2 weeks)
- [ ] **Error Notifications**: SNS alerts on pipeline failures
- [ ] **Data Quality Checks**: Great Expectations framework integration
- [ ] **Incremental Loading**: Process only new/changed records
- [ ] **Dead Letter Queue**: Capture failed messages for retry
- [ ] **CI/CD Pipeline**: GitHub Actions for automated testing and deployment

### Medium-Term (1-2 months)
- [ ] **Dimensional Modeling**: Refactor into star schema (facts + dimensions)
- [ ] **SCD Type 2**: Track historical changes in property status/price
- [ ] **Data Catalog**: AWS Glue Data Catalog for metadata management
- [ ] **Monitoring Dashboard**: CloudWatch or Grafana for real-time metrics
- [ ] **Cost Optimization**: Reserved capacity for Snowflake, S3 lifecycle policies

### Long-Term (3-6 months)
- [ ] **Stream Processing**: Kinesis for real-time data ingestion
- [ ] **ML Pipeline**: Price prediction model using SageMaker
- [ ] **API Layer**: REST API for querying data (API Gateway + Lambda)
- [ ] **Data Governance**: Implement data lineage and access controls
- [ ] **Multi-Region**: Deploy in multiple AWS regions for high availability

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:

- Tests are included for new functionality
- Documentation is updated

---


---

## 👤 Author

**Your Name**
- GitHub: 
- Email: mrazam.010124@gmail.com
- Email_for_tools : toolsaccess0101@outlook.com

---

**Last Updated**: Novemebr 2025

**Project Status**: ✅ Production Ready
