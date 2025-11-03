import snowflake.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Testing Snowflake connection...")
print(f"Account: {os.getenv('SNOWFLAKE_ACCOUNT')}")
print(f"User: {os.getenv('SNOWFLAKE_USER')}")

try:
    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse='ETL_WH',
        database='REAL_ESTATE_DB',
        schema='TRANSACTIONS'
    )
    
    print("✅ Connection successful!")
    
    # Test query
    cursor = conn.cursor()
    cursor.execute("SELECT CURRENT_VERSION()")
    version = cursor.fetchone()
    print(f"✅ Snowflake version: {version[0]}")
    
    # Check if table exists
    cursor.execute("SHOW TABLES LIKE 'TRANSACTIONS'")
    tables = cursor.fetchall()
    if tables:
        print(f"✅ Table TRANSACTIONS exists")
    else:
        print("❌ Table TRANSACTIONS not found!")
    
    # Check table structure
    cursor.execute("DESCRIBE TABLE TRANSACTIONS")
    columns = cursor.fetchall()
    print(f"✅ Table has {len(columns)} columns")
    
    # Check row count
    cursor.execute("SELECT COUNT(*) FROM TRANSACTIONS")
    count = cursor.fetchone()
    print(f"✅ Current row count: {count[0]}")
    
    conn.close()
    print("\n✅ All Snowflake tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Check your SNOWFLAKE_ACCOUNT format (should be: abc12345.us-east-1.aws)")
    print("2. Verify username and password")
    print("3. Make sure warehouse ETL_WH is running")