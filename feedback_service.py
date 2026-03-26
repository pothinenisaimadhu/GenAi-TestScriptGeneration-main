import os
import uuid
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/feedback', methods=['POST'])
def handle_feedback():
    """
    A simple endpoint to simulate receiving feedback data.
    It prints the received data and returns a simulated feedback ID.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    testcase_id = data.get('testcase_id')
    corrections = data.get('corrections')

    if not testcase_id or not corrections:
        return jsonify({"error": "Missing 'testcase_id' or 'corrections' in payload"}), 400

    print("\n--- FEEDBACK SERVICE ---")
    print(f"Received feedback for test case: {testcase_id}")
    print(f"Corrections: {corrections}")
    print("------------------------\n")

    # In a real service, you would store this data in a database.
    feedback_id = f"fb-real-{uuid.uuid4()}"
    
    return jsonify({"id": feedback_id}), 201

if __name__ == '__main__':
    from waitress import serve
    # The service will run on port 8002 as specified in the .env file
    port = int(os.environ.get('PORT', 8002))
    print(f"INFO: Starting feedback service with waitress on http://0.0.0.0:{port}")
    serve(app, host='0.0.0.0', port=port)