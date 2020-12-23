import boto3
from urllib.parse import unquote_plus
import os
s3_client = boto3.client('s3')


def run(event, context):
    initial_event_bucket = event['initial_event_bucket']
    original_file_name = event['file_name']
    clean_file_name = unquote_plus(original_file_name) #limpia de caracteres especiales

    #copio en path destino
    destination_file_name = clean_file_name.replace("source", "destination")

    copy_source_object = {'Bucket': initial_event_bucket, 'Key': clean_file_name}
    destination_bucket = os.environ['destiny_bucket']

    print(f"bucket inicial "+initial_event_bucket+" Key destiny: "+destination_file_name)

    s3_client.copy_object(CopySource=copy_source_object, Bucket=destination_bucket , Key=destination_file_name)

    print(" BUCKET: " + initial_event_bucket + " KEY: " + destination_file_name)