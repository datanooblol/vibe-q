from aws_cdk import (
    aws_lambda as _lambda,
)
from constructs import Construct

class EchoLambdaConstruct(Construct):
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.lambda_function = _lambda.Function(
            self, "EchoLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="echo_handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda")
        )
    
    @property
    def function(self) -> _lambda.Function:
        return self.lambda_function