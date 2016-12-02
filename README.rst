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
   ckanext-repeating



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
                   ckanext.repeating:presets.json

3. Put this line into your ini config file.

   scheming.dataset_schemas =  ckanext.<your_extension>:<your_scheming_json_file>


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
      },

2. (Optional) Put this block into your schema file to track the contributor and creator.
   
      {
      "field_name": "creator_user_name",
      "label": "User of record creation",
      "form_snippet": "dataset_creator.html",
      "help_text": "User name of creating this record.",
      "help_inline": false,
      "form_attrs": {"disabled": "disabled",
                     "style": "background-color:#ddd"}
      },
      {
      "field_name": "maintainers",
      "preset": "repeating_text",
      "label": "Maintainer",
      "form_blanks": 0,
      "form_attrs": {"readonly": "readonly",
                       "style": "background-color:#ddd"}
      },


--------
Notice
--------

1. All the field names should not be changed.

2. The reason will show up when select Rejected in process_state field. It is the required field. 
It will not show up when select other values. But it will with value 'NA' saved into database.

3. If change the options of process field, fanstatic/css/main.css must be maintained.

------------------------
Development Installation
------------------------

To install ckanext-workflow for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/yongjiel/ckanext-workflow.git
    cd ckanext-workflow
    python setup.py develop
    pip install -r dev-requirements.txt


-----------------
Running the Tests
-----------------

To run the tests, do::

    nosetests --nologcapture --with-pylons=test.ini

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.workflow --cover-inclusive --cover-erase --cover-tests


---------------------------------
Registering ckanext-workflow on PyPI
---------------------------------

ckanext-workflow should be availabe on PyPI as
https://pypi.python.org/pypi/ckanext-workflow. If that link doesn't work, then
you can register the project on PyPI for the first time by following these
steps:

1. Create a source distribution of the project::

     python setup.py sdist

2. Register the project::

     python setup.py register

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the first release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.1 then do::

       git tag 0.0.1
       git push --tags


----------------------------------------
Releasing a New Version of ckanext-workflow
----------------------------------------

ckanext-workflow is availabe on PyPI as https://pypi.python.org/pypi/ckanext-workflow.
To publish a new version to PyPI follow these steps:

1. Update the version number in the ``setup.py`` file.
   See `PEP 440 <http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers>`_
   for how to choose version numbers.

2. Create a source distribution of the new version::

     python setup.py sdist

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the new release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.2 then do::

       git tag 0.0.2
       git push --tags
