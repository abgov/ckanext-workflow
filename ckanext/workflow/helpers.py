from ckan.plugins import toolkit
import ckan.authz as authz
import ckan.model as model
from ckanext.workflow.logic.action.member_authorization import get_member_username_orgname
from ckanext.workflow.model  import MemberAuthorizedWorkflow
from ckan.plugins.toolkit import  Invalid, _
import  ckanext.scheming.helpers as h
import pylons.config as config
import re

NotFound = toolkit.ObjectNotFound


def is_admin(user, org):
    """ check if user is admin 
        params: user: name or id,
                org : name or id,
        rtype: boolean
    """
    username = model.User.get(user).name
    user_id = model.User.get(user).id
    if authz.is_sysadmin(username):
    	return True
    if org:
        org_id = model.Group.get(org).id
        admin_ids = authz.get_group_or_org_admin_ids(org_id)
        if user_id in admin_ids:
        	return True
    return False


def current_user_name():
    if toolkit.c.userobj:
	    return toolkit.c.userobj.name
    else:
        return None


def is_authorized_member(user, org, process_state):
    """ check if user is authorized member of full work flow 
        params: user: name or id,
                org : name or id,
        rtype: boolean
    """
    if not org:
        return False
    username = model.User.get(user).name
    groupname = model.Group.get(org).name
    data_dict = {'username': username, 'groupname': groupname}
    try:
        member, username, orgnmae = get_member_username_orgname(data_dict)
    except NotFound: 
        # For all users if dataset is public
        if process_state == "Approved":
            return True
        else: 
            return False
    session = model.Session
    if MemberAuthorizedWorkflow.exists(session, member):
        return True
    return False


def allow_full_work_flow(user, org):
    """ check if user is admin or authorized member of full work flow 
        params: user: name or id,
                org : name or id,
        rtype: boolean
    """
    if not user or not org:
        return None
    return is_admin(user, org) or is_authorized_member(user, org, '')


def get_package_process_state_by_name(pkg_name):
    if not pkg_name:
        raise Invalid(_('No dataset name exists'))
    pkg = toolkit.get_action("package_show")(data_dict={"id": pkg_name})
    if pkg:
        ps = pkg.get('process_state')
        if ps:
            return ps
    else:
        raise Invalid(_("No dataset \"{0}\" can be found".format(pkg_name)))


def _get_process_state_field(dataset_type):
    opendata_scheme = h.scheming_get_schema('dataset', dataset_type)
    fields = opendata_scheme['dataset_fields']
    return h.scheming_field_by_name(fields, "process_state")


def get_required_fields_name(dataset_type):
    opendata_scheme = h.scheming_get_schema('dataset', dataset_type)
    fields = opendata_scheme['dataset_fields']
    required_fields_name = []
    for f in fields:
        if f.get('required'):
            required_fields_name.append(f.get('field_name'))
    return  required_fields_name


def get_all_process_states(dataset_type):
    ps = _get_process_state_field(dataset_type)
    if not ps:
        return []
    return [ c['value'] for c in ps['choices'] ]


def get_process_state_list_not_allow_incomplete(dataset_type):
    ps = _get_process_state_field(dataset_type)
    if not ps:
        raise NotFound(_("Field prcess_state deos not exist. Please check your json file!"))
    return ps['form_not_allow_incomplete_dataset']


def get_dataset_types():
    types = config['scheming.dataset_schemas']
    type_list = []
    for type in types.split():
        type = re.sub(r'.*?\:(.*?).json', r'\1', type)
        type_list.append(type)
    return type_list
