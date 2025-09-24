from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_logs as logs
from cdk_nag import NagSuppressions
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

        # Create VPC Flow Logs to satisfy AwsSolutions-VPC7
        log_group = logs.LogGroup(
            self,
            "vpc-flow-logs",
            retention=logs.RetentionDays.ONE_WEEK,
        )

        ec2.FlowLog(
            self,
            "vpc-flow-log",
            resource_type=ec2.FlowLogResourceType.from_vpc(vpc),
            destination=ec2.FlowLogDestination.to_cloud_watch_logs(log_group),
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

        # Suppress AwsSolutions-IAM5 for SSM permissions required by BastionHostLinux
        # These wildcard permissions are necessary for SSM Session Manager connectivity
        NagSuppressions.add_resource_suppressions(
            host.role.node.find_child("DefaultPolicy"),
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": (
                        "SSM Session Manager requires ec2messages:* and ssmmessages:* "
                        "permissions for secure shell access. Resource wildcard is "
                        "required for SSM service functionality."
                    ),
                    "appliesTo": [
                        "Action::ec2messages:*",
                        "Action::ssmmessages:*",
                        "Resource::*"
                    ],
                }
            ],
        )

        CfnOutput(
            self,
            "start-session",
            value=f"aws ssm start-session --target {host.instance_id}",
        )
