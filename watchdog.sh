#!/bin/bash

RUNNING=$(ps aux|grep python.*tado-watcher|grep -v grep)
if [ "$RUNNING" = "" ]; then
	echo Restarting tado-watcher
	sudo /etc/init.d/tado-watcher stop
	sudo /etc/init.d/tado-watcher start
fi
