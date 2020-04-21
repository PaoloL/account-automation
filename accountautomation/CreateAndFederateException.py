class OrganizationNotFoundException(Exception):

    def __init__(self, organization):
        self.message = "Organization " + organization + " not found in YAML File"

    def getMessage(self):
        return str(self.message)

class EmailFormatException(Exception):

    def __init__(self, email):
        self.message = "Email " + email + " not valid"

    def getMessage(self):
        return str(self.message)
