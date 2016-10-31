from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from models import DiscoveryDocument, Config, TokenManager

import requests, json, sys
from tokens import token_validation
from openid import call_token_endpoint, call_userinfo_endpoint
from oauth import call_introspect, call_revocation

# GLOBALS
config = Config()
token_manager = TokenManager()

def getContext(request):
	context = {'active' : True }
	if 'tokens' in request.session:
		context['tokens'] = request.session['tokens']
		if 'claims' in request.session['tokens']:
			context['claims'] = json.dumps(request.session['tokens']['claims'],
				sort_keys=True, indent=4)
	
	if 'userInfo' in request.session:
		context['userInfo'] = request.session['userInfo']

	if 'introspect' in request.session:
		context['introspect'] = request.session['introspect']

	if 'revocation' in request.session:
		context['revocation'] = request.session['revocation']


	return context

def login_controller(request):
	okta_config = {
		'clientId' : config.client_id,
		'url' : config.audience,
		'redirectUri' : str(config.redirect_uri),
		'scope' : config.scopes,
		'idp' : config.idp
	}
	response = render(request, 'stateful/login.html', {'config' : okta_config})
	
	delete_cookies(response)

	return response

def callback_controller(request):
	# Handles the token exchange from the redirect
	def token_request(auth_code, nonce):
		# Setup Token Request

		discovery_doc = DiscoveryDocument(config.audience).getJson()
		token_endpoint = discovery_doc['token_endpoint']

		tokens = call_token_endpoint(token_endpoint, auth_code, config)
		user = None

		if tokens != None:
			if 'id_token' in tokens:
				# Perform token validation
				claims = token_validation(tokens['id_token'], config, nonce)
								
				if claims:
					token_manager.set_id_token(tokens['id_token'])
					# Authenticate User
					user = validate_user(claims)
					token_manager.set_claims(claims)

			if 'access_token' in tokens:
				token_manager.set_access_token(tokens['access_token'])

		return user, token_manager.getJson()

  	if request.POST:
		return HttpResponse({'error' : 'Endpoint not supported'})
	
	else:
		code = request.GET['code']
		state = request.GET['state']

		# Get state and nonce from cookie
		cookie_state = request.COOKIES["okta-oauth-state"]
		cookie_nonce = request.COOKIES["okta-oauth-nonce"]

		# Verify state
		if state != cookie_state:
			raise Exception("Value {} does not match the assigned state".format(state))
			return redirect('/login')
				
		user, token_manager_json = token_request(code, cookie_nonce)
		print user, token_manager_json
		request.session['tokens'] = token_manager_json

		if user is None:
			return redirect('/login')
		
		login(request, user)
		print "User logged in as {}".format(user)
		return redirect('/')

@login_required(redirect_field_name=None, login_url='/login')
def home_controller(request):
	return render(request, 'stateful/home.html', getContext(request))

@login_required(redirect_field_name=None, login_url='/login')
def revocation_controller(request):
	# Calls the revocation endpoint for revoking the accessToken
	if request.POST:

		access_token = request.POST.get('accessToken')

		discovery_doc = DiscoveryDocument(config.audience).getJson()

		revocation = call_revocation(discovery_doc['issuer'], access_token, config)

		if revocation == None:
			request.session['revocation'] = 'Access Token Revoked'
		else:
			request.session['revocation'] = json.dumps(revocation, indent=4)

	return render(request, 'stateful/home.html', getContext(request))

@login_required(redirect_field_name=None, login_url='/login')
def introspect_controller(request):
	# Calls the introspect endpoint for checking the accessToken

	if request.POST:

		access_token = request.POST.get('accessToken')
		
		discovery_doc = DiscoveryDocument(config.audience).getJson()

		introspect = call_introspect(discovery_doc['issuer'], access_token, config)
		
		if introspect != None:
			request.session['introspect'] = json.dumps(introspect, indent=4)

	return render(request, 'stateful/home.html', getContext(request))

@login_required(redirect_field_name=None, login_url='/login')
def userinfo_controller(request):
	# Calls userInfo endpoint with accessToken
	
	if request.POST:
		# Build token request
		access_token = request.POST.get('accessToken')

		discovery_doc = DiscoveryDocument(config.audience).getJson()

		user_info_endpoint = discovery_doc['userinfo_endpoint']

		# Send request
		userInfo = call_userinfo_endpoint(user_info_endpoint, access_token)
		
		if userInfo != None:
			request.session['userInfo'] = json.dumps(userInfo, indent=4)
		
	return render(request, 'stateful/home.html', getContext(request))


@login_required(redirect_field_name=None, login_url='/login')
def logout_controller(request):
	logout(request)
	token_manager = None
	return redirect('/login')

def validate_user(claims):
	# Create user for django session
	user = authenticate(
		username=claims['email'],
		password=claims['sub']
	)
	if user is None:
		# Create user
		new_user = User.objects.create_user(
			claims['email'],
			claims['email'],
			claims['sub']
		)
		print "Created User"

	return user

def delete_cookies(response):
	# Delete authJS/widget cookies
	response.set_cookie('okta-oauth-state', '', max_age=1)
	response.set_cookie('okta-oauth-nonce', '', max_age=1)
	response.set_cookie('okta-oauth-redirect-params', '', max_age=1)