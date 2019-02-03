from __future__ import print_function

import json
import urllib2
from bs4 import BeautifulSoup

print('Loading function')


def lambda_handler(event, context):
    if 'body' in event:
        event = json.loads(event["body"])

    baseURL = "https://www.fiasfreshmeals.com"
    menuURL = baseURL + "/this-weeks-menu-2"

    items = []
    for itemLink in find_item_links(menuURL):
        items.append(get_item_details(baseURL + itemLink))

    message = str(items)
    
    return {
        "statusCode": "200",
        "headers": { "Content-type": "application/json" },
        "body": json.dumps({"message": message})
    }
    
def get_soup(url):
    response = urllib2.urlopen(url)
    return BeautifulSoup(response.read(), features="html.parser")

def find_item_links(url):
    soup = get_soup(url)
    itemLinks = []
    for itemDivs in soup.findAll("div", {"class": "card-image"}):
        for link in itemDivs.findAll("a"):
            itemLinks.append(link.get("href"))

    return itemLinks

def get_item_details(itemURL):
    soup = get_soup(itemURL)
    item = {}
    item["name"] = soup.find("meta",  property="og:title")["content"]
    item["price"] = soup.find("span", {"itemprop": "price"}).contents[0].strip()
    item["calories"] = get_item_value(soup, "Calories", False)
    item["fat"] = get_item_value(soup, "Total Fat")
    item["sodium"] = get_item_value(soup, "Sodium")
    item["carbs"] = get_item_value(soup, "Total")
    item["protein"] = get_item_value(soup, "Protein")

    return item
    
def get_item_value(soup, name, withSpan = True):
    itemContent = soup.find(text=name)
    if itemContent is not None:
        if withSpan:
            itemVal = itemContent.findNext('td').span.contents[0]
        else:
            itemVal = itemContent.findNext('td').contents[0]
    else:
        # If the content does not exist, set the value to 0
        itemVal = "0"

    return itemVal