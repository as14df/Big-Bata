# Address Validation

## Pull Docker Images
### Pull Docker Image with Hadoop
	docker pull marcelmittelstaedt/spark_base:latest

### Pulocker Image with Airflow
	docker pull marcelmittelstaedt/airflow:latest

## Start Docker Images
### Start Docker Image Hadoop
	docker run -dit --name hadoop \
		-p 8088:8088 -p 9870:9870 -p 9864:9864 -p 10000:10000 \
		-p 8032:8032 -p 8030:8030 -p 8031:8031 -p 9000:9000 \
		-p 8888:8888 --net bigdatanet \
		marcelmittelstaedt/spark_base:latest

### Start Docker Image Airflow
	docker run -dit --name airflow \
		-p 8080:8080 \
		--net bigdatanet \
		marcelmittelstaedt/airflow:latest

## Start Hadoop
## Open Hadoop container bash
	docker exec -it hadoop bash

### Switch to hadoop user
	sudo su hadoop
	cd

### Start Hadoop Cluster
	start-all.sh

### Start HiveServer2
	hiveserver2

## Start second ssh connection

### Start Airflow
	docker exec -it airflow bash

### Install nano
	apt-get install nano

### Switch to airflow user
	sudo su airflow
	cd

### Open Dag File
	nano /home/airflow/airflow/dags/example_dag.py

### Open Airflow
	http://35.242.192.148:8080/admin/

## restart airflow
	docker stop airflow
	docker restart airflow

# WebApp in Node Js Container

https://codeburst.io/build-a-weather-website-in-30-minutes-with-node-js-express-openweather-a317f904897b

## Create local directory for app
	mkdir webapp
	cd webapp

## install nano + npm
	apt-get update
	apt-get install nano
	sudo apt install npm

## init app
	npm init

## install dependencies
	npm install ejs --save
	npm install mysql

## create server.js file
	nano server.js

	var express = require('express');
	var app = express();
	app.get('/', function(req, res) {
	    res.setHeader('Content-Type', 'text/plain');
	    res.end('You\'re in reception');
	});
	app.use(function(req, res, next){
	    res.setHeader('Content-Type', 'text/plain');
	    res.send(404, 'Page cannot be found!');
	});
	app.listen(8080);

## create folder views
	mkdir views
	cd views

## create html/ejs file index.ejs
	nano index.js

	<!DOCTYPE html>
	<html>
	  <head>
	    <meta charset="utf-8">
	    <title>Test</title>
	    <link rel="stylesheet" type="text/css" href="/css/style.css">
	    <link href='https://fonts.googleapis.com/css?family=Open+Sans:300' rel='stylesheet' type='text/css'>
	  </head>
	  <body>
	    <div class="container">
	      <fieldset>
	        <form action="/" method="post">
	          <input name="city" type="text" class="ghost-input" placeholder="Enter a City" required>
	          <input type="submit" class="ghost-button" value="Get Weather">
	        </form>
	      </fieldset>
	    </div>
	  </body>
	</html>

## Run server
	node server.js

## Create Dockerfile
	touch Dockerfile

	FROM node:10
	# Create app directory
	WORKDIR /usr/src/wepapp
	# Install app dependencies
	# A wildcard is used to ensure both package.json AND package-lock.json are copied
	# where available (npm@5+)
	COPY . /
	RUN npm install
	# If you are building your code for production
	# RUN npm ci --only=production
	# Bundle app source
	COPY . .
	EXPOSE 3000	
	CMD [ "node", "server.js" ]

## start docker
	sudo service docker start

## Build Image
	docker build -t as14df/node-web-app .

## run nodejs container
	docker run -p 3000:3000 --name webapp --net bigdatanet -d as14df/node-web-app


# Mysql Container

## mysql container
	docker run -d --name mysql --net bigdatanet -e MYSQL_USER=as14df -e MYSQL_PASSWORD=XXX -e MYSQL_ROOT_PASSWORD=XXX -p 3306:3306 mysql

// bei container bau: --net bigdatanet für container kommunikation untereinander

## nachträglich netzwerk änderm
	docker network connect bigdatanet mysql
	docker inspect bigdatanet

## Wenn bei Nodejs permission denied kommt: 
	mysql -u root -p

	ALTER USER 'root' IDENTIFIED WITH mysql_native_password BY 'admin123';
	flush privileges;

## bei fehler No module named 'MySQLdb' 
	pip3 install mysqlclient

## wenn pyhive fehlt
	pip3 install pyhive

## wenn sasl fehlt
	pip3 install sasl
	apt install python-dev
	apt-get install libsasl2-dev
	apt-get install build-essential
	pip3 install apache-airflow[all] <-- geht
	pip3 install apache-airflow[mysql] <-- geht vielleicht

	pip3 install psycopg2-binary


# WebApp

## docker container
	docker pull node
	docker run -p 3000:3000 --name webapp --net bigdatanet node 


## folder in container anlegen
	npm install -g express-generator

	express bigdataapp //erstellt app

	cd bigdataapp

	npm install //installiert dependencies

	npm start //start server

	npm install body-parser

# docker save container

	docker commit <containerid> <save-as-imagename>
	docker commmit webapp as14df/node-web-app

	docker push as14df/node-web-app:latest


	docker tag node-web-app as14df/node-web-app:latest

# import the exported tar ball:
	cat /home/export.tar | sudo docker import - busybox-1-export:latest
