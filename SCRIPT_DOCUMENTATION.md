# Chrome书签分类脚本 - 完整文档

## 脚本概览

### 文件: `bookmark_classifier.py`

一个完整的Chrome书签分类系统，包含3个主要类和1个主函数。

## 类结构详解

### 1. BookmarkParser 类

**继承**: `html.parser.HTMLParser`

**功能**: 解析Chrome导出的HTML书签文件

#### 属性
```python
bookmarks: List[Dict]      # 解析结果列表
folder_stack: List[str]    # 文件夹栈
current_folder: List[str]  # 当前文件夹路径
in_dt: bool               # 是否在<DT>标签内
in_h3: bool               # 是否在<H3>标签内
current_link: Dict        # 当前书签信息
folder_name: str          # 当前文件夹名称
```

#### 关键方法

**handle_starttag(tag, attrs)**
```python
# 处理开始标签
# - <DT>: 标记书签项开始
# - <H3>: 开始读取文件夹名称
# - <A>: 提取书签URL和属性
# - <DL>: 进入新的文件夹层级
```

**handle_endtag(tag)**
```python
# 处理结束标签
# - </A>: 保存完整的书签信息
# - </DT>: 标记书签项结束
# - </H3>: 结束读取文件夹名称
# - </DL>: 退出文件夹层级
```

**handle_data(data)**
```python
# 处理文本内容
# - 读取文件夹名称或书签标题
# - 自动去除前后空白
```

#### 使用示例
```python
from bookmark_classifier import BookmarkParser

with open('bookmarks25.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

parser = BookmarkParser()
parser.feed(html_content)

# 获取所有书签
bookmarks = parser.bookmarks
print(f"解析到{len(bookmarks)}个书签")

# 访问单个书签
for bookmark in bookmarks[:3]:
    print(f"{bookmark['name']}: {bookmark['url']}")
```

### 2. BookmarkClassifier 类

**功能**: 对书签进行智能分类

#### 分类规则定义

```python
CATEGORIES = {
    'Category Name': {
        'keywords': [list of keywords],      # 关键词列表
        'folder_keywords': [list of keywords] # 文件夹关键词列表
    }
}
```

#### 预定义分类

| 分类 | 主要关键词 | 文件夹关键词 |
|------|-----------|-----------|
| Programming | github, stackoverflow, coding, python, javascript, java, ... | code, programming, dev, tech, tutorial |
| Unreal Engine | unreal, ue4, ue5, unrealengine, marketplace, blueprint, ... | unreal, ue, game |
| Forum | forum, bbs, community, discussion, creaders, ... | forum, community, 论坛 |
| Youtube | youtube, youtu.be, video, bilibili, vimeo, twitch, ... | youtube, video, 视频 |
| Jobs | boss, zhipin, job, career, linkedin, indeed, ... | job, career, 招聘, boss |
| Music | music, spotify, soundcloud, netease, qq music, ... | music, 音乐 |
| Design | behance, dribbble, design, artstation, ui, ux, ... | design, art, 设计 |
| Shopping | amazon, ebay, taobao, jd, tmall, aliexpress, ... | shopping, shop, 购物 |
| News | news, bbc, cnn, reuters, nytimes, techcrunch, ... | news, 新闻 |
| Social Media | facebook, twitter, instagram, weibo, wechat, tiktok, ... | social, 社交 |

#### 关键方法

**classify_bookmark(bookmark) -> str**
```python
"""
根据单个书签的URL、名称和文件夹路径进行分类
参数:
    bookmark: Dict - 包含url, name, folder_path的字典
返回:
    str - 分类名称，或'Other'
"""
def classify_bookmark(self, bookmark):
    # 1. 提取并转换为小写
    url_lower = bookmark['url'].lower()
    name_lower = bookmark['name'].lower()
    folder_path = ' '.join(bookmark['folder_path']).lower()
    search_text = f"{url_lower} {name_lower} {folder_path}"

    # 2. 计算每个分类的得分
    scores = {}
    for category, rules in self.CATEGORIES.items():
        for keyword in rules['keywords']:
            if keyword.lower() in search_text:
                scores[category] += 2  # URL/名称权重: 2

        for keyword in rules['folder_keywords']:
            if keyword.lower() in folder_path:
                scores[category] += 1  # 文件夹权重: 1

    # 3. 返回最高得分的分类
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    return 'Other'
```

