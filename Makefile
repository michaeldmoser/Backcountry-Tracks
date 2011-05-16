
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

install-nginx: /etc/apt/sources.list.d/nginx-stable-natty.list /usr/sbin/nginx

/usr/sbin/nginx:
	sudo apt-get -y install nginx

/etc/apt/sources.list.d/nginx-stable-natty.list: /usr/bin/add-apt-repository
	sudo add-apt-repository ppa:nginx/stable
	sudo apt-get update

/usr/bin/add-apt-repository:
	sudo apt-get -y install python-software-properties

dev-environ: install-services
