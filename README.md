# Chrome书签智能分类工具

## 项目简介

这是一个Python脚本，用于解析Chrome导出的书签HTML文件，并根据URL和书签名称进行智能分类（已移除文件夹关键词匹配）。

## 功能特点

- **智能分类**：自动识别书签类型，包括：
  - 💻 Programming（编程）
  - 🎮 Unreal Engine（虚幻引擎）
  - 💬 Forum（论坛）
  - 🎥 Youtube/视频
  - 💼 Jobs/招聘
  - 🎵 Music（音乐）
  - 🎨 Design（设计）
  - 🛍️ Shopping（购物）
  - 📰 News（新闻）
  - 📱 Social Media（社交媒体）
  - 📂 Other（其他）

- **漂亮的界面**：生成现代化的HTML索引页面，支持卡片式布局
- **保留原始信息**：保留书签的添加日期等元数据（已移除图标以确保Chrome兼容性）
- **Chrome兼容**：生成的HTML文件完全兼容Chrome书签导入格式，可直接重新导入浏览器

## 使用方法

### 1. 从Chrome导出书签

1. 打开Chrome浏览器
2. 点击右上角的三个点 → 书签 → 书签管理器
3. 点击右上角的三个点 → 导出书签
4. 保存为HTML文件（例如：bookmarks25.html）

### 2. 运行分类脚本

```bash
python bookmark_classifier.py
```

脚本会：
- 读取 `D:\Code\bookmarks\bookmarks25.html`
- 解析所有书签
- 按照智能分类整理
- 在 `D:\Code\bookmarks\classified\` 目录下生成HTML文件

### 3. 查看结果

打开 `D:\Code\bookmarks\classified\index.html` 浏览你的分类书签。

## 文件结构

```
D:\Code\bookmarks\
├── bookmarks25.html              # 原始Chrome书签文件
├── bookmark_classifier.py         # 主分类脚本
├── test_parser.py                # 测试解析器（可选）
├── README.md                     # 本文件
└── classified/                   # 输出目录
    ├── index.html               # 主索引页面
    ├── programming.html         # 编程类书签
    ├── unreal_engine.html       # 虚幻引擎类书签
    ├── forum.html               # 论坛类书签
    ├── youtube.html             # 视频类书签
    ├── jobs.html                # 招聘类书签
    ├── music.html               # 音乐类书签
    ├── design.html              # 设计类书签
    ├── shopping.html            # 购物类书签
    ├── news.html                # 新闻类书签
    ├── social_media.html        # 社交媒体类书签
    └── other.html               # 其他类书签
```

## 分类统计（最新）

根据最新一次运行的结果：

- **Other**: 67 个书签
- **Youtube**: 59 个书签
- **Jobs**: 58 个书签
- **Programming**: 33 个书签
- **Design**: 23 个书签
- **Unreal Engine**: 15 个书签
- **Forum**: 11 个书签
- **Social Media**: 9 个书签
- **Shopping**: 4 个书签
- **News**: 2 个书签
- **Music**: 1 个书签

**总计**: 282 个书签，11 个类别

## 自定义分类

如果你想修改分类规则，可以编辑 `bookmark_classifier.py` 中的 `BookmarkClassifier.CATEGORIES` 字典：

```python
CATEGORIES = {
    'Programming': [
        'github', 'stackoverflow', 'coding', 'programming', 'python', 'javascript',
        'java', 'code', 'developer', 'api', 'git', 'csdn', 'blog', 'tech',
        'tutorial', 'documentation', 'docs', 'dev', 'npm', 'jquery', 'react',
        'vue', 'angular', 'node', 'typescript', 'html', 'css', 'web development',
        'coding', 'programmer', 'leetcode', 'hackerrank', 'codewars'
    ],
    # 添加或修改更多分类...
}
```

**注意**: 新版本已移除文件夹关键词匹配，分类仅基于URL和书签名称进行关键词匹配。

## 技术细节

- **Python版本**: Python 3.x
- **依赖库**: 仅使用Python标准库
  - `html.parser` - HTML解析
  - `collections.defaultdict` - 数据结构
  - `os` - 文件操作

## 注意事项

1. 生成的HTML文件采用UTF-8编码
2. **已移除书签图标**以确保Chrome导入兼容性
3. 分类使用关键词匹配，可能需要根据个人书签调整
4. 生成的HTML文件完全兼容Chrome书签格式，可直接重新导入浏览器
5. Windows系统下终端可能显示乱码，但不影响文件生成

## 重要更新日志

### v2.0 - Chrome兼容性改进
- ✅ **移除文件夹关键词匹配** - 分类仅基于URL和书签名称
- ✅ **移除ICON属性** - 解决Chrome导入失败问题
- ✅ **标准化HTML格式** - 完全符合Chrome书签导出格式
- ✅ **优化分类逻辑** - 提高分类准确性

### v1.0 - 初始版本
- 基础书签解析和分类功能
- 现代化HTML索引页面
- 文件夹关键词支持（已移除）

## 许可证

MIT License

## 作者

Created with ❤️
