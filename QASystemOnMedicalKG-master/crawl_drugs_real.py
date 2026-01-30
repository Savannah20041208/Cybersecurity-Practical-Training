#!/usr/bin/env python3
# coding: utf-8
"""
药品数据爬取脚本 - 从公开数据源获取真实药品信息
输出格式与 import_drugs.py 兼容（JSONL）

数据源选择（按优先级）：
1. 药智网开放 API（需要注册获取 API Key）
2. 丁香园用药助手公开数据
3. GitHub 上的开源药品数据集

用法:
    python crawl_drugs_real.py --source yaozh --pages 100
    python crawl_drugs_real.py --source dxy --pages 100
    python crawl_drugs_real.py --source github
    python crawl_drugs_real.py --resume

注意：请遵守各数据源的使用条款
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

REQUEST_TIMEOUT = 30
REQUEST_DELAY_MIN = 2.0
REQUEST_DELAY_MAX = 4.0
MAX_RETRIES = 3

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
]

os.makedirs(OUTPUT_DIR, exist_ok=True)


class DrugCrawler:
    """药品数据爬虫基类"""

    def __init__(self, output_file):
        self.output_file = output_file
        self.session = requests.Session()
        self.crawled_ids = set()
        self.stats = {'pages': 0, 'items': 0, 'success': 0, 'failed': 0, 'duplicates': 0}
        self._load_existing()

    def _load_existing(self):
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
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

    def _delay(self):
        time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))

    def _request(self, url, method='GET', **kwargs):
        for attempt in range(MAX_RETRIES):
            try:
                kwargs.setdefault('headers', self._get_headers())
                kwargs.setdefault('timeout', REQUEST_TIMEOUT)
                if method.upper() == 'GET':
                    resp = self.session.get(url, **kwargs)
                else:
                    resp = self.session.post(url, **kwargs)
                resp.raise_for_status()
                return resp
            except Exception as e:
                print(f"  [Retry {attempt+1}/{MAX_RETRIES}] {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
        return None

    def _save_drug(self, drug):
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

    def _save_progress(self, page, source):
        progress = {'page': page, 'source': source, 'stats': self.stats, 'timestamp': datetime.now().isoformat()}
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)

    def _load_progress(self):
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return None

    def print_stats(self):
        print(f"\n{'='*50}")
        print("[完成] 爬取统计:")
        print(f"  页数: {self.stats['pages']}")
        print(f"  总条目: {self.stats['items']}")
        print(f"  成功: {self.stats['success']}")
        print(f"  重复: {self.stats['duplicates']}")
        print(f"  失败: {self.stats['failed']}")
        print(f"  输出: {self.output_file}")
        print(f"{'='*50}")


class YaoZhCrawler(DrugCrawler):
    """
    药智网爬虫
    药智网有公开的药品数据库，但需要登录才能访问完整数据
    这里爬取公开可访问的部分
    """

    def __init__(self):
        super().__init__(os.path.join(OUTPUT_DIR, 'drugs_yaozh.jsonl'))
        self.base_url = "https://db.yaozh.com"

    def crawl_category(self, category='guochan', max_pages=100, resume=False):
        """
        爬取药品分类页面
        category: guochan(国产), jinkuo(进口)
        """
        print(f"\n{'='*50}")
        print(f"药智网药品数据爬取")
        print(f"{'='*50}")
        print(f"分类: {category}")
        print(f"目标: {max_pages} 页")
        print(f"{'='*50}\n")

        start_page = 1
        if resume:
            progress = self._load_progress()
            if progress and progress.get('source') == f'yaozh_{category}':
                start_page = progress.get('page', 1) + 1
                print(f"[Resume] 从第 {start_page} 页继续")

        for page in range(start_page, start_page + max_pages):
            print(f"[Page {page}] 正在爬取...")

            try:
                # 药智网药品目录 URL
                url = f"{self.base_url}/yaopinmulu?p={page}&pageSize=20"
                resp = self._request(url)

                if not resp:
                    print("  请求失败")
                    self._delay()
                    continue

                # 解析 HTML（需要 BeautifulSoup）
                drugs = self._parse_list_page(resp.text)

                if not drugs:
                    print("  无数据或需要登录")
                    break

                self.stats['pages'] += 1
                self.stats['items'] += len(drugs)

                saved = sum(1 for d in drugs if self._save_drug(d))
                print(f"  获取 {len(drugs)} 条，保存 {saved} 条")

                self._save_progress(page, f'yaozh_{category}')
                self._delay()

            except KeyboardInterrupt:
                print("\n[中断] 保存进度...")
                self._save_progress(page, f'yaozh_{category}')
                break
            except Exception as e:
                print(f"  [Error] {e}")
                self._delay()

        self.print_stats()

    def _parse_list_page(self, html):
        """解析列表页 HTML"""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            print("需要安装 BeautifulSoup: pip install beautifulsoup4 lxml")
            return []

        soup = BeautifulSoup(html, 'lxml')
        drugs = []

        # 查找药品表格
        table = soup.find('table', class_='table')
        if not table:
            return []

        rows = table.find_all('tr')[1:]  # 跳过表头
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
                try:
                    drug = {
                        'approval_no': cols[0].get_text(strip=True),
                        'generic_name': cols[1].get_text(strip=True),
                        'dosage_form': cols[2].get_text(strip=True),
                        'spec': cols[3].get_text(strip=True),
                        'enterprise': cols[4].get_text(strip=True),
                        'source': 'yaozh.com',
                        'updated_at': datetime.now().strftime('%Y-%m-%d'),
                    }
                    if drug['approval_no']:
                        drugs.append(drug)
                except:
                    continue

        return drugs


class GitHubDataCrawler(DrugCrawler):
    """
    从 GitHub 开源项目下载药品数据
    使用已有的开源药品数据集
    """

    # 一些开源药品数据集 URL
    DATASETS = {
        # 中文医疗知识图谱数据
        'cmekg': 'https://raw.githubusercontent.com/king-yyf/CMeKG_tools/master/data/drug.json',
        # 其他开源数据集（需要确认可用性）
    }

    def __init__(self):
        super().__init__(os.path.join(OUTPUT_DIR, 'drugs_github.jsonl'))

    def download_dataset(self, dataset_name='cmekg'):
        """下载并解析开源数据集"""
        if dataset_name not in self.DATASETS:
            print(f"未知数据集: {dataset_name}")
            print(f"可用数据集: {list(self.DATASETS.keys())}")
            return

        url = self.DATASETS[dataset_name]
        print(f"\n{'='*50}")
        print(f"下载开源药品数据集: {dataset_name}")
        print(f"URL: {url}")
        print(f"{'='*50}\n")

        resp = self._request(url)
        if not resp:
            print("下载失败")
            return

        try:
            data = resp.json()
            if isinstance(data, list):
                drugs = data
            elif isinstance(data, dict):
                drugs = data.get('data') or data.get('drugs') or [data]
            else:
                drugs = []

            print(f"获取 {len(drugs)} 条记录")

            for item in drugs:
                drug = self._normalize_drug(item, dataset_name)
                if drug:
                    self._save_drug(drug)

            self.print_stats()

        except Exception as e:
            print(f"解析失败: {e}")

    def _normalize_drug(self, item, source):
        """将不同格式的数据标准化"""
        # 尝试提取批准文号
        approval_no = (
            item.get('approval_no') or
            item.get('approvalNo') or
            item.get('批准文号') or
            item.get('id') or
            ''
        )

        # 如果没有批准文号，尝试生成一个唯一标识
        if not approval_no:
            name = item.get('name') or item.get('generic_name') or item.get('药品名称') or ''
            if name:
                approval_no = f"GITHUB_{hash(name) % 100000000:08d}"
            else:
                return None

        generic_name = (
            item.get('name') or
            item.get('generic_name') or
            item.get('药品名称') or
            item.get('通用名') or
            ''
        )

        return {
            'approval_no': str(approval_no),
            'generic_name': generic_name,
            'brand_name': item.get('brand_name') or item.get('商品名'),
            'dosage_form': item.get('dosage_form') or item.get('剂型'),
            'spec': item.get('spec') or item.get('规格'),
            'enterprise': item.get('enterprise') or item.get('生产企业') or item.get('manufacturer'),
            'indications': item.get('indications') or item.get('适应症') or item.get('功能主治'),
            'usage': item.get('usage') or item.get('用法用量'),
            'contraindications': item.get('contraindications') or item.get('禁忌'),
            'adverse_reactions': item.get('adverse_reactions') or item.get('不良反应'),
            'source': f'github_{source}',
            'updated_at': datetime.now().strftime('%Y-%m-%d'),
        }


class LocalFileCrawler(DrugCrawler):
    """
    从本地文件导入药品数据
    支持多种格式：JSON, CSV, Excel
    """

    def __init__(self):
        super().__init__(os.path.join(OUTPUT_DIR, 'drugs_local.jsonl'))

    def import_from_json(self, filepath):
        """从 JSON 文件导入"""
        print(f"\n从 JSON 文件导入: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            drugs = data
        elif isinstance(data, dict):
            drugs = data.get('data') or data.get('drugs') or data.get('list') or [data]
        else:
            drugs = []

        print(f"读取 {len(drugs)} 条记录")

        for item in drugs:
            drug = self._normalize(item)
            if drug:
                self._save_drug(drug)

        self.print_stats()

    def import_from_csv(self, filepath):
        """从 CSV 文件导入"""
        import csv
        print(f"\n从 CSV 文件导入: {filepath}")

        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                drug = self._normalize(row)
                if drug:
                    self._save_drug(drug)
                count += 1

        print(f"读取 {count} 条记录")
        self.print_stats()

    def _normalize(self, item):
        """标准化字段名"""
        # 字段映射（支持多种命名方式）
        field_map = {
            'approval_no': ['approval_no', 'approvalNo', '批准文号', 'APPROVAL_NUM', 'id'],
            'generic_name': ['generic_name', 'genericName', '通用名', '药品名称', 'PRODUCT_NAME', 'name'],
            'brand_name': ['brand_name', 'brandName', '商品名', 'TRADE_NAME'],
            'dosage_form': ['dosage_form', 'dosageForm', '剂型', 'DOSAGE_FORM'],
            'spec': ['spec', '规格', 'SPEC', 'specification'],
            'enterprise': ['enterprise', 'enterpriseName', '生产企业', 'ENTERPRISE_NAME', 'manufacturer'],
            'otc_type': ['otc_type', 'otcType', 'OTC分类', 'OTC_TYPE'],
            'indications': ['indications', '适应症', '功能主治'],
            'usage': ['usage', '用法用量'],
            'contraindications': ['contraindications', '禁忌'],
            'adverse_reactions': ['adverse_reactions', '不良反应'],
        }

        result = {'source': 'local_file', 'updated_at': datetime.now().strftime('%Y-%m-%d')}

        for target_field, source_fields in field_map.items():
            for sf in source_fields:
                if sf in item and item[sf]:
                    result[target_field] = str(item[sf]).strip()
                    break

        # 必须有批准文号
        if not result.get('approval_no'):
            return None

        return result


def main():
    parser = argparse.ArgumentParser(description='药品数据爬取')
    parser.add_argument('--source', '-s', choices=['yaozh', 'github', 'local'],
                        default='github', help='数据源')
    parser.add_argument('--pages', '-p', type=int, default=100, help='爬取页数')
    parser.add_argument('--resume', '-r', action='store_true', help='断点续爬')
    parser.add_argument('--file', '-f', help='本地文件路径（用于 local 源）')
    parser.add_argument('--dataset', '-d', default='cmekg', help='GitHub 数据集名称')
    args = parser.parse_args()

    if args.source == 'yaozh':
        crawler = YaoZhCrawler()
        crawler.crawl_category(max_pages=args.pages, resume=args.resume)
        output_file = crawler.output_file

    elif args.source == 'github':
        crawler = GitHubDataCrawler()
        crawler.download_dataset(args.dataset)
        output_file = crawler.output_file

    elif args.source == 'local':
        if not args.file:
            print("请指定本地文件: --file <path>")
            sys.exit(1)
        crawler = LocalFileCrawler()
        if args.file.endswith('.csv'):
            crawler.import_from_csv(args.file)
        else:
            crawler.import_from_json(args.file)
        output_file = crawler.output_file

    print(f"\n下一步：导入到 Neo4j")
    print(f"  python import_drugs.py --file {output_file}")


if __name__ == '__main__':
    main()
