import requests
from bs4 import BeautifulSoup
import json
import time
import re
import random

def clean_title(text):
    if not text: return ""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    mid = len(text) // 2
    if len(text) > 12 and text[:mid] == text[mid:]:
        return text[:mid]
    return text

def scrape_zhonglun():
    urls = [
        "https://www.zhonglun.com/news.html", 
        "https://www.zhonglun.com/performance.html"
    ]
    
    all_cases = []
    
    # 随机 User-Agent 池
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    ]

    for url in urls:
        try:
            print(f"--- 正在抓取: {url} ---")
            
            # === 超级伪装 Headers ===
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8", # 告诉服务器我是中文用户
                "Cache-Control": "max-age=0",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Referer": "https://www.google.com/" # 伪装成从谷歌搜索点进来的
            }
            
            # 增加 2 秒延迟，模拟人类反应
            time.sleep(2)
            
            response = requests.get(url, headers=headers, timeout=30)
            response.encoding = 'utf-8'
            
            print(f"状态码: {response.status_code}")
            
            # 如果还是 500 或 403，打印一部分内容看看是什么鬼
            if response.status_code != 200:
                print(f"被拦截内容预览: {response.text[:100]}...")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 扫描所有链接
            links = soup.find_all('a')
            print(f"页面内链接数量: {len(links)}") # 调试信息
            
            count_found = 0
            for link in links:
                try:
                    title = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    if not href or len(title) < 6: continue
                    if any(x in href for x in ['javascript', 'mailto', '#']): continue
                    
                    # 宽松的日期匹配：只要有 202x 年/月/日 格式
                    date_pattern = r'(202[3-6][-./年]\d{1,2}[-./月]\d{1,2})'
                    
                    # 扩大搜索范围：链接自己 + 父级 + 爷爷级
                    search_text = str(link)
                    if link.parent: search_text += str(link.parent)
                    if link.parent and link.parent.parent: search_text += str(link.parent.parent)

                    match = re.search(date_pattern, search_text)
                    
                    if match:
                        date_str = match.group(1).replace('.','-').replace('/','-').replace('年','-').replace('月','-').strip()
                        
                        if not href.startswith('http'):
                            href = 'https://www.zhonglun.com' + href
                        
                        clean_t = clean_title(title)
                        
                        if not any(c['link'] == href for c in all_cases):
                            all_cases.append({
                                "title": clean_t,
                                "date": date_str,
                                "tag": "最新动态",
                                "link": href
                            })
                            count_found += 1
                            
                except: continue
            
            print(f"本页面找到 {count_found} 条新闻")

        except Exception as e:
            print(f"抓取错误: {e}")

    # 排序与保存
    all_cases.sort(key=lambda x: x['date'], reverse=True)
    final_cases = all_cases[:10]

    # --- 终极保底 ---
    # 如果这次还抓不到，说明 GitHub IP 被永久拉黑了
    # 我们为了不让页面挂掉，写入一条提示
    if len(final_cases) == 0:
        print("警告：伪装后仍未抓到数据。")
        final_cases = [
            {
                "title": "系统正在维护中，请稍后访问官网查看最新业绩", 
                "date": time.strftime("%Y-%m-%d"), 
                "tag": "提示", 
                "link": "https://www.zhonglun.com"
            }
        ]
    else:
        print(f"✅ 成功！抓取到 {len(final_cases)} 条数据。")

    with open('cases.json', 'w', encoding='utf-8') as f:
        json.dump(final_cases, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_zhonglun()
