testHelpers = {
    submitForm: $.fn.tpRegistration.submitForm,
    ajax: $.fn.tpRegistration.ajax,

    reset: function() {
      $.fn.tpRegistration.submitForm = testHelpers.submitForm;
      $.fn.tpRegistration.ajax = testHelpers.ajax;
      $.dialog = testHelpers.dialog;

      testHelpers.createForm()
      testHelpers.createThankYouElement()
    },

    createForm: function() {
      testHelpers.form = $([
        '<form action="/test">',
          '<input name="test1" value="1" />',
          '<input name="test2" value="2" />',
          '<input name="test3" value="3" />',
        '</form>'
      ].join('\n'));
    },

    createThankYouElement: function() {
      testHelpers.thankYouElement =  $('<div>Thank You</div>');
    }
}

module("Registration Tests", {
  setup: function() {
    testHelpers.reset();
  }
});

test("test trigger submit calls submit handler", function() {
  var callsSubmitHandler = false;
  $.fn.tpRegistration.submitForm = function(event) {
    callsSubmitHandler = true;
  }

  testHelpers.form.tpRegistration().trigger("submit");
  ok(callsSubmitHandler, "submit handler called");
});

test("test submit form sends ajax request", function() {
  var sendsAjax = false;
  $.fn.tpRegistration.ajax = function(url, options) {
    sendsAjax = true;
  }

  testHelpers.form.tpRegistration().trigger("submit");
  ok(sendsAjax, "ajax function called");
});

test("test ajax url follows form action", function() {
  var testUrl = '';
  $.fn.tpRegistration.ajax = function(url, options) {
    testUrl = url;
  }
  testHelpers.form.tpRegistration().trigger("submit");
  ok(testUrl.indexOf('/test') >= 0)

  testHelpers.form.attr('action', '/another/test');
  testHelpers.form.tpRegistration().trigger("submit");
  ok(testUrl.indexOf('/another/test') >= 0)
});

test("test ajax sends json-encoded form as application/json", function() {
  var contentType = null;
  var data = null;
  $.fn.tpRegistration.ajax = function(url, options) {
    options.beforeSend = function(jqXHR, settings) {
      contentType = settings.contentType;
      data = settings.data;
      return false;
    }
    $.ajax(url, options);
  }
  testHelpers.form.tpRegistration().trigger("submit");

  //for some reason jsTestDriver breaks on equal()
  //use ok for now until a fix is found
  ok(contentType === 'application/json', 'data sent as application/json')
  ok(data === '{"test1":"1","test2":"2","test3":"3"}', 'form data serialized as expected')
});

test("test handle success method creates thank you modal", function() {
  $.fn.tpRegistration.ajax = function(url, options) {
    options.success({}, 'success', {})
  }

  var isOpen = false;
  testHelpers.thankYouElement.bind('dialogopen', function(event, ui) {
    isOpen = true;
  });

  testHelpers.form.tpRegistration({
    thankYouElement: testHelpers.thankYouElement
  }).trigger("submit");

  testHelpers.thankYouElement.dialog('close');
  ok(isOpen, 'thank you dialog opened')
});
