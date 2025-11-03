import boto3
import pandas as pd
import json
import os
from io import StringIO
from datetime import datetime, timezone
import snowflake.connector
from elasticsearch import Elasticsearch, helpers
from transform import transform_data  # your custom logic

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Triggered by S3 upload to SOURCE bucket.
    Reads CSV, applies your transformation logic, saves to PROCESSED bucket,
    and then loads to Snowflake and Elasticsearch.
    """
    try:
        # --- Step 1: Identify source & target buckets ---
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        source_key = event['Records'][0]['s3']['object']['key']
        processed_bucket = os.environ['PROCESSED_BUCKET']

        print(f"📥 Source file: s3://{source_bucket}/{source_key}")
        print(f"📤 Target bucket: s3://{processed_bucket}/")

        # --- Step 2: Read source CSV from S3 ---
        obj = s3_client.get_object(Bucket=source_bucket, Key=source_key)
        df = pd.read_csv(obj['Body'], low_memory=False)
        print(f"✅ Loaded {len(df)} rows from source")

        # --- Step 3: Apply your transformation logic ---
        df_transformed = transform_data(df)
        print(f"✅ Transformed: {len(df_transformed)} rows, {len(df_transformed.columns)} columns")

        # --- Step 4: Save transformed data back to processed bucket ---
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        processed_key = f"transformed_{timestamp}_{os.path.basename(source_key)}"

        csv_buffer = StringIO()
        df_transformed.to_csv(csv_buffer, index=False)

        s3_client.put_object(
            Bucket=processed_bucket,
            Key=processed_key,
            Body=csv_buffer.getvalue(),
            ContentType='text/csv'
        )
        print(f"✅ Saved transformed file to s3://{processed_bucket}/{processed_key}")

        # --- Step 5: Load to Snowflake ---
        rows_sf = load_to_snowflake(df_transformed)
        print(f"✅ Snowflake: {rows_sf} rows loaded")

        # --- Step 6: Load to Elasticsearch ---
        rows_es = load_to_elasticsearch(df_transformed)
        print(f"✅ Elasticsearch: {rows_es} documents indexed")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Pipeline executed successfully',
                'source_file': source_key,
                'processed_file': processed_key,
                'rows_processed': len(df_transformed),
                'snowflake_rows': rows_sf,
                'elasticsearch_docs': rows_es
            })
        }

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Pipeline failed',
                'error': str(e)
            })
        }


# --- Helper: Load transformed data into Snowflake ---
def load_to_snowflake(df):
    SNOWFLAKE_COLUMNS = [
        'id', 'status', 'price', 'bedrooms', 'bathrooms', 'square_feet',
        'address_line_1', 'address_line_2', 'street_number', 'street_name',
        'street_type', 'pre_direction', 'unit_type', 'unit_number',
        'city', 'state', 'zip_code', 'latitude', 'longitude',
        'full_address', 'compass_property_id', 'property_type', 'year_built',
        'presented_by', 'presented_by_first_name', 'presented_by_middle_name',
        'presented_by_last_name', 'presented_by_mobile', 'brokered_by',
        'mls', 'list_date', 'pending_date', 'oh_startTime', 'oh_company',
        'oh_contactName', 'listing_office_id', 'listing_agent_id',
        'email', 'email_1', 'email_2', 'page_link', 'scraped_date'
    ]

    available_cols = [col for col in SNOWFLAKE_COLUMNS if col in df.columns]
    df_filtered = df[available_cols].copy()
    df_filtered.columns = [col.upper() for col in df_filtered.columns]

    conn = snowflake.connector.connect(
        user=os.environ['SNOWFLAKE_USER'],
        password=os.environ['SNOWFLAKE_PASSWORD'],
        account=os.environ['SNOWFLAKE_ACCOUNT'],
        warehouse='ETL_WH',
        database='REAL_ESTATE_DB',
        schema='TRANSACTIONS'
    )

    from snowflake.connector.pandas_tools import write_pandas
    success, nchunks, nrows, _ = write_pandas(conn, df_filtered, 'TRANSACTIONS', auto_create_table=False)
    conn.close()
    return nrows


# --- Helper: Load transformed data into Elasticsearch ---
def load_to_elasticsearch(df):
    es = Elasticsearch(
        [os.environ['ELASTICSEARCH_URL']],
        basic_auth=(os.environ['ELASTICSEARCH_USER'], os.environ['ELASTICSEARCH_PASSWORD']),
        verify_certs=True
    )

    index_name = "real_estate_transactions"
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)

    def generate_actions(df):
        for _, row in df.iterrows():
            doc = row.to_dict()
            doc['loaded_at'] = datetime.now(timezone.utc).isoformat()
            doc = {k: (None if pd.isna(v) else v) for k, v in doc.items()}

            yield {
                "_index": index_name,
                "_id": doc.get('id'),
                "_source": doc
            }

    success, failed = helpers.bulk(es, generate_actions(df), raise_on_error=False)
    return success

