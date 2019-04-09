from requests import get
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from contextlib import closing
import re


# first 2 functions modified from https://realpython.com/python-web-scraping-practical-introduction/
# get stuff from URL
def simpleGet(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if isGoodResponse(resp):
                return BeautifulSoup(resp.content, "html.parser")
            else:
                return None

    except RequestException as e:
        print(e)


# is the response from simple_get good?
def isGoodResponse(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

def representsInt(string):
    try:
        int(string)
        return(True)
    except:
        return(False)

def representsFloat(string):
    try:
        float(string)
        return(True)
    except:
        return(False)

def convertToIntFloat(string):
    if representsInt(string):
        return(int(string))
    elif representsFloat(string):
        return(float(string))

def representsNumeric(string):
    if representsInt(string) or representsFloat(string):
        return(True)
    else:
        return(False)

def getItems(url):
    items = simpleGet(url).findAll(attrs={"class": "_2_1T4"})

    arrReturn = []
    counter = 0
    for i in items:
        # if counter > 80:
        #     break
        counter += 1
        arrReturn.append({})
        # arrReturn[-1]["price"]=i.find(attrs={"itemprop": "price"}).get("content")
        arrReturn[-1]["url"] = str("https://www.kogan.com" + str(i.select("a")[0].get("href")))
        itemPage = simpleGet(arrReturn[-1]["url"])
        itemAttrs = itemPage.findAll(attrs={"class": "react-sanfona-item-body"})
        for j in itemAttrs:
            if j.findAll(attrs={"class": "flFiV"}) != []:
                tags = j.findAll(attrs={"class": "flFiV"})
                values = j.findAll(attrs={"class": "EPROW"})
                for k in range(len(tags)):
                    if values[k].string != None:
                        arrReturn[-1][tags[k].string.lower()] = values[k].string

                arrReturn[-1]["name"] = i.select("h2")[0].string

                # adds the price of the item to the dictionary
                arrReturn[-1]["price"] = i.find(attrs={"itemprop": "price"}).get("content")

                # tries to get brand
                try:
                    arrReturn[-1]["brand"] = re.search(r'^[a-zA-Z]+', arrReturn[-1]["name"]).group(0)
                except:
                    pass

                # tries to get the refresh rate of the monitor
                try:
                    arrReturn[-1]["refreshRate"] = re.search(r'\d+', re.search(r'\d+Hz', arrReturn[-1]["name"],
                                                                               re.IGNORECASE).group(0)).group(0)
                except:
                    pass

                # tries to get panel type
                try:
                    arrReturn[-1]["panelType"] = re.search(r'( va | ips | tn | oled | amoled | lcd | led )',
                                                           arrReturn[-1]["name"], re.IGNORECASE).group(0).strip()
                except:
                    pass

                # tries to get the size of the monitor
                try:
                    # finds strings with pattern numbers, optional ".", optional numbers, (") or (') or ( inch)
                    arrReturn[-1]["screen size"] = re.search(r'\d+\.?\d*', (
                        re.search(r'\d+\.?\d*(\"|\'| inch)', arrReturn[-1]["name"]).group(0))).group(0)
                except Exception as e:
                    pass

                # tries to get the resolution of the monitor
                try:
                    # tries to find strings with format numbers, optional space, x or X or multiplication symbol, numbers
                    arrReturn[-1]["resolution"] = re.search(r'\d{1,6}\s?(x|X|×)\s?\d{1,6}',
                                                            arrReturn[-1]["name"]).group(0).replace(" ", "").replace(
                        "×", "x").replace("X", "x")
                except Exception as e:
                    try:
                        # converts resolution name to estimated resolution.
                        arrReturn[-1]["resolution"] = \
                        ["3440x1440", "1920x1080", "1920x1080", "1920x1080", "3840x2160", "2560x1440", "3840x2160",
                         "2560x1440", "5120x2880"][
                            ["wqhd", "1080p", "full hd", "fhd", "uhd", "qhd", "4k", "2k", "5k"].index(
                                re.search(r'(wqhd|1080p|Full HD|fhd|UHD|QHD|4k|2k|5k)', arrReturn[-1]["name"],
                                          re.IGNORECASE).group(0).lower())]
                    except:
                        pass

        # this section of the program cleans up a few of the keys
        arrYes = []
        arrNo = []
        dictionary = dict(arrReturn[-1])
        for key, content in dictionary.items():
            # if the content of a key is simply "yes" or "no", the key gets added to an array arrYes or arrNo. These
            # are then stored under the keys "present-attributes" and "absent-attributes" respectively.
            if content.lower() == "yes":
                arrYes.append(key)
                del arrReturn[-1][key]
            elif content.lower() == "no":
                del arrReturn[-1][key]
                arrNo.append(key)

            # This section converts all numeric values to numbers so they are easier to work with
            if representsInt(content):
                arrReturn[-1][key] = int(content)
            elif representsFloat(content):
                arrReturn[-1][key] = float(content)

            # any string which appears like a list will be broken into a list, as long as it isn't in the
            # "dimensions" key, as this is processed separately.
            if len(re.split(r', ',content))!=1 and key != "dimensions":
                arrReturn[-1][key]=re.split(r', | and ',content)


        # some items have a features key. This is simply added to arrYes, and included with "present-attributes" for
        # simplicity.
        if "features" in dictionary:
            for i in arrReturn[-1]["features"]:
                arrYes.append(i)
            del arrReturn[-1]["features"]

        if arrYes != []:
            arrReturn[-1]["present-attributes"] = arrYes
        if arrNo != []:
            arrReturn[-1]["absent-attributes"] = arrNo


        #this section of the code processes the dimensions of the item.
        if "dimensions" in dictionary:
            arrDimensions=re.findall(r'\d+\.?\d*',dictionary["dimensions"])
            arrDimensions=[convertToIntFloat(i) for i in arrDimensions]

            if len(arrDimensions)==3:
                arrReturn[-1]["dimensions"]={"with stand":arrDimensions}
            elif len(arrDimensions)==6:
                if arrDimensions[0]<arrDimensions[3] or arrDimensions[1]<arrDimensions[4] or arrDimensions[2]<arrDimensions[5]:
                    arrReturn[-1]["dimensions"]={"without stand":arrDimensions[:3],
                                                 "with stand":arrDimensions[3:6]}
                else:
                    arrReturn[-1]["dimensions"] = {"with stand": arrDimensions[:3],
                                                   "without stand": arrDimensions[3:6]}
            else:
                arrWithStand=[re.sub(r'[^\d^\.]','-',i.replace(" ","")) for i in re.findall(r'\d[^xX×]+\d',re.findall(r'\d[^[a-wy-zA-WY-Z]+\d',dictionary["dimensions"])[0])]

                for index,i in enumerate(arrWithStand):
                    if not representsNumeric(i):
                        arrWithStand[index]=[convertToIntFloat(j) for j in re.findall(r'\d+\.?\d*',i)]

                        arrWithStand=[{"True":convertToIntFloat(j),"False":j}[str(representsNumeric(j))] for j in arrWithStand]

                        arrWithoutStand=[convertToIntFloat(i) for i in re.findall(r'\d+\.?\d*',dictionary["dimensions"])][-3:]

                        arrReturn[-1]["dimensions"] = {"without stand": arrWithoutStand,
                                                       "with stand": arrWithStand}

                        break


        elif 'with stand' and 'without stand' in dictionary:

            arrWithStand = re.findall(r'\d+\.?\d*', dictionary["with stand"])
            arrWithStand = [convertToIntFloat(i) for i in arrWithStand]

            arrWithoutStand = re.findall(r'\d+\.?\d*', dictionary["without stand"])
            arrWithoutStand = [convertToIntFloat(i) for i in arrWithoutStand]

            arrReturn[-1]["dimensions"] = {"without stand": arrWithoutStand,
                                           "with stand": arrWithStand}
        elif "with stand" or 'without stand' in dictionary:
            if 'with stand' in dictionary:
                arrWithStand = re.findall(r'\d+\.?\d*', dictionary["with stand"])
                arrWithStand = [convertToIntFloat(i) for i in arrWithStand]
                arrReturn[-1]["dimensions"] = {"with stand": arrWithStand}
            if 'without stand' in dictionary:
                arrWithoutStand = re.findall(r'\d+\.?\d*', dictionary["without stand"])
                arrWithoutStand = [convertToIntFloat(i) for i in arrWithoutStand]
                arrReturn[-1]["dimensions"] = {"without stand": arrWithoutStand}

    return (arrReturn)


if __name__ == "__main__":
    import json

    print("getting items... this could take a while")
    items = getItems("https://www.kogan.com/au/shop/tablets-laptops/computer-monitors/?page=200")

    with open('data.json', 'w') as outfile:
        json.dump(items, outfile)
    # with open('data.json', 'r') as infile:
    #     prevData=json.load(infile)
    #
    # maxVolume=0
    # url=""
    # for i in prevData:
    #     volume=1
    #     try:
    #         for j in i['dimensions']['without stand']:
    #             volume*=float(j)
    #     except:
    #         pass
    #     if volume>maxVolume:
    #         maxVolume=volume
    #         url=i['url']
    # print(maxVolume)
    # print(url)


