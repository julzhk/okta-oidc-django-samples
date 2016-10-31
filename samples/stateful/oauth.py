import requests

def call_introspect(issuer, token, config):
	# Calls /introspect endpoint to check if accessToken is valid

	url = "{}/oauth2/v1/introspect".format(issuer) 

	header = buildHeader(config)

	data = { 'token' : token }

	# Send introspect request
	r = requests.post(url, headers=header, params=data)
	
	if r.status_code != 401:
		 # Success
		return r.json()
	else:
		# Error
		print r.json()
		return

def call_revocation(issuer, token, config):
	# Calls /revocation endpoint to revoke current accessToken

	url = "{}/oauth2/v1/revoke".format(issuer)

	header = buildHeader(config)

	data = { 'token' : token }

	# Send revocation request
	r = requests.post(url, headers=header, params=data)
	if r.status_code == 204:
		return
	else:
		return r.json()


def buildHeader(config):
	import base64
	# Builds the header for sending requests

	authorization_header = base64.b64encode('{}:{}'.format(config.client_id,config.client_secret))

	header = {
		'Authorization' : 'Basic: ' + authorization_header,
		'Content-Type': 'application/x-www-form-urlencoded'
	}

	return header
		


