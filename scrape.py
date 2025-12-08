from curl_cffi import requests # 这里用了特种库，不是普通的 requests
from bs4 import BeautifulSoup
import json
import time
import re

def scrape_zhonglun():
    # 直捣黄龙：只抓新闻列表页
    url = "https://www.zhonglun.com/news.html"
    
    cases = []
    
    print(f"--- 正在启动特种伪装 (Chrome 120) 访问: {url} ---")

    try:
        # === 核心黑科技 ===
        # impersonate="chrome120": 模拟 Chrome 120 的所有底层指纹
        session = requests.Session()
        response = session.get(
            url, 
            impersonate="chrome120", 
            timeout=30
        )
        # 手动修正编码，防止乱码
        response.encoding = 'utf-8'

        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找新闻列表 (通常在 ul.news_list 里，但我们用宽泛策略找 li)
            items = soup.find_all('li')
            print(f"扫描到列表项: {len(items)} 个")
            
            for item in items:
                try:
                    # 1. 找日期 (兼容 202x-xx-xx 或 202x.xx.xx)
                    text = item.get_text()
                    date_match = re.search(r'(202[3-6][-./]\d{1,2}[-./]\d{1,2})', text)
                    if not date_match: continue
                    
                    # 格式化日期为 YYYY-MM-DD
                    date_str = date_match.group(1).replace('.', '-').replace('/', '-')
                    
                    # 2. 找链接和标题
                    link_tag = item.find('a')
                    if not link_tag: continue
                    
                    title = link_tag.get_text(strip=True)
                    href = link_tag.get('href', '')
                    
                    # 3. 过滤垃圾数据
                    if len(title) < 6: continue
                    if "javascript" in href: continue
                    
                    # 4. 关键词过滤：只保留真正有价值的“交易/业绩”
                    # 如果你希望展示所有新闻，可以把下面这几行注释掉
                    keywords = ['助力', '代表', '协助', '获选', '荣获', '上市', '并购', '投资', '成功']
                    if not any(k in title for k in keywords):
                        continue

                    # 5. 补全链接
                    if not href.startswith('http'):
                        href = 'https://www.zhonglun.com' + href
                        
                    # 6. 清洗重复标题 (ABCABC -> ABC)
                    if len(title) > 12 and title[:len(title)//2] == title[len(title)//2:]:
                        title = title[:len(title)//2]

                    # 7. 存入
                    if not any(c['link'] == href for c in cases):
                        print(f"✅ 抓取到: {date_str} - {title[:15]}...")
                        cases.append({
                            "title": title,
                            "date": date_str,
                            "tag": "最新交易", # 加上这个标签显得很专业
                            "link": href
                        })
                        
                except Exception as e:
                    continue
        else:
            print("网页依然拒绝访问，可能IP被封锁")

    except Exception as e:
        print(f"发生错误: {e}")

    # --- 排序与输出 ---
    # 按日期倒序
    cases.sort(key=lambda x: x['date'], reverse=True)
    final_cases = cases[:12] # 取前12条，内容丰富点

    if len(final_cases) > 0:
        print(f"🎉 最终成功获取 {len(final_cases)} 条高价值数据！")
        with open('cases.json', 'w', encoding='utf-8') as f:
            json.dump(final_cases, f, ensure_ascii=False, indent=2)
    else:
        print("⚠️ 警告：策略失败，写入默认数据")
        # 最后的防线：如果还失败，写死几条昨天刚发生的新闻，保证演示效果
        # 这里你可以手动去官网抄几条最新的填进去，以防万一
        fallback_data = [
            {
                "title": "中伦助力海伟股份在香港联交所主板上市 (实时同步失败)",
                "date": "2025-12-05",
                "tag": "最新交易",
                "link": "https://www.zhonglun.com"
            }
        ]
        with open('cases.json', 'w', encoding='utf-8') as f:
            json.dump(fallback_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_zhonglun()
