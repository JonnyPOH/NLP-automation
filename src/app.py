import boto3
import os
import uuid
import json
from helpers.Lambda_Helper import Lambda_Helper
from helpers.S3_Helper import S3_Helper
from helpers.Display_Helper import Display_Helper

# Environment Variables
os.environ['LEARNER_S3_BUCKETNAME_TEXT'] = 'serverless-llmaws-2'
os.environ['LEARNER_S3_BUCKETNAME_AUDIO'] = 'serverless-llmaws-2'
os.environ['LAMBDA_LAYER_VERSION_ARN'] = 'arn:aws:lambda:us-west-2:637423214227:layer:dlai-bedrock-jinja-layer:1'

# Helper Instances
lambda_helper = Lambda_Helper()
s3_helper = S3_Helper()
display_helper = Display_Helper()

# S3 Bucket Names
bucket_name_text = os.environ['LEARNER_S3_BUCKETNAME_TEXT']
bucket_name_audio = os.environ['LEARNER_S3_BUCKETNAME_AUDIO']

# AWS Clients
s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe', region_name='us-west-2')

# Lambda Function
def lambda_handler(event, context):
    """
    Lambda function to process an audio file in an S3 bucket
    and create a transcription using Amazon Transcribe.
    """
    # Extract the bucket name and key from the incoming event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Prevent recursive loops
    if key != "dialog.mp3":
        print("This demo only works with dialog.mp3.")
        return

    try:
        # Generate a unique transcription job name
        job_name = f'transcription-job-{uuid.uuid4()}'

        # Start Transcription Job
        response = transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f's3://{bucket}/{key}'},
            MediaFormat='mp3',
            LanguageCode='en-US',
            OutputBucketName=os.environ['S3BUCKETNAMETEXT'],  # Output bucket
            OutputKey=f'{job_name}-transcript.json',
            Settings={
                'ShowSpeakerLabels': True,
                'MaxSpeakerLabels': 2
            }
        )
        print(f"Transcription job started: {response}")

    except Exception as e:
        print(f"Error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error occurred: {e}")
        }

    return {
        'statusCode': 200,
        'body': json.dumps(f"Submitted transcription job for {key} from bucket {bucket}.")
    }

# Lambda Deployment and Trigger Configuration
lambda_helper.lambda_environ_variables = {'S3BUCKETNAMETEXT': bucket_name_text}
lambda_helper.deploy_function(["lambda_function.py"], function_name="LambdaFunctionTranscribe")

lambda_helper.filter_rules_suffix = "mp3"
lambda_helper.add_lambda_trigger(bucket_name_audio, function_name="LambdaFunctionTranscribe")

# Upload and Process File in S3
s3_helper.upload_file(bucket_name_audio, 'dialog.mp3')
print("Uploaded dialog.mp3 to audio bucket.")

# List Objects in Buckets
print("Audio Bucket Contents:")
s3_helper.list_objects(bucket_name_audio)

print("Text Bucket Contents:")
s3_helper.list_objects(bucket_name_text)

# Download Transcription Result
s3_helper.download_object(bucket_name_text, 'results.txt')

# Display Transcription Result
display_helper.text_file('results.txt')
