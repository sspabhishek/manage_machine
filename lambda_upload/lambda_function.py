import boto3
import json
import os
from datetime import datetime
from requests_toolbelt.multipart import decoder
import base64

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('MachineFiles')
BUCKET_NAME = 'machine-code-files'

def lambda_handler(event, context):
    print("=== Event received ===")
    print(json.dumps(event)[:1000])  # debug only first 1000 chars

    machine_id = event['queryStringParameters'].get('machine_id')
    content_type = event['headers'].get('content-type') or event['headers'].get('Content-Type')
    print(f"Machine ID: {machine_id}")
    print(f"Content-Type: {content_type}")

    try:
        if event.get('isBase64Encoded', False):
            body_bytes = base64.b64decode(event['body'])
        else:
            body_bytes = event['body'].encode('utf-8')

        print(f"Decoded body size: {len(body_bytes)} bytes")

        multipart_data = decoder.MultipartDecoder(body_bytes, content_type)

        file_part = next((part for part in multipart_data.parts if b'filename=' in part.headers[b'Content-Disposition']), None)
        if not file_part:
            return _response(400, {'error': 'File part not found'})

        cd_header = file_part.headers[b'Content-Disposition'].decode()
        original_filename = cd_header.split('filename="')[1].split('"')[0]
        file_content = file_part.content
        file_type = file_part.headers.get(b'Content-Type', b'application/octet-stream').decode()

        print(f"Original filename: {original_filename}")
        print(f"Detected content-type: {file_type}")
        print(f"File size: {len(file_content)} bytes")

        _, ext = os.path.splitext(original_filename)
        new_filename = f"{machine_id}_{int(datetime.utcnow().timestamp())}{ext}"
        s3_key = f"files/{machine_id}/{new_filename}"

        # Delete old file if exists
        old = table.get_item(Key={'machine_id': machine_id})
        if 'Item' in old:
            print(f"Deleting old file: {old['Item']['s3_key']}")
            s3.delete_object(Bucket=BUCKET_NAME, Key=old['Item']['s3_key'])

        # Upload new file
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
            ContentType=file_type
        )
        print(f"Uploaded to S3: {s3_key}")

        # Update DynamoDB
        table.put_item(Item={
            'machine_id': machine_id,
            's3_key': s3_key,
            'original_filename': original_filename,
            'uploaded_at': datetime.utcnow().isoformat()
        })

        return _response(200, {'message': 'Upload successful'})

    except Exception as e:
        print(f"Exception: {str(e)}")
        return _response(500, {'error': str(e)})

def _response(status, body):
    return {
        'statusCode': status,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Methods': 'POST,OPTIONS',
        },
        'body': json.dumps(body)
    }
