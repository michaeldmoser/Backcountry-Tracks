testHelpers = {
    submitForm: $.fn.tpRegisration.submitForm,
    ajax: $.fn.tpRegisration.ajax,

    reset: function() {
      $.fn.tpRegisration.submitForm = testHelpers.submitForm;
      $.fn.tpRegisration.ajax = testHelpers.ajax;
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

module("Registration Tests", {
  setup: function() {
    testHelpers.reset();
  }
});

test("test trigger submit calls submit handler", function() {
  var callsSubmitHandler = false;
  $.fn.tpRegisration.submitForm = function(event) {
    callsSubmitHandler = true;
  }

  testHelpers.form.tpRegisration().trigger("submit");
  ok(callsSubmitHandler, "submit handler called");
});

test("test submit form sends ajax request", function() {
  var sendsAjax = false;
  $.fn.tpRegisration.ajax = function(url, options) {
    sendsAjax = true;
  }

  testHelpers.form.tpRegisration().trigger("submit");
  ok(sendsAjax, "ajax function called");
});

test("test ajax url follows form action", function() {
  $.fn.tpRegisration.ajax = function(url, options) {
    ok(url.indexOf('/test') > 0)
  }
  testHelpers.form.tpRegisration().trigger("submit");

  testHelpers.reset()

  testHelpers.form.attr('action', '/another/test');
  $.fn.tpRegisration.ajax = function(url, options) {
    ok(url.indexOf('/another/test') > 0)
  }
  testHelpers.form.tpRegisration().trigger("submit");
});

test("test ajax sends content as application/json", function() {
  var contentType = null;
  $.fn.tpRegisration.ajax = function(url, options) {
    options.beforeSend = function(jqXHR, settings) {
      contentType = settings.contentType;
      return false;
    }
    $.ajax(url, options);
  }
  testHelpers.form.tpRegisration().trigger("submit");

  //for some reason jsTestDriver breaks on equal()
  //use ok for now until a fix is found
  //equal(contentType, 'application/json');
  ok(contentType === 'application/json')
});

test("test ajax sends form as json", function() {
  var data = null;
  $.fn.tpRegisration.ajax = function(url, options) {
    options.beforeSend = function(jqXHR, settings) {
      data = settings.data;
      return false;
    }
    $.ajax(url, options);
  }
  testHelpers.form.tpRegisration().trigger("submit");

  //equal(data, '{"test1":"1","test2":"2","test3":"3"}');
  ok(data === '{"test1":"1","test2":"2","test3":"3"}')
});
