(function () {
	var b = {};

	b.WelcomeScreen = BackcountryTracks.MainScreen.extend({
		id: 'welcome_screen',

		events: {
			'click #welcome_step1': 'step1',
			'click #welcome_step2': 'step2',
			'click #welcome_step3': 'step2'
		},

		initialize: function () {
			_.bindAll(this, 'render', 'bubble_events', 'step1', 'step2');
			var template_string = $('#welcome_screen_template').html();
			this.template = _.template(template_string);
		},

		render: function () {
			$(this.el).html(this.template({}));

			return this;
		},

		bubble_events: function (eventname, argument) {
			this.trigger(eventname, argument);
		},

		_get_trip_orgainzer: function () {
			var trip_organizer;
			_.each(BackcountryTracks.modules.modules, function (item) {
				if (item.name == 'Trip Organizer')
					trip_organizer = item;
			});

			return trip_organizer;
		},

		step1: function () {
			var organizer = this._get_trip_orgainzer();
			if (!organizer)
				return;
			
			this.step2();
			organizer.new_trip();
		},

		step2: function () {
			Backbone.history.navigate('trips');

			var organizer = this._get_trip_orgainzer();
			if (!organizer)
				return;

			organizer.list();
		}
	});

	b.BasecampModule = BackcountryTracks.Module.extend({
		name: 'Basecamp',

		routes: {
			'': 'view'
		},
		
		initialize: function () {
			_.bindAll(this, 'view');

			this.sidebar = new BackcountryTracks.SidebarItem({
				name: 'basecamp',
				icon: 'basecamp',
				path: ''
			});

			this.view = new b.WelcomeScreen();
		},

		view: function(id) {
			BackcountryTracks.screens.activate(this.view);
		},
	});


	this.Basecamp = b;
}).call(this);

