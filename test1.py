from flask import Flask, jsonify, render_template
import requests
import feedparser
import json
import time
import random
import xml.etree.ElementTree as ET
import logging

from datetime import datetime

# Configure logging
#logging.basicConfig(level=logging.DEBUG)

def fetch_and_format_rss(api_url):
    # Fetch data from the API
    response = requests.get(api_url)
    response.raise_for_status()  # Raise an error for bad responses
    data = response.json()
    
    # Log the raw data fetched from the API
    logging.debug(f"Raw data fetched from API: {data}")

    # Get the current time for pubDate
    current_time = datetime.now().strftime("%a, %d %b %Y %H:%M:%S")

    # Create the root element of the RSS feed
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    
    # Add channel information
    title = ET.SubElement(channel, "title")
    title.text = "Hotlist RSS Feed"
    link = ET.SubElement(channel, "link")
    link.text = ""  # Set link to empty
    description = ET.SubElement(channel, "description")
    description.text = "This is an RSS feed of the hotlist data."

    # Format data as RSS items
    for item in data['data']:
        for sub_item in item['data']:
            rss_item = ET.SubElement(channel, "item")
            item_title = ET.SubElement(rss_item, "title")
            # Format title as "{type}+{title}"
            item_title.text = f"{sub_item.get('type', '')} + {sub_item.get('title', '')}"
            item_link = "" # Set item link to empty
            item_description = ET.SubElement(rss_item, "description")
            item_description.text = sub_item.get('title', '')  # Use title as description
            item_pubDate = ET.SubElement(rss_item, "pubDate")
            item_pubDate.text = current_time  # Set pubDate to current time

    # Log the formatted RSS feed
    #logging.debug(f"Formatted RSS feed: {ET.tostring(rss, encoding='utf-8', method='xml').decode('utf-8')}")

    # Convert the ElementTree to a string
    rss_feed = ET.tostring(rss, encoding='utf-8', method='xml').decode('utf-8')
    return rss_feed

app = Flask(__name__)

resoubang = "https://api.vvhan.com/api/hotlist/all"
gelonghui= "https://rss.injahow.cn/gelonghui/live"

def fetch_rss(feed_url):

    
    feed = feedparser.parse(feed_url)
    print(feed.entries)
    print("--------------------------------")
    return [{'title': entry.title, 'link': entry.link, 'pubDate': entry.get('published', '')} for entry in feed.entries]


with app.app_context():
    x=requests.get(gelonghui).text
    print(x[0:4])


    #print(jsonify(fetch_rss(gelonghui)))

