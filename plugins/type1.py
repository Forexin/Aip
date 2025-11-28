
def run(feed_url):
    import feedparser
    return [{'title': entry.title, 'link': entry.link, 'pubDate': entry.get('published', '')} for entry in feedparser.parse(feed_url).entries]



