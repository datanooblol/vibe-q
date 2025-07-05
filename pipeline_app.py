#!/usr/bin/env python3
import aws_cdk as cdk
from vibe_q.pipeline_stack import PipelineStack

app = cdk.App()

PipelineStack(
    app, 
    "VibeQPipelineStack",
    env=cdk.Environment(
        account=app.node.try_get_context('account'),
        region='ap-southeast-1'
    )
)

app.synth()