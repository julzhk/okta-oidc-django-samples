import requests

def call_token_endpoint(url, code, config):
	import base64

	""" Call /token endpoint

		Returns accessToken, idToken, or both
	"""
	
	authorization_header = base64.b64encode('{}:{}'.format(config.client_id,config.client_secret))

	header = {
		'Authorization' : 'Basic: ' + authorization_header,
		'Content-Type': 'application/x-www-form-urlencoded'
	}

	data = {
		'grant_type' : config.grant_type,
		'code' : str(code),
		'scope' : ' '.join(config.scopes),
		'redirect_uri' : config.redirect_uri
	}

	# Send token request
	r = requests.post(url, headers=header, params=data)
	response = r.json()
	# Return object
	result = {}
	if 'error' not in response:
		if 'access_token' in response:
			result['access_token'] = response['access_token']
		if 'id_token' in response:
			result['id_token'] = response['id_token']
	
	return result if len(result.keys()) > 0 else None

def call_userinfo_endpoint(url, token):
	# Call /userinfo endpoint

	header = { 'Authorization' : 'Bearer {}'.format(token) }

	r = requests.get(url, headers=header)

	if r.status_code != 401:
		# Success
		return r.json()
	return
