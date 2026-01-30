#!/usr/bin/env python3
# coding: utf-8
"""
药品数据爬取脚本 - 从公开数据源获取真实药品信息
输出格式与 import_drugs.py 兼容（JSONL）

数据源：
1. 国家药品监督管理局（NMPA）公开数据查询接口
   - 国产药品: https://www.nmpa.gov.cn/datasearch/home-index.html
   - 包含：批准文号、企业、通用名、剂型、规格等

用法:
    python crawl_drugs.py --pages 100        # 爬取前100页（约1500条）
    python crawl_drugs.py --pages 1000       # 爬取1000页（约15000条）
    python crawl_drugs.py --resume           # 断点续爬
    python crawl_drugs.py --type gcyp        # 国产药品（默认）
    python crawl_drugs.py --type jkyp        # 进口药品

注意：
- 请遵守网站 robots.txt 和使用条款
- 建议设置合理的请求间隔，避免对服务器造成压力
- 仅用于学习研究目的
"""

import os
import sys
import json
import time
import random
import argparse
from datetime import datetime
from urllib.parse import urlencode

# 需要安装: pip install requests
try:
    import requests
except ImportError:
    print("请先安装依赖: pip install requests")
    sys.exit(1)

# ============ 配置 ============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'drugs_crawled.jsonl')
PROGRESS_FILE = os.path.join(OUTPUT_DIR, 'crawl_progress.json')

# 请求配置
REQUEST_TIMEOUT = 30
REQUEST_DELAY_MIN = 1.5  # 最小请求间隔（秒）
REQUEST_DELAY_MAX = 3.5  # 最大请求间隔（秒）
MAX_RETRIES = 3

# NMPA 数据查询接口（国家药品监督管理局）
# 国产药品查询接口
NMPA_API_BASE = "https://www.nmpa.gov.cn/datasearch/search-list.html"
NMPA_API_DATA = "https://www.nmpa.gov.cn/datasearch/search-info.html"

# 药品类型配置
DRUG_TYPES = {
    'gcyp': {  # 国产药品
        'tableId': '25',
        'tableName': '国产药品',
        'searchType': 'list',
    },
    'jkyp': {  # 进口药品
        'tableId': '36',
        'tableName': '进口药品',
        'searchType': 'list',
    },
}

# User-Agent 池
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
]


