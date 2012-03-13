import requests, json
from flask import session

GATEWAY_HOST = "localhost:5000"
SERVICE_GATEWAY_BASE_URL = 'http://%s/ion-service' % GATEWAY_HOST


SERVICE_REQUEST_TEMPLATE = {
    'serviceRequest': {
        'serviceName': '', 
        'serviceOp': '',
        'params': {} # Example -> 'object_name': ['restype', {}] }
    }
}

class ServiceApi(object):
    
    @staticmethod
    def signon_user(certificate):
        res = service_gateway_post('identity_management', 'signon', params={'certificate': certificate})
        return res
    
    @staticmethod
    def find_user_info(user_id):
        user_info = service_gateway_post('identity_management', 'find_user_info_by_id', params={'user_id': user_id})
        return user_info['contact']
    
    @staticmethod
    def create_user_info(user_id, contact):
        user_info = ['UserInfo', {'contact': contact}]
        res = service_gateway_post('identity_management', 'create_user_info', params={'user_id': user_id, 'user_info': user_info})
        return res
    
    @staticmethod
    def update_user_info(contact):
        user_info = ['UserInfo', {'contact': contact}]
        res = service_gateway_get('identity_management', 'update_user_info', params={'user_info': user_info})
        return res
    
    @staticmethod
    def find_user_details(user_id):
        user_details = service_gateway_get('identity_management', 'read_user_identity', params={'user_id': user_id})
        
        if user_details.has_key('_id'):

            # CREDENTIALS
            user_details['credentials'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': user_details['_id'], 'predicate': 'hasCredentials', 'object_type': 'UserCredentials'})

            # USER INFO
            user_details['user_info'] = service_gateway_get('identity_management', 'find_user_info_by_id', params={'user_id':user_details['_id']})
        return user_details

    @staticmethod
    def find_observatory(marine_facility_id):
        marine_facility = service_gateway_get('marine_facility_management', 'read_marine_facility', params={'marine_facility_id': marine_facility_id})
        
        if marine_facility.has_key('_id'):

            # GENERAL
            marine_facility['data_products'] = service_gateway_get('resource_registry', 'find_resources', params={'restype': 'DataProduct', 'id_only': 'False'})[0]
            marine_facility['platforms'] = service_gateway_get('resource_registry', 'find_resources', params={'restype': 'PlatformDevice', 'id_only': 'False'})[0]
            marine_facility['instruments'] = service_gateway_get('resource_registry', 'find_resources', params={'restype': 'InstrumentDevice', 'id_only': 'False'})[0]

            # ADMINISTRATION
            org_id = service_gateway_get('marine_facility_management', 'find_marine_facility_org', params={'marine_facility_id': marine_facility_id})
            marine_facility['users'] = service_gateway_get('org_management', 'find_enrolled_users', params={'org_id': org_id})
            marine_facility['policies'] = service_gateway_get('org_management', 'find_org_roles', params={'org_id': org_id})
            
            # SOFTWARE
            marine_facility['instrument_agents'] = service_gateway_get('resource_registry', 'find_resources', params={'restype': 'InstrumentAgent', 'id_only': 'False'})[0]
            marine_facility['data_process_definitions'] = service_gateway_get('resource_registry', 'find_resources', params={'restype': 'DataProcessDefinition', 'id_only': 'False'})[0]
            
            # EVENTS
            marine_facility['recent_events'] = []
            marine_facility['user_requests'] = service_gateway_get('org_management', 'find_requests', params={'org_id': org_id})
            
            # DEFINITIONS
            marine_facility['platform_models'] = service_gateway_get('resource_registry', 'find_resources', params={'restype': 'PlatformModel', 'id_only': 'False'})[0]
            marine_facility['instrument_models'] = service_gateway_get('resource_registry', 'find_resources', params={'restype': 'InstrumentModel', 'id_only': 'False'})[0]
        
        return marine_facility
    
    @staticmethod
    def find_platform(platform_device_id):
        platform = service_gateway_get('instrument_management', 'read_platform_device', params={'platform_device_id': platform_device_id})
        
        if platform.has_key('_id'):
            # DEPLOYMENTS
            platform['deployments'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': platform_device_id, 'predicate': 'hasDeployment', 'object_type': 'LogicalPlatform', 'id_only': False})[0]
        
            # ADMINISTRATION        
            platform['instrument_agents'] = service_gateway_get('resource_registry', 'find_resources', params={'restype': 'InstrumentAgent'})
            platform['policies'] = service_gateway_get('policy_management', 'find_resource_policies', params={'resource_id': platform_device_id})
        
            # INSTRUMENTS - ERROR WITH PRELOAD DATA
            # logical_platform_id = platform['deployments'][0]['_id']
            # logical_instruments = service_gateway_get('resource_registry', 'find_objects', params={'subject': logical_platform_id, 'predicate': 'hasInstrument', 'id_only': False})[0]
            # platform['instruments'] = service_gateway_get('instrument_management', 'find_instrument_device_by_platform_device', params={'platform_device_id': platform_device_id})
        
            # EVENTS
            platform['recent_events'] = []
            platform['user_requests'] = []
        
            # DEFINITIONS TBD
            # FRAMES OF REFERENCE TBD
        
        return platform
    
    @staticmethod
    def find_platform_model(platform_model_id):
        platform_model = service_gateway_get('resource_registry', 'read', params={'object_id': platform_model_id})
        return platform_model

    @staticmethod
    def find_instrument(instrument_device_id):
        instrument = service_gateway_get('instrument_management', 'read_instrument_device', params={'instrument_device_id': instrument_device_id})
        
        if instrument.has_key('_id'):
            # DATA
            instrument['data'] = []
        
            # DEPLOYMENTS
            instrument['deployments'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': instrument_device_id, 'predicate': 'hasDeployment', 'object_type': 'LogicalInstrument', 'id_only': False})[0]
        
            # ADMINISTRATION
            instrument['instrument_agent'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': instrument_device_id, 'predicate': 'hasAgentInstance', 'object_type': 'InstrumentAgentInstance', 'id_only': False})[0]
        
            # POLICIES
            instrument['policies'] = service_gateway_get('policy_management', 'find_resource_policies', params={'resource_id': instrument_device_id})
        
            # FRAME OF REFERENCES TBD
        
        return instrument

    @staticmethod
    def find_instrument_model(instrument_model_id):
        instrument_model = service_gateway_get('resource_registry', 'read', params={'object_id': instrument_model_id})
        return instrument_model

    @staticmethod
    def find_instrument_agent(instrument_agent_id):
        instrument_agent = service_gateway_get('resource_registry', 'read', params={'object_id': instrument_agent_id})
        return instrument_agent
    
    @staticmethod
    def find_data_process_definition(data_process_definition_id):
        data_process_definition = service_gateway_get('resource_registry', 'read', params={'object_id': data_process_definition_id})
        
        if data_process_definition .has_key('_id'):
            data_process_definition['input_stream_definitions'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': data_process_definition_id, 'predicate': 'hasInputStreamDefinition', 'object_type': 'StreamDefinition', 'id_only': False})
            data_process_definition['output_stream_definitions'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': data_process_definition_id, 'predicate': 'hasStreamDefinition', 'object_type': 'StreamDefinition', 'id_only': False})

            # USED IN
            data_process_definition['data_process'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': data_process_definition_id, 'predicate': 'hasInstance', 'object_type': 'DataProcess', 'id_only': False})

            # POLICIES
            data_process_definition['policies'] = service_gateway_get('policy_management', 'find_resource_policies', params={'resource_id': data_process_definition_id})

        return data_process_definition
    
    @staticmethod
    def find_data_product(data_product_id):
        data_product = service_gateway_get('resource_registry', 'read', params={'object_id': data_product_id})
        return data_product
    
    @staticmethod
    def find_by_resource_type(resource_type):
        resources = service_gateway_get('resource_registry', 'find_resources', params={'restype': resource_type})[0]
        return resources




def build_get_request(service_name, operation_name, params={}):
    url = '%s/%s/%s' % (SERVICE_GATEWAY_BASE_URL, service_name, operation_name)    
    if len(params) > 0:
        param_string = '?'
        for (k, v) in params.iteritems():
            param_string += '%s=%s&' % (k,v)
        url += param_string[:-1]

    pretty_console_log('SERVICE GATEWAY GET URL', url)

    return url

def service_gateway_get(service_name, operation_name, params={}):    
    resp = requests.get(build_get_request(service_name, operation_name, params))
    pretty_console_log('SERVICE GATEWAY GET RESPONSE', resp.content)

    if resp.status_code == 200:
        resp = json.loads(resp.content)

        if type(resp) == dict:
            return resp['data']['GatewayResponse']
        elif type(resp) == list:
            return resp['data']['GatewayResponse'][0]

def build_post_request(service_name, operation_name, params={}):
    url = '%s/%s/%s' % (SERVICE_GATEWAY_BASE_URL, service_name, operation_name)    

    post_data = SERVICE_REQUEST_TEMPLATE
    post_data['serviceRequest']['serviceName'] = service_name   
    post_data['serviceRequest']['serviceOp'] = operation_name   
    if len(params) > 0:
        post_data['serviceRequest']['params'] = params

    # conditionally add user id and expiry to request
    if "user_id" in session:
        post_data['serviceRequest']['requester'] = session['user_id']
        post_data['serviceRequest']['expiry'] = session['valid_until']

    data={'payload': json.dumps(post_data)}

    pretty_console_log('SERVICE GATEWAY POST URL/DATA', url, data)

    return url, data

def service_gateway_post(service_name, operation_name, params={}):
    url, data = build_post_request(service_name, operation_name, params)
    resp = requests.post(url, data)
    pretty_console_log('SERVICE GATEWAY POST RESPONSE', resp.content)

    if resp.status_code == 200:
        resp = json.loads(resp.content)

        if type(resp) == dict:
            return resp['data']['GatewayResponse']
        elif type(resp) == list:
            return resp['data']['GatewayResponse'][0]

def pretty_console_log(label, content, data=None):
    print '\n\n\n'
    print '-------------------------------------------'
    print '%s : %s' % (label, content)
    if data:
        print 'data : %s' % data
    print '-------------------------------------------'
