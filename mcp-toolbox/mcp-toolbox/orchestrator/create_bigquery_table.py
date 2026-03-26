#!/usr/bin/env python3
"""Create BigQuery dataset and table for traceability logging"""

from google.cloud import bigquery
import os

def create_bigquery_resources():
    """Create BigQuery dataset and table"""
    try:
        client = bigquery.Client()
        project_id = os.getenv('GOOGLE_PROJECT_ID', 'h2stestcase')
        dataset_id = os.getenv('BIGQUERY_DATASET', 'mcp_toolbox_logs')
        
        # Create dataset
        dataset_ref = client.dataset(dataset_id)
        try:
            client.get_dataset(dataset_ref)
            print(f"✅ Dataset {dataset_id} already exists")
        except:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            client.create_dataset(dataset)
            print(f"✅ Created dataset {dataset_id}")
        
        # Create traceability_log table
        table_id = "traceability_log"
        table_ref = dataset_ref.table(table_id)
        
        try:
            client.get_table(table_ref)
            print(f"✅ Table {table_id} already exists")
        except:
            schema = [
                bigquery.SchemaField("test_case_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("regulatory_chunk_ids", "STRING", mode="REPEATED"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("feedback_count", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("quality_score", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("last_feedback_at", "TIMESTAMP", mode="NULLABLE"),
            ]
            
            table = bigquery.Table(table_ref, schema=schema)
            client.create_table(table)
            print(f"✅ Created table {table_id}")
        
        print(f"✅ BigQuery resources ready in project {project_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating BigQuery resources: {e}")
        return False

if __name__ == "__main__":
    create_bigquery_resources()