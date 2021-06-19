from aws_cdk import (
    aws_s3 as s3,
    aws_iam as iam,
    core as cdk
)


class SharedStack(cdk.NestedStack):

    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        s3_bucket = s3.Bucket(
            self,
            'ConfigBucket',
            removal_policy=cdk.RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED
        )

        self.s3_bucket = s3_bucket
