var GearItem = Backbone.Model.extend({
	initialize: function () {
		_.bindAll(this, 'url');
	},

	url: function () {
		var url = '/app/users/' + current_user.get('email') + '/gear';
		if (this.id)
			url = url + "/" + this.id;

		return url;
	}

});

var GearCollection = Backbone.Collection.extend({
	model: GearItem,
	url: function () {
		return '/app/users/' + current_user.get('email') + '/gear';
	}
});

var GearListItemView = Backbone.View.extend({
	tagName: 'li',

	initialize: function () {
		_.bindAll(this, 'render', 'mouseovered', 'mouseouted',
			'edit_requested', 'edit_done', 'gear_save', 'delete_requested');	

		this.build_management_buttons();
		this.build_row();

		$(this.el).mouseenter(this.mouseovered);
		$(this.el).mouseleave(this.mouseouted);

		this.editview = new GearListAddForm({
			model: this.model
		});
		this.editview.render();
		$(this.editview.el).hide();
		$(this.el).append(this.editview.el);

		this.editview.bind('gear:save', this.gear_save);
		this.editview.bind('cancel', this.edit_done);
	},

	gear_save: function (gear_item) {
		this.model.save();
		this.render();
		this.edit_done();
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
			'src': '/static/img/icons/fugue/edit.png',
			'alt': 'Edit',
			'height': '16',
			'weight': '16'
		});
		this.delete_button =$(document.createElement('img')).attr({
			'src': '/static/img/icons/fugue/minus-button.png',
			'alt': 'Delete',
			'height': '16',
			'weight': '16'
		});

		this.management_buttons = $(document.createElement('div'));
		this.management_buttons.attr('class', 'gear_list_management_buttons');

		this.management_buttons.append(this.edit_button);
		this.management_buttons.append(this.delete_button);
		this.management_buttons.hide();
		$(this.el).append(this.management_buttons);

		$(this.edit_button).click(this.edit_requested);
		$(this.delete_button).click(this.delete_requested);
	},

	edit_requested: function (ev) {
		var after_slide_up = _.bind(function () {
			$(this.row).css('position', 'absolute');
			$(this.management_buttons).hide();
			var expose_me = this.editview.el;
			this.editview.render();
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

	delete_requested: function (ev) {
		this.model.destroy();
		var after_slide_up = _.bind(function () {
			$(this.el).remove();
		}, this);
		$(this.el).slideUp(400, after_slide_up);	
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

		this.button = $('<img />', {
			'height': '66',
			'width': '148',
			'src': '/static/img/icons/gear_add32.png'
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

var FormGraphicButton = Backbone.View.extend({
	name: 'submit',
	src: '/static/img/32x32/dialog-ok.png',
	height: '32',
	width: '32',

	tagName: 'div',

	className: 'form_graphic_button',

	events: {
		'click img': 'activate'
	},

	initialize: function () {
		_.bindAll(this, 'activate');
		this.set_options();
		this.create_graphic();

		$(this.el).addClass(this.name);
	},

	create_graphic: function () {
		var src = this.src;
		var height = this.height;
		var width = this.width;
		this.button = $('<img />').attr({
			'src': src,
			'height': height,
			'width': width
		});
		$(this.el).append(this.button);
	},

	set_options: function () {
		this.name = this.options.name ? this.options.name : this.name;
		this.src = this.options.src ? this.options.src : this.src;
		this.height = this.options.height ? this.options.height : this.height;
		this.width = this.options.width ? this.options.width : this.width;
	},

	activate: function () {
		this.trigger('click');	
	}
});

var GearListAddForm = Backbone.View.extend({
	className: 'gear_list_add_form',

	initialize: function () {
		_.bindAll(this, 'hide', 'show', 'save_gear', 'cancel');
		this.create_name_input();
		this.create_weight_input();
		this.create_description_input();
		this.create_buttons();
	},

	create_name_input: function () {
		this.input_name = $(document.createElement('input')).attr({
			'name': 'gear_name'	
		});
		var input_name_container = $('<div />').append(this.input_name);
		var label = $(document.createElement('label')).attr('for', 'add_gear_name').html('Name');

		var container = $(document.createElement('div')).attr('class', 'add_gear_name');
		$(container).append(label, input_name_container);
		$(this.el).append(container);
	},

	create_weight_input: function () {
		this.input_weight = $(document.createElement('input')).attr('name', 'gear_weight');
		var label = $(document.createElement('label')).attr('for', 'add_gear_weight').html('Weight');

		var container = $(document.createElement('div')).attr('class', 'add_gear_weight');
		$(container).append(label, this.input_weight);
		$(this.el).append(container);
	},

	create_description_input: function () {
		this.input_description = $(document.createElement('textarea')).attr('name', 'gear_description');
		var label = $(document.createElement('label')).attr('for', 'add_gear_description').html('Description');

		var container = $(document.createElement('div')).attr('class', 'add_gear_description');
		$(container).append(label, this.input_description);
		$(this.el).append(container);

	},

	create_submit_button: function () {
		this.submit_button = new FormGraphicButton({
			'name': 'save',
			'height': '66',
			'width': '174',
			'src': '/static/img/icons/gear_add32.png'
		});
		$(this.el).append(this.submit_button.el);
		this.submit_button.bind('click', this.save_gear);
	},

	create_cancel_button: function () {
		this.cancel_button = new FormGraphicButton({
			'name': 'cancel',
			'height': '69',
			'width': '132',
			'src': '/static/img/cancel-button.jpg'
		});
		$(this.el).append(this.cancel_button.el);
		this.cancel_button.bind('click', this.cancel);
	},

	create_buttons: function () {
		this.create_submit_button();
		this.create_cancel_button();
	},

	save_gear: function () {
		var weight = $(this.input_weight).val();
		var	name = $(this.input_name).val();
		var description = $(this.input_description).val();

		var gear_item = this.model ? this.model : new GearItem();
		gear_item.set({
			weight: weight,
			name: name,
			description: description
		});
		this.trigger('gear:save', gear_item);
		this.reset_form();
	},

	cancel: function () {
		this.reset_form();
		this.trigger('cancel');
	},

	reset_form: function () {
		$(this.input_description).val('');
		$(this.input_weight).val('');
		$(this.input_name).val('');
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

var GearListEditForm = GearListAddForm.extend({
	create_submit_button: function () {
		this.submit_button = new FormGraphicButton({
			'height': '66',
			'width': '174',
			'src': '/static/img/icons/gear_add32.png'
		});
		$(this.el).append(this.submit_button.el);
		this.submit_button.bind('click', this.save_gear);
	}
});

var GearListView = Backbone.View.extend({
	className: 'gear_list_view_container',

	initialize: function () {
		_.bindAll(this, 'render', 'add_new_gear', 'hide_add_form', 'close_all', 'add_gear', 'cancel_add');
		this.models = this.options.models;

		this.list_el = $(document.createElement('div'));
		this.controls_el = $(document.createElement('div'));	
		$(this.el).append(this.controls_el);


		this.init_controls();
		this.init_create_listing();
		this.init_add_button();

		this.init_add_form();
		$(this.controls_el).append(this.add_form.el);

		this.models.bind('add');
		this.models.bind('change', this.render);
	},

	init_controls: function () {
		this.controls_el.attr('class', 'gear_list_view_controls');
		this.search_form = new GearListSearchForm();
		this.controls_el.append(this.search_form.el);
	},

	init_add_form: function () {
		this.add_form = new GearListAddForm();
		$(this.add_form.el).hide();

		this.add_form.bind('gear:save', this.add_gear);
		this.add_form.bind('cancel', this.cancel_add);
	},

	add_gear: function (new_gear) {
		new_gear.save();
		this.models.add(new_gear, {silent: true});
		this.hide_add_form();
		this.render();
	},

	cancel_add: function () {
		this.hide_add_form();
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

		var app_title = $('<h1 />').html('Gear Manager');
		$(this.el).append(app_title);

		this.gear = new GearCollection();	
		
		this.gearview = new GearListView({
			'models': this.gear
		});
		var gearview = this.gearview;
		this.gear.fetch({'success':function () { gearview.render(); }});

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

