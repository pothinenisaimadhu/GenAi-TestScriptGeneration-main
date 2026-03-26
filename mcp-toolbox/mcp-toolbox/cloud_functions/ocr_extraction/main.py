import functions_framework
import os
import tempfile
from google.cloud import storage
from tika import parser
import logging

# Initialize the Cloud Storage client
storage_client = storage.Client()

@functions_framework.http
def ocr_extraction_func(request):
    """
    HTTP Cloud Function to extract text from a document in GCS.
    Expects a JSON payload with a "gcs_uri" key.
    Example: {"gcs_uri": "gs://your-bucket/your-doc.pdf"}
    """
    request_json = request.get_json(silent=True)
    if not request_json or "gcs_uri" not in request_json:
        logging.error("Request is missing JSON payload or 'gcs_uri' key.")
        return 'JSON payload with "gcs_uri" key is required.', 400

    gcs_uri = request_json["gcs_uri"]

    try:
        bucket_name, blob_name = gcs_uri.replace("gs://", "").split("/", 1)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Use a temporary directory to ensure files are cleaned up even if errors occur.
        with tempfile.TemporaryDirectory() as temp_dir:
            # Preserve the original filename extension, which can help Tika
            file_name = blob_name.split("/")[-1]
            temp_file_path = os.path.join(temp_dir, file_name)

            logging.info(f"Downloading {gcs_uri} to {temp_file_path}...")
            blob.download_to_filename(temp_file_path)

            # This is the most likely point of failure if the Tika server (Java)
            # can't start due to memory or timeout issues.
            logging.info(f"Parsing {temp_file_path} with Tika...")
            parsed = parser.from_file(temp_file_path)

        if parsed and "content" in parsed and parsed["content"]:
            logging.info(f"Successfully parsed content from {gcs_uri}.")
            return {"raw_text": parsed["content"]}, 200
        else:
            logging.warning(f"Tika parsed the file {gcs_uri} but found no content.")
            return {"raw_text": ""}, 200

    except Exception as e:
        # Log the full error for debugging in Cloud Logging.
        logging.error(f"Error processing {gcs_uri}: {e}", exc_info=True)
        error_message = (
            "The OCR extraction process failed. This can happen if the document is corrupt, "
            "or if the Tika server fails to start due to resource constraints (memory/timeout). "
            "Check the Cloud Function logs for detailed error information."
        )
        return {"error": error_message, "details": str(e)}, 500