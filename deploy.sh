#!/usr/bin/env bash

git pull

if [[ "${VIRTUAL_ENV}" != "" ]]
then
    pip install -r requirements.txt
    pip install -U git+git://github.com/IRC-SPHERE/HyperStream.git#egg=hyperstream
else
    pip install -r requirements.txt --user
    pip install -U git+git://github.com/IRC-SPHERE/HyperStream.git#egg=hyperstream --user
fi

if pgrep -x "httpd" > /dev/null
then
    sudo service httpd restart
elif pgrep -x "apache2" > /dev/null
then
    sudo service apache2 restart
fi
