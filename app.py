#!/usr/bin/env python3
import os
import aws_cdk as cdk
from vibe_q.vibe_q_stack import VibeQStack
from config import get_env_config

app = cdk.App()

# Get environment from context or default to dev
env_name = app.node.try_get_context('env') or 'dev'
config = get_env_config(env_name)

# Create environment-specific stack
stack_name = f"VibeQStack-{env_name.title()}"
stack = VibeQStack(
    app, 
    stack_name,
    env=cdk.Environment(
        account=config['account'],
        region=config['region']
    ),
    env_name=env_name
)

# Add tags for environment tracking
cdk.Tags.of(stack).add("Environment", env_name)
cdk.Tags.of(stack).add("Project", "VibeQ")

app.synth()
