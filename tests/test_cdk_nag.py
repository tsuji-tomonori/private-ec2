from aws_cdk import App, Aspects, assertions
from cdk_nag import AwsSolutionsChecks

from private_ec2.private_ec2_stack import PrivateEc2Stack


def test_cdk_nag():
    app = App()
    stack = PrivateEc2Stack(app, "PrivateEc2Stack")
    Aspects.of(stack).add(AwsSolutionsChecks(verbose=True))

    # ルール ID で ERROR / WARN を抽出
    errors = assertions.Annotations.from_stack(stack).find_error(
        "*", assertions.Match.string_like_regexp(r"AwsSolutions-.*")
    )

    warns = assertions.Annotations.from_stack(stack).find_warning(
        "*", assertions.Match.string_like_regexp(r"AwsSolutions-.*")
    )

    with open("cdk_nag_report.txt", "w") as f:
        for e in errors:
            f.write(f"ERROR: {e}\n")
        for w in warns:
            f.write(f"WARN: {w}\n")

    assert errors == [], f"CDK Nag Errors: {errors}"
    assert warns == [], f"CDK Nag Warnings: {warns}"
