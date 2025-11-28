from flask import Flask, jsonify, render_template, make_response, send_from_directory
import requests
import feedparser
import json
import time
import random
import xml.etree.ElementTree as ET
import logging
import os
import importlib
import redis
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from datetime import datetime

# Configure logging
#logging.basicConfig(level=logging.DEBUG)

# 获取plugins目录的路径
# plugins_dir = 'plugins'

# 遍历plugins目录下的所有文件
# for filename in os.listdir(plugins_dir):
#     # 检查文件是否是Python文件
#     if filename.endswith('.py'):
#         # 获取模块名（去掉.py后缀）
#         module_name = filename[:-3]
#         # 构造完整的模块路径
#         module_path = f"{plugins_dir}.{module_name}"
#         # 动态导入模块
#         importlib.import_module(module_path)

def fetch_and_format_rss(api_url):
    # Fetch data from the API with headers to avoid anti-crawling
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }
    response = requests.get(api_url, headers=headers)
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
            item_link = ET.SubElement(rss_item, "link")
            item_link.text = ""  # Set item link to empty
            item_description = ET.SubElement(rss_item, "description")
            item_description.text = sub_item.get('title', '')  # Use title as description
            item_pubDate = ET.SubElement(rss_item, "pubDate")
            item_pubDate.text = current_time  # Set pubDate to current time

    # Log the formatted RSS feed
    #logging.debug(f"Formatted RSS feed: {ET.tostring(rss, encoding='utf-8', method='xml').decode('utf-8')}")

    # Convert the ElementTree to a string
    rss_feed = ET.tostring(rss, encoding='utf-8', method='xml').decode('utf-8')
    return rss_feed

network_condition = 4  # Initial network condition, range [2, 6]

app = Flask(__name__)

# Load RSS feed sources from a JSON file
def load_rss_sources():
    with open('rss_sources.json', 'r', encoding='utf-8') as f:
        sources = json.load(f)['sources']
        return {value['name']: {'url': value['url'], 'type': value['type']} for value in sources.values()}

RSS_FEEDS = load_rss_sources()

# 创建一个线程池执行器
thread_pool = ThreadPoolExecutor(max_workers=10)

async def fetch_rss_async(feed_url, feed_type):
    try:
        if feed_type == 'api':
            # 为API请求添加请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(feed_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        rss_feed = fetch_and_format_rss(feed_url)
                        result = [{'title': entry.title, 'link': entry.link, 'pubDate': entry.get('published', '')} 
                                for entry in feedparser.parse(rss_feed).entries]
                    else:
                        result = []
        elif feed_type == 'rss':
            # 为RSS请求也添加请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/rss+xml, application/xml, text/xml, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(feed_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        result = [{'title': entry.title, 'link': entry.link, 'pubDate': entry.get('published', '')} 
                                for entry in feedparser.parse(content).entries]
                    else:
                        result = []
        else:
            try:
                # 对于插件类型，使用线程池执行
                loop = asyncio.get_event_loop()
                module = importlib.import_module(f"plugins.{feed_type}")
                if hasattr(module, 'run'):
                    result = await loop.run_in_executor(thread_pool, partial(module.run, feed_url))
                else:
                    result = []
            except ModuleNotFoundError:
                result = []
        
        return result
    except Exception as e:
        logging.error(f"Error fetching RSS for {feed_url}: {str(e)}")
        return []

async def fetch_and_store_in_redis_async():
    tasks = []
    for source, details in RSS_FEEDS.items():
        feed_url = details['url']
        feed_type = details['type']
        task = asyncio.create_task(fetch_rss_async(feed_url, feed_type))
        tasks.append((source, task))
    
    for source, task in tasks:
        try:
            data = await asyncio.wait_for(task, timeout=10)  # 设置10秒超时
            if data:
                redis_client.setex(source, 300, json.dumps(data))
        except asyncio.TimeoutError:
            logging.error(f"Timeout fetching data for source: {source}")
        except Exception as e:
            logging.error(f"Error processing source {source}: {str(e)}")

def fetch_and_store_in_redis():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(fetch_and_store_in_redis_async())
    finally:
        loop.close()

@app.route('/')
def index():
    return render_template('index.html')

# Initialize Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Function to clear Redis data
def clear_redis_data():
    redis_client.flushdb()

# Clear Redis data on startup
clear_redis_data()

# Schedule the fetch_and_store_in_redis function to run every minute
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_store_in_redis, 'interval', minutes=1)
scheduler.start()

# Modify the get_rss function to fetch data from Redis
@app.route('/api/rss/<source>', methods=['GET'])
def get_rss(source):
    data = redis_client.get(source)
    if data:
        return jsonify(json.loads(data))
    else:
        return jsonify({'error': 'Data not available'}), 404

@app.route('/api/rss_sources', methods=['GET'])
def get_rss_sources():
    return jsonify([{'name': value['name'], 'type': value['type']} for value in json.load(open('rss_sources.json', 'r', encoding='utf-8'))['sources'].values()])

# Ensure the scheduler is shut down when the app exits
import atexit
atexit.register(lambda: scheduler.shutdown())

@app.route('/static/data/<path:filename>')
def serve_geojson(filename):
    response = make_response(send_from_directory('static/data', filename))
    response.headers['Cache-Control'] = 'public, max-age=31536000'  # Cache for one year
    response.headers['ETag'] = str(os.path.getmtime(os.path.join('static/data', filename)))
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 