=============
ckanext-workflow
=============

This extension does more business process states than the ckan core's states and
private choices. Process states match to state and private choices in N to 1 cardinality.
It allows more situations to fit the usage in deep. The match is like below:

    Process_state     state     private
    Draft             draft     true
    Modified          active    true
    Submitted         active    true
    Pending           active    true
    Rejected          active    true
    Approved          active    false


------------
Requirements
------------

1. Currently it needs ckan 2.6.

2. It needs two extension to support:
    
        ckanext-scheming



------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-workflow:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-workflow Python package into your virtual environment::

     pip install ckanext-workflow

3. Add ``workflow`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


---------------
Config Settings
---------------

Document any optional config settings here. For example::

1. Put workflow into ckan.plugins.

2. Put these lines into your ini config file.
   
    scheming.presets = ckanext.scheming:presets.json
  

3. Put this line into your ini config file.

    scheming.dataset_schemas =  ckanext.your_extension:your_scheming_json_file


------
Usage
------

1. Put this block into your json schema file (field names are fixed).

        {
        "field_name": "process_state",
        "label": "Change to Process State",
        "form_snippet": "process_state.html",
        "help_text": "The state of work flow is going to be changed to",
        "help_inline": false,
        "required": true,
        "validators": "scheming_required ab_ps_resource_required",
        "preset": "select",
        "choices": [
          {"value": "Draft", "label": "Draft"},
          {"value": "Modified", "label": "Modified"},
          {"value": "Submitted", "label": "Submitted"},
          {"value": "Pending", "label": "Pending"},
          {"value": "Rejected", "label": "Rejected"},
          {"value": "Approved", "label": "Approved"}
        ],
        "form_decision_restrict_choices_to": [
          "Pending", "Rejected", "Approved"
        ],
        "form_not_allow_incomplete_dataset": [
          "Submitted", "Pending", "Rejected", "Approved"
        ]
        },
        {
          "field_name": "last_process_state",
          "label": "Last Process State",
          "help_text": "The last state of work flow",
          "help_inline": false,
          "form_attrs": {"disabled": "disabled",
                         "style": "background-color:#ddd"}
        },
        {
          "field_name": "reason",
          "label": "Rejected Reason",
          "form_snippet": "markdown.html",
          "form_placeholder": "A concise narrative of the content of an information resource that includes its purpose and function.",
          "help_text": "Reason of rejected state of work flow",
          "help_inline": false,
          "required": true,
          "validators": "scheming_required" 
        }

1.1  (Optional) Put this block into your json schema file, the approved state will look up this date for approve and private field false:
        {
          "field_name": "published_date",
          "label": "Publish on this future date.",
          "preset": "date",
          "form_placeholder": "date_format='%Y-%m-%d'",
          "help_text": "The date on which an information resource will be automatically published.",
          "help_inline": false
        }

2. If use "required": true and "validators": "scheming_required" in your schema json file, change 
"scheming_required" into "ab_ps_scheming_required". It will validate fields only on "Submitted", 
"Pending", "Rejected" and "Approved" states.


3. Put these two lines into your schema.xml:
    
        <field name="process_state" type="string" indexed="true" stored="true" omitNorms="true" />
        <copyField source="process_state" dest="text"/>


4. Rebuild index and restart solr.


5. Go to organization management, you can find a tag name "Work flow". You can authorize editor of 
the same organization to work out the full work flow. If authorized, the editor can see the change
in the list of process_state field when editing a dataset. 


6. If want more flexible with no resource when switch to "Submitted", "Pending", "Rejected", "Approved",
just remove the "ab_ps_resource_required" from field process_state's validator field.



--------
Notice
--------

1. All the field names should not be changed.

2. The reason will show up when select Rejected in process_state field. It is the required field. 
It will not show up when select other values. But it will with value 'NA' saved into database.

3. If change the options of process field, fanstatic/css/main.css must be maintained.





