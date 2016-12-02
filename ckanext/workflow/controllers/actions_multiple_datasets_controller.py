import re
import ckan.logic as logic
import ckan.lib.base as base
import ckan.plugins.toolkit as toolkit

from ckan.plugins.toolkit import _, request, c
import ckan.lib.helpers as h
import ckan.logic as logic
from ckan.controllers.package import PackageController
import ckan.model as model

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
get_action = logic.get_action
abort = base.abort
ValidationError = toolkit.ValidationError
render = base.render

def get_context_org_url():
    context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}

    org = request.params.get('ext_field-hide-org', u'')
    if org:
        url = toolkit.url_for(controller="organization", action='read', id=org)
    else:
        url = toolkit.url_for(controller='user', action='dashboard_datasets')
    return context, org, url


class PackagesDeleteController(PackageController):
    """ This is used to delete multiple datasets"""
    def delete_datasets(self):
        """ If org exist, it will handle delete in organization's
            read()'s datasets, then return to organization's read().
            If not exsit, it will handle delete in user's dashboard()'s 
            datasets, then return to user's dashboard().
        """
        if 'cancel' in request.params:
            h.redirect_to(controller='package', action='search')

        context, org, url = get_context_org_url()

        dataset_type = ''
        try:
            if request.method == 'POST':
                count = 0
                for id in request.params:
                    if re.match('ext_field-', id):
                        continue
                    pkg_dict = get_action('package_show')(context, {'id': id})
                    dataset_type = pkg_dict['type']
                    get_action('package_delete')(context, {'id': id})
                    count += 1
                if count == 0:
                    h.flash_notice(_('No datasets has been deleted.'))
                else:
                    h.flash_notice(_('Datasets have been deleted.'))
                h.redirect_to(url)
        except NotAuthorized:
            abort(401, _('Unauthorized to delete package %s') % '')
        except NotFound:
            abort(404, _('Dataset not found'))
        dataset_type = dataset_type if dataset_type else 'dataset'
        if org:
            return render('/organization/'+org)
        else:
            return render('/dashboard/datasets',
                      extra_vars={'dataset_type': dataset_type})


class PackagesDeactivateController(PackageController):
    """ This is used to deactivate multiple public datasets"""
    def deactivate(self):
        """ If org exist, it will handle deactivation in organization's
            read()'s datasets, then return to organization's read().
            If not exsit, it will handle deactivation in user's dashboard()'s 
            datasets, then return to user's dashboard().
        """
        if 'cancel' in request.params:
            h.redirect_to(controller='package', action='search')
        
        context, org, url = get_context_org_url()

        try:
            if request.method == 'POST':
                count = 0
                for id in request.params:
                    if re.match('ext_field-', id):
                        continue
                    pkg_dict = get_action('package_show')(context, data_dict={'id': id})
                    pkg_dict['private'] = True
                    pkg_dict['process_state'] = "Modified"
                    pkg_dict['state'] = "active"
                    get_action('package_update')(context, data_dict=pkg_dict)
                    count += 1
                if count == 0:
                    h.flash_notice(_('No datasets has been deactivated.'))
                else:
                    h.flash_notice(_('Datasets have been deactivated.'))
                h.redirect_to(url)
        except NotAuthorized:
            abort(401, _('Unauthorized to deactivate package %s') % '')
        except NotFound:
            abort(404, _('Dataset not found'))
        return h.redirect_to(url)


class PackagesReactivateController(PackageController):
    """ This is used to reactivate multiple private datasets"""
    def reactivate(self):
        """ If org exist, it will handle reactivation in organization's
            read()'s datasets, then return to organization's read().
            If not exsit, it will handle reactivation in user's dashboard()'s 
            datasets, then return to user's dashboard().
        """
        if 'cancel' in request.params:
            h.redirect_to(controller='package', action='search')

        context, org, url = get_context_org_url()

        try:
            if request.method == 'POST':
                count = 0
                for id in request.params:
                    if re.match('ext_field-', id):
                        continue
                    pkg_dict = get_action('package_show')(context, data_dict={'id': id})
                    pkg_dict['private'] = False
                    pkg_dict['process_state'] = "Approved"
                    pkg_dict['state'] = "active"
                    get_action('package_update')(context, data_dict=pkg_dict)
                    count += 1
                if count == 0:
                    h.flash_notice(_('No datasets has been reactivated.'))
                else:
                    h.flash_notice(_('Datasets have been reactivated.'))
                h.redirect_to(url)
        except NotAuthorized:
            abort(401, _('Unauthorized to reactivate package %s') % '')
        except NotFound:
            abort(404, _('Dataset not found'))
        except ValidationError as e:
            h.flash_error( _(self._validation_error_message(e.error_dict, pkg_dict['name'])), allow_html=True )
        return h.redirect_to(url)

    def _validation_error_message(self, err_dict, pkg_name):
        message = "Dataset '{0}'  <br/><br/>ValidationErrors:  <br/>".format(pkg_name)
        for field, error in err_dict.iteritems():
            if field == 'resources':
                #[{u'classification': [u'Missing value']}, {u'classification': [u'Missing value']}]
                for idx, d in enumerate(error):
                    res_err = ''
                    for k, v in d.items():
                        res_err += "{0}: {1} ".format(k, ','.join(v))   
                    error[idx] = res_err
            message += "{0}:  {1}<br/>".format(field, ','.join(error))
        return message
