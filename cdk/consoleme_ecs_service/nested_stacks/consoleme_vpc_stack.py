import urllib.request

from aws_cdk import (
    aws_ec2 as ec2,
    core as cdk
)


class ConsolemeVPCStack(cdk.NestedStack):

    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPC and security groups

        consoleme_vpc = ec2.Vpc(
            self, f'{id}Vpc',
            max_azs=2
        )

        consoleme_lb_sg = ec2.SecurityGroup(
            self,
            f'{id}LBSG',
            vpc=consoleme_vpc,
            description='Consoleme ECS service load balancer security group',
            allow_all_outbound=True
        )

        # Open ingress to the deploying computer public IP

        my_ip_cidr = urllib.request.urlopen(
            'http://checkip.amazonaws.com').read().decode('utf-8').strip() + '/32'

        consoleme_lb_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(cidr_ip=my_ip_cidr),
            connection=ec2.Port.tcp(port=443),
            description='Allow HTTPS traffic'
        )

        consoleme_service_sg = ec2.SecurityGroup(
            self,
            f'{id}ServiceSG',
            vpc=consoleme_vpc,
            description='Consoleme ECS service containers security group',
            allow_all_outbound=True
        )

        consoleme_redis_sg = ec2.SecurityGroup(
            self,
            f'{id}ECSG',
            vpc=consoleme_vpc,
            description='Consoleme Redis security group',
            allow_all_outbound=True
        )

        consoleme_redis_sg.connections.allow_from(consoleme_service_sg, port_range=ec2.Port.tcp(
            port=6379), description='Allow ingress from ConsoleMe containers')

        self.vpc = consoleme_vpc
        self.service_sg = consoleme_service_sg
        self.redis_sg = consoleme_redis_sg
        self.alb_sg = consoleme_lb_sg
