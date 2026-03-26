import os
import uuid
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/retrain', methods=['POST'])
def handle_retrain():
    """
    A simple endpoint to simulate kicking off a model retraining job.
    It prints the received dataset URI and returns a simulated model version.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    dataset_uri = data.get('dataset_uri')

    if not dataset_uri:
        return jsonify({"error": "Missing 'dataset_uri' in payload"}), 400

    print("\n--- TRAINING SERVICE ---")
    print(f"Received retraining request for dataset: {dataset_uri}")
    print("Simulating training job kick-off...")
    print("----------------------\n")

    # In a real service, this would trigger a long-running training pipeline.
    model_version = f"retrained-model-{uuid.uuid4().hex[:8]}"
    
    return jsonify({"model_version": model_version}), 202 # 202 Accepted

if __name__ == '__main__':
    from waitress import serve
    # The service will run on port 8001 as specified in the .env file
    port = int(os.environ.get('PORT', 8001))
    print(f"INFO: Starting training service with waitress on http://0.0.0.0:{port}")
    serve(app, host='0.0.0.0', port=port)