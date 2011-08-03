var ApplicationModel = Backbone.Model.extend({
	initialize: function () {
		_.bindAll(this, 'activate');
	},

	activate: function () {
		this.trigger('activating');
	}
});

var GearItem = Backbone.Model.extend({

});

var GearCollection = Backbone.Collection.extend({
	model: GearItem
});

var GearListItemView = Backbone.View.extend({
	tagName: 'li',

	initialize: function () {
		_.bindAll(this, 'render', 'mouseovered', 'mouseouted',
			'edit_requested', 'edit_done');	

		this.build_management_buttons();
		this.build_row();

		$(this.el).mouseenter(this.mouseovered);
		$(this.el).mouseleave(this.mouseouted);
		$(this.el).click(this.edit_done);

		this.editview = new GearListAddForm({
			model: this.model
		});
		this.editview.render();
		$(this.editview.el).hide();
		$(this.el).append(this.editview.el);
	},

	mouseovered: function () {
		this.management_buttons.show();
		$(this.el).addClass('highlighted_row');
	},

	mouseouted: function () {
		this.management_buttons.hide();
		$(this.el).removeClass('highlighted_row');
	},

	build_row: function () {
		this.name_column = $(document.createElement('div')).attr({
			'class': 'gear_name gear_item_list_column'
		});

		this.column2 = $(document.createElement('div')).attr({
			'class': 'gear_weight gear_item_list_column'
		});

		this.column3 = $(document.createElement('div')).attr({
			'class': 'gear_description gear_item_list_column'
		});
		this.row = $(document.createElement('div')).attr('class', 'gear_item_row');
		$(this.row).append(this.name_column, this.column2, this.column3);
		$(this.el).append(this.row);
	},

	build_management_buttons: function () {
		this.edit_button = $(document.createElement('img')).attr({
			'src': '/static/img/22x22/actions/edit-rename.png',
			'alt': 'Edit',
			'height': '22',
			'weight': '22'
		});

		this.management_buttons = $(document.createElement('div'));
		this.management_buttons.attr('class', 'gear_list_management_buttons');

		this.management_buttons.append(this.edit_button);
		this.management_buttons.hide();
		$(this.el).append(this.management_buttons);

		$(this.edit_button).click(this.edit_requested);
	},

	edit_requested: function (ev) {
		var after_slide_up = _.bind(function () {
			$(this.row).css('position', 'absolute');
			$(this.management_buttons).hide();
			var expose_me = this.editview.el;
			$(this.editview.el).slideDown(400);
		}, this);
		
		this.trigger('begin_edit', this);
		$(this.row).fadeOut(200, after_slide_up);
		ev.stopPropagation();
	},

	edit_done: function () {
		$(this.editview.el).slideUp(400);
		var row = this.row;
		$(this.row).fadeIn(400, function () {
			$(row).css('position', 'static');
		});
	},

	render: function () {
		$(this.name_column).html(this.model.get('name'));	
		$(this.column3).html(this.model.get('description'));	
		$(this.column2).html(this.model.get('weight'));	
	}
});

var GearListAddButton = Backbone.View.extend({
	className: 'gear_list_add_button',
	events: {
		'click img': 'trigger_add_event'	
	},

	initialize: function () {
		_.bindAll(this, 'trigger_add_event');

		this.button = $(document.createElement('img')).attr({
			'height': '66',
			'width': '148',
			'src': '/static/img/add-gear-button.jpg'
		});
		$(this.el).append(this.button);
	},

	trigger_add_event: function () {
		this.trigger('click');
	}
});

var GearListSearchForm = Backbone.View.extend({
	className: 'gear_list_search_box_container',

	initialize: function() {
		_.bindAll(this, 'handle_receive_focus', 'handle_lose_focus');
		this.search_input = $(document.createElement('input')).attr({
			'type': 'text',
			'name': 'query',
			'value': 'search'
		});

		$(this.el).append(this.search_input);

		this.search_input.focus(this.handle_receive_focus);
		this.search_input.blur(this.handle_lose_focus);
	},

	handle_receive_focus: function () {
		$(this.search_input).val('');
		$(this.search_input).css('text-align', 'left');
	},

	handle_lose_focus: function () {
		$(this.search_input).val('search...');
		$(this.search_input).css('text-align', 'right');
	}
});

