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
    """书签智能分类器"""

    # 定义分类规则（关键词匹配）
    CATEGORIES = {
        'Programming': {
            'keywords': [
                'github', 'stackoverflow', 'coding', 'programming', 'python', 'javascript',
                'java', 'code', 'developer', 'api', 'git', 'csdn', 'blog', 'tech',
                'tutorial', 'documentation', 'docs', 'dev', 'npm', 'jquery', 'react',
                'vue', 'angular', 'node', 'typescript', 'html', 'css', 'web development',
                'coding', 'programmer', 'leetcode', 'hackerrank', 'codewars'
            ],
            'folder_keywords': ['code', 'programming', 'dev', 'tech', 'tutorial']
        },
        'Unreal Engine': {
            'keywords': [
                'unreal', 'ue4', 'ue5', 'unrealengine', 'marketplace', 'epic games',
                'blueprint', 'nanite', 'lumen', 'metahuman', 'houdini'
            ],
            'folder_keywords': ['unreal', 'ue', 'game']
        },
        'Forum': {
            'keywords': [
                'forum', 'bbs', 'community', 'discussion', 'creaders', 'weiming',
                'pincong', 'reddit', 'discord', 'slack', '论坛', '社区', '讨论',
                'avalon', 'projectavalon'
            ],
            'folder_keywords': ['forum', 'community', '论坛']
        },
        'Youtube': {
            'keywords': [
                'youtube', 'youtu.be', 'video', 'bilibili', 'vimeo', 'twitch',
                'xinpianchang', '新片场', '视频'
            ],
            'folder_keywords': ['youtube', 'video', '视频']
        },
        'Jobs': {
            'keywords': [
                'boss', 'zhipin', 'job', 'career', 'hiring', 'recruitment', 'linkedin',
                'indeed', 'glassdoor', '招聘', 'lagou', '拉勾', '智联', '前程无忧'
            ],
            'folder_keywords': ['job', 'career', '招聘', 'boss']
        },
        'Music': {
            'keywords': [
                'music', 'spotify', 'soundcloud', 'bandcamp', 'apple music', 'youtube music',
                'netease', 'qq music', '音乐', 'song', 'artist', 'album', 'playlist'
            ],
            'folder_keywords': ['music', '音乐']
        },
        'Design': {
            'keywords': [
                'behance', 'dribbble', 'design', 'artstation', 'deviantart', 'pinterest',
                'figma', 'sketch', 'adobe', 'photoshop', 'illustrator', 'ui', 'ux',
                'graphic design', '设计', 'designboom', 'gfxdomain', 'art'
            ],
            'folder_keywords': ['design', 'art', '设计']
        },
        'Shopping': {
            'keywords': [
                'amazon', 'ebay', 'taobao', 'jd', 'tmall', 'aliexpress', 'shopping',
                'shop', 'buy', 'purchase', '淘宝', '京东', '天猫', '购物'
            ],
            'folder_keywords': ['shopping', 'shop', '购物']
        },
        'News': {
            'keywords': [
                'news', 'bbc', 'cnn', 'reuters', 'nytimes', 'guardian', 'techcrunch',
                'hacker news', '新闻', 'xinhua', 'sina', 'sohu'
            ],
            'folder_keywords': ['news', '新闻']
        },
        'Social Media': {
            'keywords': [
                'facebook', 'twitter', 'instagram', 'weibo', 'wechat', 'tiktok',
                'social', '微博', '微信', '社交'
            ],
            'folder_keywords': ['social', '社交']
        }
    }

    def __init__(self):
        self.classified_bookmarks = defaultdict(list)

    def classify_bookmark(self, bookmark):
        """
        根据URL、书签名称和文件夹路径对书签进行分类
        """
        url_lower = bookmark['url'].lower()
        name_lower = bookmark['name'].lower()
        folder_path = ' '.join(bookmark['folder_path']).lower()

        # 组合搜索文本
        search_text = f"{url_lower} {name_lower} {folder_path}"

        # 记录匹配分数
        scores = defaultdict(int)

        # 检查每个分类
        for category, rules in self.CATEGORIES.items():
            # URL和名称关键词匹配
            for keyword in rules['keywords']:
                if keyword.lower() in search_text:
                    scores[category] += 2  # URL/名称匹配权重更高

            # 文件夹关键词匹配
            for keyword in rules['folder_keywords']:
                if keyword.lower() in folder_path:
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
        """为单个分类生成HTML文件"""
        html_content = f'''<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>{category_name} - Bookmarks</TITLE>
<H1>{category_name} - Bookmarks</H1>
<DL><p>
'''

        # 按文件夹组织书签
        folders = defaultdict(list)
        for bookmark in bookmarks:
            folder_key = ' > '.join(bookmark['folder_path']) if bookmark['folder_path'] else 'Root'
            folders[folder_key].append(bookmark)

        # 生成书签HTML
        for folder_name, folder_bookmarks in sorted(folders.items()):
            if folder_name != 'Root':
                html_content += f'    <DT><H3>{folder_name}</H3>\n'
                html_content += '    <DL><p>\n'

            for bookmark in folder_bookmarks:
                icon_attr = f' ICON="{bookmark["icon"]}"' if bookmark.get('icon') else ''
                add_date_attr = f' ADD_DATE="{bookmark["add_date"]}"' if bookmark.get('add_date') else ''

                html_content += f'        <DT><A HREF="{bookmark["url"]}"{add_date_attr}{icon_attr}>{bookmark["name"]}</A>\n'

            if folder_name != 'Root':
                html_content += '    </DL><p>\n'

        html_content += '</DL><p>\n'

        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
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

        # 为每个分类添加图标
        category_icons = {
            'Programming': '💻',
            'Unreal Engine': '🎮',
            'Forum': '💬',
            'Youtube': '🎥',
            'Jobs': '💼',
            'Music': '🎵',
            'Design': '🎨',
            'Shopping': '🛍️',
            'News': '📰',
            'Social Media': '📱',
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
            filename = category_name.lower().replace(' ', '_') + '.html'
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

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)


def main():
    """主函数"""
    # 输入文件路径
    input_file = r'D:\Code\bookmarks\bookmarks25.html'
    output_dir = r'D:\Code\bookmarks\classified'

    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("=" * 60)
    print("Chrome Bookmark Classifier - Chrome书签智能分类工具")
    print("=" * 60)
    print()

    # 读取并解析HTML文件
    print(f"[1/4] 正在读取书签文件: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
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
        filename = category_name.lower().replace(' ', '_') + '.html'
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
    print(f"  {output_dir}")
    print()
    print("请打开 index.html 浏览你的书签分类")
    print("=" * 60)


if __name__ == '__main__':
    main()
