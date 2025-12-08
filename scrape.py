import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re

def scrape_zhonglun_via_bing():
    # 使用 Bing 搜索，它是目前对爬虫最宽容的搜索引擎
    # 关键词：site:zhonglun.com (限定官网) + "助力" (限定交易新闻)
    base_url = "https://www.bing.com/search?q=site%3Azhonglun.com%2Fnews+%22%E5%8A%A9%E5%8A%9B%22&count=20"
    
    cases = []
    
    # 必须伪装成电脑浏览器，否则 Bing 会不理我们
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cookie": "SRCHHPGUSR=SRCHLANG=zh-Hans;" # 强制中文结果
    }

    try:
        print(f"--- 正在通过 Bing 搜索中伦最新业绩 ---")
        response = requests.get(base_url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Bing 的搜索结果列表通常在 li.b_algo 中
            results = soup.find_all('li', class_='b_algo')
            
            print(f"Bing 返回了 {len(results)} 条原始结果")
            
            for res in results:
                try:
                    # 1. 找标题和链接 (h2 > a)
                    title_tag = res.find('h2').find('a')
                    if not title_tag: continue
                    
                    title = title_tag.get_text(strip=True)
                    link = title_tag['href']
                    
                    # 过滤掉非官网链接 (虽然site指令已经过滤了，双重保险)
                    if "zhonglun.com" not in link: continue
                    
                    # 2. 找日期 (Bing 通常在 caption 或 snippet 里有日期)
                    # 格式通常是 "2025/12/5 · " 或 "3 days ago"
                    date = time.strftime("%Y-%m-%d") # 默认今天
                    
                    snippet_div = res.find('div', class_='b_caption')
                    if snippet_div:
                        snippet_text = snippet_div.get_text()
                        # 尝试正则提取日期 202x-x-x
                        date_match = re.search(r'(202[3-5][-/年]\d{1,2}[-/月]\d{1,2})', snippet_text)
                        if date_match:
                            raw_date = date_match.group(1)
                            # 统一格式
                            date = raw_date.replace('/','-').replace('年','-').replace('月','-').strip()
                    
                    # 3. 存入
                    # 清洗标题：去掉 " - 中伦律师事务所" 这种后缀
                    title = title.split(' - ')[0].split(' | ')[0]
                    
                    if not any(c['link'] == link for c in cases):
                        print(f"抓取到: {date} - {title[:15]}...")
                        cases.append({
                            "title": title,
                            "date": date,
                            "tag": "最新交易",
                            "link": link
                        })
                        
                except Exception as inner_e:
                    continue
        else:
            print(f"Bing 拒绝访问，状态码: {response.status_code}")

    except Exception as e:
        print(f"搜索出错: {e}")

    # --- 排序与去重 ---
    cases.sort(key=lambda x: x['date'], reverse=True)
    final_cases = cases[:10]

    # --- 保底机制 (如果Bing也挂了) ---
    if len(final_cases) == 0:
        print("⚠️ 警告：Bing 也没搜到数据，使用【最后防线】。")
        final_cases = [
            {
                "title": "中伦助力多家企业完成境内外上市及重大重组 (系统消息)",
                "date": time.strftime("%Y-%m-%d"),
                "tag": "新闻",
                "link": "https://www.zhonglun.com/news.html"
            },
            {
                "title": "点击查看中伦律师事务所官网最新业绩动态",
                "date": time.strftime("%Y-%m-%d"),
                "tag": "官网",
                "link": "https://www.zhonglun.com/performance.html"
            }
        ]
    else:
        print(f"✅ 成功！通过 Bing 抓取到 {len(final_cases)} 条数据。")

    # 保存
    with open('cases.json', 'w', encoding='utf-8') as f:
        json.dump(final_cases, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_zhonglun_via_bing()
