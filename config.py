#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome书签分类器配置文件
用于配置输入输出路径和其他参数
"""

import os

class Config:
    """配置类"""

    # 输入文件路径
    INPUT_FILE = r'D:\Code\bookmarks\bookmarksTemp.html'

    # 输出目录
    OUTPUT_DIR = r'D:\Code\bookmarks\classified'

    # 编码设置
    ENCODING = 'utf-8'

    # 应用信息
    APP_NAME = "Chrome Bookmark Classifier"
    APP_VERSION = "v2.0"
    APP_DESCRIPTION = "Chrome书签智能分类工具"

    @classmethod
    def ensure_output_dir(cls):
        """确保输出目录存在"""
        if not os.path.exists(cls.OUTPUT_DIR):
            os.makedirs(cls.OUTPUT_DIR)

    @classmethod
    def get_app_info(cls):
        """获取应用信息"""
        return f"{cls.APP_NAME} {cls.APP_VERSION} - {cls.APP_DESCRIPTION}"

    @classmethod
    def get_input_file_display(cls):
        """获取输入文件显示路径"""
        return cls.INPUT_FILE if cls.INPUT_FILE else "未配置"

    @classmethod
    def get_output_dir_display(cls):
        """获取输出目录显示路径"""
        return cls.OUTPUT_DIR if cls.OUTPUT_DIR else "未配置"