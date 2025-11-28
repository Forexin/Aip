def run(feed_url):
    import requests
    import json
    from datetime import datetime
    import time
    
    try:
        # Set request headers to avoid anti-crawling
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        
        # Get all data sources from AIP instance
        sources_response = requests.get(f"{feed_url.rstrip('/')}/api/rss_sources", headers=headers, timeout=10)
        sources_response.raise_for_status()
        sources_data = sources_response.json()
        
        all_items = []
        
        # Iterate through each data source
        for source in sources_data:
            source_name = source.get("name", "Unknown Source")
            source_type = source.get("type", "unknown")
            
            try:
                # Get content from this data source
                content_response = requests.get(f"{feed_url.rstrip('/')}/api/rss/{source_name}", headers=headers, timeout=10)
                content_response.raise_for_status()
                content_data = content_response.json()
                
                # Process each data item
                for item in content_data:
                    # Build data item in frontend format
                    item_data = {
                        "title": item.get("title", "No Title"),
                        "link": item.get("link", ""),
                        "pubDate": item.get("pubDate", ""),
                        "description": f"[AIP-{source_name}] {item.get('title', '')}",
                        "source": f"AIP-{source_name}",  # Mark source as AIP instance
                        "aip_source": source_name,  # Original data source name
                        "aip_type": source_type,  # Original data source type
                        "aip_instance": feed_url  # AIP instance address
                    }
                    
                    # Add to results if title is not empty
                    if item_data["title"] and item_data["title"] != "No Title":
                        all_items.append(item_data)
                
                # Add small delay to avoid pressure on target AIP instance
                time.sleep(0.5)
                
            except requests.exceptions.RequestException as e:
                print(f"Failed to get data source {source_name}: {e}")
                continue
            except Exception as e:
                print(f"Error processing data source {source_name}: {e}")
                continue
        
        return all_items
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to AIP instance: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Failed to parse AIP instance data: {e}")
        return []
    except Exception as e:
        print(f"Unknown error: {e}")
        return []
