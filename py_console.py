from ds_config import *
from docusign_esign import *
import os
from datetime import datetime
from datetime import timedelta


def create_api_client():
    """Create api client and construct API headers"""
    api_client = ApiClient()
    api_client.host = DS_JWT['base_path']
    access_token = getAccessToken()
    api_client.set_default_header(header_name='Authorization', header_value=f'Bearer {access_token}')
    return api_client


def getAccessToken():
    api_client = ApiClient()
    api_client.set_base_path(DS_JWT['authorization_server'])
    scopes = ['signature','impersonation']
  

    private_key_file = os.path.abspath(DS_JWT['private_key_file'])
    with open(private_key_file) as private_key_file:
        private_key = private_key_file.read()
        private_key.encode("ascii").decode("utf-8")
    

    oauthObject = api_client.request_jwt_user_token(
                client_id=DS_JWT['ds_client_id'],
                user_id=DS_JWT['ds_impersonated_user_id'],
                oauth_host_name=DS_JWT['authorization_server'],
                private_key_bytes=private_key,
                expires_in=3600,
                scopes=scopes
            )
    oauthObject = oauthObject.to_dict()
    print(oauthObject)
    return oauthObject['access_token']


def createEnvelope():

    # Create the document model
    document = Document(  # create the DocuSign document object
        document_base64=DS_Base64['base_64'],
        name='Example document',  # can be different from actual file name
        file_extension='docx',  # many different document types are accepted
        document_id=1  # a label used to reference the doc
    )

    document1 = Document(  # create the DocuSign document object
        document_base64=DS_Base64['base_64'],
        name='Example document',  # can be different from actual file name
        file_extension='docx',  # many different document types are accepted
        document_id=2  # a label used to reference the doc
    )


    # Create the signer recipient model
    signer = Signer(  # The signer
        email='bend.dstest@gmail.com', name='Ben Dowling',
        recipient_id='1', routing_order='1',
        # Setting the client_user_id marks the signer as embedded
        #client_user_id='12345'
    )

    signer2 = Signer(  # The signer
        email='bend.dstest+1@gmail.com', name='Ben Dowling',
        recipient_id='2', routing_order='2',
        # Setting the client_user_id marks the signer as embedded
        #client_user_id='12345'
    )

    

    # Create a sign_here tab (field on the document)
    sign_here = SignHere(  # DocuSign SignHere field/tab
        anchor_string="Sign Here",
        anchor_units="pixels",
        anchor_y_offset="10",
        anchor_x_offset="20"
   )

    sign_heres = SignHere(  # DocuSign SignHere field/tab
        anchor_string="Sign Heres",
        anchor_units="pixels",
        anchor_y_offset="10",
        anchor_x_offset="20"
   )
    

    salary = 123000

    text_salary = Text(
        XPosition = "200",
        YPosition = "200",
        DocumentId = "1",
        PageNumber = "1",
        font="helvetica",
        font_size="size11",
        bold="true",
        value="${:.2f}".format(salary),
        locked="true",
        tab_id="salary",
        tab_label="Salary")

    salary_custom_field = TextCustomField(
        name="salary",
        required="false",
        show="true",  # Yes, include in the CoC
        value=str(salary)
        )
    cf = CustomFields(text_custom_fields=[salary_custom_field])

    

    
    # Add the tabs model (including the sign_here tab) to the signer
    # The Tabs object wants arrays of the different field/tab types
    signer.tabs = Tabs(sign_here_tabs=[sign_here],text_tabs=[text_salary])
    signer2.tabs = Tabs(sign_here_tabs=[sign_heres],text_tabs=[text_salary])
    

    # Next, create the top level envelope definition and populate it.
    envelope_definition = EnvelopeDefinition(
        email_subject="Please sign this document sent from the Python SDK",
        documents=[document,document1],
        enforce_signer_visibility = 'true',
        # The Recipients object wants arrays for each recipient type
        recipients=Recipients(signers=[signer,signer2]),
        status="sent",# requests that the envelope be created and sent.
        custom_fields=cf,
        envelope_id_stamping = "false"
    )

    api_client = create_api_client()
    envelope_api = EnvelopesApi(api_client)
    results = envelope_api.create_envelope(account_id=DS_CONFIG['account_id'], envelope_definition=envelope_definition)
    envelope_id = results.envelope_id

    #return envelope_id

def useTemplate():
    
    # Create the envelope definition
    envelope_definition = EnvelopeDefinition(
        status = "sent", # requests that the envelope be created and sent.
        template_id = ''
    )
    # Create template role elements to connect the signer and cc recipients
    # to the template
    cc = TemplateRole(
        email = ENVELOPE_CONFIG['Email'],
        name = ENVELOPE_CONFIG['Name'],
        role_name = 'Created')
    #Create a cc template role.
     

    # Add the TemplateRole objects to the envelope object
    envelope_definition.template_roles = [cc]

    # Call Envelopes::create API method
    # Exceptions will be caught by the calling function
    api_client = create_api_client()
    envelope_api = EnvelopesApi(api_client)
    results = envelope_api.create_envelope(DS_CONFIG['account_id'], envelope_definition=envelope_definition)
    envelope_id = results.envelope_id


def listStatusChanges():
    api_client = create_api_client()
    envelope_api = EnvelopesApi(api_client)
    from_date = from_date = (datetime.utcnow() - timedelta(days=10)).isoformat()
    search_text = 'Please sign'
    results = envelope_api.list_status_changes('11254982', from_date = from_date,search_text = search_text)
    print(results) 

def getUsers(): 
    api_client = create_api_client()
    users_api = UsersApi(api_client)
    results = users_api.get_contact_by_id(DS_CONFIG['account_id'], '')
    print(results)

def getCustomFields():
    api_client = create_api_client()
    envelopes_api = EnvelopesApi(api_client)
    results = envelopes_api.list_custom_fields(DS_CONFIG['account_id'], 'ae7c7de0-5a30-4dc1-a265-8618556e5cb9')
    print(results)


# Call methods below this line
###############################################################

#createEnvelope()

#getCustomFields()

#useTemplate()    

#listStatusChanges()

#getUsers()
