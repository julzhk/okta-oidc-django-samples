# Okta OpenID Connect and OAuth2 Samples using Django
The following examples show best practices for using Okta's Sign-In Widget and AuthJS SDK with Django

### Flow
| Scenario      | Summary  |
| :-------------: |:-------------: |
| Authentication | Using the [Authorization Code Grant](https://tools.ietf.org/html/rfc6749#section-4.1), the [Sign-In Widget](http://developer.okta.com/code/javascript/okta_sign-in_widget_ref#openid-connect-oauth-20-and-social-integrations) and [AuthJS SDK](http://developer.okta.com/code/javascript/okta_auth_sdk), request an authorization code from Okta or the [Social IDP](http://developer.okta.com/docs/api/resources/social_authentication.html)
| Code Extraction | Parsed from the `/callback` URL query parameter, the `code` is exchanged for an `id_token` and `access_token` from Okta |
| Validate Token | If an `id_token` is requested, it is validated per [OpenID Spec 3.1.3.7](http://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation). If `id_token` is valid, a local user is created / matched |
| Set Session | Sets a session cookie upon successful login |

### Samples Provided
| Sample   | Button |
| :-------------: |:-------------: |
| Redirect to IdP (Okta) | ![Okta Login](https://raw.githubusercontent.com/jmelberg-okta/doc-assets/master/samples/okta.png) |
| Simple Login Experience using [Sign-In Widget](http://developer.okta.com/code/javascript/okta_sign-in_widget_ref#openid-connect-oauth-20-and-social-integrations) | ![Widget Login](https://raw.githubusercontent.com/jmelberg-okta/doc-assets/master/samples/widget.png) |
| [Social IdP (LinkedIn)](http://developer.okta.com/docs/api/resources/social_authentication.html) | ![LinkedIn Login](https://raw.githubusercontent.com/jmelberg-okta/doc-assets/master/samples/linkedin.png)

 
## Running the Samples with your Okta Organization
###Pre-requisites
This sample application was tested with an Okta organization. If you do not have an Okta organization, you can easily [sign up for a free Developer Okta org](https://www.okta.com/developer/signup/).

1. Verify OpenID Connect is enabled for your Okta organization. `Admin -> Applications -> Add Application -> Create New App -> OpenID Connect`
  - If you do not see this option, email [developers@okta.com](mailto:developers@okta.com) to enable it.
2. In the **Create A New Application Integration** screen, click the **Platform** dropdown and select **Web**
3. Press **Create**. When the page appears, enter an **Application Name**. Press **Next**.
4. Add the following to the list of *Redirect URIs*:
  - `http://localhost:8080`
  - `http://localhost:8080/stateful/callback`
5. Click **Finish** to redirect back to the *General Settings* of your application.
6. Copy the **Client ID**, as it will be needed for the client configuration.
7. Select the **Edit** button and change the **Client Authentication** to *Client Secret*. Copy the *Client Secret*, as it will be needed for the client configuration.
8. Enable [CORS access](http://developer.okta.com/docs/api/getting_started/enabling_cors.html) to your Okta organization
  - In the navigation bar, select **Security** then **API**.
  - Select the *CORS* tab
  - Click the **Edit** button and add `http://localhost:8080`
  - Save
9. Finally, select the **People** tab and **Assign to People** in your organization.

### Build Instructions
With a local copy of the samples, use the following commands on Mac OS X or Linux:
```
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt
```

### Run the Samples
Begin by syncing the local database for User authentication.
```
    $ python manage.py migrate
```
Start the web server with `python manage.py runserver [PORT]` in the `/samples` project repository. (Hint) You should see the `manage.py` file.
```
    $ python manage.py runserver 8080
```

Navigate to `http://localhost:8080/stateful/login` to login using the [Okta Sign-In Widget](http://developer.okta.com/code/javascript/okta_sign-in_widget) or the [Okta AuthJS SDK](http://developer.okta.com/code/javascript/okta_auth_sdk).