from aws_cdk import (
    aws_route53 as route53,
    aws_route53_targets as route53_targets,
    aws_elasticloadbalancingv2 as lb,
    custom_resources as cr,
    aws_certificatemanager as acm,
    aws_iam as iam,
    core as cdk
)

from constants import APPLICATION_PREFIX, HOSTED_ZONE_ID, HOSTED_ZONE_NAME


class ConsolemeDomainStack(cdk.NestedStack):

    def __init__(self, scope: cdk.Construct, id: str, alb: lb.ApplicationLoadBalancer, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        consoleme_hosted_zone = route53.PublicHostedZone.from_hosted_zone_attributes(
            self,
            f'{id}HostedZone',
            hosted_zone_id=HOSTED_ZONE_ID,
            zone_name=HOSTED_ZONE_NAME
        )

        consoleme_route53_record = route53.ARecord(
            self,
            f'{id}LBRecord',
            zone=consoleme_hosted_zone,
            record_name=APPLICATION_PREFIX,
            target=route53.RecordTarget(alias_target=(
                route53_targets.LoadBalancerTarget(alb)))
        )

        domain_identity_verification_resource = cr.AwsCustomResource(
            self,
            f'{id}VerifyDomainIdentity',
            on_create=cr.AwsSdkCall(
                service='SES',
                action='verifyDomainIdentity',
                parameters={
                    'Domain': consoleme_route53_record.domain_name
                },
                physical_resource_id=cr.PhysicalResourceId.from_response(
                    'VerificationToken')
            ),
            policy=cr.AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(
                    actions=['ses:VerifyDomainIdentity'],
                    resources=['*']
                )
            ])
        )

        domain_identity_verification_record = route53.TxtRecord(
            self,
            f'{id}SESVerificationRecord',
            zone=consoleme_hosted_zone,
            record_name='_amazonses.example.com',
            values=[domain_identity_verification_resource.get_response_field(
                'VerificationToken')]
        )

        consoleme_certificate = acm.Certificate(
            self,
            f'{id}Certificate',
            domain_name='*.' + consoleme_hosted_zone.zone_name,
            validation=acm.CertificateValidation.from_dns(
                hosted_zone=consoleme_hosted_zone)
        )

        self.hosted_zone = consoleme_hosted_zone
        self.certificate = consoleme_certificate
        self.route53_record = consoleme_route53_record
