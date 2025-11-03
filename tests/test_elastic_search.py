from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Testing Elasticsearch connection...")
print(f"URL: {os.getenv('ELASTICSEARCH_URL')}")
print(f"User: {os.getenv('ELASTICSEARCH_USER')}")

try:
    # Connect to Elasticsearch
    es = Elasticsearch(
        [os.getenv('ELASTICSEARCH_URL')],
        basic_auth=(os.getenv('ELASTICSEARCH_USER'), os.getenv('ELASTICSEARCH_PASSWORD')),
        verify_certs=True
    )
    
    # Test connection
    if es.ping():
        print("✅ Connection successful!")
    else:
        print("❌ Connection failed!")
        exit(1)
    
    # Get cluster info
    info = es.info()
    print(f"✅ Cluster name: {info['cluster_name']}")
    print(f"✅ Elasticsearch version: {info['version']['number']}")
    
    # Check if index exists
    index_name = "real_estate_transactions"
    if es.indices.exists(index=index_name):
        print(f"✅ Index '{index_name}' already exists")
        # Get document count
        count = es.count(index=index_name)
        print(f"✅ Current document count: {count['count']}")
    else:
        print(f"⚠️  Index '{index_name}' does not exist yet (will be created during pipeline run)")
    
    print("\n✅ All Elasticsearch tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Check ELASTICSEARCH_URL (should include https:// and port :9243)")
    print("2. Verify username is 'elastic'")
    print("3. Verify password (the long random string)")
    print("4. Check if deployment is ready in Elastic Cloud dashboard")