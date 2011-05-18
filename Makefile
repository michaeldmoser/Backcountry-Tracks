
dev-environ: install-services services-dev-config testing-framework
	
services-dev-config: django nginx-config riak-config

install-services: install-rabbitmq install-riak install-nginx

unittest: tests/bin/run-unittests.py
	python tests/bin/run-unittests.py

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

/srv/www:
	sudo mkdir /srv/www
	sudo chown -R `whoami`:`whoami` /srv/www

testing-framework: robotframework

robotframework: /usr/local/bin/pybot /usr/local/lib/python2.7/dist-packages/robotframework_seleniumlibrary-2.7-py2.7.egg

/usr/local/bin/pybot:
	sudo easy_install robotframework

/usr/local/lib/python2.7/dist-packages/robotframework_seleniumlibrary-2.7-py2.7.egg:
	sudo easy_install robotframework-seleniumlibrary

tests/bin/run-unittests.py:

