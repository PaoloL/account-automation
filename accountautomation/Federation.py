import boto3
import botocore
import time
from accountautomation.Account import Account

class Federation:

    def __init__(self):
        return None

    def __init__(self, hub, spoke):
        self.hub = hub
        self.spoke = spoke
        return None

    def createGroupInhubAccount(self, group_name):
        try:
            response = self.hub.client_to_iam.create_group(GroupName=group_name)
            return response
        except Exception as e:
            print(e)
            return None

    def setGroupPolicyInHubAccount(self, policy_name, policy_document, group_name):
        policy_description = 'Policy created by account automation scripts'
        try:
            response = self.hub.client_to_iam.create_policy(PolicyName=policy_name,PolicyDocument=policy_document,Description=policy_description)
            policy_arn = response['Policy']['Arn']
            self.hub.client_to_iam.attach_group_policy(GroupName=group_name,PolicyArn=policy_arn)
        except Exception as e:
            print(e)
        return None

    def createTrustRelationshipBetweenHubAndSpoke(self, role_name, role_policy_arn, trust_relationship_policy):
        role_name = self.spoke.createRole(role_name, role_policy_arn, trust_relationship_policy)
        return role_name
