from aws_cdk import (
    aws_iam as iam,
    aws_s3 as s3,
    core as cdk
)


class ConsolemeIAMStack(cdk.NestedStack):

    def __init__(self, scope: cdk.Construct, id: str,
                 consoleme_s3_bucket: s3.Bucket, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define IAM roles and policies

        consoleme_ecs_task_role = iam.Role(
            self,
            f'{id}TaskRole',
            role_name='ConsolemeTaskRole',
            assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com')
        )

        consoleme_ecs_task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    'access-analyzer:*',
                    'cloudtrail:*',
                    'cloudwatch:*',
                    'config:SelectResourceConfig',
                    'config:SelectAggregateResourceConfig',
                    'dynamodb:batchgetitem',
                    'dynamodb:batchwriteitem',
                    'dynamodb:deleteitem',
                    'dynamodb:describe*',
                    'dynamodb:getitem',
                    'dynamodb:getrecords',
                    'dynamodb:getsharditerator',
                    'dynamodb:putitem',
                    'dynamodb:query',
                    'dynamodb:scan',
                    'dynamodb:updateitem',
                    'sns:createplatformapplication',
                    'sns:createplatformendpoint',
                    'sns:deleteendpoint',
                    'sns:deleteplatformapplication',
                    'sns:getendpointattributes',
                    'sns:getplatformapplicationattributes',
                    'sns:listendpointsbyplatformapplication',
                    'sns:publish',
                    'sns:setendpointattributes',
                    'sns:setplatformapplicationattributes',
                    'sts:assumerole'
                ],
                resources=['*']
            )
        )

        consoleme_ecs_task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=['ses:sendemail', 'ses:sendrawemail'],
                resources=['*'],
                conditions={'StringLike': {'ses:FromAddress': ['admin@yourdomain.com']}} # TODO: Generate address
            )
        )

        consoleme_ecs_task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    'autoscaling:Describe*',
                    'cloudwatch:Get*',
                    'cloudwatch:List*',
                    'config:BatchGet*',
                    'config:List*',
                    'config:Select*',
                    'ec2:DescribeSubnets',
                    'ec2:describevpcendpoints',
                    'ec2:DescribeVpcs',
                    'iam:GetAccountAuthorizationDetails',
                    'iam:ListAccountAliases',
                    'iam:ListAttachedRolePolicies',
                    'ec2:describeregions',
                    's3:GetBucketPolicy',
                    's3:GetBucketTagging',
                    's3:ListAllMyBuckets',
                    's3:ListBucket',
                    's3:PutBucketPolicy',
                    's3:PutBucketTagging',
                    'sns:GetTopicAttributes',
                    'sns:ListTagsForResource',
                    'sns:ListTopics',
                    'sns:SetTopicAttributes',
                    'sns:TagResource',
                    'sns:UnTagResource',
                    'sqs:GetQueueAttributes',
                    'sqs:GetQueueUrl',
                    'sqs:ListQueues',
                    'sqs:ListQueueTags',
                    'sqs:SetQueueAttributes',
                    'sqs:TagQueue',
                    'sqs:UntagQueue'
                ],
                resources=['*'],
            )
        )

        consoleme_ecs_task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=['s3:GetObject', 's3:ListBucket'],
                resources=[consoleme_s3_bucket.bucket_arn, consoleme_s3_bucket.bucket_arn + '/*']
            )
        )

        consoleme_trust_role = iam.Role(
            self,
            f'{id}TrustRole',
            role_name='ConsolemeTrustRole',
            assumed_by=iam.ArnPrincipal(arn=consoleme_ecs_task_role.role_arn)
        )

        consoleme_trust_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    'access-analyzer:*',
                    'cloudtrail:*',
                    'cloudwatch:*',
                    'config:SelectResourceConfig',
                    'config:SelectAggregateResourceConfig',
                    'dynamodb:batchgetitem',
                    'dynamodb:batchwriteitem',
                    'dynamodb:deleteitem',
                    'dynamodb:describe*',
                    'dynamodb:getitem',
                    'dynamodb:getrecords',
                    'dynamodb:getsharditerator',
                    'dynamodb:putitem',
                    'dynamodb:query',
                    'dynamodb:scan',
                    'dynamodb:updateitem',
                    'sns:createplatformapplication',
                    'sns:createplatformendpoint',
                    'sns:deleteendpoint',
                    'sns:deleteplatformapplication',
                    'sns:getendpointattributes',
                    'sns:getplatformapplicationattributes',
                    'sns:listendpointsbyplatformapplication',
                    'sns:publish',
                    'sns:setendpointattributes',
                    'sns:setplatformapplicationattributes',
                    'sts:assumerole',
                    'autoscaling:Describe*',
                    'cloudwatch:Get*',
                    'cloudwatch:List*',
                    'config:BatchGet*',
                    'config:List*',
                    'config:Select*',
                    'ec2:DescribeSubnets',
                    'ec2:describevpcendpoints',
                    'ec2:DescribeVpcs',
                    'iam:GetAccountAuthorizationDetails',
                    'iam:ListAccountAliases',
                    'iam:ListAttachedRolePolicies',
                    'ec2:describeregions',
                    's3:GetBucketPolicy',
                    's3:GetBucketTagging',
                    's3:ListAllMyBuckets',
                    's3:ListBucket',
                    's3:PutBucketPolicy',
                    's3:PutBucketTagging',
                    'sns:GetTopicAttributes',
                    'sns:ListTagsForResource',
                    'sns:ListTopics',
                    'sns:SetTopicAttributes',
                    'sns:TagResource',
                    'sns:UnTagResource',
                    'sqs:GetQueueAttributes',
                    'sqs:GetQueueUrl',
                    'sqs:ListQueues',
                    'sqs:ListQueueTags',
                    'sqs:SetQueueAttributes',
                    'sqs:TagQueue',
                    'sqs:UntagQueue'
                ],
                resources=['*']
            )
        )

        consoleme_ecs_task_execution_role = iam.Role(
            self,
            f'{id}TaskExecutionRole',
            assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com')
        )

        consoleme_ecs_task_execution_role.add_managed_policy(
            iam.ManagedPolicy.from_managed_policy_arn(
                self,
                f'{id}ServiceRole',
                managed_policy_arn='arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy'
            )
        )

        consoleme_create_configuration_lambda_role = iam.Role(
            self,
            f'{id}CreateConfigurationFileLambdaRole',
            assumed_by=iam.ServicePrincipal(service='lambda.amazonaws.com')
        )

        consoleme_create_configuration_lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_managed_policy_arn(
                self,
                f'{id}ConfigurationBasicExecution',
                managed_policy_arn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
        )

        consoleme_create_configuration_lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=['s3:PutObject', 's3:DeleteObject'],
                resources = [consoleme_s3_bucket.bucket_arn + '/*']
            )
        )

        consoleme_configuration_lambda_statement = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['s3:PutObject'],
            resources=[consoleme_create_configuration_lambda_role.role_arn]
        )

        self.consoleme_ecs_task_role = consoleme_ecs_task_role
        self.consoleme_ecs_task_execution_role = consoleme_ecs_task_execution_role
        self.consoleme_create_configuration_lambda_role = consoleme_create_configuration_lambda_role
