#!/usr/bin/env python
import boto3
import botocore
import sys
import re
import json
import yaml
import argparse


from accountautomation.Account import Account
from accountautomation.OrganizationAccount import OrganizationAccount
from accountautomation.Federation import Federation

__version__ = '1.2.1'
__author__ = 'Paolo Latella'
__email__ = 'paolo.latella@it.clara.net'

# Read configuration from YAML file
def loadAndValidateConfigFile():
    yaml_file = open('config.yml', 'r')
    yaml_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
    return yaml_data
    # Add feature that validate the YAML file configuration

def fromJsonPolicyFile(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data

def getOrganizationData(organizations, organization_name):
    for organization in organizations:
        if organization['Name'] == organization_name:
            return organization
    return None

def getHubData(hubs, hub_name):
    for hub in hubs:
        if hub['Name'] == hub_name:
            return hub
    return None

def replaceAccountInTrustRelationshipPolicy(policy: str, account_id: str) -> str:
    trust_policy_with_correct_account = re.sub('account-id', account_id, policy)
    return trust_policy_with_correct_account

def replaceRoleNameInTrustRelationshipPolicy(policy: str, role_name: str) -> str:
    policy_with_correct_role_name = re.sub('role-name', role_name, policy)
    return policy_with_correct_role_name

if __name__ == '__main__':
    yaml_data = loadAndValidateConfigFile()
    parser = argparse.ArgumentParser(description='Federate two account between them')
    parser.add_argument('--organization-name', required=True, help='Specify the organization name as specified on yaml file')
    parser.add_argument('--hub-name', required=True, help='Specify HUB account id for federation')
    parser.add_argument('--spoke-account-id', required=True, help='specify the SPOKE account id for federation')
    parser.add_argument('--permission', required=True, choices=['admin', 'powerusers', 'readonly'], help='specify the permission')
    parser.add_argument('--role-name', required=False, help='specify the name of the role created by organization in member account')
    args = parser.parse_args()

    organization_data = getOrganizationData(yaml_data['Organizations'], args.organization_name)
    if organization_data == None:
        print("Organization " + args.organization_name + " not found in YAML File")
        sys.exit(1)
    else:
        organization = OrganizationAccount()
        organization.connectToSTSService(organization_data['AccessKeyId'],organization_data['SecretAccessKey'])
        spoke_account_id = args.spoke_account_id
        member_role_arn = "arn:aws:iam::" + str(spoke_account_id) + ":role/" + str(organization_data['AdministrationRoleName'])
        assumed_role_data = organization.assumeRoleInMemberAccount(member_role_arn)

    hub_data = getHubData(yaml_data['Hubs'], args.hub_name)
    if hub_data == None:
        print("Hub " + args.hub_name + " not found in YAML File")
        sys.exit(1)
    else:
        hub = Account()
        hub.connectToIAMService(hub_data['AccessKeyId'], hub_data['SecretAccessKey'])

    trust_policy_from_file = json.dumps(fromJsonPolicyFile('Templates/trust_relationship_policy_document.json'))
    trust_policy = replaceAccountInTrustRelationshipPolicy(trust_policy_from_file, str(hub_data['AccountId']))

    federation_role_name = ''
    if args.role_name == None:
        federation_role_name = 'AWSServiceRoleFrom' + str(args.hub_name)
    else:
        federation_role_name = hub_data['FederationRoleName']

    organization.connectToOrganizationService(organization_data['AccessKeyId'],organization_data['SecretAccessKey'])
    spoke_account_name = organization.getMemberAccountNameFromId(spoke_account_id)
    spoke_account_name = re.sub('[^a-zA-Z]+', '', spoke_account_name)

    if args.permission == 'admin':
        federation_policy = hub_data['AdminFederationPolicyArn']
        group_name = 'AdminsTo'+spoke_account_name
        group_policy_name = 'AdminTo'+spoke_account_name
    elif args.permission == 'powerusers':
        federation_policy = hub_data['PowerUserFederationPolicyArn']
        group_name = 'PowerUsersTo'+spoke_account_name
        group_policy_name = 'PowerUserTo'+spoke_account_name
    elif args.permission == 'readonly':
        federation_policy = hub_data['ReadOnlyFederationPolicyArn']
        group_name = 'ReadOnlyTo'+spoke_account_name
        group_policy_name = 'ReadOnlyTo'+spoke_account_name
    else:
        federation_policy = None
        group_name = None
        sys.exit(1)

    spoke = Account()
    spoke.connectToIAMService(assumed_role_data['Credentials']['AccessKeyId'], assumed_role_data['Credentials']['SecretAccessKey'], assumed_role_data['Credentials']['SessionToken'])

    try:
        federation = Federation(hub,spoke)
        role_name_in_hub_account = federation.createTrustRelationshipBetweenHubAndSpoke(federation_role_name, federation_policy, trust_policy)
        print(role_name_in_hub_account)
        federation.createGroupInhubAccount(group_name)

        group_policy_from_file = json.dumps(fromJsonPolicyFile('Templates/group_policy_document.json'))
        group_policy_with_correct_id = replaceAccountInTrustRelationshipPolicy(group_policy_from_file, str(spoke_account_id))
        group_policy = replaceRoleNameInTrustRelationshipPolicy(group_policy_with_correct_id, str(role_name_in_hub_account))

        federation.setGroupPolicyInHubAccount(group_policy_name, group_policy, group_name)
        print("Federation completed, please add users on " + group_name + " in your Hub account and use switch Role with the following")
        print("AccountId: " + spoke_account_id)
        print("RoleName: " + federation_role_name)
    except Exception as e:
        print(e)
        sys.exit(1)
