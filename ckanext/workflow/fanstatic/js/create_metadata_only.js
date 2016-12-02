"use strict";

/* create_metadata_only for submit button 'Save metadata only' when creating new dataset.
 *
 * This JavaScript module will empty the value of hidden field "_ckan_phase" 
 * 
 *
 */
ckan.module('create_metadata_only', function ($, _) {
  return {
    initialize: function () {
      $.proxyAll(this, /_on/);
      this.el.on('click', this._onClick);
    },

    _onClick: function(event){
        // what we need is the create mode. For edit mode, use value 
        // ''go-read' of button 'save' to control 
        if ($('[name="pkg_name"]').val() == ''){
          $('[name="_ckan_phase"]').val("");
        }
    },
  };
});