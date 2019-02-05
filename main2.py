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
    for i in items:
        arrReturn.append({})
        arrReturn[-1]["url"]=str("https://www.kogan.com"+str(i.select("a")[0].get("href")))
        itemPage=simpleGet(arrReturn[-1]["url"])
        itemAttrs=itemPage.findAll(attrs={"class": "react-sanfona-item-body"})
        for j in itemAttrs:
            if j.findAll(attrs={"class": "flFiV"}) != []:
                tags=j.findAll(attrs={"class": "flFiV"})
                values=j.findAll(attrs={"class": "EPROW"})
                for k in range(len(tags)):
                    if values[k].string != None:
                        arrReturn[-1][tags[k].string]=values[k].string
                    # print(tags[k].string,values[k].string)
        # print(arrReturn[-1])
    return(arrReturn)


if __name__ == "__main__":
    print("getting items... this could take a while")
    for i in getItems("https://www.kogan.com/au/shop/tablets-laptops/computer-monitors/?page=200"):
        print(i)
