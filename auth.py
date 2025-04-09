import os
import json
from flask import Flask, redirect, request, session
from flask_session import Session
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.secret_key = 'your_static_secret_key_123'

# Use server-side sessions
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

# OAuth client setup
oauth = OAuth(app)

quickbooks = oauth.register(
    name='quickbooks',
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    access_token_url='https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer',
    authorize_url='https://appcenter.intuit.com/connect/oauth2',
    api_base_url='https://quickbooks.api.intuit.com/',
    client_kwargs={
        'scope': 'com.intuit.quickbooks.accounting',
        'token_endpoint_auth_method': 'client_secret_post'
    }
)

# === OAuth Start ===
@app.route('/')
def login():
    redirect_uri = os.getenv("REDIRECT_URI") or "http://localhost:8000/callback"
    return quickbooks.authorize_redirect(redirect_uri)

# === OAuth Callback ===
@app.route('/callback')
def callback():
    print("\n🔄 Callback Received")
    print("🌐 Request args:", request.args)

    # Optional debug logging of CSRF state
    print("🧠 Session state stored:", session.get("oauth_quickbooks_state"))
    print("📥 State from request:", request.args.get("state"))

    try:
        token = quickbooks.authorize_access_token()
    except Exception as e:
        print("❌ Error during token exchange:", str(e))
        return "Error during authorization. Check terminal for details.", 500

    # Get realm ID from query string
    realm_id = request.args.get('realmId')
    token['realm_id'] = realm_id

    # Save token + realm ID to file
    with open('token.json', 'w') as f:
        json.dump(token, f)

    print("\n✅ Access Token:")
    print(json.dumps(token, indent=2))

    return "✅ Authorization successful! You can close this tab."

# === Start Flask server ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8000)))