var GearListAddForm = Backbone.View.extend({
	className: 'gear_list_add_form',

	initialize: function () {
		_.bindAll(this, 'hide', 'show');
		this.create_name_input();
		this.create_weight_input();
		this.create_description_input();
	},

	create_name_input: function () {
		this.input_name = $(document.createElement('input')).attr({
			'id': 'add_gear_name'	
		});
		var label = $(document.createElement('label')).attr('for', 'add_gear_name').html('Name');

		var container = $(document.createElement('div')).attr('class', 'add_gear_name');
		$(container).append(label, this.input_name);
		$(this.el).append(container);
	},

	create_weight_input: function () {
		this.input_weight = $(document.createElement('input')).attr('id', 'add_gear_weight');
		var label = $(document.createElement('label')).attr('for', 'add_gear_weight').html('Weight');

		var container = $(document.createElement('div')).attr('class', 'add_gear_weight');
		$(container).append(label, this.input_weight);
		$(this.el).append(container);
	},

	create_description_input: function () {
		this.input_description = $(document.createElement('textarea')).attr('id', 'add_gear_description');
		var label = $(document.createElement('label')).attr('for', 'add_gear_description').html('Description');

		var container = $(document.createElement('div')).attr('class', 'add_gear_description');
		$(container).append(label, this.input_description);
		$(this.el).append(container);

	},

	hide: function () {
		$(this.el).slideToggle();
	},

	show: function () {
		$(this.el).slideToggle();
	},

	render: function () {
		if (!this.model)
			return;

		$(this.input_description).val(this.model.get('description'));
		$(this.input_weight).val(this.model.get('weight'));
		$(this.input_name).val(this.model.get('name'));
	}
});

var GearListView = Backbone.View.extend({
	className: 'gear_list_view_container',

	initialize: function () {
		_.bindAll(this, 'render', 'add_new_gear', 'hide_add_form', 'close_all');
		this.models = this.options.models;

		this.list_el = $(document.createElement('div'));
		this.controls_el = $(document.createElement('div'));	
		$(this.el).append(this.controls_el);


		this.init_controls();
		this.init_create_listing();
		this.init_add_button();

		this.init_add_form();
		$(this.controls_el).append(this.add_form.el);
	},

	init_controls: function () {
		this.controls_el.attr('class', 'gear_list_view_controls');
		this.search_form = new GearListSearchForm();
		this.controls_el.append(this.search_form.el);
	},

	init_add_form: function () {
		this.add_form = new GearListAddForm();
		$(this.add_form.el).hide();
		$(this.add_form.el).mouseleave(this.hide_add_form);
	},

	hide_add_form: function () {
		$(this.add_form.el).slideToggle();
	},

	close_all: function (gear) {
		_.each(this.gear_views, function (gear_item) {
				if (gear_item == gear)
					return;

				gear_item.edit_done();
			}, this);
	},

	render: function() {
		$(this.list_el).html('');
		this.create_header();
		var row_class = 'oddrow';
		this.gear_views = new Array();
		this.models.each(function (gear_item) {
			var list_entry = new GearListItemView({'model': gear_item, className: row_class});
			this.gear_views.push(list_entry);
			list_entry.render();
			$(this.list_el).append(list_entry.el);
			row_class = row_class == 'oddrow' ? 'evenrow' : 'oddrow';
			list_entry.bind('begin_edit', this.close_all);
		}, this);	
	},

	create_header: function () {

		var header_row = $(document.createElement('li')).attr('class', 'gear_list_header');
		var name_column = $(document.createElement('div')).attr({
			'class': 'gear_name gear_item_list_column'
		}).html('Gear');
		$(header_row).append(name_column);

		var column2 = $(document.createElement('div')).attr({
			'class': 'gear_weight gear_item_list_column'
		}).html('Weight');
		$(header_row).append(column2);

		var column3 = $(document.createElement('div')).attr({
			'class': 'gear_description gear_item_list_column'
		}).html('Description');
		$(header_row).append(column3);

		$(this.list_el).append(header_row);

	},

	init_create_listing: function () {
		var container = $(document.createElement('div')).attr({
			'class': 'gear_listing'	
		});

		var listcontainer = document.createElement('ul');
		$(container).append(listcontainer);
		$(this.el).append(container);
		this.list_el = listcontainer;
	},

	init_add_button: function () {
		this.add_button = new GearListAddButton();
		this.add_button.bind('click', this.add_new_gear);
		$(this.controls_el).append(this.add_button.el);
	},

	add_new_gear: function () {
		this.add_form.show();
	}
});

