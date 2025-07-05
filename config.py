import os

ENVIRONMENTS = {
    'dev': {
        'account': os.getenv('CDK_DEFAULT_ACCOUNT'),
        'region': 'ap-southeast-1',
        'auto_deploy': True
    },
    'test': {
        'account': os.getenv('CDK_DEFAULT_ACCOUNT'),
        'region': 'ap-southeast-1',
        'auto_deploy': True
    },
    'prod': {
        'account': os.getenv('CDK_DEFAULT_ACCOUNT'),
        'region': 'ap-southeast-1',
        'auto_deploy': False,
        'require_approval': True
    }
}

def get_env_config(env_name: str):
    return ENVIRONMENTS.get(env_name, ENVIRONMENTS['dev'])