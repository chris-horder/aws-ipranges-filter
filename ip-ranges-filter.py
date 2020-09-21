import boto3
import hashlib
import json
import logging
import urllib.request, urllib.error, urllib.parse
import os

def lambda_handler(event, context):
    # Set up logging
    if len(logging.getLogger().handlers) > 0:
        logging.getLogger().setLevel(logging.ERROR)
    else:
        logging.basicConfig(level=logging.DEBUG)
    
    # Set the environment variable DEBUG to 'true' if you want verbose debug details in CloudWatch Logs.
    try:
        if os.environ['DEBUG'] == 'true':
            logging.getLogger().setLevel(logging.INFO)
    except KeyError:
        pass

    # If you want a different service, set the SERVICE environment variable.
    # It defaults to CLOUDFRONT. Using 'jq' and 'curl' get the list of possible
    # services like this:
    # curl -s 'https://ip-ranges.amazonaws.com/ip-ranges.json' | jq -r '.prefixes[] | .service' ip-ranges.json | sort -u 
    SERVICE = os.getenv( 'SERVICE', "AMAZON_CONNECT")
    REGION = os.getenv( 'REGION', "ap-southeast-2")
    results = list()
    
    message = json.loads(event['Records'][0]['Sns']['Message'])
    
    ip_ranges = json.loads(get_ip_groups_json(message['url'], message['md5']))
    
    connect_ranges = get_ranges_for_service(ip_ranges, SERVICE, "GLOBAL")
    region_ranges = get_ranges_for_service(ip_ranges, SERVICE, REGION)
    
    results = region_ranges + connect_ranges
    results.sort()
    
    logging.info(str("Found ranges: " + " ".join(results)))
    
    return results
    
def get_ip_groups_json(url, expected_hash):
    
    logging.debug("Updating from " + url)

    response = urllib.request.urlopen(url)
    ip_json = response.read()

    m = hashlib.md5()
    m.update(ip_json)
    hash = m.hexdigest()

    # if hash != expected_hash:
    #     raise Exception('MD5 Mismatch: got ' + hash + ' expected ' + expected_hash)

    return ip_json
    
def get_ranges_for_service(ranges, service, subset):
    
    service_ranges = list()
    for prefix in ranges['prefixes']:
        if prefix['service'] == service and ((subset == prefix['region'] and subset == "GLOBAL") or (subset != 'GLOBAL' and prefix['region'] == subset)):
            logging.info(('Found ' + service + ' region: ' + prefix['region'] + ' range: ' + prefix['ip_prefix']))
            service_ranges.append(prefix['ip_prefix'])

    return service_ranges
