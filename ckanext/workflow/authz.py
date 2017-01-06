'''This module monkey patches functions in ckan/authz.py and replaces the
default roles with custom roles and decorates
has_user_permission_for_group_or_org to allow an approver to editor groups,
Approveer can act as editor plus accession to all the process states, but 
have no other sysadmin powers
'''
from ckan import authz, model
from ckan.common import OrderedDict
from ckan.plugins import toolkit


# these are the permissions that roles have
authz.ROLE_PERMISSIONS = OrderedDict([
    ('admin', ['admin']),
    ('approver', ['read', 'delete_dataset', 'create_dataset', 'update_dataset', 'manage_group', 'workflow']),
    ('editor', ['read', 'delete_dataset', 'create_dataset', 'update_dataset', 'manage_group']),
    ('member', ['read', 'manage_group']),
])


def _trans_role_approver():
    return toolkit._('Workflow Approver')


authz._trans_role_approver = _trans_role_approver



def is_approver_decorator(method):
    def decorate_has_user_permission_for_group_or_org(group_id, user_name,
                                                      permission):
        user_id = authz.get_user_id_for_username(user_name, allow_none=True)
        if not user_id:
            return False
        if permission == 'workflow':
	        if is_user_authorized_workflow(group_id, user_id, permission):
	            return True
	        else:
	        	return False
        return method(group_id, user_name, permission)
    return decorate_has_user_permission_for_group_or_org


authz.has_user_permission_for_group_or_org = is_approver_decorator(
    authz.has_user_permission_for_group_or_org)


def is_user_authorized_workflow(group_id, user_id, permission):
	if not group_id:
		return False
	if not user_id:
		return False
	# check the member table
	mem_list = toolkit.get_action("member_list")(data_dict={"id": group_id, 
													   "object_type": "user",
													   "capacity": "approver"} )
	if not mem_list:
		return False
	for m in mem_list:
		if m[0] == user_id:
			return True
	return False
