import aws_cdk as core
import aws_cdk.assertions as assertions

from private_ec2.private_ec2_stack import PrivateEc2Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in private_ec2/private_ec2_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = PrivateEc2Stack(app, "private-ec2")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
