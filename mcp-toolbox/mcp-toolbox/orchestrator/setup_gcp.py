import os

def setup_gcp_credentials():
    """Setup Google Cloud credentials"""
    gcp_key_path = os.path.join(os.path.dirname(__file__), 'h2stestcase-626c99ca9bd6.json')
    
    if os.path.exists(gcp_key_path):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = gcp_key_path
        print(f"SUCCESS: Google Cloud credentials set: {gcp_key_path}")
        
        # Test connection
        try:
            from google.cloud import bigquery
            client = bigquery.Client()
            result = client.query("SELECT 1 AS test").result()
            print("SUCCESS: BigQuery connection successful")
            return True
        except Exception as e:
            print(f"ERROR: BigQuery connection failed: {e}")
            return False
    else:
        print(f"ERROR: GCP key file not found at {gcp_key_path}")
        return False

if __name__ == "__main__":
    setup_gcp_credentials()