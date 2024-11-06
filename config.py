
CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI_MCI = 'https://10.2.114.197:5000/login/authorized'
REDIRECT_URI_PORTAL = 'https://10.2.114.197:5000/login/authorized'
REDIRECT_URI_PORTALNEWS = 'https://10.2.114.197:5000/login/authorized'

AUTHORITY_URL = 'https://login.microsoftonline.com/common'

AUTH_ENDPOINT = '/oauth2/v2.0/authorize'
TOKEN_ENDPOINT = '/oauth2/v2.0/token'

RESOURCE = 'https://graph.microsoft.com/'
API_VERSION = 'v1.0'
SCOPES = ['User.Read'] # Add other scopes/permissions as needed.


# This code can be removed after configuring CLIENT_ID and CLIENT_SECRET above.
if 'ENTER_YOUR' in CLIENT_ID or 'ENTER_YOUR' in CLIENT_SECRET:
    print('ERROR: config.py does not contain valid CLIENT_ID and CLIENT_SECRET')
    import sys
    sys.exit(1)
