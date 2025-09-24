# CDK-nag レポート

## 修正前のERROR

| No.  | ルール名 | リソース | 問題の内容 | 対応が必要な箇所 | 対応が必要な理由 |
| ---- | -------- | -------- | ---------- | ---------------- | ---------------- |
| ~~1~~ | ~~AwsSolutions-VPC7~~ | ~~VPC001~~ | ~~VPCにFlow Logが関連付けられていない~~ | **修正完了** | VPCにFlow Logsを追加してCloudWatch Logsに送信 |
| ~~2~~ | ~~AwsSolutions-IAM5~~ | ~~/PrivateEc2Stack/instance001/Resource/InstanceRole/DefaultPolicy/Resource~~ | ~~IAMポリシーでワイルドカード権限(ssmmessages:*)が使用されている~~ | **抑制完了** | SSM Session Manager接続に必要な権限のため抑制 |
| ~~3~~ | ~~AwsSolutions-IAM5~~ | ~~/PrivateEc2Stack/instance001/Resource/InstanceRole/DefaultPolicy/Resource~~ | ~~IAMポリシーでワイルドカード権限(ec2messages:*)が使用されている~~ | **抑制完了** | SSM Session Manager接続に必要な権限のため抑制 |
| ~~4~~ | ~~AwsSolutions-IAM5~~ | ~~/PrivateEc2Stack/instance001/Resource/InstanceRole/DefaultPolicy/Resource~~ | ~~IAMポリシーでワイルドカードリソース(*)が使用されている~~ | **抑制完了** | SSM Session Manager接続に必要な権限のため抑制 |
| 5 | AwsSolutions-EC28 | /PrivateEc2Stack/instance001/Resource/Resource | EC2インスタンスで詳細監視が有効化されていない | EC2インスタンス設定 | コンピュートリソースの適切な監視と管理のため |
| 6 | AwsSolutions-EC29 | /PrivateEc2Stack/instance001/Resource/Resource | EC2インスタンスが終了保護無効でASGに属していない | EC2インスタンス設定 | 誤った終了からインスタンスを保護するため |

## 修正前のWARN

| No.  | ルール名 | リソース | 問題の内容 | 対応が必要な箇所 | 対応が必要な理由 |
| ---- | -------- | -------- | ---------- | ---------------- | ---------------- |
| 1 | AwsSolutions-EC23 | /PrivateEc2Stack/endpoint001/SecurityGroup/Resource | セキュリティグループのバリデーションが内部関数参照により失敗 | セキュリティグループ設定 | バリデーションエラーの抑制または設定の見直しが必要 |
| 2 | AwsSolutions-EC23 | /PrivateEc2Stack/endpoint002/SecurityGroup/Resource | セキュリティグループのバリデーションが内部関数参照により失敗 | セキュリティグループ設定 | バリデーションエラーの抑制または設定の見直しが必要 |
| 3 | AwsSolutions-EC23 | /PrivateEc2Stack/endpoint003/SecurityGroup/Resource | セキュリティグループのバリデーションが内部関数参照により失敗 | セキュリティグループ設定 | バリデーションエラーの抑制または設定の見直しが必要 |

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
