#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试初始化模块功能
"""

import os
import sys

# 添加项目根目录到Python搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.init_mode.core import run_init_tasks


def main():
    """
    测试init_mode模块的功能
    """
    print("=== 测试初始化模块功能 ===")
    
    # 获取基础路径
    base_path = os.path.dirname(os.path.abspath(__file__))
    print(f"基础路径: {base_path}")
    
    # 执行初始化任务
    try:
        result = run_init_tasks(base_path)
        print(f"\n初始化任务执行结果:")
        print(f"状态: {result['status']}")
        print(f"总数量: {result['data']['total_count']}")
        print(f"成功数量: {result['data']['success_count']}")
        print(f"失败数量: {result['data']['fail_count']}")
        
        if result['data']['fail_count'] > 0:
            print(f"\n失败原因:")
            for reason in result['data']['fail_reasons']:
                print(f"- {reason}")
        
        print("\n=== 测试完成 ===")
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        print("\n=== 测试失败 ===")


if __name__ == "__main__":
    main()
