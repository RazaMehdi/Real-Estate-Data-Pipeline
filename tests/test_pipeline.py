import pandas as pd
import snowflake.connector
from elasticsearch import Elasticsearch, helpers
import os
from dotenv import load_dotenv
from datetime import datetime
import sys
sys.path.append('..')  # To import from parent directory
from transform import transform_data

load_dotenv()

print("="*60)
print("FULL PIPELINE TEST")
print("="*60)

# Step 1: Load sample CSV
print("\n📂 Step 1: Loading CSV file...")
try:
    df = pd.read_csv('../sample_data/transactions_data.csv')
    print(f"✅ Loaded {len(df)} rows with {len(df.columns)} columns")
except FileNotFoundError:
    print("❌ Error: transactions_data.csv not found in sample_data folder")
    exit(1)

# Step 2: Transform data
print("\n🔄 Step 2: Transforming data...")
df_transformed = transform_data(df)
print(f"✅ Transformed data has {len(df_transformed.columns)} columns")

# Step 3: Load to Snowflake (all rows)
print("\n❄️  Step 3: Loading to Snowflake (all rows)...")
try:
    conn = snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse='ETL_WH',
        database='REAL_ESTATE_DB',
        schema='TRANSACTIONS'
    )

    from snowflake.connector.pandas_tools import write_pandas

    # Clean column names
    df_transformed.columns = [
        (
            col.replace(":", "_")
               .replace(" ", "_")
               .strip()
               .upper()
               if not col.startswith('Unnamed')
            else f"COL_{''.join(filter(str.isdigit, col)) or 'UNKNOWN'}"
        )
        for col in df_transformed.columns
    ]

    # Approved schema
    APPROVED_COLUMNS = [
        'STATUS', 'PRICE', 'BEDROOMS', 'BATHROOMS', 'SQUARE_FEET',
        'ADDRESS_LINE_1', 'ADDRESS_LINE_2', 'CITY', 'STATE', 'ZIP_CODE',
        'LATITUDE', 'LONGITUDE', 'COMPASS_PROPERTY_ID', 'PROPERTY_TYPE',
        'YEAR_BUILT', 'PRESENTED_BY_FIRST_NAME', 'PRESENTED_BY_LAST_NAME',
        'PRESENTED_BY_MOBILE', 'FULL_ADDRESS', 'EMAIL_1', 'EMAIL_2',
        'ID', 'LIST_DATE', 'PENDING_DATE', 'LISTING_OFFICE_ID', 'LISTING_AGENT_ID',
        'BROKERED_BY', 'PAGE_LINK', 'SCRAPED_DATE'
    ]

    # Keep only approved columns
    df_transformed = df_transformed[[c for c in APPROVED_COLUMNS if c in df_transformed.columns]]

    # Write all rows to Snowflake
    success, nchunks, nrows, _ = write_pandas(
        conn,
        df_transformed,
        'TRANSACTIONS',
        auto_create_table=False
    )
    print(f"✅ Inserted {nrows} rows into Snowflake")

    # Verify total count
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM TRANSACTIONS")
    total_count = cursor.fetchone()[0]
    print(f"✅ Total rows in Snowflake: {total_count}")

    conn.close()

except Exception as e:
    print(f"❌ Snowflake error: {str(e)}")

# Step 4: Load to Elasticsearch (all rows)
print("\n🔍 Step 4: Loading to Elasticsearch (all rows)...")
try:
    es = Elasticsearch(
        [os.getenv('ELASTICSEARCH_URL')],
        basic_auth=(os.getenv('ELASTICSEARCH_USER'), os.getenv('ELASTICSEARCH_PASSWORD')),
        verify_certs=True
    )
    
    index_name = "real_estate_transactions"

    # Create index if it doesn't exist
    if not es.indices.exists(index=index_name):
        print(f"Creating index: {index_name}")
        es.indices.create(index=index_name)

    es_df = df_transformed.copy()

    # Bulk insert generator
    def generate_actions(df):
        for idx, row in df.iterrows():  # <-- use all rows
            doc = row.to_dict()
            doc['loaded_at'] = datetime.utcnow().isoformat()
            doc = {k: (None if pd.isna(v) else v) for k, v in doc.items()}
            yield {
                "_index": index_name,
                "_id": doc.get('ID', idx),  # fallback if ID is missing
                "_source": doc
            }

    success, failed = helpers.bulk(es, generate_actions(es_df), raise_on_error=False)
    print(f"✅ Inserted {success} documents into Elasticsearch")

    # Refresh and verify
    es.indices.refresh(index=index_name)
    count = es.count(index=index_name)
    print(f"✅ Total documents in Elasticsearch: {count['count']}")

except Exception as e:
    print(f"❌ Elasticsearch error: {str(e)}")

print("\n" + "="*60)
print("✅ FULL PIPELINE TEST COMPLETE!")
print("="*60)
