import json
import boto3

s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')
sqs_client = boto3.client('sqs')


def run(event, context):
    print("El event del sqs dentro del consumer")
    print(event)

    initial_event_bucket = event['Records'][0]['messageAttributes']['InitialBucket']['stringValue']
    file_name = event['Records'][0]['messageAttributes']['FileName']['stringValue']
    parameter_function = event['Records'][0]['messageAttributes']['Lambda_final']['stringValue']

    input_params = {
        'initial_event_bucket': initial_event_bucket,
        'file_name': file_name
    }

    #llamo a funcion que indique el dynamodb parameter
    response = lambda_client.invoke(
        FunctionName=parameter_function,
        InvocationType='RequestResponse',
        Payload=json.dumps(input_params)
    )