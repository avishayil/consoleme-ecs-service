from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticache as ec,
    core as cdk
)


class ConsolemeCacheStack(cdk.NestedStack):

    def __init__(self, scope: cdk.Construct, id: str,
                 vpc: ec2.Vpc, redis_sg: ec2.SecurityGroup, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Redis node

        consoleme_subnet_ids = []
        for subnet in vpc.private_subnets:
            consoleme_subnet_ids.append(subnet.subnet_id)

        consoleme_redis_subnet_group = ec.CfnSubnetGroup(
            self,
            f'{id}RedisSubnetGroup',
            cache_subnet_group_name='redis-subnet-group',
            description='Subnet group for Redis Cluster',
            subnet_ids=consoleme_subnet_ids
        )

        consoleme_redis = ec.CfnCacheCluster(
            self,
            f'{id}RedisCluster',
            cache_node_type='cache.t3.micro',
            engine='redis',
            engine_version='6.x',
            num_cache_nodes=1,
            auto_minor_version_upgrade=True,
            cache_subnet_group_name=consoleme_redis_subnet_group.ref,
            vpc_security_group_ids=[redis_sg.security_group_id]
        )

        self.redis = consoleme_redis
