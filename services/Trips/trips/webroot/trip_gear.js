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

	trips.InventoryGear = Backbone.Collection.extend({
		model: GearManager.GearItem,

		url: function () {
			return '/app/trips/' + this.trip_id + '/gear/inventory';
		}
	});

    trips.PersonalGearView = Backbone.View.extend({
        events: {
            'click button': 'select_gear'
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
				accept: 'li',
				drop: this.gear_dropped,
				tolerance: 'touch'
            });
            this.$('button').button();
			this.$('ul').html('');

			this.collection.each(this.render_item);

            return this;
        },

        select_gear: function () {
            this.trigger('select_gear');
		},

		render_item: function (item) {
			this.$('ul').append(this.item_template(item.toJSON()));
		},

		gear_dropped: function (ev, ui) {
			var model = ui.draggable.data('model');
			this.collection.create(model.toJSON());
		}
    });

    trips.InventoryView = Backbone.View.extend({
        events: {
            'click button': 'close_inventory'
        },

        initialize: function () {
            _.bindAll(this, 'render', 'show', 'hide', 'close_inventory', 'render_item');
			var template = $('#trip_gear_inventory_item_template').html();
            this.item_template = _.template(template);

			this.collection.bind('change', this.render);
			this.collection.bind('reset', this.render);
			this.collection.bind('remove', this.render);
			this.collection.bind('add', this.render);
        },

        render: function () {
			this.$('ul').html('');
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
			this.$('ul').append(html);
		}
    });

    trips.GroupGearView = Backbone.View.extend({
        initialize: function () {
            _.bindAll(this, 'render', 'hide', 'show');
            var template = $('#trip_gear_inventory_item_template').html();
            this.item_template = _.template(template);
        },

        render: function() {
            this.$('li').draggable({
                zIndex: 9010,
                revert: true
            });

            this.$('ul').droppable({
                accept: 'li'
            });
        },

        hide: function () {
            $(this.el).hide();
        },

        show: function () {
            $(this.el).show();
        }
    });

    trips.TripGearView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render', 'select_gear', 'close_inventory', 'set_model');

			this.collections = new Object;
			this.collections.personal = new trips.PersonalGear;
			this.collections.inventory = new GearManager.GearList;

            this.views = new Object;
			this.views.personal = new trips.PersonalGearView({
				el: this.options.personal,
				collection: this.collections.personal
			});
			this.views.inventory = new trips.InventoryView({
				el: this.options.inventory,
				collection: this.collections.inventory
			});

            this.views.group = new trips.GroupGearView({el: this.options.group});

            this.views.personal.bind('select_gear', this.select_gear);
            this.views.inventory.bind('close_inventory', this.close_inventory);
        },

        render: function () {
            for (view in this.views) {
                this.views[view].render();
            }
        },

        select_gear: function () {
            this.views.group.hide();
            this.views.inventory.show();
        },

        close_inventory: function () {
            this.views.inventory.hide();
            this.views.group.show();
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

