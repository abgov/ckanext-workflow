"use strict";
/*
* This script will control the deactivation, reactivation and delete actions 
* on dataset list in dashbord of user and orgnization.
* It listens the checkbox and the selection box's states and and the filter checkbox 
* then submit the form or back the origin show-all view.
*/

/* this module is for checkbox of action */
ckan.module('actions', function ($, _) {
  return {
    initialize: function () {

      $.proxyAll(this, /_on/);

      // Add an event handler to the button, when the user clicks the button
      // our _onClick() function will be called.
      this.el.on('click', this._onChange);
    },

    _onChange: function(event) {
        var checkbox_filter = $('#ext_field-filters');
        if (this.el.is(':checked') || checkbox_filter.is(':checked') ){
          var form = $("#form_action_filter");
          form.submit();
        }else{
          // not checked.
          window.location.href = this.options['url_all_ds'];
        }
    },


  };
});

/*
* This module is for select box. 
*/
ckan.module('actions_select', function ($, _) {
  return {
    initialize: function () {

      $.proxyAll(this, /_on/);

      // Add an event handler to the button, when the user clicks the button
      // our _onClick() function will be called.
      this.el.on('change', this._onChange);
    },

    _onChange: function(event) {
        var checkbox_action = $('#ext_field-actions');
        if (checkbox_action.is(':checked') ){
          var form = $("#form_action_filter");
          form.submit();
        }else{
          // not checked.
        }
    },


  };
});
