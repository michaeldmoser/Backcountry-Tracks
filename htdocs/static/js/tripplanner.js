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
	if (data.status > 299) {
		$('#failed_login').dialog({modal: true});	
		$('#login-form #password').val('');
		return;
	}
    if (jsonData.location) {
      $.fn.tpLogin.window.location = jsonData.location;
    }
  }

})( jQuery );

/*
 * Forgot password form
 */
$(function () {
	$('#forgot-password').dialog({
		autoOpen: false,
		modal: true,
		title: 'Reset password',
		resizable: false
	});	
	$('#forgot-password-confirm').dialog({
		autoOpen: false,
		modal: true,
		title: 'Email sent',
		resizable: false
	});	

	$('#forgot-password button').button();

	$('#forgot-link').click(function (ev) {
		ev.stopPropagation();

		$('#forgot-password').dialog('open');
		
		return false;	
	});

	$('#forgot-password button').click(function (ev) {
		ev.stopPropagation();
		var ajax_promise = $.ajax({
			type: 'POST',
			url: '/app/password',
			data: JSON.stringify({reset: true, email: $('#forgot-password input[name=email]').val()}),
			contentType: 'application/json'
			});
		ajax_promise.done(function (data, status, jqxhr) {
			$('#forgot-password').dialog('close');
			$('#forgot-password-confirm').dialog('open');
		});
		
		return false;
	});
});

$(function () {
    $('#form_message').dialog({
        modal: true,
        buttons: {'Ok': function () { $(this).dialog('close'); }},
        autoOpen: false
    });

    $('#big-login-form').submit(function (ev) {
        ev.preventDefault();

        var email = $('#email').val();
        var reset_key = $('#reset_key').val();
        
        var password = $('#password').val();
        if (password != $('#retype_password').val()) {
            var form_message = $('#form_message');
            form_message.dialog('option', 'title', 'Password Mismatch!');
            form_message.html('The passwords do not match!');
            form_message.dialog('open');
            return;
        }
         
        var data = {
            'email': email,
            'password': password
        };

        var reset_defered = $.ajax('/app/password/' + reset_key,
            {
                type: 'PUT',
                data: JSON.stringify(data),
                contentType: 'application/json'
            }
        );

        reset_defered.done(function () {
            window.location.href = '/app/home';
        });

        reset_defered.fail(function () {
            var form_message = $('#form_message');
            form_message.dialog('option', 'title', 'Reset failed');
            form_message.html("We're sorry there was an error and your password could not be reset.");
            form_message.dialog('open');
        });
    });
});

