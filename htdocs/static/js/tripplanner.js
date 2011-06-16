/*
 * Registration Plugin
 */

(function( $ ){

  $.fn.tpRegisration = function() {
    this.submit($.fn.tpRegisration.submitForm);
    return this;
  }

  $.fn.tpRegisration.ajax = $.ajax;

  $.fn.tpRegisration.submitForm = function(event) {
    event.preventDefault();

    // get JSON encoded form values
    var values = {};
    $.each($(this).serializeArray(), function(i, field) {
        values[field.name] = field.value;
    });

    var data = JSON.stringify(values);

    $.fn.tpRegisration.ajax(this.action, {
      type: 'POST',
      data: data,
      contentType: 'application/json'
    }, 'json');
  };

})( jQuery );

