from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    CfnOutput,
)
from constructs import Construct
from .vibe_lambda_construct import VibeLambdaConstruct
from .echo_lambda_construct import EchoLambdaConstruct
from constructs import Construct

class VibeQStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, env_name: str = 'dev', **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.env_name = env_name

        # Lambda constructs
        vibe_lambda_construct = VibeLambdaConstruct(self, "VibeLambdaConstruct")
        echo_lambda_construct = EchoLambdaConstruct(self, "EchoLambdaConstruct")

        # API Gateway
        api = apigw.RestApi(self, "VibeApi")
        vibe_resource = api.root.add_resource("vibe")
        vibe_resource.add_method("GET", apigw.LambdaIntegration(vibe_lambda_construct.lambda_function))

        # Step Functions
        echo_task = tasks.LambdaInvoke(
            self, "EchoTask",
            lambda_function=echo_lambda_construct.lambda_function,
            result_path="$.result"
        )
        
        map_state = sfn.Map(
            self, "EchoMap",
            items_path="$.echo_arrays",
            result_path="$.results"
        ).iterator(echo_task)
        
        transform_output = sfn.Pass(
            self, "TransformOutput",
            parameters={
                "echoed.$": "$.results[*].Payload.body"
            }
        )
        
        definition = map_state.next(transform_output)
        
        step_function = sfn.StateMachine(
            self, "EchoStateMachine",
            definition=definition
        )

        # Outputs
        CfnOutput(self, "ApiEndpoint", value=f"{api.url}vibe")
        CfnOutput(self, "StateMachineArn", value=step_function.state_machine_arn)
