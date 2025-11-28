def run(feed_url):
    import requests
    import json
    from datetime import datetime
    
    try:
        # 设置请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        
        # 发送请求获取数据
        response = requests.get(feed_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 解析JSON数据
        data = response.json()
        
        # 提取所有热搜数据
        items = []
        
        # 遍历所有数据源
        for source in data.get("data", []):
            source_name = source.get("name", "未知来源")
            source_data = source.get("data", [])
            
            # 遍历每个数据源中的热搜条目
            for item in source_data:
                # 构建符合前端格式的数据项
                item_data = {
                    "title": item.get("title", "无标题"),
                    "link": item.get("url", ""),
                    "pubDate": source.get("update_time", ""),  # 使用数据源的更新时间
                    "description": f"[{source_name}] {item.get('title', '')}",  # 添加来源信息到描述中
                    "source": source_name,  # 添加来源标识
                    "hot_score": item.get("hot", ""),  # 热度分数（如果有）
                    "index": item.get("index", "")  # 排名（如果有）
                }
                
                # 如果标题不为空，添加到结果中
                if item_data["title"] and item_data["title"] != "无标题":
                    items.append(item_data)
        
        return items
        
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return []
    except Exception as e:
        print(f"未知错误: {e}")
        return []