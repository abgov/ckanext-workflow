import ckan.lib.base as base
from ckan.common import _, request, c
import ckan.lib.helpers as helpers
import ckan.model as model
import ckan.plugins.toolkit as toolkit


class MemberAuthorizedController(base.BaseController):
    """ This controller controls the actions of adding and removing
        users as authorized member of full workflow. It is implemented
        in organization edit function.
    """ 
    def _get_context_controller(self):
        context = {'model': model, 'session': model.Session,
                   'user': toolkit.c.user or toolkit.c.author}
        try:
            toolkit.check_access('member_create', context, {})
        except toolkit.NotAuthorized:
            toolkit.abort(401, toolkit._('User not authorized to manage page'))

        controller = 'ckanext.workflow.controllers:MemberAuthorizedController'
        return context, controller

    
    def _action(self, action, context, username, groupname, success_msg):
        try:
            toolkit.get_action(action)(context,
                            data_dict={'username': username, 'groupname': groupname}
            )
        except toolkit.NotAuthorized:
            toolkit.abort(401,
                          toolkit._('Unauthorized to perform that action'))
        except toolkit.ObjectNotFound as e :
            error_message = (e.error_dict or e.error_summary
                         or e.message)
            if error_message.get("message"):
                error_message = error_message.get("message")
            helpers.flash_error(error_message)
        except toolkit.ValidationError as e:
            error_message = (e.error_dict or e.error_summary
                         or e.message)
            if error_message.get("message"):
                error_message = error_message.get("message")
            helpers.flash_error(error_message)
        else:
            helpers.flash_success(toolkit._(success_msg))


    def manage(self, id):
        context, controller = self._get_context_controller()
        username = toolkit.request.params.get('username')
        group_object = model.Group.get(id)
        groupname = group_object.name

        toolkit.c.group_dict = group_object

        if toolkit.request.method == 'POST':
            if username:
                user_object = model.User.get(username)
                if not user_object:
                    helpers.flash_error("User \"{0}\" not exist!".format(username))
                else:
                    self._action('member_authorized_create', 
                         context, 
                         username, 
                         groupname, 
                         "User \"{0}\" is now an authorized Member".format(username))
            else:
                helpers.flash_error("Please input username first.")

            return toolkit.redirect_to(toolkit.url_for(controller=controller,
                                                       action='manage', id=id))

        authorized_member_list = toolkit.get_action('member_authorized_list')(context, 
                                                    data_dict={'groupname': groupname})
        return toolkit.render(
            'organization/manage_authorized_member.html',
            extra_vars={
                'authorized_member_list': authorized_member_list,
            }
        )


    def remove(self, id):
        if 'cancel' in toolkit.request.params:
            toolkit.redirect_to(controller=controller, action='manage', id=id)

        context, controller = self._get_context_controller()
        user_id = toolkit.request.params['user']
        user_object = model.User.get(user_id)
        username = user_object.name
        group_object = model.Group.get(id)
        groupname = group_object.name
        
        if toolkit.request.method == 'POST' and user_id:
            self._action('member_authorized_delete', 
                         context, 
                         username, 
                         groupname, 
                         "User \"{0}\" is no longer an Authorized Member".format(username))

        return toolkit.redirect_to(
                helpers.url_for(controller=controller, action='manage', id=id))

