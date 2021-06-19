from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_elasticache as ec,
    aws_elasticloadbalancingv2 as lb,
    aws_logs as logs,
    aws_iam as iam,
    aws_certificatemanager as acm,
    core as cdk
)

from constants import CONTAINER_IMAGE


class ComputeStack(cdk.NestedStack):

    def __init__(self, scope: cdk.Construct, id: str,
                 vpc: ec2.Vpc, service_sg: ec2.SecurityGroup,
                 s3_bucket_name: str, certificate: acm.Certificate,
                 alb: lb.ApplicationLoadBalancer, alb_sg: ec2.SecurityGroup,
                 task_role_arn: str, task_execution_role_arn: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # S3 Bucket Details


        # ECS Task definition and volumes

        imported_task_role = iam.Role.from_role_arn(
            self,
            'ImportedTaskRole',
            role_arn=task_role_arn
        )

        imported_task_execution_role = iam.Role.from_role_arn(
            self,
            'ImportedTaskExecutionRole',
            role_arn=task_execution_role_arn
        )

        ecs_task_definition = ecs.FargateTaskDefinition(
            self,
            'TaskDefinition',
            cpu=2048,
            memory_limit_mib=4096,
            execution_role=imported_task_execution_role,
            task_role=imported_task_role
        )

        # ECS Container definition, service, target group and ALB attachment

        container = ecs_task_definition.add_container(
            'Container',
            image=ecs.ContainerImage.from_registry(CONTAINER_IMAGE),
            privileged=False,
            port_mappings=[
                ecs.PortMapping(
                    container_port=8081,
                    host_port=8081,
                    protocol=ecs.Protocol.TCP
                )
            ],
            logging=ecs.LogDriver.aws_logs(
                stream_prefix='ContainerLogs-',
                log_retention=logs.RetentionDays.ONE_WEEK
            ),
            environment={
                'SETUPTOOLS_USE_DISTUTILS': 'stdlib',
                'CONSOLEME_CONFIG_S3': 's3://' + s3_bucket_name + '/config.yaml'
            },
            working_directory='/apps/consoleme',
            command=[
                "bash", "-c", "python scripts/retrieve_or_decode_configuration.py; python consoleme/__main__.py"]
        )

        celery_container = ecs_task_definition.add_container(
            'CeleryContainer',
            image=ecs.ContainerImage.from_registry(CONTAINER_IMAGE),
            privileged=False,
            logging=ecs.LogDriver.aws_logs(
                stream_prefix='CeleryContainerLogs-',
                log_retention=logs.RetentionDays.ONE_WEEK
            ),
            environment={
                'SETUPTOOLS_USE_DISTUTILS': 'stdlib',
                'CONSOLEME_CONFIG_S3': 's3://' + s3_bucket_name + '/config.yaml',
                'COLUMNS': '80'
            },
            command=["bash", "-c",
                     "python scripts/retrieve_or_decode_configuration.py; python scripts/initialize_redis_oss.py; celery -A consoleme.celery_tasks.celery_tasks worker -l DEBUG -B -E --concurrency=8"]
        )

        # ECS cluster

        cluster = ecs.Cluster(
            self, 'Cluster',
            vpc=vpc
        )

        imported_alb = lb.ApplicationLoadBalancer.from_application_load_balancer_attributes(
            self,
            'ServiceImportedALB',
            load_balancer_arn=alb.load_balancer_arn,
            vpc=vpc,
            security_group_id=alb_sg.security_group_id,
            load_balancer_dns_name=alb.load_balancer_dns_name
        )

        ecs_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, 'Service',
            cluster=cluster,
            task_definition=ecs_task_definition,
            load_balancer=imported_alb,
            desired_count=1,
            security_groups=[service_sg],
            open_listener=False
        )

        ecs_service.target_group.configure_health_check(
            path='/',
            enabled=True,
            healthy_http_codes='200-302'
        )

        imported_alb.add_listener(
            'ServiceALBListener',
            protocol=lb.ApplicationProtocol.HTTPS,
            port=443,
            certificates=[certificate],
            default_action=lb.ListenerAction.forward(
                target_groups=[ecs_service.target_group])
        )
