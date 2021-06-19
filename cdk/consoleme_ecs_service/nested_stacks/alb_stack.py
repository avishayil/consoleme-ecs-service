from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as lb,
    core as cdk
)


class ALBStack(cdk.NestedStack):

    def __init__(self, scope: cdk.Construct, id: str,
                 vpc: ec2.Vpc, alb_sg: ec2.SecurityGroup, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # ECS Load Balancer

        ecs_loadbalancer = lb.ApplicationLoadBalancer(
            self,
            'ServiceALB',
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            internet_facing=True
        )

        ecs_loadbalancer.add_security_group(
            ec2.SecurityGroup.from_security_group_id(
                self,
                'ImportedLBSG',
                security_group_id=alb_sg.security_group_id,
                mutable=False
            )
        )

        self.alb = ecs_loadbalancer
