from aws_cdk import (
    Stack,
    Stage,
    pipelines,
)
from constructs import Construct
from .vibe_q_stack import VibeQStack

class PipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the pipeline
        pipeline = pipelines.CodePipeline(
            self, "Pipeline",
            synth=pipelines.ShellStep(
                "Synth",
                input=pipelines.CodePipelineSource.connection(
                    "datanooblol/vibe-q",
                    "main",
                    connection_arn=self.node.try_get_context("codestar-connection-arn")
                ),
                commands=[
                    "npm install -g aws-cdk",
                    "python -m pip install -r requirements.txt",
                    "cdk synth"
                ]
            )
        )

        # Add deployment stages
        dev_stage = pipeline.add_stage(
            AppStage(self, "Dev", env_name="dev")
        )
        
        test_stage = pipeline.add_stage(
            AppStage(self, "Test", env_name="test")
        )
        
        prod_stage = pipeline.add_stage(
            AppStage(self, "Prod", env_name="prod"),
            pre=[
                pipelines.ManualApprovalStep("PromoteToProd")
            ]
        )

class AppStage(Stage):
    def __init__(self, scope: Construct, construct_id: str, env_name: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        VibeQStack(self, f"VibeQStack-{env_name.title()}", env_name=env_name)