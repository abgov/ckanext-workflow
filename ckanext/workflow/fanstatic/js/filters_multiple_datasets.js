"use strict";
/*
* This script will control the filtering on dataset's process_state 
* in dashbord of user and orgnization.
* It listens the checkbox and the selection box's states and then 
* submit the form.
/* this module is for checkbox of filter. */
ckan.module('filters', function ($, _) {
  return {
    initialize: function () {

      $.proxyAll(this, /_on/);

      // Add an event handler to the button, when the user clicks the button
      // our _onClick() function will be called.
      this.el.on('click', this._onChange);
    },

    _onChange: function(event) {
        var checkbox_action = $('#ext_field-actions');
        if (this.el.is(':checked') || checkbox_action.is(':checked')){
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
* This module is for select box of filter. 
*/
ckan.module('filters_select', function ($, _) {
  return {
    initialize: function () {

      $.proxyAll(this, /_on/);

      // Add an event handler to the button, when the user clicks the button
      // our _onClick() function will be called.
      this.el.on('change', this._onChange);
    },

    _onChange: function(event) {
        var checkbox_filter = $('#ext_field-filters');
        if (checkbox_filter.is(':checked')){
            var form = $("#form_action_filter");
            form.submit();
        }else{
          // not checked.
        }
    },


  };
});
