from requests import get
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from contextlib import closing
import re

#first 2 functions modified from https://realpython.com/python-web-scraping-practical-introduction/
#get stuff from URL
def simpleGet(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if isGoodResponse(resp):
                return BeautifulSoup(resp.content,"html.parser")
            else:
                return None

    except RequestException as e:
        print(e)
#is the response from simple_get good?
def isGoodResponse(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

def getItems(url):
    items=simpleGet(url).findAll(attrs={"class": "_2_1T4"})

    arrReturn=[]
    # counter=0
    for i in items:
        # if counter>20:
        #     break
        # counter+=1
        arrReturn.append({})
        # arrReturn[-1]["price"]=i.find(attrs={"itemprop": "price"}).get("content")
        arrReturn[-1]["url"]=str("https://www.kogan.com"+str(i.select("a")[0].get("href")))
        itemPage=simpleGet(arrReturn[-1]["url"])
        itemAttrs=itemPage.findAll(attrs={"class": "react-sanfona-item-body"})
        for j in itemAttrs:
            if j.findAll(attrs={"class": "flFiV"}) != []:
                tags=j.findAll(attrs={"class": "flFiV"})
                values=j.findAll(attrs={"class": "EPROW"})
                for k in range(len(tags)):
                    if values[k].string != None:
                        arrReturn[-1][tags[k].string.lower()]=values[k].string
        #--------------------------------------------------------------
                arrReturn[-1]["name"]=i.select("h2")[0].string

                #adds the price of the item to the dictionary
                arrReturn[-1]["price"]=i.find(attrs={"itemprop": "price"}).get("content")

                #tries to get brand
                try:
                    arrReturn[-1]["brand"]=re.search(r'^[a-zA-Z]+', arrReturn[-1]["name"]).group(0)
                except:
                    pass

                #tries to get the refresh rate of the monitor
                try:
                    arrReturn[-1]["refreshRate"]=re.search(r'\d+',re.search(r'\d+Hz', arrReturn[-1]["name"],re.IGNORECASE).group(0)).group(0)
                except:
                    pass

                #tries to get panel type
                try:
                    # if "Philips" in arrReturn[-1]["name"]:
                    #     arrReturn[-1]["panelType"]=re.search(r'(va|ips|tn|oled|amoled|lcd|led)', arrReturn[-1]["name"][7:],re.IGNORECASE).group(0)
                    arrReturn[-1]["panelType"]=re.search(r'( va | ips | tn | oled | amoled | lcd | led )', arrReturn[-1]["name"],re.IGNORECASE).group(0).strip()
                except:
                    pass

                #tries to get the size of the monitor
                try:
                    #finds strings with pattern numbers, optional ".", optional numbers, (") or (') or ( inch)
                    arrReturn[-1]["screen size"]=re.search(r'\d+\.?\d*',(re.search(r'\d+\.?\d*(\"|\'| inch)', arrReturn[-1]["name"]).group(0))).group(0)
                except Exception as e:
                    pass

                #tries to get the resolution of the monitor
                try:
                    #tries to find strings with format numbers, optional space, x or X or multiplication symbol, numbers
                    arrReturn[-1]["resolution"]=re.search(r'\d{1,6}\s?(x|X|×)\s?\d{1,6}', arrReturn[-1]["name"]).group(0).replace(" ", "").replace("×", "x").replace("X", "x")
                except Exception as e:
                    try:
                        #looks for resolution names as backup
                        # arrReturn[-1]["resolution"]=re.search(r'(1080p|Full HD|UHD|QHD|2k|5k)', arrReturn[-1]["name"],re.IGNORECASE).group(0)
                        #converts resolution name to estimated resolution.
                        arrReturn[-1]["resolution"]=["3440x1440","1920x1080","1920x1080","1920x1080","3840x2160","2560x1440","3840x2160","2560x1440","5120x2880"][["wqhd","1080p","full hd","fhd","uhd","qhd","4k","2k","5k"].index(re.search(r'(wqhd|1080p|Full HD|fhd|UHD|QHD|4k|2k|5k)', arrReturn[-1]["name"],re.IGNORECASE).group(0).lower())]
                    except:
                        pass
        #------------------------------------------------------------------
                    # print(tags[k].string,values[k].string)
        # print(arrReturn[-1])
    return(arrReturn)


if __name__ == "__main__":
    import json
    print("getting items... this could take a while")
    items=getItems("https://www.kogan.com/au/shop/tablets-laptops/computer-monitors/?page=200")

    with open('data.json', 'w') as outfile:
        json.dump(items, outfile)
