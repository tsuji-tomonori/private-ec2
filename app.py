from pathlib import Path

import aws_cdk as cdk
import tomllib
from aws_cdk import Tags

from private_ec2.private_ec2_stack import PrivateEc2Stack


def add_name_tag(scope):  # noqa: ANN001, ANN201
    for child in scope.node.children:
        if cdk.Resource.is_resource(child):
            tag_value = child.node.path.replace("/", "-").replace("_", "-")
            Tags.of(child).add("Name", tag_value)
        add_name_tag(child)


with (Path.cwd() / "pyproject.toml").open("rb") as f:
    project = tomllib.load(f)["project"]["name"]

app = cdk.App()
PrivateEc2Stack(
    scope=app,
    construct_id=f"{project.replace('_', '-')}",
)

Tags.of(app).add("Project", project)
Tags.of(app).add("ManagedBy", "cdk")
add_name_tag(app)

app.synth()
