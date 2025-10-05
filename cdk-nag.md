# CDK-nag レポート

## 修正前のERROR

| No.  | ルール名 | リソース | 問題の内容 | 対応が必要な箇所 | 対応が必要な理由 |
| ---- | -------- | -------- | ---------- | ---------------- | ---------------- |
| ~~1~~ | ~~AwsSolutions-VPC7~~ | ~~VPC001~~ | ~~VPCにFlow Logが関連付けられていない~~ | **修正完了** | VPCにFlow Logsを追加してCloudWatch Logsに送信 |
| ~~2~~ | ~~AwsSolutions-IAM5~~ | ~~/PrivateEc2Stack/instance001/Resource/InstanceRole/DefaultPolicy/Resource~~ | ~~IAMポリシーでワイルドカード権限(ssmmessages:*)が使用されている~~ | **抑制完了** | SSM Session Manager接続に必要な権限のため抑制 |
| ~~3~~ | ~~AwsSolutions-IAM5~~ | ~~/PrivateEc2Stack/instance001/Resource/InstanceRole/DefaultPolicy/Resource~~ | ~~IAMポリシーでワイルドカード権限(ec2messages:*)が使用されている~~ | **抑制完了** | SSM Session Manager接続に必要な権限のため抑制 |
| ~~4~~ | ~~AwsSolutions-IAM5~~ | ~~/PrivateEc2Stack/instance001/Resource/InstanceRole/DefaultPolicy/Resource~~ | ~~IAMポリシーでワイルドカードリソース(*)が使用されている~~ | **抑制完了** | SSM Session Manager接続に必要な権限のため抑制 |
| ~~5~~ | ~~AwsSolutions-EC28~~ | ~~/PrivateEc2Stack/instance001/Resource/Resource~~ | ~~EC2インスタンスで詳細監視が有効化されていない~~ | **修正完了** | EC2インスタンスの詳細監視を有効化 |
| ~~6~~ | ~~AwsSolutions-EC29~~ | ~~/PrivateEc2Stack/instance001/Resource/Resource~~ | ~~EC2インスタンスが終了保護無効でASGに属していない~~ | **修正完了** | EC2インスタンスの終了保護をL1プロパティで有効化 |

## 修正前のWARN

| No.  | ルール名 | リソース | 問題の内容 | 対応が必要な箇所 | 対応が必要な理由 |
| ---- | -------- | -------- | ---------- | ---------------- | ---------------- |
| ~~1~~ | ~~AwsSolutions-EC23~~ | ~~/PrivateEc2Stack/endpoint001/SecurityGroup/Resource~~ | ~~セキュリティグループのバリデーションが内部関数参照により失敗~~ | **抑制完了** | CDK Nagのバリデーション制限により抑制が必要 |
| ~~2~~ | ~~AwsSolutions-EC23~~ | ~~/PrivateEc2Stack/endpoint002/SecurityGroup/Resource~~ | ~~セキュリティグループのバリデーションが内部関数参照により失敗~~ | **抑制完了** | CDK Nagのバリデーション制限により抑制が必要 |
| ~~3~~ | ~~AwsSolutions-EC23~~ | ~~/PrivateEc2Stack/endpoint003/SecurityGroup/Resource~~ | ~~セキュリティグループのバリデーションが内部関数参照により失敗~~ | **抑制完了** | CDK Nagのバリデーション制限により抑制が必要 |

## 修正履歴

### AwsSolutions-VPC7 (修正完了)
**問題**: VPCにFlow Logが関連付けられていない
**修正内容**: VPC Flow LogsをCloudWatch Logsに送信するように設定
**修正ファイル**: `private_ec2/private_ec2_stack.py`
**修正日**: 2025-09-25

```python
# VPC作成後にFlow Logsを追加
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
```

**効果**: VPCのネットワークフロー情報がCloudWatch Logsに記録されるようになり、ネットワーク問題のトラブルシューティングが可能になった。

### AwsSolutions-IAM5 (抑制完了)
**問題**: BastionHostLinuxで使用されるIAMポリシーでワイルドカード権限が使用されている
**対応方法**: NagSuppressionsを使用して該当権限を抑制
**修正ファイル**: `private_ec2/private_ec2_stack.py`
**修正日**: 2025-09-25

