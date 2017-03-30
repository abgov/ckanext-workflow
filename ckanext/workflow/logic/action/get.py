from ckan.logic.action import get
import ckan.plugins.toolkit as toolkit

@toolkit.side_effect_free
def package_show_multiple(context, data_dict):
    '''Return the metadata of datasets (packages) and their resources.

    :param id: the id or name of the dataset
    :type id: string
    :param use_default_schema: use default package schema instead of
        a custom schema defined with an IDatasetForm plugin (default: False)
    :type use_default_schema: bool
    :param include_tracking: add tracking information to dataset and
        resources (default: False)
    :type include_tracking: bool
    :rtype: list of data dict

    '''
    pkg_dict_list = []
    names_or_ids = data_dict.get("ids")
    for id in names_or_ids.split(','):
        d_dict = {'id': id}
        pkg_dict = get.package_show(context, d_dict)
        pkg_dict_list.append(pkg_dict)
    return pkg_dict_list
    