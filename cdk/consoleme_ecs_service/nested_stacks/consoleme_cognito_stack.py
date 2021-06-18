from aws_cdk import (
    aws_cognito as cognito,
    custom_resources as cr,
    aws_logs as logs,
    core as cdk
)

from constants import APPLICATION_PREFIX, APPLICATION_SUFFIX, ADMIN_TEMP_PASSWORD


class ConsolemeCognitoStack(cdk.NestedStack):

    def __init__(self, scope: cdk.Construct, id: str, domain_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # User pool and user pool OAuth client

        consoleme_cognito_user_pool = cognito.UserPool(
            self,
            f'{id}UserPool',
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        consoleme_cognito_user_pool_domain = cognito.UserPoolDomain(
            self,
            f'{id}UserPoolDomain',
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=APPLICATION_PREFIX + '-' + APPLICATION_SUFFIX),
            user_pool=consoleme_cognito_user_pool
        )

        consoleme_cognito_admin_user = cr.AwsCustomResource(
            self,
            f'{id}UserPoolAdminUserResource',
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE),
            on_create=cr.AwsSdkCall(
                service='CognitoIdentityServiceProvider',
                action='adminCreateUser',
                parameters={'UserPoolId': consoleme_cognito_user_pool.user_pool_id,
                            'Username': 'consoleme_admin',
                            'UserAttributes': [{
                                'Name': 'email',
                                'Value': 'consoleme_admin@' + domain_name
                            }],
                            'TemporaryPassword': ADMIN_TEMP_PASSWORD},
                physical_resource_id=cr.PhysicalResourceId.of(
                    consoleme_cognito_user_pool.user_pool_id)
            )
        )

        consoleme_cognito_admin_group = cr.AwsCustomResource(
            self,
            f'{id}UserPoolAdminGroupResource',
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE),
            on_create=cr.AwsSdkCall(
                service='CognitoIdentityServiceProvider',
                action='createGroup',
                parameters={
                    'UserPoolId': consoleme_cognito_user_pool.user_pool_id,
                    'GroupName': 'consoleme_admins'
                },
                physical_resource_id=cr.PhysicalResourceId.of(
                    consoleme_cognito_user_pool.user_pool_id)
            )
        )

        consoleme_cognito_assign_admin_gruop = cr.AwsCustomResource(
            self,
            f'{id}UserPoolAssignAdminGroupResource',
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE),
            on_create=cr.AwsSdkCall(
                service='CognitoIdentityServiceProvider',
                action='adminAddUserToGroup',
                parameters={'UserPoolId': consoleme_cognito_user_pool.user_pool_id,
                            'GroupName': 'consoleme_admins',
                            'Username': 'consoleme_admin'},
                physical_resource_id=cr.PhysicalResourceId.of(
                    consoleme_cognito_user_pool.user_pool_id)
            )
        )

        consoleme_cognito_assign_admin_gruop.node.add_dependency(
            consoleme_cognito_admin_user)
        consoleme_cognito_assign_admin_gruop.node.add_dependency(
            consoleme_cognito_admin_group)

        self.cognito_user_pool = consoleme_cognito_user_pool
