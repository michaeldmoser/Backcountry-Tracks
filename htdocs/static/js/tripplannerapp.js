var current_user = null;
var UserModel = Backbone.Model.extend({
	url: function () {
		return "/app/user";
	}
});

var ApplicationModel = Backbone.Model.extend({
	initialize: function () {
		_.bindAll(this, 'activate');
	},

	activate: function () {
		this.trigger('activating');
	}
});


var HomeManagerApp = Backbone.View.extend({
	className: 'application_container',

	initialize: function () {
		_.bindAll(this, 'render', 'handle_activate');
		$(this.el).hide();
		this.model.bind('activating', this.handle_activate);
	},

	render: function () {
		$(this.el).html('Welcome');
	},

	handle_activate: function () {
		this.trigger('activated', this);
	}
});

var AppChooserButton = Backbone.View.extend({
	tagName: 'div',
	className: 'app_chooser_button',

	events: {
		'click': 'choose_app'
	},


	initialize: function () {
		_.bindAll(this, 'render', 'choose_app');
		this.button = new Image;
		this.button.src = this.model.get('icon');
		$(this.el).append(this.button);
	},
	
	render: function () {
		$(this.button).attr({
			'title': this.model.get('name'),
			'src': this.model.get('icon'),
			'alt': this.model.get('name')
		});

		return this;
	},

	choose_app: function () {
		this.trigger('portal:app_selected', this.model);
	}
});

var AppChooserView = Backbone.View.extend({
	initialize: function () {
		_.bindAll(this, 'render', 'add_button', 'handle_app_selected');
		this.applications = this.options.applications;
		this.button_views = new Array;
		this.applications.each(function (app) {
			var button_view = new AppChooserButton({model: app});
			button_view.render();
			this.button_views.push(button_view);
			button_view.bind('portal:app_selected', this.handle_app_selected);
		}, this);
	},

	render: function() {
		_.each(this.button_views, this.add_button, this);
		return this;
	},

	add_button: function (button) {
		$(this.el).append(button.el);
	},

	handle_app_selected: function (app_model) {
		this.trigger('portal:app_selected', app_model);
	}
});

var Applications = Backbone.Collection.extend({
	'model': ApplicationModel
});

var AppChooser = function (container, applications) {
	var appchooserview = new AppChooserView({
		'el': container,
		'applications': applications
	});	
	appchooserview.render();
};

var Portal = function (deps, containers) {
	this.active = null;

	function application_activated(app) {
		if (this.active) {
			$(this.active.el).slideToggle(200, function () {
				$(app.el).slideToggle(200);
			});
		} else {
			$(app.el).slideToggle(200);
		}

		this.active = app;
	};
	var handle_application_activated = _.bind(application_activated, this);

	this.applications = new Array;
	this.app_models = new Applications;

	_.each(deps.applications, function (app) {
		var application = new app.manager({model: app.model});
		application.bind('activated', handle_application_activated);
		application.render();
		$('#main').append(application.el);

		this.applications.push(application);
		this.app_models.add(application.model);	
	}, this);

	this.appchooser = new deps.AppChooser({
		'el': '#app_chooser_buttons',
		'applications': this.app_models
	});
	this.appchooser.render();
	this.appchooser.bind('portal:app_selected', function (app_model) {
		app_model.activate();
	});

	this.applications[0].model.activate();

	function handle_resize() {
		var viewable_height = $(window).height() - $('#topbar').height() - 1;
		$('#leftbar').height($(window).height());
	}
	$(window).resize(handle_resize);
	handle_resize();

	return this;
};

(function () {
	current_user = new UserModel();
	current_user.fetch({
		'success': function () {
			var deps = {
				'applications': {
					'HomeManager': {
						'manager': HomeManagerApp,
						'model': new ApplicationModel({
							'name': 'Home',
							'icon': '/static/imgs/home.png'
						})
					},
					'GearManager': {
						'manager': GearManagerApp,
						'model': new ApplicationModel({
							'name': 'Gear Manager',
							'icon': '/static/img/icons/gear64.png'
						})
					},
					'TripOrganizer': {
						'manager': TripOrganizerApp,
						'model': new ApplicationModel({
							'name': 'Trip Organizer',
							'icon': '/static/img/icons/trips64.png'
						})
					}
				},
				'AppChooser': AppChooserView
			};

			var portal = new Portal(deps);
		},
		'error': function (model, response) {
			urlparts = window.location.href.split('app');
			window.location.href = urlparts[0];
		}
	});
})();


