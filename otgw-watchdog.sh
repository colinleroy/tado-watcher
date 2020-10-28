#!/bin/bash
. /etc/default/tado-watcher

ERRCODE=$(echo "select value type from sensor join sensor_data on sensor.sensor_number = sensor_data.sensor_number where sensor.sensor_number=537458662 and sensor.protocol='otgw' and type='STAT_ERROR' order by timestamp desc limit 1;" |sqlite3 /home/pi/homecontrol/db/home-sensors.sqlite 2>/dev/null)

if [ "$ERRCODE" = "1" ]; then
	curl --header "Access-Token: $PUSHBULLET_TOKEN" \
	     --header 'Content-Type: application/json' \
	     --data-binary '{"body":"Heater error flag is up","title":"Heater error","type":"note"}' \
	     --request POST \
	     https://api.pushbullet.com/v2/pushes
fi
