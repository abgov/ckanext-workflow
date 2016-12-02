import ckan.logic as logic
import ckan.lib.base as base
import ckan.plugins.toolkit as toolkit

from ckan.plugins.toolkit import _, request, c
from ckan.controllers.user import UserController
from ckan.controllers.organization import OrganizationController
from ckan.controllers.package import PackageController

class DashboardFilterActionPackagesController(UserController):
    """This is used to control filtering in dashboard"""

    def __before__(self, action, **env):
        UserController.__before__(self, action, **env)
        check1 = request.params.get("ext_field-filters")
        ps = request.params.get("ext_field-filters-select")
        check2 = request.params.get("ext_field-actions")
        ac = request.params.get("ext_field-actions-select")
        if check1:
            c.process_state = ps
        if check2:
            c.action_multi = ac
            
        
class OrganizationFilterActionPackagesController(OrganizationController):
    """This is used to control filtering in organization"""

    def __before__(self, action, **env):
        OrganizationController.__before__(self, action, **env)
        check1 = request.params.get("ext_field-filters")
        ps = request.params.get("ext_field-filters-select")
        check2 = request.params.get("ext_field-actions")
        ac = request.params.get("ext_field-actions-select")
        if check1:
            c.process_state = ps
        if check2:
            c.action_multi = ac


class FilterActionPackagesController(PackageController):
    """This is used to control filtering in opendata and publications """
    """ TODO : there is still no result after filtering. Must check
        the package cotroller's search method.
    """
    def __before__(self, action, **env):
        PackageController.__before__(self, action, **env)
        check1 = request.params.get("ext_field-filters")
        ps = request.params.get("ext_field-filters-select")
        check2 = request.params.get("ext_field-actions")
        ac = request.params.get("ext_field-actions-select")
        if check1:
            c.process_state = ps
        if check2:
            c.action_multi = ac

