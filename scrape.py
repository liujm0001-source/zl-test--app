from duckduckgo_search import DDGS
import json
import time
import re

def scrape_via_search():
    # 搜索关键词：限定在中伦新闻板块，包含“助力”或“代表”的词
    # time='m' 表示只搜“过去一个月”的，确保新鲜
    keywords = "site:zhonglun.com/news (助力 OR 代表 OR 上市 OR 并购)"
    
    print(f"--- 正在通过搜索引擎查找: {keywords} ---")
    
    cases = []
    
    try:
        # 使用 DuckDuckGo 搜索
        # region='cn-zh' 优先找中文结果
        # time='m' 限制过去一个月
        # max_results=15 抓取前15条
        results = DDGS().text(keywords, region='cn-zh', time='m', max_results=15)
        
        for r in results:
            title = r.get('title', '')
            href = r.get('href', '')
            body = r.get('body', '') # 摘要，里面通常包含日期
            
            # 1. 简单清洗标题
            # 搜索结果标题通常带有 " - 中伦律师事务所"，我们要去掉
            title = title.split(' - ')[0].split(' | ')[0]
            
            # 2. 尝试从摘要里提取日期，如果没有就用今天
            # 摘要里通常会有 "2 days ago" 或者 "2023..."
            date = time.strftime("%Y-%m-%d")
            
            # 尝试匹配日期格式 YYYY-MM-DD
            date_match = re.search(r'(202[3-6][-./年]\d{1,2}[-./月]\d{1,2})', body)
            if date_match:
                date = date_match.group(1).replace('.','-').replace('/','-').replace('年','-').replace('月','-')
            
            # 3. 存入结果
            if not any(c['link'] == href for c in cases):
                print(f"🔍 搜到: {title[:15]}...")
                cases.append({
                    "title": title,
                    "date": date,
                    "tag": "最新交易", # 统一打标
                    "link": href
                })

    except Exception as e:
        print(f"搜索出错: {e}")

    # --- 兜底逻辑 ---
    # 如果搜不到（极少情况），写入一条提示
    if len(cases) == 0:
        print("⚠️ 搜索引擎未返回数据")
        cases = [
            {
                "title": "点击查看中伦官网最新业绩 (自动同步暂缓)", 
                "date": time.strftime("%Y-%m-%d"), 
                "tag": "快速访问", 
                "link": "https://www.zhonglun.com/news.html"
            }
        ]
    else:
        print(f"✅ 成功通过搜索获取 {len(cases)} 条数据！")

    # 保存
    with open('cases.json', 'w', encoding='utf-8') as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_via_search()
