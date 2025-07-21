import boto3
import json

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('MachineFiles')
BUCKET_NAME = 'machine-code-files'

def lambda_handler(event, context):
    machine_id = event['queryStringParameters'].get('machine_id')
    if not machine_id:
        return _response(400, {'error': 'Missing machine_id'})

    item = table.get_item(Key={'machine_id': machine_id})
    if 'Item' not in item:
        return _response(404, {'error': 'File not found'})

    s3_key = item['Item']['s3_key']

    presigned_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
        ExpiresIn=3600
    )

    return {
        'statusCode': 302,
        'headers': {
            'Location': presigned_url,
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,OPTIONS',
            'Access-Control-Allow-Headers': '*',
        }
    }

def _response(status, body):
    return {
        'statusCode': status,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,OPTIONS',
            'Access-Control-Allow-Headers': '*',
        },
        'body': json.dumps(body)
    }
