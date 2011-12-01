var TripModel = Backbone.Model.extend({
	initialize: function () {
		_.bindAll(this, 'url');
	},

	url: function () {
		var url = "/app/trips";
		if (this.id)
			return url + "/" + this.id;
		else
			return url;
	}
});

var TripCollection = Backbone.Collection.extend({
	model: TripModel,
	url: function () {
		return "/app/trips";
	},

	comparator: function (trip) {
		return trip.get('name');
	}
});

var TripListItemView = Backbone.View.extend({
	tagName: 'li',

	initialize: function () {
		_.bindAll(this, 'render');

		var template_string = '';
		template_string += '<div class="list_item_column trip_name"><%= name %></div>';
		template_string += '<div class="list_item_column trip_dates"><%= start %> - <%= end %></div>';
		template_string += '<div class="list_item_column trip_destination"><%= destination %></div>';
		this.template = _.template(template_string);
	},

	render: function () {
		$(this.el).html(this.template(this.model.toJSON()));
	}
});

var TripListView = Backbone.View.extend({
	id: 'trip_list_view',
	className: 'list_view', 

	initialize: function () {
		_.bindAll(this, 'render');

		this.models = this.options.models;
		this.models.bind('add', this.render, this);
		this.models.bind('remove', this.render, this);

		var list_header_string = '';
		list_header_string += '<li class="list_header">';
		list_header_string += '<div class="list_item_column trip_name">Trip</div>';
		list_header_string += '<div class="list_item_column trip_dates">When</div>';
		list_header_string += '<div class="list_item_column trip_destination">Where</div>';
		list_header_string += '</li>';

		this.list_el = $('<ul />')[0];
		$(this.list_el).html(list_header_string);
		$(this.el).append(this.list_el);
	},
	
	render: function () {
		var row_class = 'oddrow';
		this.models.each(function (trip_model) {
			var list_entry = new TripListItemView({
				'model': trip_model,
				'className': row_class
			});
			list_entry.render();
			$(this.list_el).append(list_entry.el);

			row_class = row_class == 'oddrow' ? 'evenrow' : 'oddrow';
		}, this);
	}
});

var TripAddForm = Backbone.View.extend({
	'id': 'trip_add_form',

	initialize: function () {
		_.bindAll(this, 'render', 'open', 'cancel', 'start_trip', 'handle_model_saved_success');

		$('body').append(this.el);

		var form_html = '';
		form_html += '<div class="form_row">';
		form_html += '<label for="trip_name">Trip</label> ';
		form_html += '<input type="text" id="trip_name" name="trip_name" />';
		form_html += '</div>';
		form_html += '<div class="form_row">';
		form_html += '<label for="trip_date_start">Dates</label> ';
		form_html += '<input type="text" id="trip_date_start" name="trip_start_date" class="date_start"/>';
		form_html += ' - <input type="text" id="trip_date_end" name="trip_end_date" class="date_end" />';
		form_html += '</div>';
		form_html += '<div class="form_row">';
		form_html += '<label for="trip_destination">Destination</label> ';
		form_html += '<input type="text" id="trip_destination" name="trip_destination"/>';
		form_html += '</div>';
		$(this.el).html(form_html);

		$("#trip_date_end").datepicker({
			defaultDate: "+1w",
			changeMonth: true,
			showButtonPanel: true,
			buttonImageOnly: true,
			buttonImage: '/static/img/icons/fugue/calendar.png',
			showOn: 'both',
			onSelect: function (selectedDate) {
				var instance = $( this ).data( "datepicker" );
				var date = $.datepicker.parseDate(
							instance.settings.dateFormat || $.datepicker._defaults.dateFormat,
							selectedDate, 
							instance.settings 
					);
				$('#trip_date_start').datepicker( "option", 'maxDate', date );
				$('.trip_end_date').html(selectedDate);
			}
		});

		$("#trip_date_start").datepicker({
			defaultDate: "+1w",
			changeMonth: true,
			showButtonPanel: true,
			buttonImageOnly: true,
			buttonImage: '/static/img/icons/fugue/calendar.png',
			showOn: 'both',
			onSelect: function (selectedDate) {
				var instance = $( this ).data( "datepicker" );
				var date = $.datepicker.parseDate(
							instance.settings.dateFormat || $.datepicker._defaults.dateFormat,
							selectedDate, 
							instance.settings 
					);
				$('#trip_date_end').datepicker( "option", 'minDate', date );
				$('.trip_start_date').html(selectedDate);
			}
		});

		var view = this;
		$(this.el).dialog({
			autoOpen: false,
			modal: true,
			zIndex: 9000,
			title: 'Start Trip',
			resizable: false,
			width: 500,
			buttons: {
				'Start': view.start_trip,
				'Cancel': view.cancel
			}
		});
	},

	open: function (trip) {
		this.model = trip;
		this.render();
		$(this.el).dialog('open');
	},

	cancel: function () {
		$(this.el).dialog('close');
		this.trigger('cancel');
	},

	start_trip: function () {
		var this_obj = this;
		var attributes = {
			'name': this.$('#trip_name').val(),
			'start': this.$('#trip_date_start').val(),
			'end': this.$('#trip_date_end').val(),
			'destination': this.$('#trip_destination').val()
		};

		this.model.save(attributes, {
			'success': this.handle_model_saved_success 
		});
		$(this.el).dialog('close');
	},

	handle_model_saved_success: function (model, response) {
		this.trigger('save', model);
	}
});

var TripOrganizerApp = Backbone.View.extend({
	className: 'application_container',
	'id': 'trip_organizer',

	events: {
		"click button[title='Add Trip']": "handle_add_trip_start"
	},

	initialize: function () {
		_.bindAll(this, 'render', 'handle_activate', 'handle_add_trip_start',
			'handle_trip_save');
		$(this.el).hide();
		var template_string = '<h1>Trip Organizer</h1>';
		template_string += '<button title="Add Trip"> Add Trip </button>';
		this.template = _.template(template_string);
		this.model.bind('activating', this.handle_activate);

		this.trips = new TripCollection();

		this.listview = new TripListView({
			'models': this.trips
		});

		this.addform = new TripAddForm();
		this.addform.bind('save', this.handle_trip_save)
	},

	refresh_trips: function () {
		var listview = this.listview;
		this.trips.fetch({'success': function () {
				listview.render();
			}
		});
	},

	render: function () {
		$(this.el).html(this.template({}));
		$(this.el).append(this.listview.el);
		this.$("button").button();
		this.listview.render();	
		return this;
	},

	handle_activate: function () {
		this.refresh_trips();
		this.trigger('activated', this);
	},

	handle_add_trip_start: function () {
		new_trip = new TripModel();
		this.addform.open(new_trip);
	},

	handle_trip_save: function (trip) {
		this.trips.add([trip]);
	}
});