var GearManagerApp = Backbone.View.extend({
	className: 'application_container',

	initialize: function () {
		_.bindAll(this, 'render', 'handle_activate');
		$(this.el).hide();
		this.model.bind('activating', this.handle_activate);

		this.gear = new GearCollection([
			{'name': 'Backpack', 'description': 'This is a backpack', 'weight': '24 oz'},
			{'name': 'Alcohol Stove', 'description': 'A stove that uses alcohol for fuel', 'weight': '2 oz'},
			{'name': 'Tarp', 'description': 'A tarp to protect against wind and rain', 'weight': '7 oz'},
			{'name': 'Sleeping pad', 'description': 'Closed cell foam pad', 'weight': '7 oz'},
			{'name': 'Sleeping quilt', 'description': '800 power down quilt', 'weight': '10 oz'},
			{'name': 'Backpack', 'description': 'This is a backpack', 'weight': '24 oz'},
			{'name': 'Alcohol Stove', 'description': 'A stove that uses alcohol for fuel', 'weight': '2 oz'},
			{'name': 'Tarp', 'description': 'A tarp to protect against wind and rain', 'weight': '7 oz'},
			{'name': 'Sleeping pad', 'description': 'Closed cell foam pad', 'weight': '7 oz'},
			{'name': 'Sleeping quilt', 'description': '800 power down quilt', 'weight': '10 oz'},
			{'name': 'Backpack', 'description': 'This is a backpack', 'weight': '24 oz'},
			{'name': 'Alcohol Stove', 'description': 'A stove that uses alcohol for fuel', 'weight': '2 oz'},
			{'name': 'Tarp', 'description': 'A tarp to protect against wind and rain', 'weight': '7 oz'},
			{'name': 'Sleeping pad', 'description': 'Closed cell foam pad', 'weight': '7 oz'},
			{'name': 'Sleeping quilt', 'description': '800 power down quilt', 'weight': '10 oz'},
			{'name': 'Backpack', 'description': 'This is a backpack', 'weight': '24 oz'},
			{'name': 'Alcohol Stove', 'description': 'A stove that uses alcohol for fuel', 'weight': '2 oz'},
			{'name': 'Tarp', 'description': 'A tarp to protect against wind and rain', 'weight': '7 oz'},
			{'name': 'Sleeping pad', 'description': 'Closed cell foam pad', 'weight': '7 oz'},
			{'name': 'Sleeping quilt', 'description': '800 power down quilt', 'weight': '10 oz'},
			{'name': 'Backpack', 'description': 'This is a backpack', 'weight': '24 oz'},
			{'name': 'Alcohol Stove', 'description': 'A stove that uses alcohol for fuel', 'weight': '2 oz'},
			{'name': 'Tarp', 'description': 'A tarp to protect against wind and rain', 'weight': '7 oz'},
			{'name': 'Sleeping pad', 'description': 'Closed cell foam pad', 'weight': '7 oz'},
			{'name': 'Sleeping quilt', 'description': '800 power down quilt', 'weight': '10 oz'},
		]);	
		this.gearview = new GearListView({
			'models': this.gear
		});

		$(this.el).append(this.gearview.el);
	},

	render: function () {
		this.gearview.render();
		return this;
	},

	handle_activate: function () {
		this.trigger('activated', this);
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
		$('#appcontent').append(application.el);

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
					'icon': '/static/imgs/gear_manager.png'
				})
			}
		},
		'AppChooser': AppChooserView
	};

	var portal = new Portal(deps);

})();


