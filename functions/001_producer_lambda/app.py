import boto3
import os
import uuid
import json
#from boto3.dynamodb.conditions import Key

s3_client = boto3.client('s3')
sqs = boto3.client('sqs')


def ddb_query_locations(location):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('acciona-tutorial-s3-parameterstore')

    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('location').eq(location)
    )
    return response['Items']


def run(event, context):
    initial_event_bucket = event['Records'][0]['s3']['bucket']['name']
    print(f"Bucket, {initial_event_bucket}")

    key_file_name = event['Records'][0]['s3']['object']['key']
    print(f"Nombre archivo, {key_file_name}")

    split_key = key_file_name.split('/') #file-folder-source/csvfile/csv_for_dynamo.csv
    data = ddb_query_locations(split_key[1])

    for value in data:
        print(value)
        # agrego a la lista del evento, el nombre del lambda que copia el file
        lambda_mapped = value['lambda']

    group_id = str(uuid.uuid1())
    deduplication_id= str(uuid.uuid1())

    print(f"Send message to sqs")
    response = sqs.send_message(
        QueueUrl=os.getenv('prod_queue_url'),
        MessageBody=json.dumps(event),
        MessageAttributes={
            'InitialBucket': {
                'DataType': 'String',
                'StringValue': initial_event_bucket},
            'Lambda_final': {
                'DataType': 'String',
                'StringValue': lambda_mapped},
            'FileName': {
                'DataType': 'String',
                'StringValue': key_file_name}
        },
        MessageGroupId=group_id,
        MessageDeduplicationId=deduplication_id
    )