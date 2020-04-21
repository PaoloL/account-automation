import boto3
import botocore
import time
import re
from accountautomation.Account import Account

class MemberAccount(Account):

    def __init__(self):
        return None

    def __init__(self, name, email, role_name=None):
        self.name = name
        self.email = email
        if role_name == None:
            self.role_name = 'AWSServiceRoleFromYourOrganization'
        return None

    def getName(self):
        return self.name

    def getEmail(self):
        return self.email

    def getServiceRole(self):
        return self.role_name

    def setServiceRole(self, role_name):
        self.role_name = role_name
