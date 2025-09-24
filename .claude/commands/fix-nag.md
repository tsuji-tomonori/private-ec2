---
allowed-tools: mcp__cdk-mcp-server__ExplainCDKNagRule, Bash(uv run --dev pytest), Read, Edit, Glob, Grep, MultiEdit, Bash(git)
description: CDK Nagアラートを解消するためのカスタムスラッシュコマンド
argument-hint: [rule-id] [comment] (例: AwsSolutions-APIG2 "セキュリティ上の理由で抑制")
---

## コンテキスト

CDK Nagアラートを解消するために以下の手順を実行します：

1. **ルール分析**: CDK MCPを使用してルールの詳細を把握
2. **コード修正**: private_ec2/private_ec2_stack.py 内のCDKコードを修正
3. **テスト実行**: uv run --dev pytestを実行して結果確認
4. **ドキュメント更新**: cdk-nag.mdに対応内容を追記

## 引数

- `$ARGUMENTS`: 修正対象のCDK Nagルール (例: AwsSolutions-APIG2)
- オプション: コメント（抑制理由など）を指定可能

## タスク実行

### 1. ルール分析
引数で指定されたCDK Nagルール（`$ARGUMENTS`）について、CDK MCPを使用して詳細な情報を取得します。

### 2. 現在のアラート状況確認
- 現在のCDK Nagレポート: @cdk_nag_report.txt
- 修正履歴: @cdk-nag.md

### 3. CDKコード修正
package/infra/src ディレクトリ内の関連するCDKコードを特定し、ルールに準拠するよう修正します。
コメントが指定されている場合は、NagSuppression抑制を適用し、コメントを理由として記録します。

### 4. テスト実行と結果確認
修正後、`uv run --dev pytest`を実行してCDK Nagスキャンの結果を確認します。

### 5. ドキュメント更新
修正内容をcdk-nag.mdに追記し、対応履歴を記録します。
以下のフォーマットに従います。

```md
## {{ ルール名 }}

### 問題
{{ このエラーが発生した理由を詳細に明記 }}

### 対象
{{ 修正対象のリソースを明記 }}

### 修正コード

```python
# 修正前: {{ エラーの内容を簡潔に記載 }}
# {{ 修正前のコードを引用する }}

# 修正後: {{ 修正した内容を簡潔に記載 }}
# {{ 修正後のコードを引用する }}
```

### 効果
- {{ 修正したことで発生した効果を記載 }}

```
---

**使用例**:
- `/fix-nag AwsSolutions-APIG2` (修正対応)
- `/fix-nag AwsSolutions-S1 "開発環境のため抑制"` (抑制対応)
- `/fix-nag AwsSolutions-IAM5 セキュリティ上の理由で抑制` (抑制対応)
