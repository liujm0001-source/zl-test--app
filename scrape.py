import requests
from bs4 import BeautifulSoup
import json
import time
import re
import random
import urllib3

# 禁用安全警告（因为我们特意关掉了SSL验证）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_zhonglun():
    # 你的策略：只抓新闻资讯页
    url = "https://www.zhonglun.com/news.html"
    
    cases = []
    
    # 模拟最新的 Chrome 浏览器
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": "https://www.zhonglun.com/",
        "Connection": "keep-alive"
    }

    try:
        print(f"--- 正在精准抓取: {url} ---")
        
        # verify=False 是关键！防止防火墙因为证书问题拦截
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        response.encoding = 'utf-8' # 强制 UTF-8，防止乱码
        
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 中伦新闻页通常是 ul.news_list > li 结构
            # 我们查找所有 li，只要里面有日期和链接就行
            items = soup.find_all('li')
            
            print(f"页面包含列表项: {len(items)} 个")
            
            for item in items:
                try:
                    # 1. 找日期 (兼容 span 或 div)
                    text_content = item.get_text()
                    # 正则找 202x-xx-xx
                    date_match = re.search(r'(202[3-5]-\d{2}-\d{2})', text_content)
                    
                    if not date_match: continue
                    date = date_match.group(1)
                    
                    # 2. 找标题链接
                    link = item.find('a')
                    if not link: continue
                    
                    title = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    # 3. 过滤无效数据
                    if len(title) < 5: continue # 标题太短肯定不是新闻
                    if "javascript" in href: continue
                    
                    # 补全链接
                    if not href.startswith('http'):
                        href = 'https://www.zhonglun.com' + href
                        
                    # 4. 存入 (去重)
                    if not any(c['link'] == href for c in cases):
                        # 处理一下重复标题 (有时候网页源码里标题会写两遍)
                        if len(title) > 10 and title[:len(title)//2] == title[len(title)//2:]:
                            title = title[:len(title)//2]
                            
                        print(f"抓到: {date} - {title[:10]}...")
                        cases.append({
                            "title": title,
                            "date": date,
                            "tag": "最新交易", # 统一标记
                            "link": href
                        })
                        
                except Exception as e:
                    continue
        else:
            print("网页访问失败")

    except Exception as e:
        print(f"脚本运行出错: {e}")

    # --- 排序与保存 ---
    # 按照日期从新到旧排序
    cases.sort(key=lambda x: x['date'], reverse=True)
    
    # 只留前 10 条
    final_cases = cases[:10]

    # 保底显示
    if len(final_cases) == 0:
        print("⚠️ 警告：未匹配到数据。")
        final_cases = [
            {
                "title": "暂无最新数据 (请检查网络或官网状态)", 
                "date": time.strftime("%Y-%m-%d"), 
                "tag": "提示", 
                "link": "https://www.zhonglun.com/news.html"
            }
        ]
    else:
        print(f"✅ 成功！抓取到 {len(final_cases)} 条最新交易。")

    with open('cases.json', 'w', encoding='utf-8') as f:
        json.dump(final_cases, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_zhonglun()
