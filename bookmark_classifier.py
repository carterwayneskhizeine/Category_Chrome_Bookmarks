#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome Bookmark Classifier
解析Chrome导出的书签HTML文件，并按照智能分类重新组织书签
"""

import re
from html.parser import HTMLParser
from collections import defaultdict
import os
from config import Config


class BookmarkParser(HTMLParser):
    """解析Chrome书签HTML文件"""

    def __init__(self):
        super().__init__()
        self.bookmarks = []
        self.folder_stack = []
        self.current_folder = []
        self.in_dt = False
        self.in_h3 = False
        self.current_link = None
        self.folder_name = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        tag = tag.lower()

        if tag == 'dt':
            self.in_dt = True

        elif tag == 'h3':
            self.in_h3 = True
            self.folder_name = ""

        elif tag == 'a':
            href = attrs_dict.get('href', '')
            add_date = attrs_dict.get('add_date', '')
            icon = attrs_dict.get('icon', '')

            self.current_link = {
                'url': href,
                'name': '',
                'add_date': add_date,
                'icon': icon,
                'folder_path': list(self.current_folder)
            }

        elif tag == 'dl':
            if self.folder_name:
                self.current_folder.append(self.folder_name)
                self.folder_stack.append(self.folder_name)
                self.folder_name = ""

    def handle_endtag(self, tag):
        tag = tag.lower()

        if tag == 'a':
            # 当遇到</a>标签时，保存书签
            if self.current_link and self.current_link['name']:
                self.bookmarks.append(self.current_link)
            self.current_link = None

        elif tag == 'dt':
            self.in_dt = False

        elif tag == 'h3':
            self.in_h3 = False

        elif tag == 'dl':
            if self.current_folder:
                self.current_folder.pop()

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return

        if self.in_h3:
            self.folder_name = data

        elif self.current_link is not None:
            self.current_link['name'] = data
   
class BookmarkClassifier:
    """书签智能分类器（极客 / AI / 编程 技术向重构版）"""

    # 定义分类规则（关键词匹配）
    CATEGORIES = {
        # 1. AI / Machine Learning 核心
        'AI/ML': [
            'openai', 'chatgpt', 'gpt', 'claude', 'copilot',
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'llm', 'tensorflow', 'pytorch', 'huggingface',
            'kaggle', 'fastai', 'stability.ai', 'midjourney',
            'replicate', 'vertex ai', 'bedrock', 'anthropic',
            'ai', 'ml'
        ],

        # 2. 核心编程 / 开发
        'Programming': [
            # 平台 & 托管
            'github', 'gitlab', 'bitbucket', 'gitee',
            # 通用编程关键词
            'coding', 'programming', 'developer', 'dev', 'software engineer',
            'code', 'refactor', 'algorithm', 'data structure',
            'design pattern', 'oop', 'functional programming',
            # 中文技术社区
            'csdn', '掘金', 'segmentfault', 'v2ex', '博客园',
            # 学习/文档
            'tutorial', 'documentation', 'docs', 'cookbook',
            'roadmap.sh', 'w3schools', 'geeksforgeeks'
        ],

        # 3. Python 生态
        'Python': [
            'python', 'pypi', 'pip', 'conda', 'anaconda',
            'jupyter', 'notebook', 'ipython',
            'django', 'flask', 'fastapi', 'tornado',
            'scrapy', 'pytest', 'pydantic'
        ],

        # 4. JavaScript / TypeScript / Web / Electron / Vue
        'Web & JS': [
            'javascript', 'typescript', 'node', 'node.js', 'nodejs',
            'npm', 'yarn', 'pnpm',
            'vue', 'nuxt', 'react', 'next.js', 'angular', 'svelte',
            'webpack', 'vite', 'rollup', 'babel',
            'html', 'css', 'sass', 'less', 'tailwind',
            'electron', 'web development', 'frontend', '前端'
        ],

        # 5. C / C++ / 系统底层
        'C/C++ & Systems': [
            'c++', 'cppreference', 'isocpp', 'boost',
            'cmake', 'meson', 'ninja',
            'clang', 'gcc', 'msvc',
            'gdb', 'lldb',
            'address sanitizer', 'valgrind',
            'embedded', 'rtos', 'system programming',
            '低级编程', '系统编程'
        ],

        # 6. Unreal Engine / 游戏开发技术
        'Unreal Engine & Game Dev': [
            'unreal', 'unreal engine', 'ue4', 'ue5', 'unrealengine',
            'epic games', 'marketplace', 'metahuman',
            'blueprint', 'nanite', 'lumen', 'gameplay ability system',
            '虚幻引擎', 'ue 文档', 'ue marketplace',
            # 通用游戏开发
            'game dev', 'gamedev', 'unity3d', 'unity',
            'shader', 'hlsl', 'glsl', 'rendering', 'vulkan', 'directx'
        ],

        # 7. Linux / DevOps / 云 / 工具链
        'Linux & DevOps': [
            'linux', 'ubuntu', 'debian', 'archlinux', 'fedora', 'centos',
            'manjaro', 'wsl',
            'bash', 'zsh', 'shell', 'terminal',
            'docker', 'kubernetes', 'k8s', 'helm',
            'ansible', 'terraform',
            'jenkins', 'gitlab ci', 'github actions',
            'nginx', 'apache', '容器', '运维', 'devops'
        ],

        # 8. 硬核工具 / 效率 / 极客资源
        'Tools & Productivity': [
            'vim', 'neovim', 'emacs', 'vscode', 'intellij', 'clion', 'pycharm',
            'postman', 'insomnia',
            'regex', 'regex101',
            'obsidian', 'notion',
            'productivity', 'todoist'
        ],

        # 9. 技术社区 / 讨论区
        'Tech Communities': [
            'stackoverflow', 'stack overflow',
            'reddit', 'hacker news', 'lobste.rs',
            'discord', 'slack', 'telegram',
            '论坛', '社区', 'discussion', 'community',
            'v2ex', 'pincong', 'projectavalon', 'weiming', 'creaders'
        ],

        # 10. 文档 / 官方资源（可作为更精细层）
        'Docs & Specs': [
            'rfc-editor.org', 'w3c', 'whatwg',
            'man7.org', 'mdn web docs', 'developer.mozilla.org',
            'specification', 'spec', 'api reference'
        ],

        # 11. Gaming（玩家 & 平台向）
        'Gaming': [
            'steam', 'epic games', 'gog', 'uplay', 'ea app',
            'playstation', 'psn', 'xbox', 'nintendo', 'switch',
            'battle.net', 'riot games',
            'twitch', 'discord',  # 如果你更希望归到社区，可在逻辑中设优先级
            'game', 'gaming', 'league of legends',
            'dota', 'counter-strike', 'csgo', 'call of duty', 'battlefield'
        ],

        # 12. Cryptocurrency / Web3
        'Cryptocurrency': [
            'bitcoin', 'btc', 'ethereum', 'eth',
            'crypto', 'cryptocurrency', 'blockchain',
            'defi', 'nft', 'dao', 'web3',
            'binance', 'coinbase', 'kraken', 'okx',
            'uniswap', 'metamask', 'coinmarketcap', 'coingecko'
        ],

        # 13. 视频 / 教学 / 资源
        'Video & Learning': [
            'youtube', 'youtu.be', 'bilibili', 'vimeo',
            'coursera', 'edx', 'udemy', 'pluralsight',
            'xinpianchang', '新片场',
            '视频教程', '课程', 'lecture'
        ],

        # 14. 设计 / UI / CG / 艺术（为技术服务）
        'Design & Art': [
            'behance', 'dribbble', 'artstation', 'deviantart',
            'pinterest', '设计', 'ui', 'ux',
            'figma', 'sketch', 'adobe', 'photoshop', 'illustrator',
            'cg', '3d', 'blender', 'houdini'
        ],

        # 15. 技术新闻 / 极客资讯
        'Tech News': [
            'techcrunch', 'theverge', 'wired', 'arstechnica',
            'phoronix', 'linux news',
            '新闻', 'bbc', 'cnn', 'reuters', 'nytimes', 'guardian'
        ],

        # 16. 通用购物（放最后，避免误杀）
        'Shopping': [
            'amazon', 'ebay', 'taobao', 'jd', 'tmall',
            'aliexpress', '购物', '买', 'shop', 'store', '京东', '天猫'
        ],

        # 17. 社交 / 非技术为主
        'Social Media': [
            'facebook', 'twitter', 'x.com', 'instagram', 'tiktok',
            'weibo', '微博', 'wechat', '微信',
            'social', '小红书', 'douyin'
        ],

        # 18. 工作 / 职业
        'Jobs & Career': [
            'boss', 'zhipin', 'lagou', '拉勾',
            '智联', '前程无忧',
            'linkedin', 'indeed', 'glassdoor',
            'job', 'jobs', 'career', 'hiring', 'recruitment', '招聘'
        ]
    }

    def __init__(self):
        self.classified_bookmarks = defaultdict(list)

    def classify_bookmark(self, bookmark):
        """
        根据URL和书签名称对书签进行分类（不再使用文件夹关键词）
        """
        url_lower = bookmark['url'].lower()
        name_lower = bookmark['name'].lower()

        # 组合搜索文本（只包含URL和名称）
        search_text = f"{url_lower} {name_lower}"

        # 记录匹配分数
        scores = defaultdict(int)

        # 检查每个分类
        for category, keywords in self.CATEGORIES.items():
            # URL和名称关键词匹配
            for keyword in keywords:
                if keyword.lower() in search_text:
                    scores[category] += 1

        # 返回得分最高的分类，如果没有匹配则返回 'Other'
        if scores:
            best_category = max(scores.items(), key=lambda x: x[1])[0]
            return best_category
        return 'Other'

    def classify_all(self, bookmarks):
        """对所有书签进行分类"""
        for bookmark in bookmarks:
            category = self.classify_bookmark(bookmark)
            self.classified_bookmarks[category].append(bookmark)

        return self.classified_bookmarks


class HTMLGenerator:
    """生成分类后的HTML文件"""

    @staticmethod
    def generate_category_html(category_name, bookmarks, output_file):
        """为单个分类生成HTML文件（标准Chrome书签格式）"""
        import time

        # 生成时间戳
        current_time = str(int(time.time()))

        html_content = f'''<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL>
    <DT><H3 ADD_DATE="{current_time}" LAST_MODIFIED="{current_time}">{category_name}</H3>
    <DL><p>
'''

        # 直接列出所有书签（不包含ICON以避免Chrome导入问题）
        for bookmark in bookmarks:
            # 暂时不添加ICON属性，因为Chrome可能无法正确解析长的base64数据
            # icon_attr = f' ICON="{bookmark["icon"]}"' if bookmark.get('icon') else ''
            add_date_attr = f' ADD_DATE="{bookmark["add_date"]}"' if bookmark.get('add_date') else f' ADD_DATE="{current_time}"'

            html_content += f'        <DT><A HREF="{bookmark["url"]}"{add_date_attr}>{bookmark["name"]}</A>\n'

        html_content += '''    </DL><p>
</DL><p>
'''

        # 写入文件
        with open(output_file, 'w', encoding=Config.ENCODING) as f:
            f.write(html_content)

    @staticmethod
    def generate_index_html(categories, output_file):
        """生成主索引文件"""
        html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bookmarks Index - 书签索引</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        h1 {
            text-align: center;
            color: white;
            font-size: 3rem;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        .subtitle {
            text-align: center;
            color: rgba(255,255,255,0.9);
            font-size: 1.2rem;
            margin-bottom: 50px;
        }

        .categories {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 25px;
            padding: 20px 0;
        }

        .category-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            text-decoration: none;
            display: block;
        }

        .category-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }

        .category-icon {
            font-size: 3rem;
            margin-bottom: 15px;
            text-align: center;
        }

        .category-name {
            font-size: 1.5rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            text-align: center;
        }

        .category-count {
            font-size: 1rem;
            color: #666;
            text-align: center;
        }

        .footer {
            text-align: center;
            margin-top: 50px;
            color: rgba(255,255,255,0.8);
            font-size: 0.9rem;
        }

        .stats {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 40px;
            text-align: center;
            color: white;
        }

        .stats h2 {
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 我的书签分类</h1>
        <p class="subtitle">My Organized Bookmarks</p>

        <div class="stats">
            <h2>统计信息</h2>
            <p>共有 <strong>{total_bookmarks}</strong> 个书签，分为 <strong>{total_categories}</strong> 个类别</p>
        </div>

        <div class="categories">
'''

        # 为每个分类添加图标（匹配新的分类名称）
        category_icons = {
            'AI/ML': '🤖',
            'Programming': '💻',
            'Python': '🐍',
            'Web & JS': '🌐',
            'C/C++ & Systems': '⚙️',
            'Unreal Engine & Game Dev': '🎮',
            'Linux & DevOps': '🐧',
            'Tools & Productivity': '🛠️',
            'Tech Communities': '💬',
            'Docs & Specs': '📚',
            'Gaming': '🎲',
            'Cryptocurrency': '₿',
            'Video & Learning': '🎥',
            'Design & Art': '🎨',
            'Tech News': '📰',
            'Shopping': '🛍️',
            'Social Media': '📱',
            'Jobs & Career': '💼',
            'Other': '📂'
        }

        total_bookmarks = sum(len(bookmarks) for bookmarks in categories.values())
        total_categories = len(categories)

        html_content = html_content.replace('{total_bookmarks}', str(total_bookmarks))
        html_content = html_content.replace('{total_categories}', str(total_categories))

        # 按书签数量排序分类
        sorted_categories = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)

        for category_name, bookmarks in sorted_categories:
            icon = category_icons.get(category_name, '📁')
            # 使用相同的文件名转换逻辑确保一致性
            safe_filename = category_name.lower().replace(' ', '_').replace('/', '_').replace('&', '_and_')
            filename = safe_filename + '.html'
            count = len(bookmarks)

            html_content += f'''
            <a href="{filename}" class="category-card">
                <div class="category-icon">{icon}</div>
                <div class="category-name">{category_name}</div>
                <div class="category-count">{count} 个书签</div>
            </a>
'''

        html_content += '''
        </div>

        <div class="footer">
            <p>Generated by Chrome Bookmark Classifier</p>
            <p>Created with ❤️</p>
        </div>
    </div>
</body>
</html>
'''

        with open(output_file, 'w', encoding=Config.ENCODING) as f:
            f.write(html_content)


def main():
    """主函数"""
    # 使用配置文件中的路径
    input_file = Config.INPUT_FILE
    output_dir = Config.OUTPUT_DIR

    # 确保输出目录存在
    Config.ensure_output_dir()

    # 显示应用信息
    print("=" * 60)
    print(Config.get_app_info())
    print("=" * 60)
    print()

    # 读取并解析HTML文件
    print(f"[1/4] 正在读取书签文件: {Config.get_input_file_display()}")
    with open(input_file, 'r', encoding=Config.ENCODING) as f:
        html_content = f.read()

    # 解析书签
    print("[2/4] 正在解析书签...")
    parser = BookmarkParser()
    parser.feed(html_content)
    bookmarks = parser.bookmarks
    print(f"      找到 {len(bookmarks)} 个书签")
    print()

    # 分类书签
    print("[3/4] 正在智能分类书签...")
    classifier = BookmarkClassifier()
    classified_bookmarks = classifier.classify_all(bookmarks)

    # 显示分类统计
    print()
    print("分类统计:")
    print("-" * 60)
    for category, bookmarks_list in sorted(classified_bookmarks.items(),
                                          key=lambda x: len(x[1]),
                                          reverse=True):
        print(f"  {category:20s} : {len(bookmarks_list):5d} 个书签")
    print("-" * 60)
    print()

    # 生成HTML文件
    print("[4/4] 正在生成HTML文件...")
    generator = HTMLGenerator()

    # 为每个分类生成HTML
    for category_name, bookmarks_list in classified_bookmarks.items():
        # 将分类名转换为安全的文件名（替换特殊字符）
        safe_filename = category_name.lower().replace(' ', '_').replace('/', '_').replace('&', '_and_')
        filename = safe_filename + '.html'
        output_file = os.path.join(output_dir, filename)
        generator.generate_category_html(category_name, bookmarks_list, output_file)
        print(f"      生成: {filename}")

    # 生成索引文件
    index_file = os.path.join(output_dir, 'index.html')
    generator.generate_index_html(classified_bookmarks, index_file)
    print(f"      生成: index.html (主索引)")
    print()

    print("=" * 60)
    print("[OK] 完成！所有文件已生成到:")
    print(f"  {Config.get_output_dir_display()}")
    print()
    print("请打开 index.html 浏览你的书签分类")
    print("=" * 60)


if __name__ == '__main__':
    main()
