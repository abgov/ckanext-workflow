from ckan import model
from ckan.plugins import toolkit
from ckan.logic import validate
from ckanext.workflow.model.member_authorized_workflow_model import MemberAuthorizedWorkflow
from ckanext.workflow.logic import schema
from ckan.plugins.toolkit import  Invalid, _
import ckan.lib.helpers as h

ValidationError = toolkit.ValidationError
NotFound = toolkit.ObjectNotFound

def _query_Member(user_id='', group_id=''):
    member = model.Session.query(model.Member) \
        .filter(model.Member.group_id == group_id) \
        .filter(model.Member.table_name == 'user') \
        .filter(model.Member.state == 'active') \
        .filter(model.Member.table_id == user_id).first()

    if member:
        return member.as_dict()
    else:
        user_object = model.User.get(user_id)
        org_object = model.Group.get(group_id)
        raise NotFound(
            _("User \"{0}\" is is not a member".format(user_object.name) + 
              " of organization \"{0}\".".format(org_object.name) +
              " User has to be an active editor first"+
              " before authorized for work flow.")
        )


def get_user_name_object(data_dict):
    username = data_dict['username']
    user_object = model.User.get(username)
    if not user_object:
        raise NotFound(
            _("User \"{0}\" does not exist!".format(username))
        )
    return username, user_object


def get_org_name_object(data_dict):
    orgname = data_dict.get("groupname")
    if not orgname:
        orgname = data_dict["__extras"].get("groupname")
    if not orgname:
        raise ValidationError(
            _("Group name \"{0}\" does not exist!".format(orgname))
        )
    org_object = model.Group.get(orgname)
    if not org_object:
        raise NotFound(
            _("Group object \"{0}\" does not exist!".format(orgname))
        )
    return orgname, org_object


def get_member_username_orgname(data_dict):
    username, user_object = get_user_name_object(data_dict)
    orgname, org_object = get_org_name_object(data_dict)
    return _query_Member(user_id=user_object.id, \
                         group_id=org_object.id), \
           username, \
           orgname
    

@validate(schema.member_authorized_schema)
def member_authorized_create(context, data_dict):
    '''Make a member as an authorized member for workflow

    Authorized member can change the package's process_state to 'rejected',
    'pending' or "approved". Except that, he cannot do anything else as 
    org admin or sysadmin

    :param username: the username of the authorized member to delete
    :type username: str

    :param groupname: the organization of the authorized member
    :type groupname: str

    :rtype: bool (success)
    '''
    ''' Only sysadmin and org admin can do member_create, they can do this action '''
    toolkit.check_access('member_create', context, data_dict)
    session = context['session']
    member_dict, username, orgname = get_member_username_orgname(data_dict)
    
    if MemberAuthorizedWorkflow.exists(session, member_dict):
        error_msg = _("User \"{0}\" is already an authorized".format(username) +
                      " member of organization \"{0}\".".format( orgname))
        raise ValidationError(error_msg)
    return MemberAuthorizedWorkflow.create(session, member_dict)


@validate(schema.member_authorized_schema)
def member_authorized_delete(context, data_dict):
    '''Delete an authorized member

    You must be a sysadmin to make this api call

    :param user_id: the user_id of the authorized member to delete
    :type user_id: str

    :param group_id: the group_id of the organization of authorized member 
    :type group_id: str

    :rtype: bool (success)
    '''
    ''' Only sysadmin and org admin can do member_create, they can do this action '''
    toolkit.check_access('member_create', context, data_dict)
    session = context['session']
    
    member_dict, username, orgname = get_member_username_orgname(data_dict)

    authorized_member = MemberAuthorizedWorkflow.get(session, 
                                                    member_id=member_dict['id'], 
                                                    group_id=member_dict['group_id'])
    if authorized_member:
        session.delete(authorized_member)
        session.commit()
    else:
        raise NotFound(
            _("User \"{0}\" is not an authorized".format(username) + 
              " member of organization \"{0}\".".format(orgname))
        )


def member_authorized_list(context, data_dict):
    '''Show the list of authorized members of some organization

    You must be a sysadmin to make this api call

    :rtype: list of user ids
    '''
    ''' Only sysadmin and org admin can do member_create, they can do this action '''
    toolkit.check_access('member_create', context, data_dict)
    session = context['session']
    orgname = data_dict['groupname']
    org_object = model.Group.get(orgname)
    instances = MemberAuthorizedWorkflow.get_all(session, group_id=org_object.id)
    user_ids = [i.user_id for i in instances]
    
    return [toolkit.get_action('user_show')(data_dict={'id': user_id})
            for user_id in user_ids]


@toolkit.side_effect_free
def is_member_authorized(context, data_dict):
    '''Show the list of authorized members of some organization

    You don't have to be a sysadmin to make this api call

    :rtype: boolean
    '''
    ''' Only sysadmin and org admin can do member_create, they can do this action '''
    toolkit.check_access('member_create', context, data_dict)
    session = context['session']
    
    member_dict, username, orgname = get_member_username_orgname(data_dict)

    if not member_dict:
        raise NotFound(
            _("User \"{0}\" is not an authorized".format(username) + 
              " member of organization \"{0}\".".format(orgname))
        )

    if MemberAuthorizedWorkflow.exists(session, member_dict):
        return True

    return False
