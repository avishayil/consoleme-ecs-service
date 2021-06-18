from aws_cdk import (
    aws_s3 as s3,
    core as cdk
)

from nested_stacks.consoleme_shared_stack import ConsolemeSharedStack
from nested_stacks.consoleme_iam_stack import ConsolemeIAMStack
from nested_stacks.consoleme_vpc_stack import ConsolemeVPCStack
from nested_stacks.consoleme_alb_stack import ConsolemeALBStack
from nested_stacks.consoleme_compute_stack import ConsolemeComputeStack
from nested_stacks.consoleme_cache_stack import ConsolemeCacheStack
from nested_stacks.consoleme_domain_stack import ConsolemeDomainStack
from nested_stacks.consoleme_dynamodb_stack import ConsolemeDynamodbStack
from nested_stacks.consoleme_cognito_stack import ConsolemeCognitoStack
from nested_stacks.consoleme_configuration_stack import ConsolemeConfigurationStack

from constants import BASE_NAME


class ConsolemeEcsServiceStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        consoleme_shared_stack = ConsolemeSharedStack(
            self,
            f'{BASE_NAME}SharedStack'
        )

        consoleme_iam_stack = ConsolemeIAMStack(
            self,
            f'{BASE_NAME}IAMStack',
            consoleme_s3_bucket=consoleme_shared_stack.s3_bucket
        )

        consoleme_dynamodb_stack = ConsolemeDynamodbStack(
            self,
            f'{BASE_NAME}DynamoDBStack'
        )

        consoleme_vpc_stack = ConsolemeVPCStack(
            self,
            f'{BASE_NAME}VPCStack'
        )

        consoleme_alb_stack = ConsolemeALBStack(
            self,
            f'{BASE_NAME}ALBStack',
            vpc=consoleme_vpc_stack.vpc,
            alb_sg=consoleme_vpc_stack.alb_sg
        )

        consoleme_domain_stack = ConsolemeDomainStack(
            self,
            f'{BASE_NAME}DomainnStack',
            alb=consoleme_alb_stack.alb
        )

        consoleme_cognito_stack = ConsolemeCognitoStack(
            self,
            f'{BASE_NAME}CognitoStack',
            domain_name=consoleme_domain_stack.route53_record.domain_name
        )

        consoleme_cache_stack = ConsolemeCacheStack(
            self,
            f'{BASE_NAME}CacheStack',
            vpc=consoleme_vpc_stack.vpc,
            redis_sg=consoleme_vpc_stack.redis_sg
        )

        consoleme_configuration_stack = ConsolemeConfigurationStack(
            self,
            f'{BASE_NAME}ConfigurationStack',
            consoleme_cognito_user_pool=consoleme_cognito_stack.cognito_user_pool,
            consoleme_redis=consoleme_cache_stack.redis,
            consoleme_domain_name=consoleme_domain_stack.route53_record.domain_name,
            consoleme_s3_bucket_name=consoleme_shared_stack.s3_bucket.bucket_name,
            consoleme_create_configuration_lambda_role_arn=consoleme_iam_stack.consoleme_create_configuration_lambda_role.role_arn
        )

        consoleme_compute_stack = ConsolemeComputeStack(
            self,
            f'{BASE_NAME}ComputeStack',
            vpc=consoleme_vpc_stack.vpc,
            service_sg=consoleme_vpc_stack.service_sg,
            alb=consoleme_alb_stack.alb,
            alb_sg=consoleme_vpc_stack.alb_sg,
            s3_bucket_name=consoleme_shared_stack.s3_bucket.bucket_name,
            certificate=consoleme_domain_stack.certificate,
            task_role_arn=consoleme_iam_stack.consoleme_ecs_task_role.role_arn,
            task_execution_role_arn=consoleme_iam_stack.consoleme_ecs_task_execution_role.role_arn
        )

        consoleme_compute_stack.node.add_dependency(
            consoleme_configuration_stack)

        # Output the service URL to CloudFormation outputs

        cdk.CfnOutput(
            self,
            f'{BASE_NAME}ConsolemeURL',
            value='https://' + consoleme_domain_stack.route53_record.domain_name
        )
