var TripModel = Backbone.Model.extend({
	defaults: {
		'name': '',
		'start': '',
		'end': '',
		'destination': '',
		'description': ''
	},

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
		return trip.get('name').toLowerCase();
	}
});

var TripConfirmDeleteDialog = Backbone.View.extend({
	id: 'trip_confirm_delete',

	initialize: function () {
		_.bindAll(this, 'delete_trip', 'cancel', 'render', 'open', 'close');
		this.template = _.template('Are you sure you want to delete the <%= name %> trip?');
		$(this.el).hide();
		$('body').append(this.el);
		var view = this;
		$(this.el).dialog({
			autoOpen: false,
			modal: true,
			zIndex: 9000,
			title: 'Delete Trip?',
			resizable: false,
			width: 500,
			buttons: {
				'Delete!': view.delete_trip,
				'Cancel': view.cancel
			}
		});
	},

	delete_trip: function () {
		this.model.destroy();
		this.close();
	},

	close: function () {
		this.model = null;
		$(this.el).dialog('close');
	},

	cancel: function () {
		this.close();
	},

	render: function () {
		$(this.el).html(this.template(this.model.toJSON()));
	},

	open: function (model) {
		this.model = model;
		this.render();
		$(this.el).dialog('open');
	}
});
var deletetripdialog = new TripConfirmDeleteDialog();

var TripListItemView = Backbone.View.extend({
	tagName: 'li',

	events: {
		'click .list_item_controls img[alt="Delete"]': 'handle_delete_clicked',
		'click': 'handle_click'
	},

	initialize: function () {
		_.bindAll(this, 'render', 'handle_delete_clicked', 'handle_click');

		var template_string = '';
		template_string += '<div class="list_item_column trip_name"><%= name %></div>';
		template_string += '<div class="list_item_column trip_dates"><%= start %> - <%= end %></div>';
		template_string += '<div class="list_item_column trip_destination"><%= destination %></div>';
		template_string += '<div class="list_item_controls"><img src="/static/img/icons/fugue/slash.png" alt="Delete" /></div>';
		this.template = _.template(template_string);
	},

	render: function () {
		$(this.el).html(this.template(this.model.toJSON()));
		$(this.el).hover(function () { $(this).toggleClass('highlight'); });
		this.$('.list_item_controls img[alt="Delete"]').button();
	},

	handle_delete_clicked: function (ev) {
		ev.stopPropagation();
		deletetripdialog.open(this.model);
	},

	handle_click: function () {
		this.trigger('view_trip', this.model);
	}
});

var TripListView = Backbone.View.extend({
	id: 'trip_list_view',
	className: 'list_view', 

	initialize: function () {
		_.bindAll(this, 'render', 'handle_list_item_events');

		this.models = this.options.models;
		this.models.bind('add', this.render, this);
		this.models.bind('remove', this.render, this);

		this.listitemviews = new Array;

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
		_.each(this.listitemviews, function (item) {
			item.remove();
			delete item;
		});
		this.models.each(function (trip_model) {
			var list_entry = new TripListItemView({
				'model': trip_model,
				'className': row_class
			});
			list_entry.render();
			list_entry.bind('all', this.handle_list_item_events);
			$(this.list_el).append(list_entry.el);
			this.listitemviews.push(list_entry);

			row_class = row_class == 'oddrow' ? 'evenrow' : 'oddrow';
		}, this);
	},

	handle_list_item_events: function (eventname, trip) {
		this.trigger(eventname, trip);
	}
});

