# aws-ipranges-filter
Small Lambda function to filter IP's for specific region and service

## Usage
* Create a lambda function that subscribes to the AmazonIpSpaceChanged SNS topic (arn:aws:sns:us-east-1:806199016981:AmazonIpSpaceChanged)
* Add the encironment variable `REGION` and the values as AWS region (e.g. ap-southeast-2 for Sydney region)
* Add the encironment variable `DEBUG` and the values `true` for debug information in logs
* Set a target SNS topic to receive the current IP ranges
