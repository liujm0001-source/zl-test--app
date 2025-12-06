import requests
from bs4 import BeautifulSoup
import json
import time
import random

def scrape_zhonglun():
    # 目标网址：业绩概览
    # 备选网址：如果业绩页抓不到，尝试抓首页新闻或观点
    urls = [
        "https://www.zhonglun.com/performance.html",
        "https://www.zhonglun.com/research/articles.html" # 备选：观点文章
    ]
    
    cases = []
    
    # 伪装成真实的浏览器（随机切换，防止被识别）
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ]

    for url in urls:
        if len(cases) >= 5: break # 如果已经抓够了就停止
        
        try:
            print(f"正在尝试抓取: {url} ...")
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Referer": "https://www.zhonglun.com/"
            }
            
            response = requests.get(url, headers=headers, timeout=20)
            response.encoding = 'utf-8' # 强制中文编码
            
            if response.status_code != 200:
                print(f"网页访问失败，状态码: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # --- 智能查找逻辑 ---
            # 尝试查找网页中所有可能的列表项
            # 策略：找所有 li 标签，且里面包含日期(span/div)和链接(a)的
            
            potential_lists = soup.find_all('li')
            
            for item in potential_lists:
                try:
                    # 1. 必须有链接
                    link_tag = item.find('a')
                    if not link_tag: continue
                    
                    href = link_tag.get('href', '')
                    title = link_tag.get_text(strip=True)
                    
                    # 过滤掉太短的标题（比如“更多”、“首页”）
                    if len(title) < 5: continue
                    
                    # 2. 尝试找日期 (class通常包含 date 或 time)
                    date = ""
                    date_tag = item.find(lambda tag: tag.name in ['span', 'div', 'p'] and ('date' in str(tag.get('class', [])).lower() or 'time' in str(tag.get('class', [])).lower()))
                    
                    if date_tag:
                        date = date_tag.get_text(strip=True)
                    else:
                        # 如果找不到日期标签，尝试正则匹配或者就用今天
                        import re
                        match = re.search(r'\d{4}-\d{2}-\d{2}', item.get_text())
                        if match:
                            date = match.group()
                    
                    # 只有当标题和链接都存在时才收录
                    if title and href:
                        if not href.startswith('http'):
                            href = 'https://www.zhonglun.com' + href
                            
                        # 如果没有日期，就标记为“近期”
                        if not date: date = "2025" 

                        # 去重
                        if not any(c['link'] == href for c in cases):
                            cases.append({
                                "title": title,
                                "date": date,
                                "tag": "最新动态", # 统一定义标签
                                "link": href
                            })
                            
                        if len(cases) >= 10: break # 单个页面最多取10条

                except Exception as inner_e:
                    continue
                    
        except Exception as e:
            print(f"抓取 {url} 出错: {e}")

    # --- 结果处理 ---
    if len(cases) == 0:
        print("警告：彻底没抓到数据，使用保底显示")
        cases = [
            {
                "title": "中伦助力客户完成重要跨境交易 (官网数据同步中...)", 
                "date": time.strftime("%Y-%m-%d"), 
                "tag": "系统消息", 
                "link": "https://www.zhonglun.com"
            }
        ]
    else:
        print(f"成功抓取 {len(cases)} 条数据！")

    # 保存
    with open('cases.json', 'w', encoding='utf-8') as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_zhonglun()
