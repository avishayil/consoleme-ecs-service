"""
Domain stack for running ConsoleMe on ECS
"""

from aws_cdk import (
    aws_route53 as route53,
    aws_route53_targets as route53_targets,
    aws_elasticloadbalancingv2 as lb,
    aws_certificatemanager as acm,
    core as cdk
)

from constants import APPLICATION_PREFIX, HOSTED_ZONE_ID, HOSTED_ZONE_NAME


class DomainStack(cdk.NestedStack):
    """
    Domain stack for running ConsoleMe on ECS
    """

    def __init__(self, scope: cdk.Construct, id: str, consoleme_alb: lb.ApplicationLoadBalancer, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        hosted_zone = route53.PublicHostedZone.from_hosted_zone_attributes(
            self,
            'HostedZone',
            hosted_zone_id=HOSTED_ZONE_ID,
            zone_name=HOSTED_ZONE_NAME
        )

        route53_record = route53.ARecord(
            self,
            'LBRecord',
            zone=hosted_zone,
            record_name=APPLICATION_PREFIX,
            target=route53.RecordTarget(alias_target=(
                route53_targets.LoadBalancerTarget(consoleme_alb)))
        )

        certificate = acm.Certificate(
            self,
            'Certificate',
            domain_name='*.' + hosted_zone.zone_name,
            validation=acm.CertificateValidation.from_dns(
                hosted_zone=hosted_zone)
        )

        self.hosted_zone = hosted_zone
        self.certificate = certificate
        self.route53_record = route53_record
