from ckan.plugins import toolkit


not_missing = toolkit.get_validator('not_missing')
user_exists = toolkit.get_validator('user_id_or_name_exists')
ignore_missing = toolkit.get_validator('ignore_missing')
int_validator = toolkit.get_validator('int_validator')
boolean_validator = toolkit.get_validator('boolean_validator')
as_org_id = toolkit.get_validator(
    'convert_group_name_or_id_to_id')
as_user_id = toolkit.get_validator(
    'convert_user_name_or_id_to_id')


def member_authorized_schema():
    return {
        'username': [not_missing, unicode, user_exists],
    }


