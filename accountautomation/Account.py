import boto3
import botocore
import time
import re

class Account:

    def __init__(self, access_key=None, secret_key=None):
        if access_key != None:
            self.access_key = access_key
        if secret_key != None:
            self.secret_key = secret_key
        self.client_to_sts = None
        self.client_to_iam = None
        return None

    def getAccountId(self):
        return self.account_id

    def setAccountId(self, account_id):
        self.account_id = account_id

    def connectToIAMService(self, access_key, secret_key, session_token=None):
        try:
            self.client_to_iam = boto3.client('iam', aws_access_key_id=access_key, aws_secret_access_key=secret_key, aws_session_token=session_token)
            return None
        except Exception as e:
            print(e)

    def connectToSTSService(self, access_key, secret_key):
        try:
            self.client_to_sts = boto3.client('sts', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        except Exception as e:
            print(e)
        return None

    def createRole(self, role_name, role_policy_arn, trust_relationship_policy):
        try:
            create_role_response = self.client_to_iam.create_role(RoleName=role_name,AssumeRolePolicyDocument=trust_relationship_policy)
            attach_role_response = self.client_to_iam.attach_role_policy(RoleName=role_name,PolicyArn=role_policy_arn)
            return create_role_response['Role']['RoleName']
        except Exception as e:
            print(e)
