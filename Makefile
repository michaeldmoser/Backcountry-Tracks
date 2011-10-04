
dev-environ: install-dependencies install-infrastructure install-libraries install-services infrastructure-dev-config testing-framework
	
infrastructure-dev-config: django nginx-config riak-config app-config

install-infrastructure: install-rabbitmq install-riak install-nginx

install-libraries: install-messaging install-plugins

install-services: install-groupleader install-adventurer2 install-gear install-trailhead install-adventurer varrun install-smokesignal install-trips

install-dependencies: install-libyaml install-python-setproctitle

install-libyaml: /usr/lib/libyaml.so /usr/include/yaml.h /usr/include/python2.7/Python.h

/usr/include/python2.7/Python.h:
	sudo aptitude install python-dev

/usr/lib/libyaml.so:
	sudo aptitude install libyaml-0-2

/usr/include/yaml.h:
	sudo aptitude install libyaml-dev

test: testing/bin/run_make_test
	sudo testing/bin/run_make_test

unittest: testing/bin/run_unittests.py
	python testing/bin/run_unittests.py

systest: testing/system
	cd testing/system && sudo python setup.py test

inttest: unittest testing/integration
	cd testing/integration && sudo python setup.py test

install-rabbitmq: /usr/sbin/rabbitmq-server

/usr/sbin/rabbitmq-server: /usr/bin/erl
	wget http://www.rabbitmq.com/releases/rabbitmq-server/v2.4.1/rabbitmq-server_2.4.1-1_all.deb
	sudo dpkg -i rabbitmq-server_2.4.1-1_all.deb
	rm rabbitmq-server_2.4.1-1_all.deb

/usr/bin/erl:
	sudo apt-get -y install erlang-nox

install-riak: /usr/sbin/riak
	
/usr/sbin/riak: /usr/bin/erl
	wget http://downloads.basho.com/riak/riak-0.14/riak_0.14.0-1_amd64.deb
	sudo dpkg -i riak_0.14.0-1_amd64.deb
	rm riak_0.14.0-1_amd64.deb
	sudo touch /usr/sbin/riak

riak-config: config/riak/app.config

config/riak/app.config: /usr/sbin/riak /usr/local/lib/python2.7/dist-packages/django config/riak.in/app.config config/riak.in/vm.args /srv/riak
	sudo /etc/init.d/riak stop
	python tools/build-riak-dev-config.py
	if test -d /etc/riak && test ! -h /etc/riak; then \
		sudo mv /etc/riak /etc/riak.bak && sudo ln -sf `pwd`/config/riak /etc/riak; \
	fi
	sudo /etc/init.d/riak start

config/riak.in/vm.args: 

config/riak.in/app.config:

/srv/riak:
	sudo cp -a /var/lib/riak /srv/riak

install-nginx: /usr/sbin/nginx

/usr/sbin/nginx: /etc/apt/sources.list.d/nginx-stable-natty.list
	sudo apt-get -y install nginx
	sudo touch /usr/sbin/nginx

/etc/apt/sources.list.d/nginx-stable-natty.list: /usr/bin/add-apt-repository
	sudo add-apt-repository ppa:nginx/stable
	sudo apt-get update

/usr/bin/add-apt-repository:
	sudo apt-get -y install python-software-properties

django: /usr/local/lib/python2.7/dist-packages/django

/usr/local/lib/python2.7/dist-packages/django:
	sudo pip install django

nginx-config: config/nginx/nginx.conf /srv/www

config/nginx/nginx.conf: /usr/sbin/nginx /usr/local/lib/python2.7/dist-packages/django config/nginx.in/nginx.conf
	python tools/build-nginx-dev-config.py
	if test -d /etc/nginx && test ! -h /etc/nginx; then \
		sudo mv /etc/nginx /etc/nginx.bak && sudo ln -sf `pwd`/config/nginx /etc/nginx; \
	fi
	sudo /etc/init.d/nginx restart

config/nginx.in/nginx.conf:

install-python-setproctitle: /usr/lib/pyshared/python2.7/setproctitle.so

/usr/lib/pyshared/python2.7/setproctitle.so:
	sudo apt-get install python-setproctitle

app-config: /etc/tripplanner/tpapp.yaml

/etc/tripplanner/tpapp.yaml: config/tpapp.yaml
	sudo mkdir /etc/tripplanner -p
	sudo ln -sf `pwd`/config/tpapp.yaml /etc/tripplanner/tpapp.yaml

config/tpapp.yaml:
	python tools/build-tpapp-dev-config.py

/srv/www: htdocs
	sudo ln -sf `pwd`/htdocs /srv/www
	sudo chown -R `whoami`:`whoami` /srv/www

testing-framework: robotframework tptesting systemtests integrationtests tptesting-config nginx-config-test js-testing-config

tptesting-config: /etc/tptesting.yaml

js-testing-config: testing/etc/jsTestDriver.conf

testing/etc/jsTestDriver.conf:
	python testing/bin/build-js-test-driver-conf.py

