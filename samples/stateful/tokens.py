import time
import jwt as jwt_python 
from jose import jwt
from jose import jws
import requests

# Validate token (Taken from http://openid.net/specs/openid-connect-core-1_0.html#TokenResponseValidation)

def token_validation(token, config, nonce):
	# Perform Token Validation

	
	def jwks(kid, url):
		# Get keys from jwks_uri

		r = requests.get(url)
		jwks = r.json()
		return [key for key in jwks['keys'] if kid == key['kid']]

	
	while(True):
	#	Callback for token validation
		
		try:
			"""	Step 1

				If encrypted, decrypt it using the keys and algorithms specified in the meta_data
					If encryption was negotiated but not provided, REJECT
			"""
			decoded_token = jwt_python.decode(token.decode('utf-8'), verify=False)
			dirty_alg = jwt.get_unverified_header(token)['alg']
			dirty_kid = jwt.get_unverified_header(token)['kid']
			
			# Get discovery document
			r = requests.get(decoded_token['iss'] + "/.well-known/openid-configuration")
			discovery = r.json()

			dirty_keys = jwks(dirty_kid, discovery["jwks_uri"])
			keys = []
			for key in dirty_keys:
				# Validate the key
				try:
					keys.append(jws.verify(token, key, algorithms=[dirty_alg]))
				except Exception as err:
					print err
					raise ValueError(err)

			if discovery['issuer'] != decoded_token['iss']:
				""" Step 2

					Issuer Identifier for the OpenID Provider (which is typically
					obtained during Discovery) MUST exactly match the value of the iss (issuer) Claim.
				"""
				raise ValueError('Discovery document Issuer does not match client_id')
			
			if decoded_token['iss'] != config.audience:
				""" Step 3

					Client MUST validate:
		 				aud (audience) contains the same `client_id` registered
		 				iss (issuer) identified as the aud (audience)
		 				aud (audience) Claim MAY contain an array with more than one element (Not implemented by Okta)
					The ID Token MUST be rejected if the ID Token does not list the Client as a valid
					audience, or if it contains additional audiences not trusted by the Client.
				"""
				raise ValueError('Issuer does not match client_id')
			

			if isinstance(decoded_token['aud'], str):
				# Single element
				
				if decoded_token['aud'] != config.client_id:
					raise ValueError('Audience does not match client_id')
			
			if isinstance(decoded_token['aud'], list):
				# Multiple aud values
				exists = [aud for aud in decoded_token['aud'] if aud == config.client_id ]
				
				if len(exists) == 0:
					raise ValueError('No Issuers match client_id')
				else:
					if 'azp' in decoded_token:
						""" Step 4

							If ID Token contains multiple audiences, verify that an azp claim is present
						"""
						
						if decoded_token['azp'] != config.client_id:
							"""	Step 5

								If azp (authorized part), verify client_id matches
							"""
							
							raise ValueError('azp value does not match client_id')
					else:
						raise ValueError('azp value not provided')
			
						
			""" Step 6 : TLS server validation not implemented by Okta

				If ID Token is received via direct communication between Client and Token Endpoint,
				TLS server validation may be used to validate the issuer in place of checking token
				signature. MUST validate according to JWS algorithm specialized in JWT alg Header.
				MUST use keys provided.
			"""
						
			
			if dirty_alg not in discovery['id_token_signing_alg_values_supported']:
				""" Step 7

					The alg value SHOULD default to RS256 or sent in id_token_signed_response_alg param during Registration
				"""
				
				raise ValueError('alg provided in token does not match id_token_signing_alg_values_supported')
						

			""" Step 8 : Not implemented due to Okta configuration

				If JWT alg Header uses MAC based algorithm (HS256, HS384, etc) the octets of UTF-8 of the
				client_secret corresponding to the client_id are contained in the aud (audience) are
				used to validate the signature. For MAC based, if aud is multi-valued or if azp value
				is different than aud value - behavior is unspecified.
			"""

			if decoded_token['exp'] < int(time.time()):
				""" Step 9

				The current time MUST be before the time represented by exp
				"""
				
				raise ValueError('exp provided has expired')


			if decoded_token['iat'] < (int(time.time()) - 100000):
				""" Step 10 - Defined 'too far away time' : approx 24hrs

					The iat can be used to reject tokens that were issued too far away from current time,
					limiting the time that nonces need to be stored to prevent attacks. 
				"""
				
				raise ValueError('iat too far in the past ( > 1 day)')


			if nonce is not None:
				""" Step 11

					If a nonce value is sent in the Authentication Request, a nonce MUST be present and be
					the same value as the one sent in the Authentication Request. Client SHOULD check for nonce value
					to prevent replay attacks.
				"""
				if nonce != decoded_token['nonce']:
					raise ValueError('nonce value does not match Authentication Request nonce')

			
			""" Step 12:  Not implemented by Okta
				
				If acr was requested, check that the asserted Claim Value is appropriate
			"""

			
			if 'auth_time' in decoded_token:
				""" Step 13

					If auth_time was requested, check claim value and request re-authentication if too much time elapsed
				"""
				if decoded_token['auth_time'] < (int(time.time()) - 100000):
					raise ValueError('auth_time too far in past ( > 1 day)')

			return decoded_token

		except ValueError as err:
			return err
