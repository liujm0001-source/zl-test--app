import requests
from bs4 import BeautifulSoup
import json
import time
import re
import random

def clean_title(text):
    """清洗标题：去除首尾空格，解决重复问题"""
    text = text.strip()
    mid = len(text) // 2
    if len(text) > 10 and text[:mid] == text[mid:]:
        return text[:mid]
    return text

def scrape_zhonglun():
    # --- 策略升级：同时抓取“业绩”和“新闻”两个页面 ---
    urls = [
        "https://www.zhonglun.com/performance.html", # 业绩页
        "https://www.zhonglun.com/news.html"        # 新闻页 (这里往往更新更快)
    ]
    
    all_cases = [] # 暂存所有抓到的数据
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/119.0.0.0 Safari/537.36"
    ]

    for url in urls:
        try:
            print(f"正在抓取: {url} ...")
            headers = {
                "User-Agent": random.choice(user_agents),
                "Referer": "https://www.zhonglun.com/"
            }
            
            response = requests.get(url, headers=headers, timeout=20)
            response.encoding = 'utf-8'

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找所有列表项
                all_list_items = soup.find_all('li')
                
                for item in all_list_items:
                    # 1. 必须包含日期 (YYYY-MM-DD)
                    full_text = item.get_text(strip=True)
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', full_text)
                    
                    if not date_match: continue
                    date = date_match.group(1)
                    
                    # 2. 找链接和标题
                    link_tag = item.find('a')
                    if not link_tag: continue
                    
                    raw_title = link_tag.get_text(strip=True)
                    title = clean_title(raw_title)
                    href = link_tag.get('href', '')
                    
                    if not href or len(title) < 5: continue
                    
                    if not href.startswith('http'):
                        href = 'https://www.zhonglun.com' + href
                    
                    # 3. 放入暂存区 (防止不同页面抓到重复的)
                    if not any(c['link'] == href for c in all_cases):
                        all_cases.append({
                            "title": title,
                            "date": date,
                            "tag": "最新动态",
                            "link": href
                        })

            else:
                print(f"网页 {url} 返回错误: {response.status_code}")

        except Exception as e:
            print(f"抓取 {url} 出错: {e}")

    # --- 核心逻辑：排序 ---
    # 无论先抓哪个页面，最后统一按日期倒序排列 (最新的在最前)
    # x['date'] 是字符串，'2025-12-05' > '2025-11-28'，可以直接比大小
    all_cases.sort(key=lambda x: x['date'], reverse=True)
    
    # 只保留最新的 10 条
    final_cases = all_cases[:10]

    # --- 结果处理 ---
    if len(final_cases) == 0:
        print("未抓到数据，使用系统默认消息")
        final_cases = [
            {
                "title": "中伦官网数据同步中...", 
                "date": time.strftime("%Y-%m-%d"), 
                "tag": "系统消息", 
                "link": "https://www.zhonglun.com"
            }
        ]
    else:
        print(f"共抓取并排序了 {len(final_cases)} 条最新数据！最新日期为: {final_cases[0]['date']}")

    # 保存
    with open('cases.json', 'w', encoding='utf-8') as f:
        json.dump(final_cases, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_zhonglun()
