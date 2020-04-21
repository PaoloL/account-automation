#!/usr/bin/env python
import boto3
import botocore
import sys
import re
import json
import yaml
import argparse

from accountautomation.MemberAccount import MemberAccount
from accountautomation.OrganizationAccount import OrganizationAccount

__version__ = '1.2.1'
__author__ = 'Paolo Latella'
__email__ = 'paolo.latella@it.clara.net'

# Read configuration from YAML file
def loadAndValidateConfigFile():
    yaml_file = open('config.yml', 'r')
    yaml_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
    # Add feature that validate the YAML file configuration
    return yaml_data

def fromJsonPolicyFile(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data

def getOrganizationData(organizations, organization_name):
    for organization in organizations:
        if organization['Name'] == organization_name:
            return organization
    return None

def getOrganizationData(organizations, organization_name):
    for organization in organizations:
        if organization['Name'] == organization_name:
            return organization
    return None

if __name__ == '__main__':
    yaml_data = loadAndValidateConfigFile()
    parser = argparse.ArgumentParser(description='Create account under AWS Organization')
    parser.add_argument('--organization-name', required=True, help='Specify organization name as specified on yaml file')
    parser.add_argument('--member-name', required=True, help='Specify the name of the member account')
    parser.add_argument('--member-email', required=True, help='Specify the e-mail of the member account')
    parser.add_argument('--member-ou-id', required=False, help='Specify the OU id of the member account')
    args = parser.parse_args()

    organization_data = getOrganizationData(yaml_data['Organizations'], args.organization_name)
    if organization_data == None:
        print("Organization " + args.organization_name + " not found in YAML File")
        sys.exit(1)

    if re.match(yaml_data['General']['EmailValidation'], args.member_email) == None:
        print("Email " + args.member_email + " not valid")
        sys.exit(1)

    member = MemberAccount(args.member_name, args.member_email)
    member.setServiceRole(organization_data['AdministrationRoleName'])

    organization = OrganizationAccount()
    organization.connectToOrganizationService(organization_data['AccessKeyId'],organization_data['SecretAccessKey'] )
    if organization.existAccountName(member.getName()) == True:
        print("An account with name " + args.member_name + " already exist in organization")
        sys.exit(1)

    member_account_id = organization.createMemberAccount(member)
    print("Account " + str(member_account_id) + " created!")
    print("Service-linked role " + member.getServiceRole() + " created")

    if args.member_ou_id != None:
        ou_name = organization.changeOUOfMemberAccount(member_account_id, args.member_ou_id)
        print("Account moved on " + ou_name)
