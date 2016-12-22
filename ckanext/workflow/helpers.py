from ckan.plugins import toolkit
import ckan.authz as authz
import ckan.model as model
from ckanext.workflow.logic.action.member_authorization import get_member_username_orgname
from ckanext.workflow.model  import MemberAuthorizedWorkflow
from ckan.plugins.toolkit import  Invalid, _
import  ckanext.scheming.helpers as h
import pylons.config as config
import re
import ckan.lib.helpers as help
NotFound = toolkit.ObjectNotFound


def is_admin(user, org):
    """ check if user is admin 
        params: user: name or id,
                org : name or id,
        rtype: boolean
    """
    if not org or not user:
        return False
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
    if not org or not user:
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
    dataset_scheme = h.scheming_get_schema('dataset', dataset_type)
    if not dataset_scheme:
        return None
    fields = dataset_scheme['dataset_fields']
    return h.scheming_field_by_name(fields, "process_state")


def get_required_fields_name(dataset_type):
    dataset_scheme = h.scheming_get_schema('dataset', dataset_type)
    fields = dataset_scheme['dataset_fields']
    required_fields_name = []
    for f in fields:
        if f.get('required'):
            required_fields_name.append(f.get('field_name'))
    return  required_fields_name


def get_all_process_states(dataset_type):
    if not dataset_type:
        return []
    ps = _get_process_state_field(dataset_type)
    if not ps:
        return []
    return [ c['value'] for c in ps['choices'] ]


def has_process_state_field_in_schema(dataset_type):
    if not dataset_type:
        return False
    ps = _get_process_state_field(dataset_type)
    if not ps:
        return False
    return True


def has_published_date_field_in_schema(dataset_type):
    if not dataset_type:
        return False
    dataset_scheme = h.scheming_get_schema('dataset', dataset_type)
    fields = dataset_scheme['dataset_fields']
    pd = h.scheming_field_by_name(fields, "published_date")
    if not pd:
        return False
    return True


def get_process_state_list_not_allow_incomplete(dataset_type):
    if not dataset_type:
        return []
    ps = _get_process_state_field(dataset_type)
    if not ps:
        return []
    return ps['form_not_allow_incomplete_dataset']


def get_dataset_types():
    types = config['scheming.dataset_schemas']
    if not types:
        return []
    type_list = []
    for type in types.split():
        type = re.sub(r'.*?\:(.*?).json', r'\1', type)
        type_list.append(type)
    return type_list


def get_required_fields_name_label_dict(dataset_type):
    if not dataset_type:
        return {}
    dataset_scheme = h.scheming_get_schema('dataset', dataset_type)
    fields = dataset_scheme['dataset_fields']
    required_dict = {}
    for f in fields:
        if f.get('required'):
            required_dict[f.get('field_name')] = f.get('label')
    return  required_dict


def get_required_items_missing(pkg_dict):
    if not pkg_dict:
        return []
    if not pkg_dict.get("id"):
        m = re.search(r"/edit/([^/]*)", help.full_current_url())
        pkg_dict = toolkit.get_action("package_show")(data_dict={"id": m.group(1)})
    if not pkg_dict.get("type"):
        m = re.search(r"/([^/]*?)/new", help.full_current_url())
        type = m.group(1)
    else:
        type = pkg_dict['type']
    required_dict = get_required_fields_name_label_dict(type)
    missing = []
    for e in required_dict.keys():
        if e in pkg_dict and not pkg_dict[e]:
            missing.append('{0}: Missing value'.format(required_dict[e]))

    if not pkg_dict['resources'] and resource_required(type):
        missing.append("At least one resource must exist")
    return missing


def resource_required(dataset_type):
    if not dataset_type:
        return False
    dataset_scheme = h.scheming_get_schema('dataset', dataset_type)
    fields = dataset_scheme['dataset_fields']
    for f in fields:
        if f.get('validators') and re.search("ab_ps_resource_required", f.get('validators')):
            return True
    return False


def has_process_state_field(pkg_id):
    if not pkg_id:
        return False
    try: 
        pkg_dict = toolkit.get_action("package_show")(data_dict={"id": pkg_id})
    except NotFound:
        return False
    else:
        try:
            pkg_dict['process_state']
        except KeyError:
            return False
        else:
            return True


def is_in_process_state_list_not_allow_incomplete(pkg_id):
    if not pkg_id:
        return False
    try:
       pkg_dict = toolkit.get_action("package_show")(data_dict={"id": pkg_id}) 
    except NotFound:
        return False
    else:
        last_process_state = pkg_dict['last_process_state']
        lst = get_process_state_list_not_allow_incomplete(pkg_dict['type'])
        if last_process_state in lst:
            return True
        else:
            return False