```python
# SSM Session Manager接続に必要なワイルドカード権限を抑制
NagSuppressions.add_resource_suppressions_by_path(
    self,
    "/PrivateEc2Stack/instance001/Resource/InstanceRole/DefaultPolicy/Resource",
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
```

**効果**: SSM Session Manager機能に必要なワイルドカード権限（ec2messages:*、ssmmessages:*、Resource:*）が適切に文書化された理由と共に抑制され、CDK Nag違反が解消された。

### AwsSolutions-EC28 (修正完了)
**問題**: EC2インスタンスで詳細監視が有効化されていない
**修正内容**: BastionHostLinux の EC2インスタンスで詳細監視を有効化
**修正ファイル**: `private_ec2/private_ec2_stack.py`
**修正日**: 2025-09-25

```python
# 修正前: 詳細監視が無効
host = ec2.BastionHostLinux(
    self,
    "instance001",
    vpc=vpc,
    # 他のパラメータ...
)

# 修正後: CloudFormationリソースにアクセスして詳細監視を有効化
# Enable detailed monitoring to satisfy AwsSolutions-EC28
cfn_instance = host.instance.node.default_child
cfn_instance.monitoring = True
```

**効果**: EC2インスタンスで詳細監視が有効になり、1分間隔でのメトリクス収集によってコンピュートリソースの適切な監視と管理が可能になった。

### AwsSolutions-EC29 (修正完了)
**問題**: EC2インスタンスが終了保護無効でASGに属していない
**修正内容**: L1 CfnInstanceプロパティで終了保護を有効化
**修正ファイル**: `private_ec2/private_ec2_stack.py`
**修正日**: 2025-09-25

```python
# 修正前: add_overrideを使用（CDK Nagが検出しにくい）
cfn_instance.add_override("Properties.DisableApiTermination", True)

# 修正後: L1プロパティを直接使用（CDK Nagが正しく検出）
cfn_instance = host.instance.node.default_child
cfn_instance.disable_api_termination = True
```

**効果**: EC2インスタンスに終了保護が設定され、誤った操作による終了からインスタンスが保護される。L1プロパティを使用することで、CDK NagがDisableApiTermination設定を正しく認識し、抑制なしでルールを通過できる。

### AwsSolutions-EC23 (抑制完了)
**問題**: VPCエンドポイントのセキュリティグループでCDK Nagのバリデーションが内部関数参照により失敗
**対応方法**: CdkNagValidationFailureを抑制し、適切なセキュリティグループ設定を実装
**修正ファイル**: `private_ec2/private_ec2_stack.py`
**修正日**: 2025-09-25

```python
# 修正前: VPCエンドポイントがデフォルトのセキュリティグループを使用
ec2.InterfaceVpcEndpoint(
    self,
    "endpoint001",
    service=ec2.InterfaceVpcEndpointAwsService.EC2_MESSAGES,
    vpc=vpc,
)

# 修正後: 明示的なセキュリティグループを作成し、VPC CIDRのみからのアクセスを許可
endpoint_sg = ec2.SecurityGroup(
    self,
    "endpoint-sg",
    vpc=vpc,
    description="Security group for VPC endpoints - restrict to VPC CIDR only",
    allow_all_outbound=False,
)

endpoint_sg.add_ingress_rule(
    peer=ec2.Peer.ipv4("10.0.0.0/16"),
    connection=ec2.Port.tcp(443),
    description="Allow HTTPS from VPC CIDR (10.0.0.0/16)",
)

# CDK Nagバリデーション制限の抑制
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

ec2.InterfaceVpcEndpoint(
    self,
    "endpoint001",
    service=ec2.InterfaceVpcEndpointAwsService.EC2_MESSAGES,
    vpc=vpc,
    security_groups=[endpoint_sg],
)
```

**効果**: VPCエンドポイントのセキュリティグループが適切に設定され、VPC CIDR（10.0.0.0/16）からのHTTPSアクセスのみを許可し、0.0.0.0/0からのアクセスを防ぐ。CDK Nagのバリデーション制限により抑制が必要だが、実際のセキュリティ設定は適切に実装されている。
