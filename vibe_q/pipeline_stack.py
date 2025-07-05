from aws_cdk import (
    Stack,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
    aws_iam as iam,
)
from constructs import Construct

class PipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Source artifact
        source_output = codepipeline.Artifact()
        
        # Build project
        build_project = codebuild.PipelineProject(
            self, "BuildProject",
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {
                            "python": "3.11",
                            "nodejs": "18"
                        },
                        "commands": [
                            "npm install -g aws-cdk",
                            "python -m pip install --upgrade pip",
                            "pip install -r requirements.txt"
                        ]
                    },
                    "build": {
                        "commands": [
                            "cdk synth -c env=dev",
                            "cdk synth -c env=test", 
                            "cdk synth -c env=prod"
                        ]
                    }
                },
                "artifacts": {
                    "files": ["**/*"]
                }
            })
        )

        # Add CDK permissions to build role
        build_project.add_to_role_policy(iam.PolicyStatement(
            actions=["sts:AssumeRole"],
            resources=["arn:aws:iam::*:role/cdk-*"]
        ))

        # Build artifact
        build_output = codepipeline.Artifact()

        # Pipeline
        pipeline = codepipeline.Pipeline(
            self, "VibeQPipeline",
            stages=[
                # Source stage
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[
                        codepipeline_actions.CodeStarConnectionsSourceAction(
                            action_name="GitHub_Source",
                            owner=self.node.try_get_context("github-owner"),
                            repo="vibe-q",
                            branch="main",
                            connection_arn=self.node.try_get_context("codestar-connection-arn"),
                            output=source_output
                        )
                    ]
                ),
                
                # Build stage
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[
                        codepipeline_actions.CodeBuildAction(
                            action_name="Build",
                            project=build_project,
                            input=source_output,
                            outputs=[build_output]
                        )
                    ]
                ),
                
                # Deploy Dev
                codepipeline.StageProps(
                    stage_name="Deploy_Dev",
                    actions=[
                        codepipeline_actions.CloudFormationCreateUpdateStackAction(
                            action_name="Deploy_Dev",
                            stack_name="VibeQStack-Dev",
                            template_path=build_output.at_path("cdk.out/VibeQStack-Dev.template.json"),
                            admin_permissions=True
                        )
                    ]
                ),
                
                # Deploy Test
                codepipeline.StageProps(
                    stage_name="Deploy_Test",
                    actions=[
                        codepipeline_actions.CloudFormationCreateUpdateStackAction(
                            action_name="Deploy_Test",
                            stack_name="VibeQStack-Test",
                            template_path=build_output.at_path("cdk.out/VibeQStack-Test.template.json"),
                            admin_permissions=True
                        )
                    ]
                ),
                
                # Manual Approval
                codepipeline.StageProps(
                    stage_name="Approve_Prod",
                    actions=[
                        codepipeline_actions.ManualApprovalAction(
                            action_name="Manual_Approval",
                            additional_information="Please review and approve production deployment"
                        )
                    ]
                ),
                
                # Deploy Prod
                codepipeline.StageProps(
                    stage_name="Deploy_Prod",
                    actions=[
                        codepipeline_actions.CloudFormationCreateUpdateStackAction(
                            action_name="Deploy_Prod",
                            stack_name="VibeQStack-Prod",
                            template_path=build_output.at_path("cdk.out/VibeQStack-Prod.template.json"),
                            admin_permissions=True
                        )
                    ]
                )
            ]
        )