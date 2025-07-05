import json

def lambda_handler(event, context):
    echo_name = event.get('echo_name', '')
    
    return {
        'statusCode': 200,
        'body': json.dumps({"vibe_echo": echo_name})
    }