class DrugCrawler:
    """药品数据爬虫"""

    def __init__(self, output_file=OUTPUT_FILE, delay_range=(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)):
        self.output_file = output_file
        self.delay_range = delay_range
        self.session = requests.Session()
        self.crawled_approval_nos = set()  # 已爬取的批准文号（去重）
        self.stats = {
            'total_pages': 0,
            'total_items': 0,
            'success': 0,
            'failed': 0,
            'duplicates': 0,
        }

        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # 加载已爬取的批准文号（用于去重和断点续爬）
        self._load_existing()

    def _load_existing(self):
        """加载已爬取的数据（用于去重）"""
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            if data.get('approval_no'):
                                self.crawled_approval_nos.add(data['approval_no'])
                        except:
                            pass
            print(f"[Resume] 已加载 {len(self.crawled_approval_nos)} 条已爬取记录")

    def _get_headers(self):
        """获取随机请求头"""
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

    def _delay(self):
        """随机延迟"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)

    def _request(self, url, method='GET', **kwargs):
        """发送请求（带重试）"""
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
                print(f"  [Retry {attempt + 1}/{MAX_RETRIES}] {url[:80]}... Error: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # 指数退避

        return None

    def _save_drug(self, drug_data):
        """保存单条药品数据"""
        approval_no = drug_data.get('approval_no')
        if not approval_no:
            return False

        # 去重
        if approval_no in self.crawled_approval_nos:
            self.stats['duplicates'] += 1
            return False

        self.crawled_approval_nos.add(approval_no)

        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(drug_data, ensure_ascii=False) + '\n')

        self.stats['success'] += 1
        return True

    def _save_progress(self, current_page):
        """保存爬取进度"""
        progress = {
            'current_page': current_page,
            'stats': self.stats,
            'timestamp': datetime.now().isoformat(),
        }
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)

    def _load_progress(self):
        """加载爬取进度"""
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    # ============ 数据源1：药智网（yaozh.com）============
    # 注意：实际使用时请确认网站的使用条款
    def crawl_yaozh_list(self, page=1):
        """
        从药智网获取药品列表
        这是一个示例实现，实际 URL 和解析逻辑需要根据网站结构调整
        """
        # 药智网药品目录页面（示例，需要根据实际情况调整）
        url = f"https://db.yaozh.com/yaopinmulu?p={page}"

        resp = self._request(url)
        if not resp:
            return []

        soup = BeautifulSoup(resp.text, 'lxml')
        drugs = []

        # 解析药品列表（示例，需要根据实际 HTML 结构调整）
        # 这里是一个占位实现
        rows = soup.select('table.list tbody tr')
        for row in rows:
            try:
                cols = row.select('td')
                if len(cols) >= 5:
                    drug = {
                        'approval_no': cols[0].get_text(strip=True),
                        'generic_name': cols[1].get_text(strip=True),
                        'dosage_form': cols[2].get_text(strip=True),
                        'spec': cols[3].get_text(strip=True),
                        'enterprise': cols[4].get_text(strip=True),
                        'source': 'yaozh.com',
                        'updated_at': datetime.now().strftime('%Y-%m-%d'),
                    }
                    drugs.append(drug)
            except Exception as e:
                continue

        return drugs

    # ============ 数据源2：模拟数据生成（用于测试） ============
    def generate_mock_data(self, count=1000):
        """
        生成模拟药品数据（用于测试导入流程）
        实际使用时应替换为真实爬取逻辑
        """
        print(f"[Mock] 生成 {count} 条模拟药品数据...")

        # 常见药品通用名
        generic_names = [
            '阿莫西林', '头孢克肟', '阿奇霉素', '左氧氟沙星', '甲硝唑',
            '布洛芬', '对乙酰氨基酚', '双氯芬酸钠', '塞来昔布', '美洛昔康',
            '奥美拉唑', '雷贝拉唑', '法莫替丁', '多潘立酮', '莫沙必利',
            '二甲双胍', '格列美脲', '阿卡波糖', '西格列汀', '达格列净',
            '氨氯地平', '硝苯地平', '缬沙坦', '氯沙坦', '厄贝沙坦',
            '阿托伐他汀', '瑞舒伐他汀', '辛伐他汀', '普伐他汀', '氟伐他汀',
            '氯雷他定', '西替利嗪', '依巴斯汀', '非索非那定', '地氯雷他定',
            '板蓝根', '连花清瘟', '藿香正气', '六味地黄', '逍遥丸',
            '维生素C', '维生素B族', '钙尔奇', '善存', '汤臣倍健',
            '蒙脱石散', '益生菌', '乳果糖', '开塞露', '酚酞片',
        ]

        # 剂型
        dosage_forms = ['片剂', '胶囊剂', '颗粒剂', '口服液', '注射液', '软膏剂', '滴眼液', '喷雾剂', '缓释片', '分散片']

        # 企业
        enterprises = [
            '华北制药股份有限公司', '哈药集团制药总厂', '石药集团欧意药业有限公司',
            '扬子江药业集团有限公司', '齐鲁制药有限公司', '正大天晴药业集团股份有限公司',
            '江苏恒瑞医药股份有限公司', '广州白云山制药股份有限公司', '上海医药集团股份有限公司',
            '中国医药集团有限公司', '复星医药', '科伦药业', '人福医药', '华润三九',
            '同仁堂', '云南白药', '片仔癀', '东阿阿胶', '康美药业', '天士力',
        ]

        # OTC 类型
        otc_types = ['处方药', 'OTC甲类', 'OTC乙类']

        # 规格模板
        spec_templates = [
            '{mg}mg*{count}片', '{mg}mg*{count}粒', '{g}g*{count}袋',
            '{ml}ml*{count}支', '{mg}mg/片*{count}片', '{g}g*{count}瓶',
        ]

        generated = 0
        for i in range(count):
            # 生成批准文号
            prefix = random.choice(['H', 'Z', 'S', 'J', 'B'])
            number = random.randint(10000000, 99999999)
            approval_no = f"国药准字{prefix}{number}"

            # 跳过已存在的
            if approval_no in self.crawled_approval_nos:
                continue

            generic_name = random.choice(generic_names)
            dosage_form = random.choice(dosage_forms)
            enterprise = random.choice(enterprises)
            otc_type = random.choice(otc_types)

            # 生成规格
            spec_tpl = random.choice(spec_templates)
            spec = spec_tpl.format(
                mg=random.choice([50, 100, 250, 500]),
                g=random.choice([1, 2, 3, 5, 10]),
                ml=random.choice([5, 10, 20, 50, 100]),
                count=random.choice([6, 10, 12, 20, 24, 30, 60])
            )

            # 生成商品名（部分有）
            brand_name = None
            if random.random() > 0.3:
                brand_prefixes = ['康', '健', '安', '宁', '舒', '泰', '欣', '乐', '美', '优']
                brand_suffixes = ['欣', '康', '宁', '舒', '泰', '乐', '美', '健', '安', '达']
                brand_name = random.choice(brand_prefixes) + random.choice(brand_suffixes) + ' ' + generic_name

            drug = {
                'approval_no': approval_no,
                'generic_name': generic_name + dosage_form.replace('剂', ''),
                'brand_name': brand_name,
                'dosage_form': dosage_form,
                'spec': spec,
                'otc_type': otc_type,
                'packing': random.choice(['盒', '瓶', '袋']),
                'enterprise': enterprise,
                'ingredients': generic_name,
                'indications': f"用于{generic_name}适应症相关疾病的治疗。（模拟数据）",
                'usage': f"口服。成人一次{random.choice([1, 2])}片/粒，一日{random.choice([2, 3])}次。（模拟数据）",
                'contraindications': f"对{generic_name}过敏者禁用。（模拟数据）",
                'warnings': "请在医生指导下使用。（模拟数据）",
                'adverse_reactions': "偶见胃肠道不适、皮疹等。（模拟数据）",
                'interactions': "与其他药物合用时请咨询医生。（模拟数据）",
                'special_population': "孕妇及哺乳期妇女慎用。（模拟数据）",
                'storage': "密封，置阴凉干燥处保存。",
                'validity': f"{random.choice([24, 36])}个月",
                'aliases': [generic_name],
                'source': 'mock_data',
                'updated_at': datetime.now().strftime('%Y-%m-%d'),
            }

            if self._save_drug(drug):
                generated += 1

            if generated % 500 == 0:
                print(f"  已生成 {generated} 条...")

        print(f"[Mock] 完成！共生成 {generated} 条模拟数据")
        return generated

    # ============ 主爬取流程 ============
    def crawl(self, max_pages=100, with_detail=False, resume=False):
        """
        主爬取流程
        由于实际网站结构可能变化，这里提供框架，具体解析逻辑需要根据目标网站调整
        """
        start_page = 1

        # 断点续爬
        if resume:
            progress = self._load_progress()
            if progress:
                start_page = progress.get('current_page', 1)
                print(f"[Resume] 从第 {start_page} 页继续爬取")

        print(f"[Crawl] 开始爬取，目标页数: {max_pages}，起始页: {start_page}")
        print(f"[Crawl] 输出文件: {self.output_file}")

        for page in range(start_page, start_page + max_pages):
            print(f"\n[Page {page}] 正在爬取...")

            try:
                # 获取列表页数据
                drugs = self.crawl_yaozh_list(page)

                if not drugs:
                    print(f"  第 {page} 页无数据或请求失败")
                    # 可能已到末页
                    if page > start_page + 5:
                        print("  连续多页无数据，可能已到末页，停止爬取")
                        break
                    continue

                self.stats['total_pages'] += 1
                self.stats['total_items'] += len(drugs)

                # 保存数据
                saved = 0
                for drug in drugs:
                    if self._save_drug(drug):
                        saved += 1

                print(f"  获取 {len(drugs)} 条，保存 {saved} 条，跳过重复 {len(drugs) - saved} 条")

                # 保存进度
                self._save_progress(page)

                # 延迟
                self._delay()

            except KeyboardInterrupt:
                print("\n[Interrupt] 用户中断，保存进度...")
                self._save_progress(page)
                break

            except Exception as e:
                print(f"  [Error] {e}")
                self._save_progress(page)
                continue

        # 打印统计
        print("\n" + "=" * 50)
        print("[Stats] 爬取统计:")
        print(f"  总页数: {self.stats['total_pages']}")
        print(f"  总条目: {self.stats['total_items']}")
        print(f"  成功保存: {self.stats['success']}")
        print(f"  重复跳过: {self.stats['duplicates']}")
        print(f"  失败: {self.stats['failed']}")
        print(f"  输出文件: {self.output_file}")
        print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description='药品数据爬取脚本')
    parser.add_argument('--pages', '-p', type=int, default=100, help='爬取页数（每页约50条）')
    parser.add_argument('--detail', '-d', action='store_true', help='同时爬取说明书详情（较慢）')
    parser.add_argument('--resume', '-r', action='store_true', help='断点续爬')
    parser.add_argument('--mock', '-m', type=int, default=0, help='生成模拟数据条数（用于测试）')
    parser.add_argument('--output', '-o', default=OUTPUT_FILE, help='输出文件路径')
    args = parser.parse_args()

    crawler = DrugCrawler(output_file=args.output)

    if args.mock > 0:
        # 生成模拟数据（用于测试导入流程）
        crawler.generate_mock_data(args.mock)
    else:
        # 真实爬取
        print("=" * 50)
        print("药品数据爬取脚本")
        print("=" * 50)
        print("\n注意：")
        print("1. 请确保遵守目标网站的 robots.txt 和使用条款")
        print("2. 建议使用 --mock 参数先生成模拟数据测试导入流程")
        print("3. 实际爬取需要根据目标网站结构调整解析逻辑")
        print("\n示例用法：")
        print("  python crawl_drugs.py --mock 5000    # 生成5000条模拟数据")
        print("  python crawl_drugs.py --pages 100   # 爬取100页真实数据")
        print("  python crawl_drugs.py --resume      # 断点续爬")
        print()

        # 默认先生成模拟数据用于测试
        if args.pages <= 0:
            print("提示：使用 --mock 5000 生成模拟数据进行测试")
        else:
            crawler.crawl(max_pages=args.pages, with_detail=args.detail, resume=args.resume)


if __name__ == '__main__':
    main()
