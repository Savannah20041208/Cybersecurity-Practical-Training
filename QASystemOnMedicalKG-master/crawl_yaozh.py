#!/usr/bin/env python3
# coding: utf-8
"""
从药智网爬取药品数据（权威来源）
药智网整合了 NMPA 的结构化数据

用法:
    python crawl_yaozh.py --pages 100
    python crawl_yaozh.py --pages 500 --headless
    python crawl_yaozh.py --resume

依赖:
    pip install playwright
    playwright install chromium
"""

import os
import sys
import json
import time
import random
import argparse
import re
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("请先安装依赖: pip install playwright && playwright install chromium")
    sys.exit(1)

# ============ 配置 ============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'drugs_yaozh.jsonl')
PROGRESS_FILE = os.path.join(OUTPUT_DIR, 'yaozh_progress.json')

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 药智网数据库入口
YAOZH_DB_URL = "https://db.yaozh.com/"


class YaoZhCrawler:
    """药智网药品数据爬虫"""

    def __init__(self, headless=False):
        self.headless = headless
        self.crawled_ids = set()
        self.stats = {'pages': 0, 'items': 0, 'success': 0, 'failed': 0}
        self._load_existing()

    def _load_existing(self):
        """加载已爬取记录"""
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if data.get('approval_no'):
                                self.crawled_ids.add(data['approval_no'])
                        except:
                            pass
            print(f"[Resume] 已加载 {len(self.crawled_ids)} 条记录")

    def _save_drug(self, drug):
        """保存药品数据"""
        approval_no = drug.get('approval_no')
        if not approval_no:
            self.stats['failed'] += 1
            return False

        if approval_no in self.crawled_ids:
            return False

        self.crawled_ids.add(approval_no)
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(drug, ensure_ascii=False) + '\n')
        self.stats['success'] += 1
        return True

    def _save_progress(self, page, db_name):
        """保存进度"""
        progress = {
            'page': page,
            'db_name': db_name,
            'stats': self.stats,
            'timestamp': datetime.now().isoformat()
        }
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)

    def _load_progress(self):
        """加载进度"""
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return None

    def crawl(self, max_pages=100, resume=False):
        """主爬取流程"""
        print(f"\n{'='*50}")
        print("药智网药品数据爬取")
        print(f"{'='*50}")
        print(f"目标: {max_pages} 页")
        print(f"输出: {OUTPUT_FILE}")
        print(f"{'='*50}\n")

        with sync_playwright() as p:
            print("[Init] 启动浏览器...")
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()

            try:
                # 访问药智网数据库首页
                print(f"[Navigate] 访问 {YAOZH_DB_URL}")
                page.goto(YAOZH_DB_URL, wait_until='networkidle', timeout=60000)
                time.sleep(3)

                # 截图调试
                page.screenshot(path=os.path.join(OUTPUT_DIR, 'yaozh_home.png'))
                print("[Debug] 已保存首页截图到 data/yaozh_home.png")

                # 查找数据库入口链接
                print("[Navigate] 查找药品数据库入口...")

                # 尝试找到"国产药品"或类似链接
                db_links = []
                links = page.query_selector_all('a')
                for link in links:
                    try:
                        text = link.inner_text().strip()
                        href = link.get_attribute('href') or ''
                        if any(kw in text for kw in ['国产药品', '药品目录', '药品数据', 'OTC', '处方药']):
                            db_links.append({'text': text, 'href': href})
                            print(f"  找到链接: {text} -> {href}")
                    except:
                        continue

                if not db_links:
                    print("[Debug] 未找到药品数据库链接，尝试搜索功能...")
                    
                    # 尝试使用搜索功能
                    search_input = page.query_selector('input[type="text"], input[placeholder*="搜索"], .search-input')
                    if search_input:
                        print("[Search] 找到搜索框，尝试搜索常用药品...")
                        
                        # 搜索一些常用药品
                        test_drugs = ['阿莫西林', '布洛芬', '头孢', '感冒灵']
                        
                        for drug_name in test_drugs:
                            try:
                                search_input.fill(drug_name)
                                time.sleep(0.5)
                                
                                # 点击搜索按钮
                                search_btn = page.query_selector('button[type="submit"], .search-btn, button:has-text("搜索")')
                                if search_btn:
                                    search_btn.click()
                                else:
                                    search_input.press('Enter')
                                
                                time.sleep(3)
                                
                                # 截图
                                page.screenshot(path=os.path.join(OUTPUT_DIR, f'yaozh_search_{drug_name}.png'))
                                print(f"  搜索 '{drug_name}' 完成，已保存截图")
                                
                                # 解析搜索结果
                                drugs = self._parse_search_results(page)
                                if drugs:
                                    for drug in drugs:
                                        self._save_drug(drug)
                                    print(f"  获取 {len(drugs)} 条结果")
                                
                                # 返回首页
                                page.goto(YAOZH_DB_URL, wait_until='networkidle', timeout=30000)
                                time.sleep(2)
                                search_input = page.query_selector('input[type="text"], input[placeholder*="搜索"], .search-input')
                                
                            except Exception as e:
                                print(f"  搜索 '{drug_name}' 失败: {e}")
                    else:
                        print("[Debug] 未找到搜索框")
                        
                        # 保存页面源码用于分析
                        content = page.content()
                        with open(os.path.join(OUTPUT_DIR, 'yaozh_home.html'), 'w', encoding='utf-8') as f:
                            f.write(content)
                        print("[Debug] 已保存页面源码到 data/yaozh_home.html")
                else:
                    # 点击第一个数据库链接
                    first_link = db_links[0]
                    print(f"[Navigate] 点击: {first_link['text']}")
                    
                    if first_link['href'].startswith('http'):
                        page.goto(first_link['href'], wait_until='networkidle', timeout=60000)
                    else:
                        page.click(f'a:has-text("{first_link["text"]}")')
                    
                    time.sleep(3)
                    page.screenshot(path=os.path.join(OUTPUT_DIR, 'yaozh_db.png'))
                    print("[Debug] 已保存数据库页面截图")
                    
                    # 解析数据表格
                    self._crawl_table_pages(page, max_pages, resume)

            except Exception as e:
                print(f"[Error] {e}")
                import traceback
                traceback.print_exc()
            finally:
                browser.close()

        # 统计
        print(f"\n{'='*50}")
        print("[完成] 爬取统计:")
        print(f"  页数: {self.stats['pages']}")
        print(f"  总条目: {self.stats['items']}")
        print(f"  成功: {self.stats['success']}")
        print(f"  失败: {self.stats['failed']}")
        print(f"  输出: {OUTPUT_FILE}")
        print(f"{'='*50}")

    def _parse_search_results(self, page):
        """解析搜索结果"""
        drugs = []
        
        # 尝试多种选择器
        selectors = [
            '.search-result-item',
            '.result-item',
            '.drug-item',
            'table tbody tr',
            '.list-item',
        ]
        
        for selector in selectors:
            items = page.query_selector_all(selector)
            if items:
                print(f"  使用选择器 '{selector}' 找到 {len(items)} 个结果")
                for item in items:
                    drug = self._parse_result_item(item)
                    if drug:
                        drugs.append(drug)
                break
        
        return drugs

    def _parse_result_item(self, item):
        """解析单个结果项"""
        try:
            text = item.inner_text()
            
            # 尝试提取批准文号
            approval_match = re.search(r'国药准字[A-Z]\d{8}', text)
            if not approval_match:
                approval_match = re.search(r'[A-Z]{1,2}\d{8}', text)
            
            approval_no = approval_match.group(0) if approval_match else None
            
            # 提取药品名称（通常是第一行或标题）
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            generic_name = lines[0] if lines else None
            
            if approval_no or generic_name:
                drug = {
                    'approval_no': approval_no,
                    'generic_name': generic_name,
                    'source': 'yaozh.com',
                    'updated_at': datetime.now().strftime('%Y-%m-%d'),
                    'raw_text': text[:500],  # 保存原始文本用于后续解析
                }
                
                # 尝试提取更多字段
                for line in lines:
                    if '企业' in line or '生产' in line:
                        drug['enterprise'] = line.split('：')[-1].split(':')[-1].strip()
                    elif '剂型' in line:
                        drug['dosage_form'] = line.split('：')[-1].split(':')[-1].strip()
                    elif '规格' in line:
                        drug['spec'] = line.split('：')[-1].split(':')[-1].strip()
                
                return drug
        except:
            pass
        return None

    def _crawl_table_pages(self, page, max_pages, resume):
        """爬取表格分页数据"""
        start_page = 1
        if resume:
            progress = self._load_progress()
            if progress:
                start_page = progress.get('page', 1) + 1
                print(f"[Resume] 从第 {start_page} 页继续")

        empty_count = 0

        for page_num in range(start_page, start_page + max_pages):
            print(f"\n[Page {page_num}] 正在爬取...")

            try:
                time.sleep(random.uniform(2.0, 4.0))

                # 查找表格
                table = page.query_selector('table tbody, .el-table__body, .data-table')
                if not table:
                    empty_count += 1
                    print(f"  未找到表格（连续 {empty_count} 页）")
                    if empty_count >= 3:
                        break
                    continue

                rows = table.query_selector_all('tr')
                drugs = []

                for row in rows:
                    cells = row.query_selector_all('td')
                    if len(cells) >= 3:
                        try:
                            drug = {
                                'approval_no': cells[0].inner_text().strip() if len(cells) > 0 else None,
                                'generic_name': cells[1].inner_text().strip() if len(cells) > 1 else None,
                                'dosage_form': cells[2].inner_text().strip() if len(cells) > 2 else None,
                                'spec': cells[3].inner_text().strip() if len(cells) > 3 else None,
                                'enterprise': cells[4].inner_text().strip() if len(cells) > 4 else None,
                                'source': 'yaozh.com',
                                'updated_at': datetime.now().strftime('%Y-%m-%d'),
                            }
                            if drug['approval_no'] and '批准文号' not in drug['approval_no']:
                                drugs.append(drug)
                        except:
                            continue

                if drugs:
                    empty_count = 0
                    self.stats['pages'] += 1
                    self.stats['items'] += len(drugs)
                    saved = sum(1 for d in drugs if self._save_drug(d))
                    print(f"  获取 {len(drugs)} 条，保存 {saved} 条")
                else:
                    empty_count += 1

                self._save_progress(page_num, 'drug')

                # 翻页
                next_btn = page.query_selector('.el-pagination .btn-next:not(.disabled), .next-page, button:has-text("下一页")')
                if next_btn:
                    next_btn.click()
                else:
                    print("  已到最后一页")
                    break

            except KeyboardInterrupt:
                print("\n[中断] 保存进度...")
                self._save_progress(page_num, 'drug')
                break
            except Exception as e:
                print(f"  [Error] {e}")


def main():
    parser = argparse.ArgumentParser(description='药智网药品数据爬取')
    parser.add_argument('--pages', '-p', type=int, default=100, help='爬取页数')
    parser.add_argument('--headless', action='store_true', help='无头模式')
    parser.add_argument('--resume', '-r', action='store_true', help='断点续爬')
    args = parser.parse_args()

    crawler = YaoZhCrawler(headless=args.headless)
    crawler.crawl(max_pages=args.pages, resume=args.resume)

    print(f"\n下一步：导入到 Neo4j")
    print(f"  python import_drugs.py --file {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
