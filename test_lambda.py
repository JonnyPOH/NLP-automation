import json
from src.app import lambda_handler

# Simulate an S3 event as the input
mock_event = {
    "Records": [
        {
            "s3": {
                "bucket": {
                    "name": "mock-bucket"
                },
                "object": {
                    "key": "mock-file-transcript.json"
                }
            }
        }
    ]
}

# Simulate a Lambda context (can be left empty for basic testing)
mock_context = {}

# Invoke the Lambda handler
response = lambda_handler(mock_event, mock_context)

# Print the response
print("Lambda Response:")
print(json.dumps(response, indent=4))
