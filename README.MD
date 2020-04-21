# Introduction

# Installation and configuration

Install virtual environment `pip install virtualenv`

Create and enable virtual environment
`python3 -m venv myenv3`
`source myenv3/bin/activate`

Install Boto3
`pip install boto3`

Install Yaml Parser
`pip install pyyaml`

Rename `config-example.yml` in `config.yml` and insert information about Organization and Hub accounts

```
General:
  EmailValidation: '^aws-[a-z][a-z,-]{3,20}@xpeppers.com$'
  MemberAccountNameValiation: '^aws-[a-z][a-z,-]{3,20}@xpeppers.com$'

Organizations:

  - Name: Payer
    AccountId: 7527225182XY
    AccessKeyId: AKIXXXXXXXXXXXXXXXX
    SecretAccessKey: exxxxxxxxxxxxxxxxxxxxxxx
    AdministrationRoleName: PayerOrganizationAccountAccessRole

  - Name: Reseller
    AccountId: 9063453403XY
    AccessKeyId: AKIXXXXXXXXXXXXXXXX
    SecretAccessKey: exxxxxxxxxxxxxxxxxxxxxxx
    AdministrationRoleName: ResellerOrganizationAccountAccessRole

Hubs:

  - Name: XPeppersCentral
    AccountId: 5402184232XY
    AccessKeyId: AKIXXXXXXXXXXXXXXXX
    SecretAccessKey: exxxxxxxxxxxxxxxxxxxxxxx+
    FederationRoleName: AdministrationFromXPeppersCentral
    AdminFederationPolicyArn: arn:aws:iam::aws:policy/AdministratorAccess
    PowerUsersFederationPolicyArn: arn:aws:iam::aws:policy/PowerUserAccess
    ReadOnlyFederationPolicyArn: arn:aws:iam::aws:policy/ReadOnlyAccess
```

# Create IAM Policy
On *Hub* Account create the following policy for this script
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "iam:CreateGroup",
                "iam:ListGroups",
                "iam:CreatePolicy",
                "iam:AttachGroupPolicy"
            ],
            "Resource": "*"
        }
    ]
}
```

# Create a new account

Create a new account
`python create.py --organization-name <account organization name> --member-name <account member name> --member-email <account member email>`

This script return informations as these:
```
Account 420736453999 created!
Service-linked role GrampusOrganizationAccountAccessRole created
```

# Federate a new or existing account

`python federate.py --organization-name <account organization name> --hub-name <account hub name> --spoke-account-id <account id returned on create operation>`

This script return informations as these:
```
Federation completed, please add users on AdminsToTestAccount in your Hub account, use switch Role with the following:
AccountId: 4207364539999
RoleName: AWSServiceRoleFromXPeppersCentral
```
