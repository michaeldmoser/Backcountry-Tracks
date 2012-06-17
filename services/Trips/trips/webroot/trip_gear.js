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
            _.bindAll(this, 'render', 'select_gear', 'render_item');
            this.item_template = _.template($('#trip_personal_gear_item_template').html())

			this.collection.bind('change', this.render);
			this.collection.bind('reset', this.render);
			this.collection.bind('remove', this.render);
			this.collection.bind('add', this.render);
        },

        render: function () {
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
			this.$('ul.personal_gear').append(html);
        }
    });

    trips.InventoryView = Backbone.View.extend({
        events: {
            'click #close_inventory': 'close_inventory',
            'click #add_gear': 'add_gear'
        },

        initialize: function () {
            _.bindAll(this, 'render', 'show', 'hide', 'close_inventory', 'render_item', 'add_gear', 'gear_dropped');
			$('body').append(this.el);
			$(this.el).dialog({
				autoOpen: false,
				modal: true,
				zIndex: 9000,
				title: 'Gear Organizer',
				resizable: false,
				width: 830,
				height: 660
			});

			var template = $('#trip_gear_organizer').html();
            this.template = _.template(template);
			$(this.el).html(this.template({}));

			this.collection.bind('change', this.render);
			this.collection.bind('reset', this.render);
			this.collection.bind('remove', this.render);
			this.collection.bind('add', this.render);
			$(this.el).hide();
        },

        render: function () {
            //$(this.el).droppable({
			//	accept: 'li.trip_gear',
			//	drop: this.gear_dropped,
			//	tolerance: 'touch'
            //});
            //this.$('button').button();
			//this.$('ul.inventory_gear').html('');

			//this.collection.each(this.render_item);

            //this.$('button').button();
        },

        show: function () {
            $(this.el).dialog('open');
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
            _.bindAll(this, 'render', 'hide', 'show', 'render_item');
            var template = $('#trip_gear_group_item_template').html();
            this.item_template = _.template(template);

			this.collection.bind('change', this.render);
			this.collection.bind('reset', this.render);
			this.collection.bind('remove', this.render);
			this.collection.bind('add', this.render);
        },

        render: function() {
			this.$('ul').html('');
			this.collection.each(this.render_item);
        },

		render_item: function (item) {
            var gear_item = item.toJSON();
            var model = this.model();
            var friends = model.get('friends');

            var find_owner = function (friend) {
                return friend.email == item.get('owner');
            }
            var owner = _.find(friends, find_owner);
			if (BackcountryTracks.current_user.get('email') == owner.email)
				gear_item['owner_name'] = 'me';
			else
				gear_item['owner_name'] = owner.first + " " + owner.last;

			var html = $(this.item_template(gear_item));
			this.$('ul').append(html);
		},

        hide: function () {
            $(this.el).hide();
        },

        show: function () {
            $(this.el).show();
		}
    });

    trips.GearListView = Backbone.View.extend({
        initialize: function () {
            _.bindAll(this, 'render', 'render_item', 'gear_dropped');

			var line_item_template = $('#gear_organizer_line_item_template').html();
			this.line_item_template = _.template(line_item_template);

			var line_item_owner_template = $('#gear_organizer_line_item_owner_template').html();
			this.line_item_owner_template = _.template(line_item_owner_template);

			this.list_header_template = $('#gear_organizer_list_header_template').html();

			this.collection.bind('change', this.render);
			this.collection.bind('reset', this.render);
			this.collection.bind('remove', this.render);
			this.collection.bind('add', this.render);
        },

        render: function () {
			var $this = this;
			this.$('ul').html(this.list_header_template);

            $(this.el).droppable({
				drop: this.gear_dropped,
				tolerance: 'pointer',
				accept: function (ui) {
					return _.any($this.options.accept, 
							function (filter) { return ui.hasClass(filter); });
				},
				activate: function () {
					$(this).css({'outline': '5px dashed #ffcc66'});
				},
				deactivate: function () {
					$(this).css({'outline': 'none'});
				}
            });
			this.collection.each(this.render_item);

            return this;
        },

        select_gear: function () {
            this.trigger('select_gear');
		},

		render_item: function (item) {
			if (this.options.display_filter) {
				var display_filter = _.bind(this.options.display_filter, this);
				if (!display_filter(item))
					return;
			}

            var template = this.line_item_template;
                
            var gear_item = item.toJSON();
            if (this.options.show_owner) {
                var model = this.model();
                var friends = model.get('friends');

                var find_owner = function (friend) {
                    return friend.email == item.get('owner');
                }
                var owner = _.find(friends, find_owner);
				if (BackcountryTracks.current_user.get('email') == owner.email)
					gear_item['owner_name'] = 'me';
				else
					gear_item['owner_name'] = owner.first + " " + owner.last;

                var template = this.line_item_owner_template;
            }

			var html = $(template(gear_item));
			if (!this.options.show_owner || ((this.options.show_owner && gear_item['owner_name'] == 'me'))) {
				var draggable = html.draggable({
					zIndex: 9010,
					helper: 'clone',
					appendTo: '#trip_gear_organizer'
				});
				draggable.data('model', item);
			}
			this.$('ul').append(html);
			html.addClass(this.options.filterClass);
		},

		gear_dropped: function (ev, ui) {
			var model = ui.draggable.data('model');
			this.trigger('gear_dropped', this.collection, model, this.options.filterClass);
		}
 	});

	trips.GearOrganizer = Backbone.View.extend({
		id: "gear_organizer",
		
        initialize: function () {
			var $this = this;
            _.bindAll(this, 'render', 'show', 'hide', 'add_new_gear', 'add_to_personal_gear');
			$('body').append(this.el);
			$(this.el).dialog({
				autoOpen: false,
				modal: true,
				zIndex: 9000,
				title: 'Gear Organizer',
				resizable: false,
				width: 830,
                height: 660,
                show: {
                    effect: 'fade',
                    duration: 400
                },
                hide: {
                    effect: 'fade',
                    duration: 400
                }
			});

			var template = $('#trip_gear_organizer_template').html();
            this.template = _.template(template);
			$(this.el).html(this.template({}));
			$(this.el).hide();

			var line_item_template = $('#gear_organizer_line_item_template').html();
			this.line_item_template = _.template(line_item_template);

			this.list_header_template = $('#gear_organizer_list_header_template').html();

			this.list_views = new Object;
			this.list_views.personal = new trips.GearListView({
				el: this.$('#trip_gear_personal'),
                model: this.model,
				collection: this.options.collections.personal,
				accept: ['group', 'inventory'],
				filterClass: 'personal',
			});
			this.list_views.personal.bind('gear_dropped', function (collection, item, filter_class) {
				var personal_gear = item.clone();
				var not_inventory = filter_class != 'inventory';
				var gear_id = (not_inventory && item.get('gear_id')) ? item.get('gear_id') : item.get('id');
				var find_gear = function (gear_item) {
					return gear_item.get('gear_id') == gear_id;
				}
				var gear = $this.options.collections.group.find(find_gear);
				if (gear) $this.options.collections.group.remove(gear);

				personal_gear.set({'gear_id': gear_id});
				personal_gear.set({'id': null});
				collection.create(personal_gear.toJSON());
			});

			this.list_views.group = new trips.GearListView({
				el: this.$('#trip_gear_group'),
                model: this.model,
                show_owner: true,
				collection: this.options.collections.group,
				accept: ['inventory', 'personal'],
				filterClass: 'group'
			});
			this.list_views.group.bind('gear_dropped', function (collection, item, filter_class) {
				var personal_gear = item.clone();
				var not_inventory = filter_class != 'inventory';
				var gear_id = (not_inventory && item.get('gear_id')) ? item.get('gear_id') : item.get('id');
				var find_gear = function (gear_item) {
					return gear_item.get('gear_id') == gear_id;
				}
				var gear = $this.options.collections.personal.find(find_gear);
				if (gear) $this.options.collections.personal.remove(gear);

				personal_gear.set({'gear_id': gear_id});
				personal_gear.set({'id': null});
				collection.create(personal_gear.toJSON());
			});

			this.list_views.inventory = new trips.GearListView({
				el: this.$('#trip_gear_personal_inventory'),
                model: this.model,
				collection: this.options.collections.inventory,
				accept: ['group', 'personal'],
				filterClass: 'inventory',
				display_filter: function (item) {
					var gear_id = item.get('id');
					var find_gear = function (gear_item) {
						return gear_item.get('gear_id') == gear_id;
					}
					if ($this.options.collections.personal.any(find_gear) ||
							$this.options.collections.group.any(find_gear))
						return false;

					return true;
				}
			});
			this.list_views.inventory.bind('gear_dropped', function (collection, item) {
				var personal = $this.options.collections.personal.get(item.get('id'));	
				if (personal) personal.destroy();

				var group = $this.options.collections.group.get(item.get('id'));	
				if (group) group.destroy();
			});

			_.each([this.options.collections.personal, this.options.collections.group],
				function (collection) {
					collection.bind('change', $this.list_views.inventory.render);
					collection.bind('reset', $this.list_views.inventory.render);
					collection.bind('remove', $this.list_views.inventory.render);
					collection.bind('add', $this.list_views.inventory.render);
				}
			);

			this.$('button').button();
			this.$('#gearorgctrls button').click(function () {
				$($this.el).dialog('close');
			});

			this.$('#newgearbuttons button').click(this.add_new_gear);
		},

		render: function () {
			var $this = this;
			this.list_views.inventory.render();
			this.list_views.personal.render();
			this.list_views.group.render();
		},

        show: function () {
			this.render();
            $(this.el).dialog('open');
        },

        hide: function () {
            $(this.el).hide();
        },

		add_new_gear: function () {
			var gear_name = this.$('#newgearname').val();
			var gear_description = this.$('#newgeardescription').val();
			var gear_weight = this.$('#newgearweight').val();
			var gear_makemodel = this.$('#newgearmakemodel').val();

			var gear = {
				name: gear_name,
				description: gear_description,
				weight: gear_weight,
				make: gear_makemodel
			};

			var model = new GearManager.GearItem(gear);
			model.bind('change', this.add_to_personal_gear);
			this.options.collections.inventory.create(model, {'wait': true});
		},

		add_to_personal_gear: function (model) {
			this.$('#newgearname').val('');
			this.$('#newgeardescription').val('');
			this.$('#newgearweight').val('');
			this.$('#newgearmakemodel').val('');

			var personal_item = model.clone();
			personal_item.set({
				'gear_id': personal_item.get('id'),
				'id': null
			});

			this.options.collections.personal.create(personal_item.toJSON());
		}
	});

    trips.TripGearView = Backbone.View.extend({
        initialize: function() {
            var $this = this;
            _.bindAll(this, 'render', 'select_gear', 'close_inventory', 'set_model', 'add_gear', 'save_new_gear', 'add_to_personal_gear');

			this.collections = new Object;
			this.collections.personal = new trips.PersonalGear;
			this.collections.inventory = new GearManager.GearList;
			this.collections.group = new trips.GroupGear;

            var get_model = function () {
                return $this.model;
            }

            this.views = new Object;
			this.views.personal = new trips.PersonalGearView({
				el: this.options.personal,
				collection: this.collections.personal
			});
            this.views.personal.bind('select_gear', this.select_gear);

			this.views.organizer = new trips.GearOrganizer({
                collections: this.collections,
                model: get_model
			});
			this.views.organizer.bind('new_gear', this.save_new_gear);


			this.views.group = new trips.GroupGearView({
				el: this.options.group,
                collection: this.collections.group,
                model: get_model
			});
        },

        render: function () {
            for (view in this.views) {
                this.views[view].render();
            }
        },

        select_gear: function () {
            this.views.organizer.show();
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