**classify_all(bookmarks) -> dict**
```python
"""
对所有书签进行分类
参数:
    bookmarks: List[Dict] - 书签列表
返回:
    dict - {分类名称: [书签列表]}
"""
```

#### 使用示例
```python
from bookmark_classifier import BookmarkClassifier

classifier = BookmarkClassifier()
classified = classifier.classify_all(bookmarks)

# 查看各分类统计
for category, items in classified.items():
    print(f"{category}: {len(items)}")

# 获取编程类书签
programming_bookmarks = classified['Programming']
for bookmark in programming_bookmarks:
    print(f"- {bookmark['name']}")
```

### 3. HTMLGenerator 类

**功能**: 生成分类后的HTML文件

#### 静态方法

**generate_category_html(category_name, bookmarks, output_file)**
```python
"""
为单个分类生成HTML文件
参数:
    category_name: str - 分类名称
    bookmarks: List[Dict] - 该分类的书签列表
    output_file: str - 输出文件路径
"""
```

生成的HTML格式:
```html
<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- Chrome兼容格式 -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>编程 - Bookmarks</TITLE>
<H1>编程 - Bookmarks</H1>
<DL><p>
    <DT><H3>文件夹名称</H3>
    <DL><p>
        <DT><A HREF="url" ADD_DATE="timestamp" ICON="base64">书签标题</A>
    </DL><p>
</DL><p>
```

**generate_index_html(categories, output_file)**
```python
"""
生成主索引HTML文件
参数:
    categories: dict - {分类名称: [书签列表]}
    output_file: str - 输出文件路径
"""
```

索引页面特性:
- 响应式网格布局 (CSS Grid)
- 渐变背景 (蓝紫色渐变)
- 悬停动画效果
- 分类图标和统计信息
- 现代化卡片设计

#### 使用示例
```python
from bookmark_classifier import HTMLGenerator

generator = HTMLGenerator()

# 生成单个分类
generator.generate_category_html(
    'Programming',
    programming_bookmarks,
    'output/programming.html'
)

# 生成索引
generator.generate_index_html(
    classified_bookmarks,
    'output/index.html'
)
```

## 主函数工作流

### main() 函数

```python
def main():
    """主程序入口"""

    # [1/4] 读取文件
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # [2/4] 解析书签
    parser = BookmarkParser()
    parser.feed(html_content)
    bookmarks = parser.bookmarks

    # [3/4] 智能分类
    classifier = BookmarkClassifier()
    classified_bookmarks = classifier.classify_all(bookmarks)

    # [4/4] 生成HTML
    generator = HTMLGenerator()

    for category_name, bookmarks_list in classified_bookmarks.items():
        generator.generate_category_html(...)

    generator.generate_index_html(...)
```

## 数据结构

### 书签对象结构

```python
{
    'url': str,              # 完整URL
    'name': str,             # 书签标题
    'add_date': str,         # 添加时间戳
    'icon': str,             # Base64编码的图标
    'folder_path': List[str] # 文件夹路径列表
}

# 示例:
{
    'url': 'https://github.com',
    'name': 'GitHub',
    'add_date': '1720123456',
    'icon': 'data:image/png;base64,iVBORw0K...',
    'folder_path': ['Temp', 'Programming']
}
```

### 分类结果结构

```python
{
    'Programming': [
        {书签对象1},
        {书签对象2},
        ...
    ],
    'Forum': [...],
    'Other': [...]
}
```

## 自定义分类

### 添加新分类

```python
# 修改 BookmarkClassifier 类中的 CATEGORIES

CATEGORIES = {
    # ... 现有分类 ...

    'Gaming': {
        'keywords': [
            'steam', 'epic games', 'game', 'gaming',
            'twitch', 'discord', 'valve', 'playstation'
        ],
        'folder_keywords': ['game', 'gaming', '游戏']
    },

    'Cryptocurrency': {
        'keywords': [
            'bitcoin', 'ethereum', 'crypto', 'blockchain',
            'coinbase', 'kraken', 'defi', 'nft'
        ],
        'folder_keywords': ['crypto', 'blockchain', '加密']
    }
}
```

### 调整关键词权重

