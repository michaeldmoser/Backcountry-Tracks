/*
 * Registration Plugin
 */

(function( $ ){

  $.fn.tpRegistration = function(options) {

    var $this = this;

    this.errorElement = $('<ul/>')
      .addClass('register-error ui-state-error ui-corner-all')
      .hide()
      .appendTo(this);

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
      complete: function(data, textStatus, jqXHR) {
        $.fn.tpRegistration.handleSuccess.call($this, data, textStatus, jqXHR)
      }
    });
  };

  $.fn.tpRegistration.handleSuccess = function(data, textStatus, jqXHR) {
    var jsonData = $.parseJSON(data.responseText);
    if (jsonData.successful) {
      this.options.thankYouElement.dialog({modal: true});
      this.errorElement.hide();
    } else {
      var $this = this;
      this.errorElement.empty();
      _(jsonData.messages).each(function(elementMessages) {
        _(elementMessages).each(function(message){
          var li = $('<li></li>').html(message);
          this.errorElement.append(li)
        }, this)
      }, this);
      this.errorElement.fadeIn();
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
  $.fn.tpLogin.window = window;

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
        $.fn.tpLogin.handleComplete.call($this, data)
      }
    });
  };

  $.fn.tpLogin.handleComplete = function(data) {
    var jsonData = $.parseJSON(data.responseText);
    if (jsonData.location) {
      $.fn.tpLogin.window.location = jsonData.location;
    }
//    var headers = response.getAllResponseHeaders();
//    var results = headers.match('X-Location: (.*)\n');
//    if (results && results.length == 2) {
//      var location = results[1];
//
//    }
  }

})( jQuery );
