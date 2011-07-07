/*
 * Registration Plugin
 */

(function( $ ){

  $.fn.tpRegistration = function(options) {

    var $this = this;

    this.options = $.extend({
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

    var $this = this;

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
    });
  };

  $.fn.tpRegistration.handleSuccess = function(data, textStatus, jqXHR) {
    if (this.options.thankYouElement) {
      this.options.thankYouElement.dialog();
    }
  }

})( jQuery );

/*
 * Login Plugin
 */

(function( $ ){

  $.fn.tpLogin = function(options) {
    var $this = this
    this.submit(function(event) {
      $.fn.tpLogin.submitForm.call($this, event)
    });
    return this;
  }

  $.fn.tpLogin.ajax = $.ajax;
  $.fn.tpLogin.window = $.window;

  $.fn.tpLogin.submitForm = function(event) {
    event.preventDefault();

    var $this = this;

    // get JSON encoded form values
    var values = {};
    $.each($(this).serializeArray(), function(i, field) {
        values[field.name] = field.value;
    });

    var data = JSON.stringify(values);

    var response = $.fn.tpLogin.ajax($(this).attr('action'), {
      type: 'POST',
      data: data,
      contentType: 'application/json',
      complete: function(data, textStatus, jqXHR) {
        $.fn.tpLogin.handleComplete.call($this, data, textStatus, jqXHR)
      }
    });
  };

  $.fn.tpLogin.handleComplete = function(data, textStatus, jqXHR) {
    $.fn.tpLogin.window.location = data.redirect_url;
  }

})( jQuery );
