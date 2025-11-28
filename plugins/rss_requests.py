def run(feed_url):
    import requests
    import xml.etree.ElementTree as ET
    response = requests.get(feed_url)
    response.raise_for_status()  # Raise an error for bad responses
    root = ET.fromstring(response.content)

    # Parse the RSS feed
    items = []
    for item in root.findall('.//item'):
        title = item.find('title').text if item.find('title') is not None else 'No Title'
        link = item.find('link').text if item.find('link') is not None else 'No Link'
        pubDate = item.find('pubDate').text if item.find('pubDate') is not None else 'No Date'
        items.append({'title': title, 'link': link, 'pubDate': pubDate})

    return items 






