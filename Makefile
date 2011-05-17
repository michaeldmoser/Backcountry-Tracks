
dev-environ: install-services services-dev-config
	
services-dev-config: django nginx-config

install-services: install-rabbitmq install-riak install-nginx

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

config/nginx/nginx.conf: config/nginx.in/nginx.conf
	python tools/build-nginx-dev-config.py
	if test -d config && test ! -h config; then \
		sudo mv /etc/nginx /etc/nginx.bak && sudo ln -sf `pwd`/config/nginx /etc/nginx; \
	fi
	sudo /etc/init.d/nginx restart

config/nginx.in/nginx.conf:

/srv/www:
	sudo mkdir /srv/www
	chown -R `whoami`:`whoami` /srv/www

