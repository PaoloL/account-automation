import boto3
import botocore
import time

class OrganizationAccount:

    def __init__(self):
        self.aws_access_key = None
        self.aws_secret_key = None
        self.aws_session_token = None
        self.account_id = None
        self.client_to_organization = None
        self.client_to_sts = None
        return None

    def setAccountId(self, account_id):
        self.account_id = account_id

    def getAccountId(self):
        return self.account_id

    def getOrganizationClient(self):
        return self.client_to_organization

    def getSTSClient(self):
        return self.client_to_sts

    def getMemberAccountNameFromId(self, account_id):
        account_name = self.client_to_organization.describe_account(AccountId=str(account_id)).get('Account').get('Name')
        return str(account_name)

    def existAccountName(self, account_name):
        #TBD
        return False

    def connectToOrganizationService(self, access_key, secret_key):
        try:
            self.client_to_organization = boto3.client('organizations', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        except Exception as e:
            print(e)
        return None

    def connectToSTSService(self, access_key, secret_key):
        try:
            self.client_to_sts = boto3.client('sts', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        except Exception as e:
            print(e)
        return None

    def createMemberAccount(self, m):
        try:
            create_account_response = self.client_to_organization.create_account(Email=m.getEmail(), AccountName=m.getName(), RoleName=m.getServiceRole())
            create_account_request_id=create_account_response.get('CreateAccountStatus').get('Id')
            # Waiting for completition
            account_status = 'IN_PROGRESS'
            while account_status == 'IN_PROGRESS':
                create_account_status_response = self.client_to_organization.describe_create_account_status(CreateAccountRequestId=create_account_request_id)
                account_status = create_account_status_response.get('CreateAccountStatus').get('State')
                time.sleep(1)
            if account_status == 'SUCCEEDED':
                account_id = create_account_status_response.get('CreateAccountStatus').get('AccountId')
                return account_id
            if account_status == 'FAILED':
                error = create_account_status_response.get('CreateAccountStatus').get('FailureReason')
                raise Exception(error)
        except Exception as e:
            print(e)
            return None

    def changeOUOfMemberAccount(self, account_id, destination_parent_id, source_parent_id=None):
        try:
            if source_parent_id == None:
                source_parent_id = self.client_to_organization.list_roots().get('Roots')[0].get('Id')
            move_account_response = self.client_to_organization.move_account(AccountId=account_id, SourceParentId=source_parent_id, DestinationParentId=destination_parent_id)
            ou_name = self.client_to_organization.describe_organizational_unit(OrganizationalUnitId=str(DestinationParentId))
            return ou_name
        except Exception as e:
            print(e)

    def assumeRoleInMemberAccount(self, role_arn):
        try:
            role_session_name = "SessionFromAccountAdministration"
            assumed_role_object=self.client_to_sts.assume_role(RoleArn=role_arn, RoleSessionName=role_session_name)
            return assumed_role_object
        except Exception as e:
            print(e)
