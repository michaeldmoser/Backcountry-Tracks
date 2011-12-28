var SidebarViewChooserButton = Backbone.View.extend({
	className: 'app_chooser_button',

	initialize: function () {
		_.bindAll(this, 'render');
	},

	render: function () {
		var icon_class = this.model.get('icon');
		var path = this.model.get('path');
		var name = this.model.get('name');
		$(this.el).addClass(icon_class);
		$(this.el).html('<a href="#' + path + '">' + name + "</a>");
	}
});

var SidebarView = Backbone.View.extend({

	initialize: function() {
		_.bindAll(this, 'render');
		this.$el = $(this.el);
	},

	render: function () {
		this.model.each(function (app) {
			if (app.SidebarView) {
				var chooser_button = new app.SidebarView({'model': app});
			} else {
				var chooser_button = new SidebarViewChooserButton({'model': app});
			}
			chooser_button.render();
			this.$el.append(chooser_button.el);
		}, this);
	}
});

var ScreensView = Backbone.View.extend({
	initialize: function () {
		_.bindAll(this, 'activate_screen');

		this.collection.bind('activate', this.activate_screen);

		this.collection.each(function (screen) {
			$(screen.el).hide();
			$(this.el).append(screen.el);
			screen.render();
		}, this);

		this.current = null;
	},

	activate_screen: function (screen) {
		if (this.current)
			$(this.current.el).hide();

		$(screen.el).show();
		this.current = screen;
	}
});

(function () {
	var root = this;
	var bct = {};
	_.templateSettings['interpolate'] = /\{\{(.+?)\}\}/g;

	bct.ConfirmDialog = Backbone.View.extend({
		initialize: function () {
			_.bindAll(this, 'confirm', 'cancel', 'render', 'open', 'close');
			this.template = _.template(this.options.template);

			var buttons = {};
			confirm_text = this.options.confirm_text || 'OK';
			buttons[confirm_text] = this.confirm;

			cancel_text = this.options.cancel_text || 'Cancel';
			buttons[cancel_text] = this.cancel;

			$(this.el).hide();
			$('body').append(this.el);
			var view = this;
			$(this.el).dialog({
				autoOpen: false,
				modal: true,
				zIndex: 9000,
				title: this.options.title,
				resizable: false,
				width: 500,
				buttons: buttons,
				dialogClass: this.options.dialogClass || ''
			});
		},

		confirm: function () {
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

	bct.MainScreen = function (options) {
		this.className = 'application_container';
		Backbone.View.call(this, options);
		bct.screens.register(this);
	};
	_.extend(bct.MainScreen.prototype, Backbone.View.prototype);
	bct.MainScreen.extend = Backbone.View.extend;

	bct.Module = function (attributes) {
		attributes || (attributes = {});
		this.name = this.name || "Application";
		this.icon = this.icon || "gear64";

		this.SidebarView = this.SidebarView || null;

		Backbone.Router.call(this);
		bct.modules.add([this]);
	};
	_.extend(bct.Module.prototype, Backbone.Router.prototype, {
		initialize: function () {}	
	});
	bct.Module.extend = Backbone.Model.extend;

	var Modules = function () {
		this.modules = new Array;
	};	
	_.extend(Modules.prototype, Backbone.Events, {
		add: function (module) {
			this.modules.push(module);
		}
	});
	bct.modules = new Modules;

	bct.SidebarItem = Backbone.Model.extend({
		defaults: {
			'name': 'Application',
			'icon': 'gear64',
			'path': ''
		},

		initialize: function () {
			bct.Sidebar.register(this);
		},

		fetch: function () {},
		save: function () {},
		destroy: function () {}
	});

	bct.Registry = function () {
		this.items = new Array;
	};
	_.extend(bct.Registry.prototype, Backbone.Events, {
		register: function (item) {
			this.items.push(item);
		}
	});

	// Mix in each Underscore method as a proxy to `Collection#models`
	// This is borrowed from backbone.js http://documentcloud.github.com/backbone
	var underscore_methods = ['forEach', 'each', 'map', 'reduce', 'reduceRight', 'find', 'detect',
    'filter', 'select', 'reject', 'every', 'all', 'some', 'any', 'include',
    'contains', 'invoke', 'max', 'min', 'sortBy', 'sortedIndex', 'toArray', 'size',
    'first', 'rest', 'last', 'without', 'indexOf', 'lastIndexOf', 'isEmpty', 'groupBy'];
	_.each(underscore_methods, function(method) {
		bct.Registry.prototype[method] = function() {
			return _[method].apply(_, [this.items].concat(_.toArray(arguments)));
		};
	});

	bct.Sidebar = new bct.Registry;

	var Screens = function () {
		bct.Registry.call(this);
	};
	_.extend(Screens.prototype, bct.Registry.prototype, {
		activate: function (screen) {
			this.trigger('activate', screen);
		}
	});
	bct.screens = new Screens;

	bct.UserModel = Backbone.Model.extend({
		url: function () {
			return '/app/user';
		}
	});
	bct.current_user = new bct.UserModel();

	bct.initialize = function () {
		bct.current_user.fetch({success: function () {
				new TripOrganizer.TripsModule;
				new GearManager.GearModule;

				bct.sidebar = new SidebarView({
					el: $('#app_chooser_buttons')[0],
					model: BackcountryTracks.Sidebar
				});
				bct.sidebar.render();

				bct.mainview = new ScreensView({
					el: $('#main')[0],
					collection: BackcountryTracks.screens	
				});
				bct.mainview.render();

				Backbone.history.start();
			}
		});

	};

	root.BackcountryTracks = bct;
		
}).call(this);