```python
# 修改 classify_bookmark 方法

def classify_bookmark(self, bookmark):
    # ...
    for keyword in rules['keywords']:
        if keyword.lower() in search_text:
            scores[category] += 3  # 改为3

    for keyword in rules['folder_keywords']:
        if keyword.lower() in folder_path:
            scores[category] += 2  # 改为2
    # ...
```

## 性能优化技巧

### 1. 并行处理

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(
        classifier.classify_bookmark,
        bookmarks
    )
```

### 2. 缓存分类结果

```python
from functools import lru_cache

@lru_cache(maxsize=10000)
def _cached_classify(url_hash, name_hash, folder_hash):
    return self.classify_bookmark(...)
```

### 3. 增量更新

```python
def classify_incremental(self, new_bookmarks, cached_results):
    """只处理新增书签"""
    new_bookmarks_set = {b['url'] for b in new_bookmarks}
    cached_urls = {url for category, items in cached_results.items()
                   for url in {b['url'] for b in items}}

    only_new = [b for b in new_bookmarks if b['url'] not in cached_urls]

    return self.classify_all(only_new)
```

## 错误处理

### 常见问题

#### 1. 文件编码问题
```python
# 确保使用UTF-8编码
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
```

#### 2. HTML解析异常
```python
try:
    parser = BookmarkParser()
    parser.feed(html_content)
except Exception as e:
    print(f"解析错误: {e}")
    # 尝试修复HTML或使用容错模式
```

#### 3. 路径问题
```python
import os

# 确保目录存在
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 使用绝对路径
abs_path = os.path.abspath(file_path)
```

## 调试技巧

### 1. 打印解析进度
```python
parser = BookmarkParser()
parser.feed(html_content)
print(f"解析到 {len(parser.bookmarks)} 个书签")

for i, bookmark in enumerate(parser.bookmarks[:10]):
    print(f"{i+1}. {bookmark['name']} ({bookmark['url']})")
```

### 2. 检查分类结果
```python
classifier = BookmarkClassifier()
classified = classifier.classify_all(bookmarks)

for category, items in sorted(classified.items(),
                               key=lambda x: len(x[1]),
                               reverse=True):
    print(f"{category}: {len(items)} 个")

    # 显示样本
    for item in items[:2]:
        print(f"  - {item['name']}")
```

### 3. 导出调试数据
```python
import json

# 导出分类结果为JSON
debug_data = {
    category: [
        {
            'name': b['name'],
            'url': b['url'],
            'folder': ' > '.join(b['folder_path'])
        }
        for b in items
    ]
    for category, items in classified.items()
}

with open('debug_classified.json', 'w', encoding='utf-8') as f:
    json.dump(debug_data, f, ensure_ascii=False, indent=2)
```

## 扩展示例

### 示例1: 按主域名再分类

```python
from urllib.parse import urlparse

def get_domain_category(url):
    """基于URL域名的二级分类"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    # 提取主域名
    if domain.startswith('www.'):
        domain = domain[4:]

    return domain

# 在 classify_all 中使用
def classify_with_domains(self, bookmarks):
    classified = self.classify_all(bookmarks)

    for category in classified:
        # 按域名分组
        by_domain = defaultdict(list)
        for bookmark in classified[category]:
            domain = get_domain_category(bookmark['url'])
            by_domain[domain].append(bookmark)

        classified[category] = by_domain

    return classified
```

### 示例2: 生成统计报告

```python
def generate_report(classified):
    """生成分类统计报告"""
    report = []
    total = 0

    report.append("=" * 60)
    report.append("书签分类统计报告")
    report.append("=" * 60)

    for category in sorted(classified.keys()):
        count = len(classified[category])
        total += count
        percentage = (count / sum(len(items) for items in classified.values())) * 100
        report.append(f"{category:20s} : {count:5d} 个 ({percentage:5.1f}%)")

    report.append("-" * 60)
    report.append(f"{'总计':20s} : {total:5d} 个")
    report.append("=" * 60)

    return '\n'.join(report)
```

## 总结

该脚本提供了一个完整的书签处理解决方案，包括:
- 高效的HTML解析
- 灵活的分类系统
- 专业的HTML生成
- 易于扩展的架构

可根据需要进行定制和扩展，以满足更复杂的需求。
