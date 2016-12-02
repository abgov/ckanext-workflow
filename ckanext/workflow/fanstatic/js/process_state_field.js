"use strict";

/* process_state_field
 *
 * This JavaScript module will check the value of last_process_state field.  If its value is 
 * 'Rejected', the reason will show and set up the last value of reason. If the value of process_state
 * field is switched to 'Rejected' again, reason field will show up with blank value.
 * Also the process state field will control the private field. If not Approved, private field is true.
 *
 * is_admin - the admin and authorized member check, 'True' or 'False'
 * options - the options for this field. Dictionary{ 'value', option_value, 'text': option_label }
 * restrict_options - the option values that are allowed by sysadmin or org admin. Array.
 *
 */
ckan.module('process_state_field', function ($, _) {
  return {
    initialize: function () {
      $.proxyAll(this, /_on/);
      
      var r = $("#field-reason");
      var lps = $("#field-last_process_state");
      if(lps.val() == "Rejected"){  // display the reason only
         if (this.options.is_admin == "False"){ // non-admin user cannot change the reason field
           r.attr("readonly", "readonly");
           r.css("background-color", "#ddd");
         }
      }else{
         r.parent().parent().css("display", 'none');
         r.val("NA");
      }
      //if the admin does not input anything of reason but keep process_state rejected.
      if(this.el.val() == "Rejected"){ // only admin can do this, display for admin only
          r.parent().parent().css("display", 'block');
          if (r.val() == "NA"){
            r.val(""); // validator will not allow None
          }
      }
      // hide the field private.
      // process state field to control the work flow and state.
      var p = $("#field-private");
      p.parent().parent().hide();
      if (this.el.val() != "Approved") {
          p.val("True");
      }else{
          p.val("False");
      }

      this.el.on('change', this._onChange);
    },

    _onChange: function(event){
        var r = $("#field-reason");
        var lps = $("#field-last_process_state");
        if(this.el.val() == "Rejected"){ // only admin can do this,  display for admin only
          r.removeAttr("disabled");
          r.css("background-color", "");
          r.parent().parent().css("display", 'block');
          r.val("");
        }else{ //  the other values for all users
          r.parent().parent().css("display", 'none');
          r.val("NA");
        }
        var p = $("#field-private");
        if (this.el.val() != "Approved") {
            p.val("True");
        }else{
            p.val("False");
        }
        
    },
  };
});