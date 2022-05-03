import time
import requests
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import start_http_server
import socket
import os

# Credential Comfiguration
username = os.getenv('username')
password = os.getenv('password')
url= os.getenv("url") ### Url of Stream data http://node_media_server_ip:port/api/streams

#scrape Time
scrape_time=int(os.getenv("scrape_time"))


#Standard Resouloutions -- sd,hd,fhd
standard_height=[480,720,1080]
# standard_width=[640,1280,1920]
#get hostname for instance name
instance=socket.gethostname()

def getMetrics():

    global sd
    global hd
    global fhd
    global unknown
    global livestream_count
    sd = 0
    hd = 0
    fhd = 0
    unknown = 0
    response = requests.get(url, auth=(username, password))
    if response.status_code == 200:
        print(response)
    else:
        print("you get ",response.status_code, "response code, check your information")
        exit()

    responseDict=response.json()
    livestream=responseDict.get('livestream')
    livestream_count=(len(livestream))
    data = list(livestream.values())
    for i in range((livestream_count)):
        streamer_data=data[i]
        publisher_data=streamer_data.get("publisher")
        video= publisher_data.get("video")
        width= video.get("width")
        height= video.get("height")
        if height in standard_height:
            match width:
                case 640:
                        if width == 640:
                            sd = sd + 1               
                case 1280:
                        if width == 1280:
                            hd = hd + 1
                case 1920:
                        if width == 1280:
                            fhd = fhd + 1
                case _:
                    unknown= unknown+1
        else:
            unknown= unknown+1


class prometheusCollector(object):
    def __init__(self):
        pass
    def collect(self):
        getMetrics()

        livestreams_total = GaugeMetricFamily("livestreams_total", 'Help text', labels=["instance"])
        livestreams_total.add_metric([instance], livestream_count)
        yield livestreams_total
        sd_streams = GaugeMetricFamily("SD_Streams", 'Help text', labels=["instance"])
        sd_streams.add_metric([instance], sd)
        yield sd_streams
        hd_streams = GaugeMetricFamily("HD_Streams", 'Help text', labels=["instance"])
        hd_streams.add_metric([instance], hd)
        yield hd_streams
        fhd_streams = GaugeMetricFamily("Full_HD_Streams", 'Help text', labels=["instance"])
        fhd_streams.add_metric([instance], fhd)
        yield fhd_streams
        Unknown_streams = GaugeMetricFamily("Unknown_Streams", 'Help text', labels=["instance"])
        Unknown_streams.add_metric([instance], unknown)
        yield Unknown_streams                
if __name__ == '__main__':
    start_http_server(8000)

    REGISTRY.register(prometheusCollector())
    while True:
        getMetrics()
        time.sleep(scrape_time)