#!/usr/bin/python3

import click
import libtado.api
import requests
import re
import time
import syslog
from pushbullet import Pushbullet

@click.command()
@click.option('--username', '-u', required=True, envvar='TADO_USERNAME', help='Tado username')
@click.option('--password', '-p', required=True, envvar='TADO_PASSWORD', help='Tado password')
@click.option('--pushbullettoken', '-t', required=True, envvar='PUSHBULLET_TOKEN', help='Pushbullet token for pushing alerts')
def main(username, password, pushbullettoken):
    """
    This script provides a command line client for the Tado API.
    You can use the environment variables TADO_USERNAME and TADO_PASSWORD
    instead of the command line options.
    Call 'tado COMMAND --help' to see available options for subcommands.
    """

    secret = get_secret()
    t = libtado.api.Tado(username, password, secret)
    
    pb = Pushbullet(pushbullettoken)

    while True:
        zones = t.get_zones()
        for zone in zones:
            if zone["type"] == "HEATING":
                state = t.get_state(zone["id"])
                if state["overlayType"] == "MANUAL":
                    manual_setting_alert(zone, state, pb)
                if state["link"]["state"] != "ONLINE":
                    offline_alert(zone, state, pb)
        time.sleep(300)


def get_secret():
    url = "https://my.tado.com/webapp/env.js"

    r = requests.get(url, stream=True)
    for line in r.iter_lines():
        line = line.decode('utf-8', 'replace')
        if "clientSecret: " in line:
            m = re.search("'(.+?)'", line)
            if m:
                secret = m.group(1)
                return secret

    return None

manual_alerts = {}
def manual_setting_alert(zone, state, pb):
    if zone["id"] not in manual_alerts or time.time() - manual_alerts[zone["id"]] > 3600:
        alert = "Zone {} has been manually set to {}".format(
            zone["name"], state["overlay"]["setting"]["temperature"]["celsius"])
        syslog.syslog(alert)
        push_alert(alert, pb)
        manual_alerts[zone["id"]] = time.time()

offline_alerts = {}
def offline_alert(zone, state, pb):
    if zone["id"] not in offline_alerts or time.time() - offline_alerts[zone["id"]] > 3600:
        alert = "Zone {} is not online: {}".format(
            zone["name"], state["link"]["state"])
        syslog.syslog(alert)
        push_alert(alert, pb)
        offline_alerts[zone["id"]] = time.time()

def push_alert(alert, pb):
    pb.push_note("Tado alert", alert)

main()
