function TripGearViews() {
    /*
     * This is an internal function intended to be used only by trips.js. DO NOT USE
     */
    var trips = this;

	trips.PersonalGear = Backbone.Collection.extend({
		model: GearManager.GearItem,

		url: function () {
			return '/app/trips/' + this.trip_id + '/gear/personal';
		}
	});

	trips.GroupGear = Backbone.Collection.extend({
		model: GearManager.GearItem,

		url: function () {
			return '/app/trips/' + this.trip_id + '/gear/group';
		}
	});

	trips.InventoryGear = Backbone.Collection.extend({
		model: GearManager.GearItem,

		url: function () {
			return '/app/trips/' + this.trip_id + '/gear/inventory';
		}
	});

    trips.PersonalGearView = Backbone.View.extend({
        events: {
            'click #select_gear': 'select_gear'
        },

        initialize: function () {
            _.bindAll(this, 'render', 'select_gear', 'render_item', 'gear_dropped');
            this.item_template = _.template($('#trip_personal_gear_item_template').html())

			this.collection.bind('change', this.render);
			this.collection.bind('reset', this.render);
			this.collection.bind('remove', this.render);
			this.collection.bind('add', this.render);
        },

        render: function () {
            $(this.el).droppable({
				accept: function (ui) {
					if (ui.hasClass('group_gear') || ui.hasClass('inventory_gear'))
						return true;

					return false;
				},
				drop: this.gear_dropped,
				tolerance: 'touch'
            });
            this.$('button').button();
			this.$('ul.personal_gear').html('');

			this.collection.each(this.render_item);

            return this;
        },

        select_gear: function () {
            this.trigger('select_gear');
		},

		render_item: function (item) {
			var html = $(this.item_template(item.toJSON()));
            var draggable = html.draggable({
				zIndex: 9010,
				revert: true
            });
			draggable.data('model', item);
			this.$('ul.personal_gear').append(html);
		},

		gear_dropped: function (ev, ui) {
			var model = ui.draggable.data('model');
			if (ui.draggable.hasClass('group_gear')) {
				model.destroy();
			}
			this.collection.create(model.toJSON());
		}
 	});

    trips.InventoryView = Backbone.View.extend({
        events: {
            'click #close_inventory': 'close_inventory',
            'click #add_gear': 'add_gear'
        },

        initialize: function () {
            _.bindAll(this, 'render', 'show', 'hide', 'close_inventory', 'render_item', 'add_gear', 'gear_dropped');
			var template = $('#trip_gear_inventory_item_template').html();
            this.item_template = _.template(template);

			this.collection.bind('change', this.render);
			this.collection.bind('reset', this.render);
			this.collection.bind('remove', this.render);
			this.collection.bind('add', this.render);
			$(this.el).hide();
        },

        render: function () {
            $(this.el).droppable({
				accept: 'li.trip_gear',
				drop: this.gear_dropped,
				tolerance: 'touch'
            });
            this.$('button').button();
			this.$('ul.inventory_gear').html('');

			this.collection.each(this.render_item);

            this.$('button').button();
        },

        show: function () {
            $(this.el).show();
        },

        hide: function () {
            $(this.el).hide();
        },

        close_inventory: function (ev) {
            ev.stopPropagation();
            this.trigger('close_inventory');
		},

		render_item: function (item) {
			var html = $(this.item_template(item.toJSON()));
            var draggable = html.draggable({
				zIndex: 9010,
				revert: true
            });
			draggable.data('model', item);
			this.$('ul.inventory_gear').append(html);
		},

		add_gear: function () {
			this.trigger('add_gear');
		},

		gear_dropped: function (ev, ui) {
			var model = ui.draggable.data('model');
			model.destroy();
		}
    });

    trips.GroupGearView = Backbone.View.extend({
        initialize: function () {
            _.bindAll(this, 'render', 'hide', 'show', 'gear_dropped', 'render_item');
            var template = $('#trip_gear_group_item_template').html();
            this.item_template = _.template(template);

			this.collection.bind('change', this.render);
			this.collection.bind('reset', this.render);
			this.collection.bind('remove', this.render);
			this.collection.bind('add', this.render);
        },

        render: function() {
            $(this.el).droppable({
				accept: 'li.trip_gear',
				tolerance: 'touch',
				drop: this.gear_dropped
            });
			this.$('ul').html('');

			this.collection.each(this.render_item);
        },

		render_item: function (item) {
			var html = $(this.item_template(item.toJSON()));
            var draggable = html.draggable({
				zIndex: 9010,
				revert: true
            });
			draggable.data('model', item);
			this.$('ul').append(html);
		},

        hide: function () {
            $(this.el).hide();
        },

        show: function () {
            $(this.el).show();
		},

		gear_dropped: function (ev, ui) {
			var model = ui.draggable.data('model');
			this.collection.create(model.toJSON());
			model.destroy();
		}
    });

    trips.TripGearView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render', 'select_gear', 'close_inventory', 'set_model', 'add_gear', 'save_new_gear', 'add_to_personal_gear');

			this.collections = new Object;
			this.collections.personal = new trips.PersonalGear;
			this.collections.inventory = new GearManager.GearList;
			this.collections.group = new trips.GroupGear;

            this.views = new Object;
			this.views.personal = new trips.PersonalGearView({
				el: this.options.personal,
				collection: this.collections.personal
			});
            this.views.personal.bind('select_gear', this.select_gear);

			this.views.inventory = new trips.InventoryView({
				el: this.options.inventory,
				collection: this.collections.inventory
			});
            this.views.inventory.bind('close_inventory', this.close_inventory);
			this.views.inventory.bind('add_gear', this.add_gear);

			this.views.group = new trips.GroupGearView({
				el: this.options.group,
				collection: this.collections.group
			});

			this.addform = new GearManager.GearAddForm();
			this.addform.bind('save', this.save_new_gear);
        },

        render: function () {
            for (view in this.views) {
                this.views[view].render();
            }
        },

        select_gear: function () {
            //this.views.group.hide();
            this.views.inventory.show();
        },

        close_inventory: function () {
            this.views.inventory.hide();
            this.views.group.show();
		},

		add_gear: function () {
			this.addform.open();
		},

		save_new_gear: function (attributes) {
			var model = new GearManager.GearItem(attributes);
			model.bind('change', this.add_to_personal_gear);
			this.collections.inventory.create(model);
		},

		add_to_personal_gear: function (model) {
			this.collections.personal.create(model.toJSON());
		},

		set_model: function (model) {
			_.each(this.collections, function (collection) {
				collection.trip_id = model.id;
				collection.fetch();
			}, this);

			this.model = model;
		}
    });
}

