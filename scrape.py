import requests
from bs4 import BeautifulSoup
import json
import time
import re
import random

def clean_title(text):
    """清洗标题"""
    if not text: return ""
    text = text.strip()
    # 去除多余的换行和空格
    text = re.sub(r'\s+', ' ', text)
    # 解决重复标题问题
    mid = len(text) // 2
    if len(text) > 12 and text[:mid] == text[mid:]:
        return text[:mid]
    return text

def scrape_zhonglun():
    urls = [
        "https://www.zhonglun.com/news.html",       # 新闻资讯 (通常更新最快)
        "https://www.zhonglun.com/performance.html" # 业绩概览
    ]
    
    all_cases = []
    
    # 随机浏览器指纹
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/119.0.0.0 Safari/537.36"
    ]

    for url in urls:
        try:
            print(f"--- 正在抓取: {url} ---")
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": "https://www.zhonglun.com/"
            }
            
            # 发送请求
            response = requests.get(url, headers=headers, timeout=25)
            response.encoding = 'utf-8'
            
            print(f"状态码: {response.status_code}, 页面大小: {len(response.text)} 字符")
            
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # === 核弹级策略：扫描页面所有链接 ===
            # 不再局限于 li 或 div，只要是链接就检查
            links = soup.find_all('a')
            
            for link in links:
                try:
                    # 1. 获取链接文本
                    title = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    if not href or len(title) < 6: continue # 标题太短跳过
                    
                    # 排除显而易见的非新闻链接
                    if any(x in href for x in ['javascript', 'mailto', 'tel:', '#']): continue
                    
                    # 2. 寻找日期 (支持 -, ., / 三种分隔符)
                    # 策略A: 在链接文本里找
                    # 策略B: 在链接的父级元素里找 (比如 li > a + span)
                    
                    date_pattern = r'(202[3-6][-./年]\d{1,2}[-./月]\d{1,2})'
                    
                    # 先看这一行的所有文本（包括链接自己和它旁边的字）
                    # 向上找3层父级，确保能涵盖 li 或 div
                    parent_text = ""
                    curr = link
                    for _ in range(3):
                        if curr.parent:
                            curr = curr.parent
                            parent_text += " " + curr.get_text(strip=True)
                        else:
                            break
                    
                    match = re.search(date_pattern, parent_text)
                    
                    if match:
                        date_str = match.group(1)
                        # 统一格式化为 YYYY-MM-DD
                        date_str = date_str.replace('.','-').replace('/','-').replace('年','-').replace('月','-').strip()
                        
                        # 补全链接
                        if not href.startswith('http'):
                            href = 'https://www.zhonglun.com' + href
                        
                        # 清洗标题
                        clean_t = clean_title(title)
                        
                        # 3. 存入 (去重)
                        if not any(c['link'] == href for c in all_cases):
                            print(f"发现: {date_str} - {clean_t[:10]}...")
                            all_cases.append({
                                "title": clean_t,
                                "date": date_str,
                                "tag": "最新动态",
                                "link": href
                            })
                            
                except Exception as inner_e:
                    continue

        except Exception as e:
            print(f"抓取错误: {e}")

    # --- 排序与保存 ---
    # 按日期倒序 (最新的在最前)
    all_cases.sort(key=lambda x: x['date'], reverse=True)
    
    # 截取前 10 条
    final_cases = all_cases[:10]

    # 如果还是没抓到
    if len(final_cases) == 0:
        print("警告：全网扫描未发现带日期的新闻。")
        final_cases = [
            {
                "title": "中伦官网数据同步中 (暂未匹配到新闻)", 
                "date": time.strftime("%Y-%m-%d"), 
                "tag": "系统消息", 
                "link": "https://www.zhonglun.com"
            }
        ]
    else:
        print(f"✅ 抓取成功！共找到 {len(final_cases)} 条新闻，最新日期: {final_cases[0]['date']}")

    with open('cases.json', 'w', encoding='utf-8') as f:
        json.dump(final_cases, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_zhonglun()
