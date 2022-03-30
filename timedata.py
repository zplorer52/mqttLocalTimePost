import sys
import os
import time
import json
import socket
import paho.mqtt.client as paho
from collections import namedtuple
from pathlib import Path

Connected = False
tclient = None


def isNetworkActive(ip=None, port=1883):
    flag = False
    if not ip or not port:
        return flag

    try:
        socket.setdefaulttimeout(20)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(
            (ip, port))
        flag = True
    except socket.error as err:
        print(str(e))
    except Exception as e:
        print(str(e))

    return flag

# configuration json parsing


def get_app_config(conf_name=None):
    """
    USAGE:
    print(obj.app[0].active, obj.app[0].comm)
    """
    conf_obj = None
    if conf_name is None:
        print("Valid confguration file required...")
        return conf_obj
    conf_name = str(Path.cwd())+"\\"+conf_name
    try:
        if os.path.exists(conf_name):
            with open(conf_name, 'r') as conf:
                app_conf = json.load(conf)
                json_str = json.dumps(app_conf)
                # parse json into an object with attributes corresponding to dict keys
                conf_obj = json.loads(
                    json_str, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    except SyntaxError as e:
        print("Parsing error: {}".format(str(e)))
    except Exception as e:
        print("File error: {}".format(str(e)))

    return conf_obj


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected
        Connected = True
    else:
        print("Connection falied!")


def on_publish(client, userdata, result):
    if result:
        print("data published \n")

    # print("Timestamp: {}".format(time.strftime('%m/%d/%Y %H:%M:%S', t)))


def main(flag=False):
    # get configuration file
    obj = get_app_config(conf_name="mqtt.json")
    # print(obj)
    if obj is None:
        print("No configuration file!")
        return None

    global tclient
    # create client object with name
    tclient = paho.Client(obj.clientid)
    user = obj.user
    passwd = obj.password
    if(user and passwd):
        # print(user,passwd)
        tclient.username_pw_set(user, password=passwd)

    # assign function to callback
    tclient.on_connect = on_connect
    tclient.on_publish = on_publish
    # establish connection
    try:
        if(isNetworkActive(obj.broker, obj.port)):
            tclient.connect(obj.broker, obj.port)
            tclient.loop_start()  # start the loop
            Connected = True
    except Exception as e:
        print(str(e))

    while(flag & Connected):
        t = time.localtime()
        hr, min, sec = t.tm_hour, t.tm_min, t.tm_sec

        if hr in range(23) and min in range(60) and sec in range(60):
            tdate = "{}".format(time.strftime(obj.fmtDate, t))
            ttime = "{}".format(time.strftime(obj.fmtTime, t))
            mqttFmt = {
                "tdate": tdate,
                "ttime": ttime
            }
            # convert into JSON:
            y = json.dumps(mqttFmt)
            # Post timestamp to the server as Json object
            if Connected:
                ret = tclient.publish(
                    topic=obj.topic, payload=y, qos=obj.qos, retain=obj.retain)
            time.sleep(obj.update)


if __name__ == "__main__":
    run_flag = True
    try:
        main(run_flag)
    except Exception as err:
        print(str(err))
    except KeyboardInterrupt:
        run_flag = False
        tclient.disconnect()
        tclient.loop_stop()
        # Connected =False
        print("Stopping...")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
