(function () {
	var g = {};

	g.GearItem = Backbone.Model.extend({
		defaults: {
			'name': '',
			'weight': '',
			'description': ''
		},

		initialize: function () {
			_.bindAll(this, 'url');
		}
	});

	g.GearList = Backbone.Collection.extend({
		model: g.GearItem,
		url: function () {
			return '/app/users/' + BackcountryTracks.current_user.get('email') + '/gear';
		},

		comparator: function (gear) {
			return gear.get('name').toLowerCase();
		}
	});
	
	g.GearAddForm = Backbone.View.extend({
		'id': 'gear_add_form',

		initialize: function () {
			_.bindAll(this, 'render', 'open', 'cancel', 'save_gear');

			this.template = _.template($('#gear_add_form_template').html());

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
				this.model = new g.GearItem;

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

			this.trigger('save', attributes);
			$(this.el).dialog('close');
		}
	});
	
	g.GearListItemView = Backbone.View.extend({
		tagName: 'li',

		events: {
			'click .list_item_controls img[alt="Delete"]': 'handle_delete_clicked',
			'click': 'handle_click'
		},

		initialize: function () {
			_.bindAll(this, 'render', 'handle_delete_clicked', 'handle_click');

			this.template = _.template($('#gear_list_item_template').html());
		},

		render: function () {
			$(this.el).html(this.template(this.model.toJSON()));
			$(this.el).hover(function () { $(this).toggleClass('highlight'); });
			this.$('.list_item_controls img[alt="Delete"]').button();
		},

		handle_delete_clicked: function (ev) {
			ev.stopPropagation();
			g.deletedialog.open(this.model);
		},

		handle_click: function () {
			this.trigger('edit', this.model);
		}
	});
	
	g.GearListView = Backbone.View.extend({
		id: 'gear_list_view',
		className: 'list_view', 

		initialize: function () {
			_.bindAll(this, 'render', 'handle_list_item_events', 'handle_item_change');

			this.collection = this.options.collection;
			this.collection.bind('add', this.render, this);
			this.collection.bind('remove', this.render, this);
			this.collection.bind('change', this.handle_item_change, this);

			this.listitemviews = new Array;
		},
		
		render: function () {
			var row_class = 'oddrow';
			_.each(this.listitemviews, function (item) {
				item.remove();
				delete item;
			});

			this.collection.each(function (model) {
				var list_entry = new g.GearListItemView({
					'model': model,
					'className': row_class
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
			this.collection.sort();
			this.render();
		}

	});

	g.deletedialog = new BackcountryTracks.ConfirmDialog({
		template: 'Are you sure you want to delete the {{ name }} gear?',
		title: 'Delete Gear?',
		confirm_text: 'Delete!'
	});

	g.GearScreen = BackcountryTracks.MainScreen.extend({
		id: 'gear_manager',

		initialize: function () {
			_.bindAll(this, 'render', 'add_gear', 'edit_gear');

			this.template = $('#gear_manager_template').html();
			$(this.el).append(this.template);
			this.$('button[title="Add Gear"]').button();
			this.$('button[title="Add Gear"]').click(this.add_gear);

			var view_el = this.$('#gear_list_view ul')[0];
			var list_item_template = $('#gear_list_item_template').html();
			this.gearview = new g.GearListView({
				'collection': this.collection,
				'el': view_el,
				'list_item_template': list_item_template
			});
			this.gearview.bind('edit', this.edit_gear);
		},

		render: function () {
			if (this.gearview) {
				this.gearview.render();
			}
		},

		add_gear: function () {
			this.trigger('new');
		},

		edit_gear: function (gear) {
			this.trigger('edit', gear);
		}
	});


	g.GearModule = BackcountryTracks.Module.extend({

		routes: {
			'gear': 'main'
		},

		initialize: function () {
			_.bindAll(this, 'main', 'add_gear', 'save_gear', 'edit_gear');

			var sidebar = new BackcountryTracks.SidebarItem({
				name: 'my gear',
				icon: 'gear64',
				path: 'gear',
			});

			this.collection = new g.GearList;
			this.views = new Array;
			this.views.gearlist = new g.GearScreen({
				collection: this.collection
			});
			this.views.gearlist.bind('new', this.add_gear);
			this.views.gearlist.bind('edit', this.edit_gear);

			this.addform = new g.GearAddForm;
			this.addform.bind('save', this.save_gear);
		},

		main: function () {
			var gearlist = this.views.gearlist
			this.collection.fetch({'success': function () {
					gearlist.render();	
				}
			});

			BackcountryTracks.screens.activate(this.views.gearlist);
		},

		add_gear: function () {
			var gear = new g.GearItem;
			this.addform.open(gear);
		},

		save_gear: function (gear_data) {
			var gear = this.collection.get(gear_data.id);
			if (!gear) {
				this.collection.create(gear_data);
			} else {
				gear.set(gear_data);
				gear.save();
			};
		},
		
		edit_gear: function (gear) {
			this.addform.open(gear);
		}

	});

	this.GearManager = g;
}).call(this);
