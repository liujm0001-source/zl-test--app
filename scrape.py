from duckduckgo_search import DDGS
import json
import time
import re

def scrape_via_search():
    # 扩大范围：不再限制 /news 子目录，搜全站
    keywords = "site:zhonglun.com (助力 OR 代表 OR 上市 OR 并购 OR 获选)"
    
    print(f"--- 正在全网搜索: {keywords} ---")
    
    cases = []
    
    try:
        # === 核心修改：去掉了 timelimit='m'，不再限制时间 ===
        results = DDGS().text(keywords, region='cn-zh', max_results=15)
        
        print(f"搜索服务返回了 {len(list(results)) if results else 0} 条结果")

        for r in results:
            title = r.get('title', '')
            href = r.get('href', '')
            body = r.get('body', '') 
            
            # 1. 过滤：必须是中伦官网
            if "zhonglun.com" not in href: continue
            
            # 2. 清洗标题
            title = title.split(' - ')[0].split(' | ')[0]
            
            # 3. 提取日期 (如果搜不到日期，就给个默认的“近期”)
            date = "近期动态"
            # 尝试匹配 2023-2025 年的日期
            date_match = re.search(r'(202[3-6][-./年]\d{1,2}[-./月]\d{1,2})', body)
            if date_match:
                date = date_match.group(1).replace('.','-').replace('/','-').replace('年','-').replace('月','-')
            
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

    # 排序：把带具体日期的排前面
    cases.sort(key=lambda x: x['date'] if x['date'][0].isdigit() else '0000', reverse=True)
    
    if len(cases) == 0:
        print("⚠️ 依然未搜到，使用保底数据")
        cases = [
            {
                "title": "中伦助力海伟股份在香港联交所主板上市", 
                "date": "2025-12-05", 
                "tag": "最新交易", 
                "link": "https://www.zhonglun.com"
            }
        ]
    else:
        print(f"✅ 成功获取 {len(cases)} 条数据！")

    with open('cases.json', 'w', encoding='utf-8') as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_via_search()
