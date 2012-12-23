
dev-environ: install-dependencies install-infrastructure install-libraries install-services infrastructure-dev-config testing-framework webroot
	
infrastructure-dev-config: django nginx-config riak-config app-config

install-infrastructure: install-rabbitmq install-riak install-nginx

install-libraries: install-bctks install-messaging install-plugins install-servicelib install-gpsutils install-glbldb

install-services: install-groupleader install-adventurer install-gear install-trailhead varrun install-smokesignal install-trips install-postoffice install-gpsbabel install-messagingservices 

install-dependencies: install-libyaml install-python-setproctitle install-python-packages

install-libyaml: /usr/lib/libyaml.so /usr/include/yaml.h /usr/include/python2.7/Python.h

install-python-packages: python-defer

python-defer: /usr/lib/python2.7/dist-packages/defer

/usr/lib/python2.7/dist-packages/defer:
	sudo apt-get -y install python-defer

/usr/include/python2.7/Python.h:
	sudo aptitude install python-dev

/usr/lib/libyaml.so:
	sudo aptitude install libyaml-0-2

/usr/include/yaml.h:
	sudo aptitude install libyaml-dev

test: smalltests mediumtests largetests 

unittest: testing/bin/run_unittests.py
	python testing/bin/run_unittests.py

smalltests: testing/bin/run_unittests.py
	sudo python testing/bin/run_unittests.py

mediumtests: testing/bin/run_mediumtests.py
	sudo python testing/bin/run_mediumtests.py

largetests: testing/bin/run_largetests.py
	sudo python testing/bin/run_largetests.py

systest: testing/system
	cd testing/system && sudo python setup.py test

inttest: unittest testing/integration
	cd testing/integration && sudo python setup.py test

acceptance: testing/acceptance
	sudo pybot testing/acceptance

webroot: /srv/www
	sudo python tools/build-webroot.py

install-gpsbabel: /usr/bin/gpsbabel

/usr/bin/gpsbabel:
	sudo apt-get -y install gpsbabel

install-rabbitmq: /usr/sbin/rabbitmq-server

/usr/sbin/rabbitmq-server: /usr/bin/erl
	wget http://www.rabbitmq.com/releases/rabbitmq-server/v2.8.7/rabbitmq-server_2.8.7-1_all.deb
	sudo dpkg -i rabbitmq-server_2.8.7-1_all.deb
	rm rabbitmq-server_2.8.7-1_all.deb

/usr/bin/erl:
	sudo apt-get -y install erlang-nox

install-riak: /usr/sbin/riak
	
/usr/sbin/riak: /usr/bin/erl
	wget http://downloads.basho.com.s3-website-us-east-1.amazonaws.com/riak/CURRENT/ubuntu/precise/riak_1.2.1-1_amd64.deb
	sudo dpkg -i riak_1.2.1-1_amd64.deb
	rm riak_1.2.1-1_amd64.deb
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

robotframework: /usr/local/bin/pybot /usr/local/lib/python2.7/dist-packages/robotframework_seleniumlibrary-2.8.egg-info 

/usr/local/bin/pybot:
	sudo easy_install robotframework

/usr/local/lib/python2.7/dist-packages/robotframework_seleniumlibrary-2.8.egg-info:
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

install-adventurer: services/Adventurer/setup.py services/Adventurer/Adventurer.egg-info

services/Adventurer/setup.py:
	cd services/Adventurer && sudo python setup.py develop
	
services/Adventurer/Adventurer.egg-info:
	cd services/Adventurer && sudo python setup.py develop

install-messagingservices: services/MessagingServices/setup.py services/MessagingServices/MessagingServices.egg-info

services/MessagingServices/setup.py:
	cd services/MessagingServices && sudo python setup.py develop
	
services/MessagingServices/MessagingServices.egg-info:
	cd services/MessagingServices && sudo python setup.py develop

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

install-postoffice: services/PostOffice/setup.py services/PostOffice/PostOffice.egg-info

services/PostOffice/setup.py:
	cd services/PostOffice && sudo python setup.py develop
	
services/PostOffice/PostOffice.egg-info:
	cd services/PostOffice && sudo python setup.py develop

install-trailhead: services/TrailHead/setup.py services/TrailHead/TrailHead.egg-info

services/TrailHead/setup.py:
	cd services/TrailHead && sudo python setup.py develop
	
services/TrailHead/TrailHead.egg-info:
	cd services/TrailHead && sudo python setup.py develop

install-smokesignal: services/SmokeSignal/setup.py services/SmokeSignal/SmokeSignal.egg-info
	
services/SmokeSignal/setup.py: 
	cd services/SmokeSignal && sudo python setup.py develop
	
services/SmokeSignal/SmokeSignal.egg-info:
	cd services/SmokeSignal && sudo python setup.py develop

install-bctks: lib/BcTks/setup.py lib/BcTks/BackcountryTracks_Infrastructure.egg-info

lib/BcTks/setup.py:
	cd lib/BcTks && sudo python setup.py develop
	
lib/BcTks/BackcountryTracks_Infrastructure.egg-info:
	cd lib/BcTks && sudo python setup.py develop

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

install-servicelib: lib/Services/setup.py lib/Services/BackcountryTracks_Services.egg-info

lib/Services/setup.py:
	cd lib/Services && sudo python setup.py develop
	
lib/Services/BackcountryTracks_Services.egg-info:
	cd lib/Services && sudo python setup.py develop

install-gpsutils: lib/GPSUtils/setup.py lib/GPSUtils/GPSUtils.egg-info

lib/GPSUtils/setup.py:
	cd lib/GPSUtils && sudo python setup.py develop
	
lib/GPSUtils/GPSUtils.egg-info:
	cd lib/GPSUtils && sudo python setup.py develop

install-glbldb: lib/GlobalDatabase/setup.py lib/GlobalDatabase/GlobalDatabase.egg-info

lib/GlobalDatabase/setup.py:
	cd lib/GlobalDatabase && sudo python setup.py develop
	
lib/GlobalDatabase/GlobalDatabase.egg-info:
	cd lib/GlobalDatabase && sudo python setup.py develop


varrun: /var/run/tripplanner

/var/run/tripplanner:
	sudo mkdir /var/run/tripplanner
	sudo chown `whoami` /var/run/tripplanner

devreset:
	sudo python testing/bin/start-services.py


