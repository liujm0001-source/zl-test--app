
import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_zhonglun():
    # 目标网址：中伦官网-业绩概览
    url = "https://www.zhonglun.com/performance.html"
    
    # 伪装成浏览器，防止被拦截
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        print(f"正在抓取: {url} ...")
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8' # 确保中文不乱码
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        cases = []
        
        # --- 解析逻辑 (针对中伦官网结构) ---
        # 寻找新闻列表
        news_list = soup.find_all('li', class_='clearfix') 
        if not news_list:
            news_list = soup.select('ul.news_list li') 

        for item in news_list[:10]: # 只取前10条
            try:
                # 找标题和链接
                link_tag = item.find('a')
                if not link_tag: continue
                
                title = link_tag.get_text(strip=True)
                href = link_tag['href']
                if not href.startswith('http'):
                    href = 'https://www.zhonglun.com' + href
                
                # 找日期
                date_tag = item.find('span', class_='date')
                date = date_tag.get_text(strip=True) if date_tag else time.strftime("%Y-%m-%d")

                cases.append({
                    "title": title,
                    "date": date,
                    "tag": "最新业绩",
                    "link": href
                })
            except Exception as e:
                continue

        # 如果抓不到数据，用备用数据防止页面空白
        if len(cases) == 0:
            print("警告：未抓取到有效数据，使用备用数据")
            cases = [
                {"title": "中伦助力多家企业完成境内外上市 (自动抓取暂无数据)", "date": time.strftime("%Y-%m-%d"), "tag": "系统消息", "link": "https://www.zhonglun.com"}
            ]
        else:
            print(f"成功抓取 {len(cases)} 条数据")

        # 保存为 cases.json
        with open('cases.json', 'w', encoding='utf-8') as f:
            json.dump(cases, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"抓取失败: {e}")

if __name__ == "__main__":
    scrape_zhonglun()
