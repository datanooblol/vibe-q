from aws_cdk import (
    Stack,
    Stage,
)
import aws_cdk as cdk
from constructs import Construct
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep, ManualApprovalStep
from .vibe_q_stack import VibeQStack

class AppStage(Stage):
    def __init__(self, scope: Construct, construct_id: str, env_name: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        VibeQStack(self, f"VibeQStack", env_name=env_name)

class PipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the pipeline - this will create the actual CodePipeline in AWS
        pipeline = CodePipeline(
            self, "VibeQPipeline",
            pipeline_name="VibeQCICDPipeline",
            synth=ShellStep(
                "Synth",
                input=CodePipelineSource.connection(
                    "datanooblol/vibe-q",
                    "main",
                    connection_arn=self.node.try_get_context("codestar-connection-arn")
                ),
                commands=[
                    "npm install -g aws-cdk",
                    "python -m pip install -r requirements.txt",
                    "cdk synth --app 'python app.py'"
                ]
            )
        )

        # Add deployment stages
        dev_stage = pipeline.add_stage(
            AppStage(self, "Dev", env_name="dev", 
                    env=cdk.Environment(region="ap-southeast-1"))
        )
        
        test_stage = pipeline.add_stage(
            AppStage(self, "Test", env_name="test",
                    env=cdk.Environment(region="ap-southeast-1"))
        )
        
        prod_stage = pipeline.add_stage(
            AppStage(self, "Prod", env_name="prod",
                    env=cdk.Environment(region="ap-southeast-1")),
            pre=[
                ManualApprovalStep("PromoteToProd")
            ]
        )
        
        # Output the pipeline name
        cdk.CfnOutput(self, "PipelineName", value=pipeline.pipeline.pipeline_name)