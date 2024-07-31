from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class PrivateEc2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:  # noqa: ANN101, ANN003
        super().__init__(scope, construct_id, **kwargs)

        # create vpc, subnet nad route table
        vpc = ec2.Vpc(
            self,
            "vpc001",
            max_azs=1,
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                ),
                ec2.SubnetConfiguration(
                    name="private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                ),
            ],
            nat_gateways=0,
        )

        # create vpc endpoint
        ec2.InterfaceVpcEndpoint(
            self,
            "endpoint001",
            service=ec2.InterfaceVpcEndpointAwsService.EC2_MESSAGES,
            vpc=vpc,
        )
        ec2.InterfaceVpcEndpoint(
            self,
            "endpoint002",
            service=ec2.InterfaceVpcEndpointAwsService.SSM,
            vpc=vpc,
        )
        ec2.InterfaceVpcEndpoint(
            self,
            "endpoint003",
            service=ec2.InterfaceVpcEndpointAwsService.SSM_MESSAGES,
            vpc=vpc,
        )

        # create ec2 instance
        host = ec2.BastionHostLinux(
            self,
            "instance001",
            vpc=vpc,
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/sdh",
                    volume=ec2.BlockDeviceVolume.ebs(
                        volume_size=8,
                        encrypted=True,
                    ),
                ),
            ],
        )

        CfnOutput(
            self,
            "start-session",
            value=f"aws ssm start-session --target {host.instance_id}",
        )

