(function () {
	var b = {};

	b.WelcomeScreen = BackcountryTracks.MainScreen.extend({
		id: 'welcome_screen',

		events: {
			'click #welcome_step2': 'step2'
		},

		initialize: function () {
			_.bindAll(this, 'render', 'bubble_events');
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

		step2: function () {
			var trip_organizer;
			_.each(BackcountryTracks.modules.modules, function (item) {
				if (item[0].name == 'Trip Organizer')
					trip_organizer = item[0];
			});

			if (!trip_organizer)
				return;

			Backbone.history.navigate('trips');
			trip_organizer.list();
			trip_organizer.new_trip();
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