var TripAddForm = Backbone.View.extend({
	'id': 'trip_add_form',

	initialize: function () {
		_.bindAll(this, 'render', 'open', 'cancel', 'start_trip', 'handle_model_saved_success');

		$('body').append(this.el);
	},

	render: function () {
		var form_html = '';
		form_html += '<div class="form_row">';
		form_html += '<label for="trip_name">Trip</label> ';
		form_html += '<input type="text" id="trip_name" name="trip_name" value="<%= name %>"/>';
		form_html += '</div>';
		form_html += '<div class="form_row">';
		form_html += '<label for="trip_date_start">Dates</label> ';
		form_html += '<input type="text" id="trip_date_start" name="trip_start_date" class="date_start" value="<%= start %>"/>';
		form_html += ' - <input type="text" id="trip_date_end" name="trip_end_date" class="date_end"  value="<%= end %>" />';
		form_html += '</div>';
		form_html += '<div class="form_row">';
		form_html += '<label for="trip_destination">Destination</label> ';
		form_html += '<input type="text" id="trip_destination" name="trip_destination" value="<%= destination %>"/>';
		form_html += '</div>';

		var template = _.template(form_html);
		$(this.el).html(template(this.model.toJSON()));

		$("#trip_date_end").datepicker({
			defaultDate: "+1w",
			changeMonth: true,
			dateFormat: 'yy-mm-dd',
			changeYear: true,
			yearRange: 'c-2:+3',
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
			changeYear: true,
			yearRange: 'c-2:+3',
			dateFormat: 'yy-mm-dd',
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

var FieldEditor = Backbone.View.extend({
	
	initialize: function () {
		_.bindAll(this, 'render', 'highlight_on_hover', 'edit_on_click', 'save_on_blur');
		this.input = this.$(this.options.input_selector);
		this.label = this.$(this.options.label_selector);
		this.field = this.options.field;

		this.input.hide();
		this.label.hover(this.highlight_on_hover);
		this.label.click(this.edit_on_click);
		this.input.blur(this.save_on_blur);
	},

	highlight_on_hover: function () {
		this.label.toggleClass('highlight');
	},

	edit_on_click: function () {
		this.label.hide();
		this.input.val(this.label.html());
		this.input.show();
		this.input.focus();
		this.input.select();
	},

	save_on_blur: function () {
		this.input.hide()
		this.label.html(this.input.val());
		this.label.show();

		var update = new Object;
		update[this.field] = this.input.val();
		this.model.save(update);
	},

	render: function () {
		var field_value = this.model.get(this.field);
		if (field_value == '' && this.options.default_value)
			field_value = this.options.default_value
		this.label.html(field_value);
	}
});

var DateRangeEditor = Backbone.View.extend({
	initialize: function () {
		_.bindAll(this, 'render', 'start_hover', 'end_hover',
			'set_min_date', 'set_max_date', 'open_start_picker', 'open_end_picker',
			'on_select_date_start', 'on_select_date_end');
		this.start_label = this.$(this.options.start_date_label);
		this.start = this.$(this.options.start_input);
		this.end_label = this.$(this.options.end_date_label);
		this.end = this.$(this.options.end_input);
		
		var on_select_start_date = this.on_select_date_start;
		this.start.datepicker({
			defaultDate: "+1w",
			dateFormat: 'yy-mm-dd',
			changeMonth: true,
			changeYear: true,
			yearRange: 'c-2:+3',
			showButtonPanel: true,
			buttonImageOnly: true,
			buttonImage: '/static/img/icons/fugue/calendar.png',
			showOn: 'both',
			onSelect: on_select_start_date
		});
		this.start_label.hover(this.start_hover);
		this.start_label.click(this.open_start_picker);

		var on_select_end_date = this.on_select_date_end;
		this.end.datepicker({
			defaultDate: "+1w",
			dateFormat: 'yy-mm-dd',
			changeMonth: true,
			changeYear: true,
			yearRange: 'c-2:+3',
			showButtonPanel: true,
			buttonImageOnly: true,
			buttonImage: '/static/img/icons/fugue/calendar.png',
			showOn: 'both',
			onSelect: on_select_end_date
		});
		this.end_label.hover(this.end_hover);
		this.end_label.click(this.open_end_picker);

	},

	set_min_date: function (selected_date) {
		var instance = this.start.data( "datepicker" );
		var date = $.datepicker.parseDate(
					instance.settings.dateFormat || $.datepicker._defaults.dateFormat,
					selected_date,
					instance.settings 
			);
		this.end.datepicker( "option", 'minDate', date );
	},

	set_max_date: function (selected_date) {
		var instance = this.end.data( "datepicker" );
		var date = $.datepicker.parseDate(
					instance.settings.dateFormat || $.datepicker._defaults.dateFormat,
					selected_date,
					instance.settings 
			);
		this.start.datepicker( "option", 'maxDate', date );
	},

	start_hover: function () {
		this.start_label.toggleClass('highlight');
	},

	end_hover: function () {
		this.end_label.toggleClass('highlight');
	},

	open_start_picker: function () {
		this.start.datepicker('show');
	},

	open_end_picker: function () {
		this.end.datepicker('show');
	},

	on_select_date_start: function (selected_date) {
		this.set_min_date(selected_date);
		this.model.save({'start': this.start.val()});
	},

	on_select_date_end: function (selected_date) {
		this.set_max_date(selected_date);
		this.model.save({'end': this.end.val()});
	},

	render: function () {
		this.start_label.html(this.model.get('start'));
		this.start.datepicker('setDate', this.model.get('start'));
		this.set_min_date(this.model.get('start'));

		this.end_label.html(this.model.get('end'));
		this.end.datepicker('setDate', this.model.get('end'));
		this.set_max_date(this.model.get('end'));
	},

	set_model: function (model) {
		if (this.model)
			this.model.unbind('change', this.render);

		this.model = model;
		this.model.bind('change', this.render);
	},

});

var TripDetailView = Backbone.View.extend({
	className: 'application_container',

	initialize: function () {
		_.bindAll(this, 'receive_template', 'set_model', 'render', 'show', 'reset_map');

		var receive_template = this.receive_template;
		$.ajax({
			url: '/static/trip_detail_view_template.html',
			success: receive_template
		});

	},

	finish_init: function() {
		var this_element = this.el;
		var this_model = this.model;
		$(this.el).html(this.template());

		this.views = new Object;
		var views = {
			'name': {
				input_selector: 'input.trip_title',
				label_selector: 'h1',
				field: 'name'
			},
			'description': {
				input_selector: 'textarea.trip_description',
				label_selector: 'p.trip_description',
				field: 'description',
				default_value: 'Enter a description...'
			},
			'destination': {
				input_selector: 'input[name="trip_destination"]',
				label_selector: 'div.route_overview_section h4',
				field: 'destination',
			},
		};
		_.each(views, function(view) {
			view.el = this.el;
			view.model = this.model;
			this.views[view.field] = new FieldEditor(view);
		}, this);

		date_range_options = {
			start_date_label: 'div.trip_dates span.trip_start_date',
			start_input: 'div.trip_dates input[name="trip_start_date"]',
			end_date_label: 'div.trip_dates span.trip_end_date',
			end_input: 'div.trip_dates input[name="trip_end_date"]',
			el: this.el,
			model: this.model
		}
		this.views.date_range = new DateRangeEditor(date_range_options);

		$('#trip_organizer_tabs').tabs({
			fx: {
				opacity: 'toggle',
				duration: 125
			}
		});

		this.create_maps();
	},

	create_maps: function () {
		var latlng = new google.maps.LatLng(33.224795, -108.25165);
		var myOptions = {
		  zoom: 12,
		  center: latlng,
		  mapTypeId: google.maps.MapTypeId.SATELLITE
		};
		this.map = new google.maps.Map($("#route_map")[0], myOptions);
	},

	reset_map: function () {
		google.maps.event.trigger(this.map, 'resize');
	},

	render: function () {
		_.each(this.views, function (view) {
			view.render();
		});
	},

	receive_template: function (data) {
		this.template = _.template(data);
		this.finish_init();
	},

	set_model: function (model) {
		this.model = model;
		_.each(this.views, function (view) {
			if (view.set_model)
				view.set_model(model);
			else
				view.model = model;
		});
		this.render();
	},

	show: function () {
		$(this.el).fadeIn(125, this.reset_map);
	},

	hide: function () {
		$(this.el).hide();
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
			'handle_trip_save', 'view_trip');
		$(this.el).hide();
		var template_string = '<div class="trip_list_container"><h1>Trip Organizer</h1>';
		template_string += '<button title="Add Trip"> Add Trip </button></div>';
		this.template = _.template(template_string);
		this.model.bind('activating', this.handle_activate);

		this.trips = new TripCollection();

		this.detailview = new TripDetailView;
		this.detailview.hide();

		this.listview = new TripListView({
			'models': this.trips
		});
		this.listview.bind('view_trip', this.view_trip);

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
		this.$('div.trip_list_container').append(this.listview.el);
		$(this.el).append(this.detailview.el);
		this.$("button").button();
		this.listview.render();	

		return this;
	},

	handle_activate: function () {
		this.refresh_trips();
		this.detailview.hide();
		this.$('div.trip_list_container').show();
		this.trigger('activated', this);
	},

	handle_add_trip_start: function () {
		new_trip = new TripModel();
		this.addform.open(new_trip);
	},

	handle_trip_save: function (trip) {
		this.trips.add([trip]);
	},

	view_trip: function (trip) {
		this.detailview.set_model(trip);	
		var detailview = this.detailview;
		this.$('div.trip_list_container').fadeOut(125, detailview.show);
	}
});

