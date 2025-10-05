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

        # Create security group for VPC endpoints to satisfy AwsSolutions-EC23
        # Restrict access to VPC CIDR only instead of 0.0.0.0/0
        endpoint_sg = ec2.SecurityGroup(
            self,
            "endpoint-sg",
            vpc=vpc,
            description="Security group for VPC endpoints - restrict to VPC CIDR only",
            allow_all_outbound=False,  # Explicitly disable all outbound to be more restrictive
        )

        # Allow HTTPS inbound from VPC CIDR only (not 0.0.0.0/0)
        # Use explicit CIDR to avoid CDK Nag validation issues with intrinsic functions
        endpoint_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4("10.0.0.0/16"),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS from VPC CIDR (10.0.0.0/16)",
        )

        # Suppress CdkNagValidationFailure for endpoint security group
        # This occurs because CDK Nag cannot validate intrinsic functions at synthesis time
        NagSuppressions.add_resource_suppressions(
            endpoint_sg,
            [
                {
                    "id": "CdkNagValidationFailure",
                    "reason": (
                        "CDK Nag validation failure occurs due to intrinsic function "
                        "references. Security group is configured to allow HTTPS from "
                        "VPC CIDR only (10.0.0.0/16), not 0.0.0.0/0."
                    ),
                }
            ],
        )

        # create vpc endpoint with explicit security group
        ec2.InterfaceVpcEndpoint(
            self,
            "endpoint001",
            service=ec2.InterfaceVpcEndpointAwsService.EC2_MESSAGES,
            vpc=vpc,
            security_groups=[endpoint_sg],
        )
        ec2.InterfaceVpcEndpoint(
            self,
            "endpoint002",
            service=ec2.InterfaceVpcEndpointAwsService.SSM,
            vpc=vpc,
            security_groups=[endpoint_sg],
        )
        ec2.InterfaceVpcEndpoint(
            self,
            "endpoint003",
            service=ec2.InterfaceVpcEndpointAwsService.SSM_MESSAGES,
            vpc=vpc,
            security_groups=[endpoint_sg],
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

        # Enable detailed monitoring and termination protection to satisfy AwsSolutions-EC28 and AwsSolutions-EC29
        # Access the underlying CloudFormation resource
        cfn_instance = host.instance.node.default_child
        cfn_instance.monitoring = True  # type: ignore
        # Use L1 property instead of override for better CDK Nag detection
        cfn_instance.disable_api_termination = True  # type: ignore

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
                        "Resource::*",
                    ],
                }
            ],
        )

        CfnOutput(
            self,
            "start-session",
            value=f"aws ssm start-session --target {host.instance_id}",
        )