nginx-config-test: /srv/test

/srv/test:
	sudo ln -sf `pwd`/testing/javascript/public /srv/test
	sudo chown -R `whoami`:`whoami` /srv/test

/etc/tptesting.yaml: testing/etc/tptesting.yaml
	sudo ln -sf `pwd`/testing/etc/tptesting.yaml /etc/tptesting.yaml

testing/etc/tptesting.yaml:
	python testing/bin/build-testing-yaml.py

tptesting.yaml: 
	python testing/bin/build-testing-yaml.py

robotframework: /usr/local/bin/pybot /usr/local/lib/python2.7/dist-packages/robotframework_seleniumlibrary-2.7-py2.7.egg

/usr/local/bin/pybot:
	sudo easy_install robotframework

/usr/local/lib/python2.7/dist-packages/robotframework_seleniumlibrary-2.7-py2.7.egg:
	sudo easy_install robotframework-seleniumlibrary

testing/bin/run_unittests.py:

testing/bin/run_make_test:

systemtests: testing/system/TripPlannerSystemTesting.egg-info testing/system/setup.py

testing/system/TripPlannerSystemTesting.egg-info:
	cd testing/system && sudo python setup.py develop

testing/system/setup.py:
	cd testing/system && sudo python setup.py develop

integrationtests: testing/integration/TripPlannerIntegrationTesting.egg-info testing/integration/setup.py
	
testing/integration/TripPlannerIntegrationTesting.egg-info:
	cd testing/integration && sudo python setup.py develop

testing/integration/setup.py:
	cd testing/integration && sudo python setup.py develop

tptesting: testing/TripPlannerTestingLib/TripPlannerTestingLib.egg-info testing/TripPlannerTestingLib/setup.py

testing/TripPlannerTestingLib/TripPlannerTestingLib.egg-info:
	cd testing/TripPlannerTestingLib && sudo python setup.py develop

testing/TripPlannerTestingLib/setup.py:
	cd testing/TripPlannerTestingLib && sudo python setup.py develop

install-groupleader: services/GroupLeader/setup.py services/GroupLeader/GroupLeader.egg-info

services/GroupLeader/setup.py:
	cd services/GroupLeader && sudo python setup.py develop
	
services/GroupLeader/GroupLeader.egg-info:
	cd services/GroupLeader && sudo python setup.py develop

install-adventurer2: services/Adventurer2/setup.py services/Adventurer2/Adventurer2.egg-info

services/Adventurer2/setup.py:
	cd services/Adventurer2 && sudo python setup.py develop
	
services/Adventurer2/Adventurer2.egg-info:
	cd services/Adventurer2 && sudo python setup.py develop

install-gear: services/Gear/setup.py services/Gear/Gear.egg-info

services/Gear/setup.py:
	cd services/Gear && sudo python setup.py develop
	
services/Gear/Gear.egg-info:
	cd services/Gear && sudo python setup.py develop

install-trips: services/Trips/setup.py services/Trips/Trips.egg-info

services/Trips/setup.py:
	cd services/Trips && sudo python setup.py develop
	
services/Trips/Trips.egg-info:
	cd services/Trips && sudo python setup.py develop

install-trailhead: services/TrailHead/setup.py services/TrailHead/TrailHead.egg-info

services/TrailHead/setup.py:
	cd services/TrailHead && sudo python setup.py develop
	
services/TrailHead/TrailHead.egg-info:
	cd services/TrailHead && sudo python setup.py develop

install-adventurer: services/Adventurer/setup.py services/Adventurer/Adventurer.egg-info

services/Adventurer/setup.py:
	cd services/Adventurer && sudo python setup.py develop

services/Adventurer/Adventurer.egg-info:
	cd services/Adventurer && sudo python setup.py develop

install-smokesignal: services/SmokeSignal/setup.py services/SmokeSignal/SmokeSignal.egg-info
	
services/SmokeSignal/setup.py: 
	cd services/SmokeSignal && sudo python setup.py develop
	
services/SmokeSignal/SmokeSignal.egg-info:
	cd services/SmokeSignal && sudo python setup.py develop

install-messaging: lib/Messaging/setup.py lib/Messaging/BackcountryTracks_Messaging.egg-info

lib/Messaging/setup.py:
	cd lib/Messaging && sudo python setup.py develop
	
lib/Messaging/BackcountryTracks_Messaging.egg-info:
	cd lib/Messaging && sudo python setup.py develop

install-plugins: lib/Plugins/setup.py lib/Plugins/BackcountryTracks_Plugins.egg-info

lib/Plugins/setup.py:
	cd lib/Plugins && sudo python setup.py develop
	
lib/Plugins/BackcountryTracks_Plugins.egg-info:
	cd lib/Plugins && sudo python setup.py develop

varrun: /var/run/tripplanner

/var/run/tripplanner:
	sudo mkdir /var/run/tripplanner
	sudo chown `whoami` /var/run/tripplanner


