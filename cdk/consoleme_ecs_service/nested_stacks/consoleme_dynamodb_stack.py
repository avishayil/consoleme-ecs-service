from aws_cdk import (
    aws_dynamodb as db,
    core as cdk
)


class ConsolemeDynamodbStack(cdk.NestedStack):

    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # DynamoDB tables

        consoleme_iamroles_table = db.Table(
            self,
            f'{id}IAMRolesTable',
            table_name='consoleme_iamroles_global',
            partition_key=db.Attribute(
                name='arn', type=db.AttributeType.STRING),
            sort_key=db.Attribute(
                name='accountId', type=db.AttributeType.STRING),
            billing_mode=db.BillingMode.PROVISIONED,
            read_capacity=100,
            write_capacity=100,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        consoleme_config_table = db.Table(
            self,
            f'{id}ConfigTable',
            table_name='consoleme_config_global',
            partition_key=db.Attribute(
                name='id', type=db.AttributeType.STRING),
            billing_mode=db.BillingMode.PROVISIONED,
            read_capacity=10,
            write_capacity=10,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        consoleme_requests_table = db.Table(
            self,
            f'{id}RequestsTable',
            table_name='consoleme_policy_requests',
            partition_key=db.Attribute(
                name='request_id', type=db.AttributeType.STRING),
            sort_key=db.Attribute(name='arn', type=db.AttributeType.STRING),
            billing_mode=db.BillingMode.PROVISIONED,
            read_capacity=10,
            write_capacity=10,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        consoleme_requests_table.add_global_secondary_index(
            index_name='arn-request_id-index',
            partition_key=db.Attribute(
                name='arn', type=db.AttributeType.STRING),
            read_capacity=123,
            write_capacity=123,
            projection_type=db.ProjectionType.ALL
        )

        consoleme_cache_table = db.Table(
            self,
            f'{id}CacheTable',
            table_name='consoleme_resource_cache',
            partition_key=db.Attribute(
                name='resourceId', type=db.AttributeType.STRING),
            sort_key=db.Attribute(name='resourceType',
                                  type=db.AttributeType.STRING),
            billing_mode=db.BillingMode.PROVISIONED,
            read_capacity=10,
            write_capacity=10,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        consoleme_cache_table.add_global_secondary_index(
            index_name='arn-index',
            partition_key=db.Attribute(
                name='arn', type=db.AttributeType.STRING),
            read_capacity=123,
            write_capacity=123,
            projection_type=db.ProjectionType.ALL
        )

        consoleme_cloudtrail_table = db.Table(
            self,
            f'{id}CloudTrailTable',
            table_name='consoleme_cloudtrail',
            partition_key=db.Attribute(
                name='arn', type=db.AttributeType.STRING),
            sort_key=db.Attribute(
                name='request_id', type=db.AttributeType.STRING),
            billing_mode=db.BillingMode.PROVISIONED,
            read_capacity=10,
            write_capacity=10,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        consoleme_users_table = db.Table(
            self,
            f'{id}UsersTable',
            table_name='consoleme_users_global',
            partition_key=db.Attribute(
                name='username', type=db.AttributeType.STRING),
            billing_mode=db.BillingMode.PROVISIONED,
            read_capacity=5,
            write_capacity=5,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )
