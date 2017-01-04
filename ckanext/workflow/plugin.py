import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.workflow.helpers as helpers
from ckan.controllers.package import PackageController
from ckan.controllers.group import GroupController
from ckanext.workflow.controllers.package import _save_new
from ckanext.workflow.logic import action
from model.package_process_state_model import (
    get_package_last_process_state, 
    add_package_process_state
)
from model import package_process_state_model, member_authorized_workflow_model
from ckan.config.routing import SubMapper
from logic import validation
from ckan.plugins.toolkit  import c
import ckan.lib.helpers as h
import re
from datetime import date, datetime
import dateutil.parser as parser


class WorkflowPlugin(plugins.SingletonPlugin):
    """
        This class includes process state field and control work flow on it, also
        includes authorization of user from org admin or sys admin to do the full 
        work flow set.
    """

    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IValidators)

    """ 
        Monkey patching PackageController's behavior. The process state of 'draft' state
        should have metadata and new resource creation separated.
    """
    PackageController._save_new = _save_new 


    """
    IAction
    """
    def get_actions(self):
        actions = dict((name, function) for name, function
                       in action.__dict__.items()
                       if callable(function))
        return actions

    """
    IPackageController
    """       
    def after_show(self, context, pkg_dict):
        if not helpers.has_process_state_field_in_schema(pkg_dict['type']) or pkg_dict['state'] == 'deleted':
            return
        if pkg_dict['state'] == 'draft' and pkg_dict['process_state'] == 'Draft':
            pkg_dict['state'] = 'active'
        package_last_process_state = get_package_last_process_state(context['session'], 
        	                                                        pkg_dict['id'])
        #set up the last_process_state field's value.
        curr_user_name = helpers.current_user_name()
        if package_last_process_state:
            pkg_dict['last_process_state'] = package_last_process_state.process_state

        #set up the process_state field for old dataset with no process_state
        ps_exist = self._check_extras(pkg_dict)

        if not pkg_dict.get("process_state") and not ps_exist:
            if not pkg_dict.get('private'): # public
                pkg_dict['process_state'] = 'Approved'
                pkg_dict['last_process_state'] = 'Approved'
                pkg_dict['state'] = 'active'
            else:
                pkg_dict['process_state'] = 'Modified'
                pkg_dict['last_process_state'] = 'Modified'
                pkg_dict['state'] = 'active'
    
        
    def _check_extras(self, pkg_dict):
        ps_exist = False
        if pkg_dict.get('extras'):
            for dict in pkg_dict.get('extras'):
                if dict.get('key') and dict.get('key') == 'process_state':
                   ps_exist = True
        return ps_exist

                    
    def _update_package_process_state_table(self, context, pkg_dict):
        # pkg_dict does not bring up all fields to UI
        pkg_dict = toolkit.get_action("package_show")(data_dict={"id": pkg_dict['id']})
        package_last_process_state = get_package_last_process_state(context['session'], 
        	                                                         pkg_dict['id'])

        if package_last_process_state:
            last_process_state = package_last_process_state.process_state
            last_reason = package_last_process_state.reason
        else:
            last_process_state = ''
            last_reason = 'NA'
        
        modifior_id = context['model'].User.get(context['user']).id
        ps = pkg_dict.get("process_state")

        if ps and ps != "Rejected":
            pkg_dict['reason'] = 'NA'
        
        if ps and ps != last_process_state or \
               ps and ps == "Rejected" and pkg_dict['reason'] != last_reason:
            add_package_process_state(context['session'], pkg_dict, modifior_id=modifior_id)


    def _check_published_date(self, pkg_dict):
        is_future_date = False
        if helpers.has_published_date_field_in_schema(pkg_dict['type']):
            if pkg_dict.has_key('published_date') and pkg_dict['published_date']:
                dt = parser.parse(pkg_dict['published_date']).date()
                if dt > date.today():
                    is_future_date = True
        return is_future_date


    def _check_published_date_exist_any_empty(self, pkg_dict):
        if helpers.has_published_date_field_in_schema(pkg_dict['type']):
            if pkg_dict.has_key('published_date') and not pkg_dict['published_date'] or \
                not pkg_dict.has_key('published_date'):
                return True
        return False

                
    def _update_pkg(self, context, pkg_dict):
        # state field is not in pkg_dict.
        pkg_dict = toolkit.get_action('package_show')(data_dict={'id': pkg_dict['id']})

        update_flag = False
        # update state field
        if pkg_dict.get("process_state") and pkg_dict['state'] != "deleted":
            if pkg_dict['process_state'] != 'Draft' and pkg_dict['state'] == "draft":
                pkg_dict['state'] = 'active' 
                update_flag = True

        # update private field
        is_future_date = self._check_published_date(pkg_dict)
        if pkg_dict['process_state'] == 'Approved':
            if pkg_dict['private'] and not is_future_date: 
            # there is published_date in schema file and not a future day 
            # or there is no published_date in schema file.
                pkg_dict['private'] = False
                update_flag = True
                if self._check_published_date_exist_any_empty(pkg_dict):
                    pkg_dict['published_date'] = datetime.now()
            elif not pkg_dict['private'] and is_future_date:
                pkg_dict['private'] = True
                update_flag = True
        elif pkg_dict['process_state'] != 'Approved' and  not pkg_dict['private']:
            pkg_dict['private'] = True
            update_flag = True
        
        if update_flag:
            pkg_dict = toolkit.get_action('package_update')(data_dict=pkg_dict)


    def after_update(self, context, pkg_dict):
        if not pkg_dict.has_key('state'):
            pkg_dict['state'] = 'draft'
        if not helpers.has_process_state_field_in_schema(pkg_dict['type']) or pkg_dict['state'] == 'deleted':
            return
        self._update_package_process_state_table(context, pkg_dict)
        self._update_pkg(context, pkg_dict)
        return super(WorkflowPlugin, self).after_update(context, pkg_dict)

                
    def after_create(self, context, pkg_dict):
        if not pkg_dict.has_key('state'):
            pkg_dict['state'] = 'draft'
        if not helpers.has_process_state_field_in_schema(pkg_dict['type']) or pkg_dict['state'] == 'deleted':
            return
        self._update_package_process_state_table(context, pkg_dict)
        self._update_pkg(context, pkg_dict)
        return super(WorkflowPlugin, self).after_create(context, pkg_dict)
    

    def before_view(self, pkg_dict):
        if pkg_dict['state'] == 'deleted':
            return pkg_dict
        if not helpers.has_process_state_field_in_schema(pkg_dict['type']):
            return pkg_dict
        if not pkg_dict.get('reason'):
            pkg_dict['reason'] = 'NA'
        #handle old data with no process_state field
        ps_exist = self._check_extras(pkg_dict)

        if not pkg_dict.get('process_state') and not ps_exist:
            if not pkg_dict.get('private'):
                pkg_dict['process_state'] = 'Approved'
                pkg_dict['state'] = 'active'
            else:
                pkg_dict['process_state'] = 'Modified' 
                pkg_dict['state'] = 'active'
            # has to update the old dataset in database to support new feature like 
            # on process_state
            #toolkit.get_action('package_update')(data_dict=pkg_dict)
        return pkg_dict

    def before_search(self, search_params):
    	user_member_of_orgs = [org['id'] for org
                               in h.organizations_available('read')]

        if (c.group and c.group.id in user_member_of_orgs):
            # added for more control on result datasets 
            # based on our requirement
            search_params.update(
	            {'include_private': True,
	             'include_drafts': True}
            )
    	if c.process_state:
    		# for the filters in user dashboard and organization.
    		if search_params.get("q"):
    			search_params['q'] += ' %s: "%s"' % ('process_state', c.process_state)
    		else:
    			search_params['q'] = '%s: "%s"' % ('process_state', c.process_state)
    	if search_params.get('fq'):
    	    if re.search(r'dataset_type', search_params['fq']):
    	    	# this is for general search
    	    	search_params.update(
		            {'include_private': True,
		             'include_drafts': True}
	            )
    	return search_params

    """
    IConfigurable
    """
    def configure(self, config):
        package_process_state_model.setup()
        member_authorized_workflow_model.setup()
    
    """
    ITemplateHelpers
    """
    def get_helpers(self):
        return {
            'ab_ps_is_admin': helpers.is_admin,
            'ab_ps_current_user_name': helpers.current_user_name,
            'ab_ps_is_authorized_member': helpers.is_authorized_member,
            'ab_ps_get_package_process_state_by_name': helpers.get_package_process_state_by_name,
            'ab_ps_allow_full_work_flow': helpers.allow_full_work_flow,
            'ab_ps_get_all_process_states': helpers.get_all_process_states,
            'ab_ps_get_required_fields_name': helpers.get_required_fields_name,
            'ab_ps_get_process_state_list_not_allow_incomplete': helpers.get_process_state_list_not_allow_incomplete,
            'ab_ps_get_dataset_types': helpers.get_dataset_types,
            'ab_ps_has_process_state_field_in_schema': helpers.has_process_state_field_in_schema,
            'ab_ps_get_required_items_missing': helpers.get_required_items_missing,
            'ab_ps_is_in_process_state_list_not_allow_incomplete': helpers.is_in_process_state_list_not_allow_incomplete
        }

    """
    IRoutes
    """
    def before_map(self, map):
        controller = 'ckanext.workflow.controllers:MemberAuthorizedController'
        with SubMapper(map, controller=controller) as m:
            m.connect('authorized_members', '/organization/{id}/authorized_members',
                      action='manage', ckan_icon='user')
            m.connect('authorized_members_remove', '/organization/{id}/authorized_members_remove',
                      action='remove')

        # for actions on user's dashboard or organization
        map.connect('deactivate-multiple', '/datasets/deactivate-multiple',
                  controller='ckanext.workflow.controllers:PackagesDeactivateController',
                  action='deactivate')
        map.connect('reactivate-multiple', '/datasets/reactivate-multiple',
                  controller='ckanext.workflow.controllers:PackagesReactivateController',
                  action='reactivate')
        map.connect('delete-multiple' ,'/datasets/delete-multiple',
                  controller='ckanext.workflow.controllers:PackagesDeleteController',
                  action='delete_datasets')

        # for filters on user's dashboard or organization
        map.connect('dashboard-filter-action', '/dashboard/datasets/filter-action',
                  controller='ckanext.workflow.controllers:DashboardFilterActionPackagesController',
                  action='dashboard_datasets')
        map.connect('organization-filter-action', '/organization/{id}/filter-action',
                  controller='ckanext.workflow.controllers:OrganizationFilterActionPackagesController',
                  action='read')
        map.connect('opendata-filter-action', '/opendata/filter-action',
                  controller='ckanext.workflow.controllers:FilterActionPackagesController',
                  action='search')
        map.connect('publications-filter-action', '/publications/filter-action',
                  controller='ckanext.workflow.controllers:FilterActionPackagesController',
                  action='search')
        return map
    
    """
    IConfigurer
    """
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'workflow')

    """
    IValidators
    """
    def get_validators(self):
        return {'ab_ps_scheming_required': validation.scheming_required,
                'ab_ps_resource_required': validation.resource_required}

