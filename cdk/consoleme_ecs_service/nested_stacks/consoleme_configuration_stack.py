import secrets
import uuid
import yaml

from aws_cdk import (
    aws_cognito as cognito,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_s3 as s3,
    custom_resources as cr,
    aws_logs as logs,
    aws_elasticache as ec,
    core as cdk
)

from aws_cdk.aws_lambda_python import PythonFunction as lambda_python


class ConsolemeConfigurationStack(cdk.NestedStack):

    def __init__(self, scope: cdk.Construct, id: str,
                 consoleme_cognito_user_pool: cognito.UserPool, consoleme_s3_bucket_name: str,
                 consoleme_create_configuration_lambda_role_arn: str,
                 consoleme_redis: ec.CfnCacheCluster, consoleme_domain_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        config_yaml = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)
        spoke_accounts = config_yaml['spoke_accounts']

        consoleme_cognito_user_pool_client = cognito.UserPoolClient(
            self,
            f'{id}UserPoolClient',
            user_pool=consoleme_cognito_user_pool,
            generate_secret=True,
            supported_identity_providers=[
                cognito.UserPoolClientIdentityProvider.COGNITO],
            prevent_user_existence_errors=True,
            o_auth=cognito.OAuthSettings(
                callback_urls=[
                    'https://' + consoleme_domain_name + '/auth',
                    'https://' + consoleme_domain_name + '/oauth2/idpresponse'
                ],
                logout_urls=[
                    'https://' + consoleme_domain_name + '/logout'
                ],
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                    implicit_code_grant=True
                ),
                scopes=[
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.EMAIL
                ]
            ),
            auth_flows=cognito.AuthFlow(user_password=True, user_srp=True)
        )

        consoleme_describe_cognito_user_pool_client = cr.AwsCustomResource(
            self,
            f'{id}UserPoolClientIDResource',
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE),
            on_create=cr.AwsSdkCall(
                service='CognitoIdentityServiceProvider',
                action='describeUserPoolClient',
                parameters={'UserPoolId': consoleme_cognito_user_pool.user_pool_id,
                            'ClientId': consoleme_cognito_user_pool_client.user_pool_client_id},
                physical_resource_id=cr.PhysicalResourceId.of(
                    consoleme_cognito_user_pool_client.user_pool_client_id)
            ),
            install_latest_aws_sdk=True,
            log_retention=logs.RetentionDays.ONE_WEEK
        )

        consoleme_cognito_user_pool_client_secret = consoleme_describe_cognito_user_pool_client.get_response_field(
            'UserPoolClient.ClientSecret')

        imported_create_configuration_lambda_role = iam.Role.from_role_arn(
            self,
            f'{id}ImportedCreateConfigurationFileLambdaRole',
            role_arn=consoleme_create_configuration_lambda_role_arn
        )

        consoleme_create_configuration_lambda = lambda_python(
            self,
            f'{id}CreateConfigurationFileLambda',
            entry='resources/create_config_lambda',
            timeout=cdk.Duration.seconds(30),
            runtime=lambda_.Runtime.PYTHON_3_8,
            role=imported_create_configuration_lambda_role,
            environment={
                'DEPLOYMENT_BUCKET': consoleme_s3_bucket_name,
                'JWT_SECRET': secrets.token_urlsafe(16),
                'OIDC_CLIENT_ID': consoleme_cognito_user_pool_client.user_pool_client_id,
                'OIDC_CLIENT_SECRET': consoleme_cognito_user_pool_client_secret,
                'OIDC_METADATA_URL': 'https://cognito-idp.' + self.region + '.amazonaws.com/' + consoleme_cognito_user_pool.user_pool_id + '/.well-known/openid-configuration',
                'REDIS_HOST': consoleme_redis.attr_redis_endpoint_address,
                'SES_IDENTITY_ARN': 'arn:aws:ses:eu-west-1:123456789123:identity/domain.com',  # TODO: Create identity
                'SUPPORT_CHAT_URL': 'https://discord.gg/nQVpNGGkYu',
                'APPLICATION_ADMIN': 'consoleme_admin',
                'ACCOUNT_NUMBER': self.account,
                'ISSUER': consoleme_domain_name,
                'SPOKE_ACCOUNTS': ','.join(spoke_accounts)
            }
        )

        consoleme_create_configuration_resource_provider = cr.Provider(
            self,
            f'{id}CreateConfigurationFileProvider',
            on_event_handler=consoleme_create_configuration_lambda,
            log_retention=logs.RetentionDays.ONE_WEEK
        )

        consoleme_create_configuration_resource = cdk.CustomResource(
            self,
            f'{id}CreateConfigurationFile',
            service_token=consoleme_create_configuration_resource_provider.service_token,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            properties={'UUID': str(uuid.uuid4())}
        )
