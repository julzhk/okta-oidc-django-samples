# Create your models here.
from __future__ import unicode_literals
from django.conf import settings
from django.db import models

import requests

class DiscoveryDocument:
	# Find the OIDC metadata through discovery

	def __init__(self, base_url):
		r = requests.get(base_url + "/.well-known/openid-configuration")
		self.json = r.json()

	def getJson(self):
		return self.json

class Config:
	# Configuration object
	client_id = settings.CLIENT_ID
	client_secret = settings.CLIENT_SECRET
	audience = settings.AUDIENCE
	idp = settings.IDP

	# OpenID Specific
	grant_type = 'authorization_code'
	scopes = settings.SCOPES
	redirect_uri = 'http://localhost:8080/callback'

class TokenManager:
	def __init__(self):
		self.idToken = None
		self.accessToken = None
		self.claims = None

	def set_id_token(self, token):
		self.idToken = token

	def set_access_token(self, token):
		self.accessToken = token

	def set_claims(self, claims):
		self.claims = claims

	def getJson(self):
		response = {}
		if self.idToken:
			response['idToken'] = self.idToken

		if self.accessToken:
			response['accessToken'] = self.accessToken

		if self.claims:
			response['claims'] = self.claims
		return response
