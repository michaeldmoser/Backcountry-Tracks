var GearItem = Backbone.Model.extend({
	defaults: {
		'name': '',
		'weight': '',
		'description': ''
	},

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
	},

	comparator: function (trip) {
		return trip.get('name').toLowerCase();
	}
});

var GearConfirmDeleteDialog = Backbone.View.extend({
	id: 'gear_confirm_delete',

	initialize: function () {
		_.bindAll(this, 'delete_trip', 'cancel', 'render', 'open', 'close');
		this.template = _.template('Are you sure you want to delete the {{ name }} gear?');
		$(this.el).hide();
		$('body').append(this.el);
		var view = this;
		$(this.el).dialog({
			autoOpen: false,
			modal: true,
			zIndex: 9000,
			title: 'Delete Gear?',
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
var deletegeardialog = new GearConfirmDeleteDialog();

var GearAddForm = Backbone.View.extend({
	'id': 'gear_add_form',

	initialize: function () {
		_.bindAll(this, 'render', 'open', 'cancel', 'save_gear', 'handle_model_saved_success');

		this.template = _.template(this.options.template);

		$('body').append(this.el);
		var view = this;
		$(this.el).dialog({
			autoOpen: false,
			modal: true,
			zIndex: 8000,
			title: 'Add Gear',
			resizable: false,
			width: 500,
			dialogClass: 'gear_add_form',
			buttons: {
				'Save': view.save_gear,
				'Cancel': view.cancel
			}
		});

	},

	render: function () {
		if (!this.model)
			this.model = new GearItem;

		$(this.el).html(this.template(this.model.toJSON()));
	},

	open: function (model) {
		this.model = model;
		this.render();
		$(this.el).dialog('open');
	},

	cancel: function () {
		$(this.el).dialog('close');
		this.trigger('cancel');
	},

	save_gear: function () {
		var this_obj = this;
		var attributes = {
			'name': this.$('input[name="gear_name"]').val(),
			'weight': this.$('input[name="gear_weight"]').val(),
			'description': this.$('textarea[name="gear_description"]').val()
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

var GearListItemView = Backbone.View.extend({
	tagName: 'li',

	events: {
		'click .list_item_controls img[alt="Delete"]': 'handle_delete_clicked',
		'click': 'handle_click'
	},

	initialize: function () {
		_.bindAll(this, 'render', 'handle_delete_clicked', 'handle_click');

		this.template = _.template(this.options.template);
	},

	render: function () {
		$(this.el).html(this.template(this.model.toJSON()));
		$(this.el).hover(function () { $(this).toggleClass('highlight'); });
		this.$('.list_item_controls img[alt="Delete"]').button();
	},

	handle_delete_clicked: function (ev) {
		ev.stopPropagation();
		deletegeardialog.open(this.model);
	},

	handle_click: function () {
		this.trigger('edit', this.model);
	}
});

var GearListView = Backbone.View.extend({
	id: 'gear_list_view',
	className: 'list_view', 

	initialize: function () {
		_.bindAll(this, 'render', 'handle_list_item_events', 'handle_item_change');

		this.models = this.options.models;
		this.models.bind('add', this.render, this);
		this.models.bind('remove', this.render, this);
		this.models.bind('change', this.handle_item_change, this);

		this.listitemviews = new Array;
	},
	
	render: function () {
		var row_class = 'oddrow';
		_.each(this.listitemviews, function (item) {
			item.remove();
			delete item;
		});

		var list_item_template = this.options.list_item_template;
		this.models.each(function (model) {
			var list_entry = new GearListItemView({
				'model': model,
				'className': row_class,
				'template': list_item_template
			});
			list_entry.render();
			list_entry.bind('all', this.handle_list_item_events);
			$(this.el).append(list_entry.el);
			this.listitemviews.push(list_entry);

			row_class = row_class == 'oddrow' ? 'evenrow' : 'oddrow';
		}, this);
	},

	handle_list_item_events: function (eventname, trip) {
		this.trigger(eventname, trip);
	},

	handle_item_change: function () {
		this.models.sort();
		this.render();
	}

});

var GearManagerApp = Backbone.View.extend({
	className: 'application_container',

	initialize: function () {
		_.bindAll(this, 'render', 'handle_activate', 'receive_template', 'add_gear', 'handle_gear_save', 'edit_gear');
		$(this.el).hide();

		var receive_template = this.receive_template;
		$.ajax({
			url: '/static/gear_manager_template.html',
			success: receive_template
		});

		this.model.bind('activating', this.handle_activate);

		this.gear = new GearCollection();	
	},

	render: function () {
		this.$('button[title="Add Gear"]').button();
		if (this.gearview) {
			this.gearview.render();
		}

		return this;
	},

	receive_template: function (data) {
		this.templates = $('<div />', {'class': 'templates'}).html(data);
		$('body').append(this.templates);

		var gear_manager = $('div[title="gear manager template"]', this.templates).html();
		$(this.el).append(gear_manager);

		this.setup_add_form();
		this.$('button[title="Add Gear"]').click(this.add_gear);

		var view_el = this.$('#gear_list_view ul')[0];
		var list_item_template = $('div[title="list item template"]', this.templates).html();
		this.gearview = new GearListView({
			'models': this.gear,
			'el': view_el,
			'list_item_template': list_item_template
		});
		this.gearview.bind('edit', this.edit_gear);

		this.render();
	},

	setup_add_form: function () {
		var add_form_template = $('div[title="add form template"]', this.templates).html();
		this.add_form = new GearAddForm({
			template: add_form_template
		});
		this.add_form.bind('save', this.handle_gear_save);
	},

	refresh_gear: function () {
		var listview = this.gearview;
		this.gear.fetch({'success': function () {
				listview.render();
			}
		});
	},

	handle_activate: function () {
		this.refresh_gear();
		this.trigger('activated', this);
	},

	add_gear: function () {
		var model = new GearItem;
		this.add_form.open(model);
	},

	edit_gear: function (model) {
		this.add_form.open(model);
	},

	handle_gear_save: function (gear) {
		if (!this.gear.get(gear.id))
			this.gear.add([gear]);
	}
});

