import re
import csv
import urllib.request
from bs4 import BeautifulSoup
import requests as req
import time

#start command
#C:\Users\REI\Documents\Programs\.venv\Scripts\python.exe C:\Users\REI\Documents\Programs\Python\earthquake.py

TOKEN = 'your token'
api_url = 'https://notify-api.line.me/api/notify'

output_file = "earthquake.csv"
output_file_old = "earthquake_old.csv"

header = ["イベントID","地震発生場所","地震発生時刻","観測点で地震を検知した時刻","緯度","経度",
          "マグニチュード","県名称","市町村名称","最大震度","震度観測点の情報"]

while True:
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(header)

            url = "http://www.data.jma.go.jp/developer/xml/feed/eqvol.xml"
            res = urllib.request.urlopen(url).read()
            soup = BeautifulSoup(res,features="html.parser")

            search = re.compile('.*VXSE.*')

            count = 0

            for vxse in soup.find_all(text=search):
                if count == 0:

                    res = urllib.request.urlopen(vxse).read()
                    soup = BeautifulSoup(res,features="html.parser")

                    event_id = soup.find("eventid").text

                    headline = soup.find("headline").text

                    for content in soup.find_all("body"):
                        earthquake = content.find("earthquake")

                        if earthquake is not None:
                            location = earthquake.find("name").text
                            origintime = earthquake.find("origintime").text
                            arrivaltime = earthquake.find("arrivaltime").text

                            coordinate = earthquake.find("jmx_eb:coordinate").text
                            lat = coordinate[1:coordinate[1:].find("+") + 1]
                            lon = coordinate[coordinate[1:].find("+") + 2:coordinate[1:].find("+") + 7]
                            lat = int(lat[0:2])+(int(lat[3:])/60)+(0/3600)
                            lon = int(lon[0:3])+(int(lon[4:])/60)+(0/3600)
                            magnitude = earthquake.find("jmx_eb:magnitude").text

                        intensity = content.find("intensity")
                        if intensity is not None:
                            for pref in intensity.find_all("pref"):

                                prefectuer = pref("name")[0].text

                                for city in pref.find_all("city"):
                                    city_name = city("name")[0].text
                                    maxint = city("maxint")[0].text

                                    write_list = []
                                    write_list.append(event_id)
                                    write_list.append(location)
                                    write_list.append(origintime)
                                    write_list.append(arrivaltime)
                                    write_list.append(lat)
                                    write_list.append(lon)
                                    write_list.append(magnitude)
                                    write_list.append(prefectuer)
                                    write_list.append(city_name)
                                    write_list.append(maxint)

                                    intensity_station = ""
                                    for intensitystation in pref.find_all("intensitystation"):
                                        intensity_station = intensity_station + intensitystation("name")[0].text + " "

                                    write_list.append(intensity_station)

                                    writer.writerow(write_list)
                    count+=1
                else:
                    break
            f.close()
        with open(output_file, 'r',encoding="utf-8_sig") as f:
            file_read1=f.read()
            f.close()
        with open(output_file_old, 'r',encoding="utf-8_sig") as f:
            file_read2=f.read()
            f.close()

        if file_read1 != file_read2:
            mag=float(magnitude)
            if mag >=5:
                urls=f'https://www.google.com/maps/@{lat},{lon},8z?authuser=0'
                send_contents=f"""\n{headline}\n地震発生場所:{location}\n発生時刻:{origintime}\n北緯:{lat} 東経:{lon}
                                    \nマグニチュード:{magnitude}\n県名称:{prefectuer} 市町村名称:{city_name} 最大震度:{maxint}\n URL:{urls}"""
                print(send_contents)
                TOKEN_dic = {'Authorization': 'Bearer'+' '+TOKEN}
                send_dic = {'message': send_contents}
                try:
                    req.post(api_url, headers=TOKEN_dic, data=send_dic)
                except Exception as e:
                    print(f"Error {e}")
                with open(output_file_old,'w',encoding="utf-8_sig") as f:
                    f.write(file_read1)
                    f.close()
            else:
                with open(output_file_old,'w',encoding="utf-8_sig") as f:
                    f.write(file_read1)
                    f.close()
        else:
            pass
    except Exception as e:
        print(f"Error {e}")

    time.sleep(60)
