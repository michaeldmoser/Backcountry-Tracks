(function($) {

var testHelpers = {
    submitForm: $.fn.tpLogin.submitForm,
    ajax: $.fn.tpLogin.ajax,
    window: $.fn.tpLogin.window,

    reset: function() {
      $.fn.tpLogin.submitForm = testHelpers.submitForm;
      $.fn.tpLogin.ajax = testHelpers.ajax;
      $.fn.tpLogin.window = testHelpers.window;

      testHelpers.createForm()
    },

    createForm: function() {
      testHelpers.form = $([
        '<form action="/test">',
          '<input name="test1" value="1" />',
          '<input name="test2" value="2" />',
          '<input name="test3" value="3" />',
        '</form>'
      ].join('\n'));
    }
}

module("Login Tests", {
  setup: function() {
    testHelpers.reset();
  }
});

test("test trigger submit calls submit handler", function() {
  var callsSubmitHandler = false;
  $.fn.tpLogin.submitForm = function(event) {
    callsSubmitHandler = true;
  }

  testHelpers.form.tpLogin().trigger("submit");
  ok(callsSubmitHandler, "submit handler called");
});

test("test submit form sends ajax request", function() {
  var sendsAjax = false;
  $.fn.tpLogin.ajax = function(url, options) {
    sendsAjax = true;
  }

  testHelpers.form.tpLogin().trigger("submit");
  ok(sendsAjax, "ajax function called");
});

test("test ajax url follows form action", function() {
  var testUrl = '';
  $.fn.tpLogin.ajax = function(url, options) {
    testUrl = url;
  }
  testHelpers.form.tpLogin().trigger("submit");
  ok(testUrl.indexOf('/test') >= 0)

  testHelpers.form.attr('action', '/another/test');
  testHelpers.form.tpLogin().trigger("submit");
  ok(testUrl.indexOf('/another/test') >= 0)
});

test("test ajax sends json-encoded form as application/json", function() {
  var contentType = null;
  var data = null;
  $.fn.tpLogin.ajax = function(url, options) {
    options.beforeSend = function(jqXHR, settings) {
      contentType = settings.contentType;
      data = settings.data;
      return false;
    }
    $.ajax(url, options);
  }
  testHelpers.form.tpLogin().trigger("submit");

  //for some reason jsTestDriver breaks on equal()
  //use ok for now until a fix is found
  ok(contentType === 'application/json', 'data sent as application/json')
  ok(data === '{"test1":"1","test2":"2","test3":"3"}', 'form data serialized as expected')
});

test("test handle complete redirects to given url", function() {
  var path = '/path/to/home';
  var fakeResponse = {
    getAllResponseHeaders: function() {
      return 'X-Location: ' + path + '\n';
    }
  }

  $.fn.tpLogin.window = {location: null};
  $.fn.tpLogin.handleComplete(fakeResponse);
  ok($.fn.tpLogin.window.location == '/path/to/home', 'complete redirects to given url')
});

})(jQuery);
