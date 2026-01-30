#!/usr/bin/env python3
# coding: utf-8
"""
药品数据爬取脚本 - 从国家药品监督管理局（NMPA）获取真实药品信息
输出格式与 import_drugs.py 兼容（JSONL）

数据源：国家药品监督管理局公开数据查询
- 国产药品: tableId=25
- 进口药品: tableId=36

用法:
    python crawl_drugs_nmpa.py --pages 100       # 爬取100页（约1500条）
    python crawl_drugs_nmpa.py --pages 3000      # 爬取3000页（约45000条）
    python crawl_drugs_nmpa.py --resume          # 断点续爬
    python crawl_drugs_nmpa.py --type jkyp       # 爬取进口药品

注意：
- 请遵守网站使用条款，设置合理请求间隔
- 仅用于学习研究目的
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
    import requests
except ImportError:
    print("请先安装依赖: pip install requests")
    sys.exit(1)

# ============ 配置 ============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'data')
PROGRESS_FILE = os.path.join(OUTPUT_DIR, 'crawl_progress.json')

# 请求配置
REQUEST_TIMEOUT = 30
REQUEST_DELAY_MIN = 1.5
REQUEST_DELAY_MAX = 3.0
MAX_RETRIES = 3
PAGE_SIZE = 15  # NMPA 每页条数

# NMPA API 配置
NMPA_LIST_API = "https://www.nmpa.gov.cn/datasearch/search-list.html"
NMPA_INFO_API = "https://www.nmpa.gov.cn/datasearch/search-info.html"

# 药品类型
DRUG_TYPES = {
    'gcyp': {'tableId': '25', 'name': '国产药品'},
    'jkyp': {'tableId': '36', 'name': '进口药品'},
}

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]


class NMPACrawler:
    """NMPA 药品数据爬虫"""

    def __init__(self, drug_type='gcyp', output_file=None):
        self.drug_type = drug_type
        self.type_config = DRUG_TYPES.get(drug_type, DRUG_TYPES['gcyp'])
        self.output_file = output_file or os.path.join(OUTPUT_DIR, f'drugs_{drug_type}.jsonl')
        self.session = requests.Session()
        self.crawled_ids = set()
        self.stats = {'pages': 0, 'items': 0, 'success': 0, 'failed': 0, 'duplicates': 0}

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        self._load_existing()

    def _load_existing(self):
        """加载已爬取记录"""
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if data.get('approval_no'):
                                self.crawled_ids.add(data['approval_no'])
                        except:
                            pass
            print(f"[Resume] 已加载 {len(self.crawled_ids)} 条记录")

    def _get_headers(self):
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://www.nmpa.gov.cn',
            'Referer': 'https://www.nmpa.gov.cn/datasearch/home-index.html',
        }

    def _delay(self):
        time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))

    def _request_post(self, url, payload, retries=MAX_RETRIES):
        """POST 请求"""
        for attempt in range(retries):
            try:
                resp = self.session.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=REQUEST_TIMEOUT
                )
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                print(f"  [Retry {attempt+1}/{retries}] Error: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        return None

    def _save_drug(self, drug):
        """保存药品数据"""
        approval_no = drug.get('approval_no')
        if not approval_no:
            self.stats['failed'] += 1
            return False

        if approval_no in self.crawled_ids:
            self.stats['duplicates'] += 1
            return False

        self.crawled_ids.add(approval_no)
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(drug, ensure_ascii=False) + '\n')
        self.stats['success'] += 1
        return True

    def _save_progress(self, page, drug_type):
        """保存进度"""
        progress = {
            'page': page,
            'drug_type': drug_type,
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

    def fetch_list_page(self, page=1):
        """
        获取药品列表页
        NMPA 使用 POST 请求，返回 JSON 数据
        """
        payload = {
            "tableId": self.type_config['tableId'],
            "pageNum": page,
            "pageSize": PAGE_SIZE,
            "searchValue": "",
            "conditionList": []
        }

        data = self._request_post(NMPA_LIST_API, payload)
        if not data:
            return []

        # 解析返回数据
        items = []
        try:
            # NMPA 返回格式: {"list": [...], "totalCount": xxx}
            drug_list = data.get('list') or data.get('data') or []
            for item in drug_list:
                drug = self._parse_list_item(item)
                if drug:
                    items.append(drug)
        except Exception as e:
            print(f"  [Parse Error] {e}")

        return items

    def _parse_list_item(self, item):
        """
        解析列表项
        NMPA 返回字段（国产药品 tableId=25）:
        - APPROVAL_NUM: 批准文号
        - PRODUCT_NAME: 产品名称
        - ENTERPRISE_NAME: 生产企业
        - DOSAGE_FORM: 剂型
        - SPEC: 规格
        等
        """
        try:
            # 字段名可能有变化，尝试多种可能
            approval_no = (
                item.get('APPROVAL_NUM') or
                item.get('approvalNum') or
                item.get('approval_num') or
                item.get('批准文号') or
                ''
            ).strip()

            if not approval_no:
                return None

            generic_name = (
                item.get('PRODUCT_NAME') or
                item.get('productName') or
                item.get('product_name') or
                item.get('产品名称') or
                ''
            ).strip()

            enterprise = (
                item.get('ENTERPRISE_NAME') or
                item.get('enterpriseName') or
                item.get('enterprise_name') or
                item.get('生产企业') or
                ''
            ).strip()

            dosage_form = (
                item.get('DOSAGE_FORM') or
                item.get('dosageForm') or
                item.get('dosage_form') or
                item.get('剂型') or
                ''
            ).strip()

            spec = (
                item.get('SPEC') or
                item.get('spec') or
                item.get('规格') or
                ''
            ).strip()

            # 构建标准格式
            drug = {
                'approval_no': approval_no,
                'generic_name': generic_name,
                'brand_name': None,  # 列表页通常没有商品名
                'dosage_form': dosage_form,
                'spec': spec,
                'enterprise': enterprise,
                'source': 'NMPA',
                'source_type': self.type_config['name'],
                'updated_at': datetime.now().strftime('%Y-%m-%d'),
            }

            # 尝试提取更多字段
            if item.get('OTC_TYPE') or item.get('otcType'):
                drug['otc_type'] = item.get('OTC_TYPE') or item.get('otcType')

            return drug

        except Exception as e:
            print(f"  [Parse Item Error] {e}")
            return None

    def crawl(self, max_pages=100, resume=False):
        """主爬取流程"""
        start_page = 1

        if resume:
            progress = self._load_progress()
            if progress and progress.get('drug_type') == self.drug_type:
                start_page = progress.get('page', 1) + 1
                print(f"[Resume] 从第 {start_page} 页继续")

        print(f"\n{'='*50}")
        print(f"NMPA 药品数据爬取")
        print(f"{'='*50}")
        print(f"类型: {self.type_config['name']} (tableId={self.type_config['tableId']})")
        print(f"目标: {max_pages} 页（约 {max_pages * PAGE_SIZE} 条）")
        print(f"输出: {self.output_file}")
        print(f"{'='*50}\n")

        empty_count = 0  # 连续空页计数

        for page in range(start_page, start_page + max_pages):
            print(f"[Page {page}] 正在爬取...")

            try:
                items = self.fetch_list_page(page)

                if not items:
                    empty_count += 1
                    print(f"  无数据（连续 {empty_count} 页）")
                    if empty_count >= 5:
                        print("  连续5页无数据，可能已到末页")
                        break
                    self._delay()
                    continue

                empty_count = 0
                self.stats['pages'] += 1
                self.stats['items'] += len(items)

                saved = sum(1 for item in items if self._save_drug(item))
                print(f"  获取 {len(items)} 条，保存 {saved} 条")

                self._save_progress(page, self.drug_type)
                self._delay()

            except KeyboardInterrupt:
                print("\n[中断] 保存进度...")
                self._save_progress(page, self.drug_type)
                break
            except Exception as e:
                print(f"  [Error] {e}")
                self._save_progress(page, self.drug_type)
                self._delay()

        # 统计
        print(f"\n{'='*50}")
        print("[完成] 爬取统计:")
        print(f"  页数: {self.stats['pages']}")
        print(f"  总条目: {self.stats['items']}")
        print(f"  成功: {self.stats['success']}")
        print(f"  重复: {self.stats['duplicates']}")
        print(f"  失败: {self.stats['failed']}")
        print(f"  输出: {self.output_file}")
        print(f"{'='*50}")


def main():
    parser = argparse.ArgumentParser(description='NMPA 药品数据爬取')
    parser.add_argument('--pages', '-p', type=int, default=100, help='爬取页数')
    parser.add_argument('--type', '-t', choices=['gcyp', 'jkyp'], default='gcyp',
                        help='药品类型: gcyp=国产药品, jkyp=进口药品')
    parser.add_argument('--resume', '-r', action='store_true', help='断点续爬')
    parser.add_argument('--output', '-o', help='输出文件路径')
    args = parser.parse_args()

    crawler = NMPACrawler(drug_type=args.type, output_file=args.output)
    crawler.crawl(max_pages=args.pages, resume=args.resume)

    print(f"\n下一步：导入到 Neo4j")
    print(f"  python import_drugs.py --file {crawler.output_file}")


if __name__ == '__main__':
    main()
