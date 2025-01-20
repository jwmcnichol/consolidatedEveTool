def get_access_token(client_id, client_secret, scopes):
    auth_url = 'https://login.eveonline.com/v2/oauth/authorize'
    token_url = 'https://login.eveonline.com/v2/oauth/token'
    # page = 1
    print("ACCESS TOKEN REQUIRED: ")
    esi_session = OAuth2Session(
                                client_id,
                                redirect_uri='https://localhost/callback',
                                scope=scopes
                                )
    authorization_url, state = esi_session.authorization_url(auth_url) #add page=page
    print(f"URL:\n{authorization_url}")
    authorization_response = input("Paste redirect: ")
    token = esi_session.fetch_token(
                                    token_url,
                                    authorization_response=authorization_response,
                                    client_secret=client_secret
                                    )
    return token['access_token']