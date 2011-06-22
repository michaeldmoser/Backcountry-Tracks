/*
 * Registration Plugin
 */

(function( $ ){

  $.fn.tpRegistration = function(options) {

    $this = this

    $this.options = $.extend({
      thankYouElement: null
    }, options);

    this.submit(function(event) {
      $.fn.tpRegistration.submitForm.call($this, event)
    });
    return this;
  }

  $.fn.tpRegistration.ajax = $.ajax;

  $.fn.tpRegistration.submitForm = function(event) {
    event.preventDefault();

    $this = this;

    // get JSON encoded form values
    var values = {};
    $.each($(this).serializeArray(), function(i, field) {
        values[field.name] = field.value;
    });

    var data = JSON.stringify(values);

    $.fn.tpRegistration.ajax($(this).attr('action'), {
      type: 'POST',
      data: data,
      contentType: 'application/json',
      success: function(data, textStatus, jqXHR) {
        $.fn.tpRegistration.handleSuccess.call($this, data, textStatus, jqXHR)
      }
    }, 'json');
  };

  $.fn.tpRegistration.handleSuccess = function(data, textStatus, jqXHR) {
    if (this.options.thankYouElement) {
      this.options.thankYouElement.dialog();
    }
  }

})( jQuery );

