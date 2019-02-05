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

def getMonitors(html):
    items=html.findAll(attrs={"class": "_2_1T4"})
    arrReturn=[]
    # dictReturn={}
    for i in items:
        # print(i,"\n")
        #process an item each loop
        #adds an empty dictionary to the end of the array
        arrReturn.append({})

        #adds the name of the item to the dictionary
        arrReturn[-1]["name"]=i.select("h2")[0].string

        #gets url
        arrReturn[-1]["url"]=i.select("a")[0].get("href")

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
            arrReturn[-1]["size"]=re.search(r'\d+\.?\d*',(re.search(r'\d+\.?\d*(\"|\'| inch)', arrReturn[-1]["name"]).group(0))).group(0)
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

        if "monitor" in arrReturn[-1]["name"].lower() or "display" in arrReturn[-1]["name"].lower():
            pass
        else:
            pass
            # print(arrReturn[-1])
    return(arrReturn)

def getTV(html):
    items=html.findAll(attrs={"class": "_2_1T4"})
    print(items)

def goSearch(category):
    if category == "computer-monitors":
        return(getMonitors(simpleGet("https://www.kogan.com/au/shop/tablets-laptops/computer-monitors/?page=200")))
    elif category == "LEDTVs":
        return(getMonitors(simpleGet("https://www.kogan.com/au/shop/televisions/led-tv/?page=200")))
    else:
        strError=str(category)+" is not a valid category."
        raise KeyError(strError)

for i in goSearch("computer-monitors"):
    print(i)


# for i in (getMonitors(simpleGet("https://www.kogan.com/au/shop/televisions/?page=200"))):
#     print(i)
    # try:
    #     if i["resolution"]=="3840x2160":
    #         print(i["brand"],i["price"],i["size"],i["url"])
    # except:
    #     pass
    # # try:
    #     if i["resolution"]=="3840x2160":
    #         print(i["size"],i["price"])
    # except:
    #     pass
# getPageProducts(simpleGet("https://www.kogan.com/au/shop/tablets-laptops/computer-monitors/?order_by=price&facet-monitor-resolution-filterable=Ultrawide%20QHD&page=10"))
# counter=0
# counterInvalid=0
# for i in getMonitors(simpleGet("https://www.kogan.com/au/shop/tablets-laptops/computer-monitors/?page=200")):
#     print(i)
