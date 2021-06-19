from aws_cdk import (
    aws_s3 as s3,
    core as cdk
)

from nested_stacks.shared_stack import SharedStack
from nested_stacks.iam_stack import IAMStack
from nested_stacks.vpc_stack import VPCStack
from nested_stacks.alb_stack import ALBStack
from nested_stacks.compute_stack import ComputeStack
from nested_stacks.cache_stack import CacheStack
from nested_stacks.domain_stack import DomainStack
from nested_stacks.db_stack import DBStack
from nested_stacks.auth_stack import AuthStack
from nested_stacks.config_stack import ConfigStack

from constants import BASE_NAME


class ConsolemeEcsServiceStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        shared_stack = SharedStack(
            self,
            'Shared'
        )

        iam_stack = IAMStack(
            self,
            'IAM',
            s3_bucket=shared_stack.s3_bucket
        )

        db_stack = DBStack(
            self,
            'DB'
        )

        vpc_stack = VPCStack(
            self,
            'VPC'
        )

        alb_stack = ALBStack(
            self,
            'ALB',
            vpc=vpc_stack.vpc,
            alb_sg=vpc_stack.alb_sg
        )

        domain_stack = DomainStack(
            self,
            'Domain',
            alb=alb_stack.alb
        )

        auth_stack = AuthStack(
            self,
            'Auth',
            domain_name=domain_stack.route53_record.domain_name
        )

        cache_stack = CacheStack(
            self,
            'Cache',
            vpc=vpc_stack.vpc,
            redis_sg=vpc_stack.redis_sg
        )

        config_stack = ConfigStack(
            self,
            'Config',
            cognito_user_pool=auth_stack.cognito_user_pool,
            redis=cache_stack.redis,
            domain_name=domain_stack.route53_record.domain_name,
            s3_bucket_name=shared_stack.s3_bucket.bucket_name,
            create_configuration_lambda_role_arn=iam_stack.create_configuration_lambda_role.role_arn
        )

        compute_stack = ComputeStack(
            self,
            'Compute',
            vpc=vpc_stack.vpc,
            service_sg=vpc_stack.service_sg,
            alb=alb_stack.alb,
            alb_sg=vpc_stack.alb_sg,
            s3_bucket_name=shared_stack.s3_bucket.bucket_name,
            certificate=domain_stack.certificate,
            task_role_arn=iam_stack.ecs_task_role.role_arn,
            task_execution_role_arn=iam_stack.ecs_task_execution_role.role_arn
        )

        compute_stack.node.add_dependency(config_stack)

        # Output the service URL to CloudFormation outputs

        cdk.CfnOutput(
            self,
            f'{BASE_NAME}URL',
            value='https://' + domain_stack.route53_record.domain_name
        )
