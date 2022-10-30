import RPi.GPIO as GPIO
import os
import time
import json
import boto3
from datetime import datetime

# S3 Setup
s3 = boto3.client('s3')
bucket = os.getenv('HEALTH_TRACKER_S3_BUCKET_NAME')

# RPI Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.IN)
prev_input = 0
start = datetime.now()
duration = 0
queue_text = 0

while True:
    # take a reading
    input = GPIO.input(4)

    # if the prev input was low and current input is high, set start_ts
    if ((not prev_input) and input):
        queue_text = 1
        print("Under Pressure")
        start = datetime.now()

    # if a transaction is queued for sending to S3 AND plate is not being pressed, set end_ts and send transaction to S3
    if queue_transaction and not input:
        end = datetime.now()
        duration = end-start
        print(duration)

        # send transaction to S3 as a JSON file
        transactionToUpload = {'start_ts': start, 'end_ts': end}
        fileName = f'{start}.json'
        uploadByteStream = bytes(json.dumps(transactionToUpload, default=str).encode('UTF-8'))
        s3.put_object(Bucket=bucket, Key=fileName, Body=uploadByteStream)
        
        # reset
        queue_transaction = 0

    # update previous input
    prev_input = input

    #slight pause
    time.sleep(0.10)

