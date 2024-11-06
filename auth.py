import os
import urllib.parse
import uuid
from flask import Flask, redirect, request, render_template, session
import adal
import requests
import config

app = Flask(__name__, template_folder='static/templates')
app.secret_key = 'development'
app.debug = True

SESSION = requests.Session()

# Gunakan sertifikat dan kunci yang sudah dibuat di root proyek
CERT_FILE = 'cert.pem'
KEY_FILE = 'key.pem'

# Periksa apakah file sertifikat dan kunci ada
if not os.path.isfile(CERT_FILE) or not os.path.isfile(KEY_FILE):
    raise FileNotFoundError("The certificate or key file was not found.")

# Gunakan sertifikat dan kunci yang sudah dibuat
ssl_context = (CERT_FILE, KEY_FILE)

@app.route('/')
def homepage():
    """Render halaman utama."""
    return render_template('homepage.html', sample='ADAL')

@app.route('/login')
def login():
    """Minta pengguna untuk mengotentikasi."""
    app_type = request.args.get('app_type', 'mci')  # Default to 'mci' if not provided
    auth_state = str(uuid.uuid4())
    session['auth_state'] = auth_state
    session['app_type'] = app_type  # Save app_type in session

    # Define redirect URIs based on app type
    if app_type == 'mci':
        redirect_uri = config.REDIRECT_URI_MCI
    elif app_type == 'portal':
        redirect_uri = config.REDIRECT_URI_PORTAL
    else:  # Assuming the new app_type is 'portalnews'
        redirect_uri = config.REDIRECT_URI_PORTALNEWS

    params = urllib.parse.urlencode({'response_type': 'code',
                                     'client_id': config.CLIENT_ID,
                                     'redirect_uri': redirect_uri,
                                     'state': auth_state,
                                     'resource': config.RESOURCE,
                                     'prompt': 'select_account',
                                     'scope': 'User.Read email',
                                     'app_type': app_type})  # Pass app_type in query params

    return redirect(config.AUTHORITY_URL + '/oauth2/authorize?' + params)


@app.route('/login/authorized')
def authorized():
    """Penangan untuk Redirect Uri aplikasi."""
    code = request.args['code']
    auth_state = request.args['state']
    app_type = session.get('app_type', 'mci')  # Get app_type from session

    if auth_state != session['auth_state']:
        raise Exception('state returned to redirect URL does not match!')

    auth_context = adal.AuthenticationContext(config.AUTHORITY_URL, api_version=None)
    
    # Select the correct redirect URI based on app_type
    if app_type == 'mci':
        redirect_uri = config.REDIRECT_URI_MCI
    elif app_type == 'portal':
        redirect_uri = config.REDIRECT_URI_PORTAL
    else:  # Assuming the new app_type is 'portalnews'
        redirect_uri = config.REDIRECT_URI_PORTALNEWS
    
    token_response = auth_context.acquire_token_with_authorization_code(
        code, redirect_uri, config.RESOURCE,
        config.CLIENT_ID, config.CLIENT_SECRET
    )

    # Dapatkan data dari Microsoft Graph
    graph_endpoint = 'https://graph.microsoft.com/v1.0/me'
    http_headers = {'Authorization': f"Bearer {token_response['accessToken']}"}
    graph_data = SESSION.get(graph_endpoint, headers=http_headers, stream=False).json()

    # Redirect based on the app_type
    if app_type == 'mci':
        redirect_url = (
            f"https://10.2.114.197/mcitsel/callback?displayName={graph_data.get('displayName')}&"
            f"id={graph_data.get('id')}&jobTitle={graph_data.get('jobTitle')}&"
            f"mail={graph_data.get('mail')}&mobilePhone={graph_data.get('mobilePhone')}&"
            f"officeLocation={graph_data.get('officeLocation')}"
        )
    elif app_type == 'portal':
        redirect_url = (
            f"https://10.2.114.197/portaldashboardv2/callback?displayName={graph_data.get('displayName')}&"
            f"id={graph_data.get('id')}&jobTitle={graph_data.get('jobTitle')}&"
            f"mail={graph_data.get('mail')}&mobilePhone={graph_data.get('mobilePhone')}&"
            f"officeLocation={graph_data.get('officeLocation')}"
        )
    else:  # For 'portalnews'
        redirect_url = (
            f"https://10.2.114.197/portalnews/callback?displayName={graph_data.get('displayName')}&"
            f"id={graph_data.get('id')}&jobTitle={graph_data.get('jobTitle')}&"
            f"mail={graph_data.get('mail')}&mobilePhone={graph_data.get('mobilePhone')}&"
            f"officeLocation={graph_data.get('officeLocation')}"
        )

    return redirect(redirect_url)

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=ssl_context, use_debugger=True, use_reloader=True)
