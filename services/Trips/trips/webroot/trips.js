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

	edit_on_click: function (evt, eh) {
		if (evt.target.tagName == 'A') {
			window.open(evt.target.href, '_blank');
			evt.stopPropagation();
			return false;
		}

		this.label.hide();
		this.input.val(this.model.get(this.field));
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
		this.render();
	},

	render: function () {
		var field_value = this.model.get(this.field);
		if (field_value == '' && this.options.default_value)
			field_value = this.options.default_value;

		var urlreg = /((http:\/\/)|(www\.))([^ \n]+)/igm;
		var urls = field_value.match(urlreg, '<a href="http://$4$5" target="_blank">$1</a>');
		for(url_index in urls) {
			var url = urls[url_index];
			if (url.indexOf('http://') > -1)
				field_value = field_value.replace(url, '<a href="' + url + '">' + url + '</a>');
			else
				field_value = field_value.replace(url, '<a href="http://' + url + '">' + url + '</a>');
		}
		this.label.html(field_value.replace('\n', '\n<br />'));
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
			buttonImage: '/static/img/calendar_icon.png',
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
			buttonImage: '/static/img/calendar_icon.png',
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

(function() {
	var t = {};

	TripGearViews.call(t);

	t.TripFriend = Backbone.Model.extend({
		defaults: {
			email: '',
			first: '',
			last: '',
			invite_status: 'invited'
		},

		accept: function () {
			this.save({'invite_status': 'accepted'});
		},

		ignore: function () {
			this.save({'invite_status': 'not coming'});
		}
	});

	t.TripFriends = Backbone.Collection.extend({
		model: t.TripFriend,

		initialize: function (models, options) {
			if (options) this.trip_id = options.trip_id;
		},

		url: function () {
			return "/app/trips/" + this.trip_id + "/friends";
		},

		invite: function (invitees) {
			var email_addy = /[-a-z0-9~!$%^&*_=+}{\'?]+(\.[-a-z0-9~!$%^&*_=+}{\'?]+)*@([a-z0-9_][-a-z0-9_]*(\.[-a-z0-9_]+)*\.(aero|arpa|biz|com|coop|edu|gov|info|int|mil|museum|name|net|org|pro|travel|mobi|[a-z][a-z])|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,5})?/gi;
			var people = $.trim(invitees).replace('\r\n', '\n').replace('\r', '\n').split('\n');
			_.each(people, function (person) {
				var email = person.match(email_addy);
				var name = person.replace(email_addy, '');
				name = $.trim(name);
				name = name.split(/ +/, 2);

				this.create({
					email: email[0],
					first: name[0],
					last: name[1] || ''
				});
			}, this);
		},

		accept_invite: function (email) {
			var friend = this.get(email);
			friend.accept();
		},

		ignore_invite: function (email) {
			var friend = this.get(email);
			friend.ignore();
		}
	});

	t.Comment = Backbone.Model.extend({
		defaults: {
			'owner': '',
			'date': '',
			'comment': '',
			'first_name': '',
			'last_name': ''
		},

		local_date: function () {
			var local_date = new Date(this.get('date'));
			
			return local_date.toLocaleDateString();
		},

		local_time: function () {
			var local_date = new Date(this.get('date'));
			return local_date.toLocaleTimeString();
		}
	});

	t.Comments = Backbone.Collection.extend({
		model: t.Comment,

		ordering: -1,

		initialize: function () {
			_.bindAll(this, 'comparator', 'url', 'reverse_sort', 'forward_sort');
		},

		url: function () {
			return "/app/trips/" + this.trip_id + "/comments";
		},

		comparator: function (item) {
			var date = new Date(item.get('date'));
			return this.ordering * date.getTime();
		},

		reverse_sort: function () {
			this.ordering = -1;
			this.sort();
		},

		forward_sort: function () {
			this.ordering = 1;
			this.sort();
		}
	});

	t.Trip = Backbone.Model.extend({
		defaults: {
			'name': '',
			'start': '',
			'end': '',
			'destination': '',
			'description': '',
			'route_description': '',
			'trip_distance': '',
			'elevation_gain': '',
			'difficulty': '',
			'itinerary': '',
			'friends': null,
			'organizer': true,
			'responded': false
		},

		initialize: function () {
			_.bindAll(this, 'url', 'update_friends_collection',
				'update_friends_attribute', 'calculate_responded');

			if (this.get('friends') == null) {
				this.attributes.friends = new Array;
			}

			this.friends = new t.TripFriends(this.attributes.friends, {trip_id: this.id});
			this.friends.bind('change', this.update_friends_attribute);

			this.gear = new t.PersonalGear;
			this.inventory = new t.InventoryGear;
			this.calculate_responded();
		},

		calculate_responded: function () {
			var $this = this;
			this.friends.each(function (friend) {
				if (friend.get('email') == BackcountryTracks.current_user.get('email')) {
					$this.set({'organizer': false});

					if (friend.get('invite_status') == 'accepted' || friend.get('invite_status') == 'rejected') {
						$this.set({'responded': true});
					}
				} 
			});

		},

		url: function () {
			var url = "/app/trips";
			if (this.id) {
				return url + "/" + this.id;
			} else {
				return url;
			}
		},

		update_friends_collection: function () {
			var friends = this.get('friends');
			this.friends.reset(friends);
		},

		update_friends_attribute: function () {
			var friends = this.friends.toJSON();
			this.set({'friends': friends});
			this.calculate_responded();
		},

		accept_invite: function (email) {
			this.friends.accept_invite(email);
		},

		ignore_invite: function (email) {
			this.friends.ignore_invite(email);
			this.collection.remove(this); // FIXME: err, should the model really be accessing the collection?
		}
	});

	t.Trips = Backbone.Collection.extend({
		model: t.Trip,
		url: function () {
			return "/app/trips";
		},

		comparator: function (trip) {
			return trip.get('name').toLowerCase();
		}
	});
	
	t.AddForm = Backbone.View.extend({
		'id': 'trip_add_form',

		initialize: function () {
			_.bindAll(this, 'render', 'open', 'cancel', 'start_trip', 'handle_model_saved_success');

			$('body').append(this.el);
		},

		render: function () {
			var form_html = '';
			form_html += '<div class="form_row">';
			form_html += '<label for="trip_name">Trip</label> ';
			form_html += '<input type="text" id="trip_name" name="trip_name" value="{{ name }}"/>';
			form_html += '</div>';
			form_html += '<div class="form_row">';
			form_html += '<label for="trip_date_start">Dates</label> ';
			form_html += '<input type="text" id="trip_date_start" name="trip_start_date" class="date_start" value="{{ start }}"/>';
			form_html += ' - <input type="text" id="trip_date_end" name="trip_end_date" class="date_end"  value="{{ end }}" />';
			form_html += '</div>';
			form_html += '<div class="form_row">';
			form_html += '<label for="trip_destination">Destination</label> ';
			form_html += '<input type="text" id="trip_destination" name="trip_destination" value="{{ destination }}"/>';
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
				buttonImage: '/static/img/calendar_icon.png',
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
				buttonImage: '/static/img/calendar_icon.png',
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

	t.TripFriendsInviteView = Backbone.View.extend({

		initialize: function () {
			_.bindAll(this, 'invite_people');

			$(this.el).html($('#friends_invite_template').html());

			$(this.el).dialog({
				autoOpen: false,
				modal: true,
				zIndex: 9010,
				title: 'Invite friends',
				resizable: false,
				width: 500,
				buttons: {
					'Invite': this.invite_people,
					'Cancel': function () { $(this).dialog('close'); },	
				}
			});
		},

		open: function () {
			this.$('textarea[name="invitees"]').val('');
			$(this.el).dialog('open');
		},

		invite_people: function () {
			var invitee_text = this.$('textarea[name="invitees"]').val();
			this.trigger('invited', invitee_text);
			$(this.el).dialog('close');
		}
	});

	t.FriendsListItem = Backbone.View.extend({
		tagName: 'li',
		
		initialize: function () {
			_.bindAll(this, 'render');

			this.template = _.template($('#friends_list_view_item_template').html());
		},

		render: function () {
			$(this.el).html(this.template(this.model.toJSON()));	
		}
	});

	t.FriendsListView = Backbone.View.extend({
		
		initialize: function () {
			_.bindAll(this, 'render');

			this.collection.bind('all', this.render);
		},

		render: function () {
			$(this.el).html('');
			this.collection.each(function (trip_friend) {
				var list_item = new t.FriendsListItem({model: trip_friend});
				$(this.el).append(list_item.el);
				list_item.render();
			}, this);
		}
	});

	t.TripRouteMap = Backbone.View.extend({
		className: 'route_overview_section',

		initialize: function () {
			_.bindAll(this, 'reset_map', 'render', 'create_maps', 'remove_map_overlays',
					'set_model', 'reset_filedrop');

			this.drophere_template = _.template($('#gear_organizer_filedrop_template').html());

			this.create_maps();
			this.reset_filedrop();
		},

		render: function () {

		},

		create_maps: function () {
			var latlng = new google.maps.LatLng(33.224795, -108.25165);
			var myOptions = {
			  center: latlng,
			  mapTypeId: google.maps.MapTypeId.TERRAIN,
			  scaleControl: true
			};
			this.map = new google.maps.Map(this.$("#route_map")[0], myOptions);
		},

		reset_map: function () {
			try {
				google.maps.event.trigger(this.map, 'resize');
				this.kml = new google.maps.KmlLayer('http://' + window.location.hostname + '/app/trips/' + this.model.id + '/map/route?dummy=' + (new Date()).getTime());
				this.kml.setMap(this.map);
			} catch (err) {
				// yeah, do nothing, that's the way to handle it
			};
		},

		remove_map_overlays: function () {
			if (!this.kml)
				return;

			this.kml.setMap(null);
			this.kml = null;
		},

		reset_filedrop: function () {
			if (!this.model) return;

			var $this = this;
			$('#drophere').remove();
			$('#route_map_block > div').prepend(this.drophere_template());
			$('#drophere').filedrop({
				fallback_id: 'upload_button',
				url: '/app/trips/' + $this.model.id + '/map/route',
				paramname: 'userfile',
				afterAll: function () {
					$this.reset_map();	
				},
				error: function (err, file) {
					switch(err) {
						case 'FileTooLarge':
							alert('The file you are trying to upload is to large. Please limit your route files to 2 MB');
							break;
					}
				},
				maxfilesize: 2,
				docOver: function () {
					if ($('#drophere').hasClass('highlight'))
						return;

					$('#drophere').addClass('highlight');
				},

				docLeave: function () {
					$('#drophere').removeClass('highlight');
				}
			});

			$('#drophere button').button();
			$('#drophere button').click(function (evt) {
				evt.stopPropagation();	
				$('#upload_button').click();
			});

		},

		set_model: function (model) {
			this.model = model;
			this.remove_map_overlays();
			this.reset_filedrop();
			this.render();
		}
	});

	t.TripDetailFriendsView = Backbone.View.extend({
		className: 'friends_section',

		initialize: function () {
			_.bindAll(this, 'invite_friends_to_trip', 'render', 'invite_people', 'set_model');
			this.$('button').button();

			this.invitedialog = new t.TripFriendsInviteView({});
			$('body').append(this.invitedialog);
			this.$('button').click(this.invite_friends_to_trip);

			this.invitedialog.bind('invited', this.invite_people);

			this.friendlist = new t.FriendsListView({
				collection: this.collection,
				el: this.$('.friends_list')[0]
			});
		},

		invite_friends_to_trip: function () {
			this.invitedialog.open();
		},

		render: function () {
			this.friendlist.render();
		},

		invite_people: function(invitees) {
			this.collection.invite(invitees);
		},

		set_model: function (model) {
			this.model = model
			this.collection.trip_id = model.id;
			this.collection.reset(this.model.get('friends'));
		}
	});

	t.CommentListView = Backbone.View.extend({
		className: 'trip_discussion',

		events: {
			'click .discussion_controls button': 'post_comment',
			'click a.posted': 'sort_order_posted',
			'click a.recent': 'sort_recent_first'
		},

		initialize: function () {
			_.bindAll(this, 'post_comment', 'render', 'render_comment',
				'sort_order_posted', 'sort_recent_first');

			this.template = _.template($('#trip_discussion_comment_template').html());
			this.collection.bind('add', this.render, this);
			this.collection.bind('remove', this.render, this);
			this.collection.bind('reset', this.render, this);
			this.$('button').button();

			this.row_class = '';
		},

		post_comment: function () {
			var comment = this.$('textarea').val();
			this.collection.create({
				'comment': comment
			});
			this.$('textarea').val('');
		},

		sort_order_posted: function (ev) {
			this.collection.forward_sort();
			ev.stopPropagation();
			return false;
		},

		sort_recent_first: function (ev) {
			this.collection.reverse_sort();
			ev.stopPropagation();
			return false;
		},

		render: function () {
			this.$('.trip_comments').html('');
			this.collection.each(this.render_comment);

			this.$('.trip_comments time').each(function (item) {
				var commentdate = $(this).attr('datetime');
				var prettydate = prettyDate(commentdate);
				if (prettydate == undefined) {
					var prettydate = (new Date(commentdate)).toLocaleDateString() + " " + (new Date(commentdate)).toLocaleTimeString();
				}
				$(this).html(prettydate);
			});

			return this;	
		},

		render_comment: function (comment) {
			var local_date = comment.local_date();
			var local_time = comment.local_time();

			var rendered_comment = comment.toJSON();
			rendered_comment['date'] = local_date;
			rendered_comment['time'] = local_time;
			rendered_comment['datetime'] = comment.get('date');

			var urlreg = /(((http:\/\/)|(www\.))([^ ]+))/gmi;
			rendered_comment['comment'] = rendered_comment['comment'].replace(urlreg, '<a href="http://$4$5" target="_blank">$1</a>');

			var html_comment = this.template(rendered_comment);
			this.$('.trip_comments').append(html_comment);

			this.row_class = this.row_class == '' ? 'odd' : '';
		},

		set_model: function (model) {
			this.model = model
			this.collection.trip_id = model.id;
		}
	});

	t.TripDetail = BackcountryTracks.MainScreen.extend({

		initialize: function () {
			this.rendered_once = false;
			_.bindAll(this, 'set_model', 'render', 'show', 'reset_view');
			this.kml = null;

			this.model = new t.Trip;

			this.template = _.template($('#trips_detail_template').html());

			$(this.el).html(this.template());

			this.views = new Object;
			var views = {
				'name': {
					input_selector: 'input.trip_title',
					label_selector: 'h1.component_title',
					field: 'name'
				},
				'description': {
					input_selector: 'textarea.trip_description',
					label_selector: 'div.trip_description',
					field: 'description',
					default_value: 'Enter a description...'
				},
				'destination': {
					input_selector: 'input[name="trip_destination"]',
					label_selector: 'div.route_overview_section h4',
					field: 'destination'
				},
				'trip_distance': {
					input_selector: 'input[name="trip_distance"]',
					label_selector: '#trip_distance',
					field: 'trip_distance',
					default_value: 'Enter a distance...'
				},
				'elevation_gain': {
					input_selector: 'input[name="elevation_gain"]',
					label_selector: '#trip_elevation_gain',
					field: 'elevation_gain',
					default_value: 'Enter an elevation gain/loss'
				},
				'difficulty': {
					input_selector: 'input[name="difficulty"]',
					label_selector: '#trip_difficulty',
					field: 'difficulty',
					default_value: 'Enter a difficulty...'
				},
				'route_description': {
					input_selector: 'textarea[name="route_description"]',
					label_selector: 'div.trip_route_description',
					field: 'route_description',
					default_value: 'Enter a description...'
				},
				'itinerary': {
					input_selector: 'textarea.trip_itinerary',
					label_selector: 'div.trip_itinerary_content',
					field: 'itinerary',
					default_value: 'Enter the itinerary...'
				}
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


			this.views.friends = new t.TripDetailFriendsView({
				el: this.$('.friends_section')[0],
				collection: new t.TripFriends()
			});

			this.views.gear = new t.TripGearView({
				el: this.$('#gear_tab')[0],
				personal: this.$('#trip_personal_gear')[0],
				inventory: this.$('#add_personal_gear')[0],
				group: this.$('#trip_group_gear')[0]
			});

			this.views.discussion = new t.CommentListView({
				collection: new t.Comments(),
				el: this.$('#trip_discussion')[0]
			});

			this.views.route = new t.TripRouteMap({
				el: this.$('#route_map_block')[0]
			});

			this.$('#trip_detail_view').tabs({
				show: this.reset_view,
				select: function (evnt, ui) {
					var position = $(ui.tab.parentNode).position();
					var width = $(ui.tab.parentNode).width();
					$('#trip_organizer_header_marker img').css({'left': (position.left + (width / 2) - 19)});
				}
			});
		},

		reset_view: function (evnt, ui) {
			if (ui.panel.id == 'route_tab') {
					this.views.route.reset_map();
			} else if (ui.panel.id == 'trip_discussion') {
				this.views.discussion.collection.fetch();
			}
		},

		remove_map_overlays: function () {
			if (!this.kml)
				return;

			this.kml.setMap(null);
			this.kml = null;
		},

		render: function () {
			this.$('#trip_detail_view').tabs('select', 0);

			_.each(this.views, function (view) {
				view.render();
			});
		},

		set_model: function (model) {
			this.model = model;
			_.each(this.views, function (view) {
				if (view.set_model)
					view.set_model(model);
				else
					view.model = model;
			});
			this.remove_map_overlays();
			this.render();
		},

		show: function () {
			$(this.el).fadeIn(125, this.reset_map);
		},

		hide: function () {
			$(this.el).hide();
		},

		select_tab: function (tab_id) {
			var tab_ids = new Array;
			this.$('#trip_detail_view > ul.ui-tabs-nav li a').each(function (index, item) {
				var parts = item.href.split('#');
				tab_ids.push(parts[1]);
			});

			var tab_index = tab_ids.indexOf(tab_id);
			this.$('#trip_detail_view').tabs('select', tab_index);
		}
	});

	t.TripListItemView = Backbone.View.extend({
		tagName: 'li',

		events: {
			'click .list_item_controls button[title="Delete"]': 'handle_delete_clicked',
			'click button[title="Accept"]': 'accept_invitation',
			'click button[title="Ignore"]': 'ignore_invitation',
			'click': 'handle_click'
		},

		initialize: function () {
			_.bindAll(this, 'render', 'handle_delete_clicked', 'handle_click');
			this.template = _.template($('#trip_list_item').html());
			this.model.bind('change', this.render);
		},

		render: function () {
			var $this = this;

			$(this.el).html(this.template(this.model.toJSON()));
			$(this.el).mouseenter(function () { $(this).addClass('highlight'); });
			$(this.el).mouseleave(function () { $(this).removeClass('highlight'); });
			this.$('.list_item_controls img[alt="Delete"]').button();
			this.$('.list_item_controls button').button();

			this.$('button[title="Ignore"]').hide();
			this.$('button[title="Accept"]').hide();

			if (!this.model.get('organizer') && !this.model.get('responded')) {
				$this.$('button[title="Ignore"]').show();
				$this.$('button[title="Accept"]').show();
			}
		},

		handle_delete_clicked: function (ev) {
			ev.stopPropagation();
			t.deletedialog.open(this.model);
		},

		handle_click: function () {
			this.trigger('view_trip', this.model);
		},

		accept_invitation: function (ev) {
			ev.stopPropagation();
			this.model.accept_invite(BackcountryTracks.current_user.get('email'));
		},

		ignore_invitation: function (ev) {
			ev.stopPropagation();
			this.model.ignore_invite(BackcountryTracks.current_user.get('email'));
		}
	});

	t.TripListView = Backbone.View.extend({
		id: 'trip_list_view',
		className: 'list_view', 
		tagName: 'section',

		initialize: function () {
			_.bindAll(this, 'render', 'handle_list_item_events');

			this.collection.bind('add', this.render, this);
			this.collection.bind('remove', this.render, this);
			this.collection.bind('reset', this.render, this);

			this.listitemviews = new Array;

			this.list_el = $('<ul />')[0];
			$(this.el).append(this.list_el);
		},
		
		render: function () {
			var row_class = 'oddrow';
			_.each(this.listitemviews, function (item) {
				item.remove();
				delete item;
			});
			this.collection.each(function (trip_model) {
				var list_entry = new t.TripListItemView({
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

	t.deletedialog = new BackcountryTracks.ConfirmDialog({
		template: 'Are you sure you want to the {{ name }} trip?',
		title: 'Delete Trip?',
		confirm_text: 'Delete!',
		dialogClass: 'delete_gear'
	});

	t.TripsScreen = BackcountryTracks.MainScreen.extend({
		id: 'trip_organizer',

		events: {
			'click button[title="Add Trip"]': 'handle_add_trip_start'
		},

		initialize: function () {
			_.bindAll(this, 'render', 'bubble_events');
			var template_string = $('#trip_organizer_list_template').html();
			this.template = _.template(template_string);


		},

		render: function () {
			$(this.el).html(this.template({}));

			var listview_section = this.$('section')[0];
			this.listview = new t.TripListView({
				collection: this.collection,
				el: listview_section
			});

			this.listview.bind('all', this.bubble_events);
			$(this.el).append(this.listview.el);
			this.$("button").button();
			this.listview.render();	

			return this;
		},

		handle_add_trip_start: function () {
			this.trigger('new');
		},

		bubble_events: function (eventname, argument) {
			this.trigger(eventname, argument);
		}
	});

	t.TripsModule = BackcountryTracks.Module.extend({
		name: 'Trip Organizer',

		routes: {
			'trips/:id': 'view',
			'trips': 'list',
			'trips/:id/discussion': 'view_discussion'
		},
		
		initialize: function () {
			_.bindAll(this, 'view', 'list', 'new_trip', 'save_trip', 'view_trip');

			this.sidebar = new BackcountryTracks.SidebarItem({
				name: 'my trips',
				icon: 'trips64',
				path: 'trips'
			});

			this.collection = new t.Trips();
			this.views = new Array;
			this.views.trips = new t.TripsScreen({
				collection: this.collection
			});
			this.views.trips.bind('new', this.new_trip);
			this.views.trips.bind('view_trip', this.view_trip);

			this.addform = new t.AddForm();
			this.addform.bind('save', this.save_trip)

			this.views.detail = new t.TripDetail;
		},

		view_trip: function(trip) {
			Backbone.history.navigate('trips/' + trip.id);
			this.view(trip.id);
		}, 

		view: function(id) {
			var view_trip = _.bind(function () {
					var trip = this.collection.get(id)
					this.views.detail.set_model(trip);
					BackcountryTracks.screens.activate(this.views.detail);
				}, this);
			this.collection.fetch({success: view_trip});
		},

		view_discussion: function (id) {
			var view_trip = _.bind(function () {
					var trip = this.collection.get(id)
					this.views.detail.set_model(trip);
					BackcountryTracks.screens.activate(this.views.detail);
					this.views.detail.select_tab('trip_discussion');
				}, this);
			this.collection.fetch({success: view_trip});
		},

		list: function () {
			this.collection.fetch();
			BackcountryTracks.screens.activate(this.views.trips);
		},

		new_trip: function () {
			var trip = new t.Trip;
			this.addform.open(trip);
		},

		save_trip: function (trip) {
			this.collection.add([trip]);
		}
	});


	this.TripOrganizer = t;
}).call(this);
