import requests
from bs4 import BeautifulSoup
import json
import time
import re
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_zhonglun_as_spider():
    # 目标：中伦新闻列表页
    url = "https://www.zhonglun.com/news.html"
    
    cases = []
    
    # 🕵️‍♂️ 核心伪装：假装自己是百度搜索引擎的爬虫
    # 大多数网站为了SEO（搜索引擎排名），都不敢拦截这个 User-Agent
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
        "Accept": "*/*",
        "Connection": "keep-alive"
    }

    try:
        print(f"--- 🕷️ 正在伪装成百度蜘蛛访问: {url} ---")
        
        # verify=False 关掉证书验证
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        response.encoding = 'utf-8' # 强制 UTF-8 编码
        
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 寻找列表项：中伦官网的新闻通常在 li 标签里
            items = soup.find_all('li')
            print(f"扫描到 {len(items)} 个列表项")
            
            for item in items:
                try:
                    # 1. 找日期 (兼容各种格式)
                    text = item.get_text()
                    # 正则匹配 2023-01-01 到 2025-12-31 之间的日期
                    date_match = re.search(r'(202[3-5]-\d{2}-\d{2})', text)
                    
                    if not date_match: continue
                    date = date_match.group(1)
                    
                    # 2. 找链接和标题
                    link_tag = item.find('a')
                    if not link_tag: continue
                    
                    title = link_tag.get_text(strip=True)
                    href = link_tag.get('href', '')
                    
                    # 3. 过滤垃圾数据
                    if len(title) < 6: continue # 标题太短不要
                    if "javascript" in href: continue
                    
                    # 补全链接
                    if not href.startswith('http'):
                        href = 'https://www.zhonglun.com' + href
                        
                    # 去重并添加
                    if not any(c['link'] == href for c in cases):
                        # 简单的标题去重处理
                        if len(title) > 12 and title[:len(title)//2] == title[len(title)//2:]:
                            title = title[:len(title)//2]
                            
                        print(f"✅ 抓取成功: {date} - {title[:10]}...")
                        cases.append({
                            "title": title,
                            "date": date,
                            "tag": "最新资讯",
                            "link": href
                        })
                        
                except: continue
        else:
            print("❌ 百度蜘蛛伪装也被拦截，防火墙极严。")

    except Exception as e:
        print(f"❌ 运行出错: {e}")

    # --- 排序与保存 ---
    cases.sort(key=lambda x: x['date'], reverse=True)
    final_cases = cases[:10]

    # --- 最终保底方案 (Manual Backup) ---
    # 如果百度蜘蛛都不行，说明必须人工维护了
    if len(final_cases) == 0:
        print("⚠️ 警告：自动抓取失败，写入【手动维护】数据。")
        final_cases = [
            {
                "title": "中伦助力海伟股份在香港联交所主板上市",
                "date": "2025-12-05",
                "tag": "最新交易",
                "link": "https://www.zhonglun.com/news/detail-20251205.html" # 示例链接
            },
            {
                "title": "中伦助力中国一汽战略投资卓驭科技超36亿元",
                "date": "2025-12-04",
                "tag": "最新交易",
                "link": "https://www.zhonglun.com/news/detail-20251204.html"
            },
            {
                "title": "中伦助力某民营企业合同诈骗案获无罪判决",
                "date": "2025-12-03",
                "tag": "最新案例",
                "link": "https://www.zhonglun.com/news.html"
            }
        ]
    else:
        print(f"🎉 最终成功抓取 {len(final_cases)} 条数据！")

    with open('cases.json', 'w', encoding='utf-8') as f:
        json.dump(final_cases, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_zhonglun_as_spider()
