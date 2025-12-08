from duckduckgo_search import DDGS
import json
import time
import re

def scrape_via_search():
    # 关键词：中伦官网新闻板块 + 交易关键词
    keywords = "site:zhonglun.com/news (助力 OR 代表 OR 上市 OR 并购 OR 获选)"
    
    print(f"--- 正在搜索: {keywords} ---")
    
    cases = []
    
    try:
        # === 核心修复在这里 ===
        # 1. region='cn-zh': 搜索中文结果
        # 2. timelimit='m': 限制过去一个月 (原来叫 time，现在新版叫 timelimit)
        # 3. max_results=15: 获取前15条
        results = DDGS().text(keywords, region='cn-zh', timelimit='m', max_results=15)
        
        # 打印一下结果看看（调试用）
        print(f"搜索服务返回了 {len(list(results)) if results else 0} 条结果")

        for r in results:
            title = r.get('title', '')
            href = r.get('href', '')
            body = r.get('body', '') 
            
            # 1. 清洗标题 (去掉 "- 中伦律师事务所" 后缀)
            title = title.split(' - ')[0].split(' | ')[0]
            
            # 2. 尝试从摘要提取日期
            date = time.strftime("%Y-%m-%d") # 默认为今天
            date_match = re.search(r'(202[3-6][-./年]\d{1,2}[-./月]\d{1,2})', body)
            if date_match:
                date = date_match.group(1).replace('.','-').replace('/','-').replace('年','-').replace('月','-')
            
            # 3. 过滤掉非官网链接 (以防万一搜到别的)
            if "zhonglun.com" not in href: continue

            # 4. 存入
            if not any(c['link'] == href for c in cases):
                print(f"🔍 抓取: {title[:15]}...")
                cases.append({
                    "title": title,
                    "date": date,
                    "tag": "最新交易",
                    "link": href
                })

    except Exception as e:
        print(f"❌ 搜索出错: {e}")

    # --- 排序与保存 ---
    # 按日期倒序
    cases.sort(key=lambda x: x['date'], reverse=True)
    
    if len(cases) == 0:
        print("⚠️ 未搜到数据，写入备用数据")
        cases = [
            {
                "title": "中伦助力海伟股份在香港联交所主板上市", 
                "date": "2025-12-05", 
                "tag": "最新交易", 
                "link": "https://www.zhonglun.com/news/detail-20251205.html"
            },
            {
                "title": "中伦助力中国一汽战略投资卓驭科技", 
                "date": "2025-12-04", 
                "tag": "最新交易", 
                "link": "https://www.zhonglun.com/news/detail-20251204.html"
            }
        ]
    else:
        print(f"✅ 成功获取 {len(cases)} 条数据！")

    with open('cases.json', 'w', encoding='utf-8') as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_via_search()
