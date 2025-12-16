#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖分析工具

该脚本用于分析Python项目的依赖使用情况，识别未被实际使用的依赖包，并计算它们的存储空间大小。
"""

import os
import sys
import pkg_resources
import shutil
import json
from typing import Dict, List, Set
import re


def get_installed_packages() -> List[pkg_resources.Distribution]:
    """
    获取所有已安装的Python包
    
    Returns:
        List[pkg_resources.Distribution]: 已安装包的列表
    """
    return list(pkg_resources.working_set)


def get_package_size(package_name: str) -> int:
    """
    计算指定包的存储空间大小（字节）
    
    Args:
        package_name: 包名
    
    Returns:
        int: 包的存储空间大小（字节）
    """
    try:
        # 获取包的安装位置
        package = pkg_resources.get_distribution(package_name)
        package_path = package.location
        
        # 如果是editable安装，获取实际源码目录
        if package.egg_info and 'editable' in package.egg_info.lower():
            # 对于editable安装，需要解析egg-link文件
            egg_link_path = os.path.join(package_path, f"{package_name}.egg-link")
            if os.path.exists(egg_link_path):
                with open(egg_link_path, 'r') as f:
                    package_path = f.readline().strip()
        
        # 计算目录大小
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(package_path):
            # 跳过虚拟环境中的其他包目录
            if os.path.basename(dirpath) == 'site-packages' or 'venv' in dirpath.lower():
                continue
            
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        
        return total_size
    except Exception as e:
        print(f"[ERROR] 无法计算包 {package_name} 的大小: {e}")
        return 0


def find_imports_in_codebase(codebase_path: str) -> Set[str]:
    """
    查找代码库中所有导入的包名
    
    Args:
        codebase_path: 代码库根目录
    
    Returns:
        Set[str]: 导入的包名集合
    """
    imports = set()
    
    # 正则表达式匹配import语句
    import_pattern = re.compile(r'^\s*(?:import|from)\s+([a-zA-Z0-9_]+)', re.MULTILINE)
    
    for root, dirs, files in os.walk(codebase_path):
        # 跳过某些目录
        if any(exclude in root for exclude in ['.venv', '__pycache__', '.git', 'build', 'dist']):
            continue
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # 查找所有import语句
                    matches = import_pattern.findall(content)
                    for match in matches:
                        # 添加导入的包名
                        imports.add(match)
                except Exception as e:
                    print(f"[ERROR] 无法读取文件 {file_path}: {e}")
    
    return imports


def get_package_dependencies(package_name: str) -> Set[str]:
    """
    获取指定包的所有依赖
    
    Args:
        package_name: 包名
    
    Returns:
        Set[str]: 依赖包名集合
    """
    dependencies = set()
    
    try:
        package = pkg_resources.get_distribution(package_name)
        for req in package.requires():
            dependencies.add(req.key)
            # 递归获取依赖的依赖
            dependencies.update(get_package_dependencies(req.key))
    except Exception as e:
        print(f"[ERROR] 无法获取包 {package_name} 的依赖: {e}")
    
    return dependencies


def analyze_dependencies(codebase_path: str, venv_path: str) -> Dict[str, any]:
    """
    分析依赖使用情况
    
    Args:
        codebase_path: 代码库根目录
        venv_path: 虚拟环境目录
    
    Returns:
        Dict[str, any]: 依赖分析结果
    """
    # 获取所有已安装的包
    installed_packages = get_installed_packages()
    package_names = [pkg.key for pkg in installed_packages]
    
    # 查找代码库中导入的包
    imported_packages = find_imports_in_codebase(codebase_path)
    
    # 获取项目声明的依赖（从requirements.txt和dev-requirements.txt）
    declared_dependencies = set()
    
    # 读取requirements.txt
    req_files = [
        os.path.join(codebase_path, 'Localization_Tool', 'requirements.txt'),
        os.path.join(codebase_path, 'Localization_Tool', 'dev-requirements.txt')
    ]
    
    for req_file in req_files:
        if os.path.exists(req_file):
            with open(req_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 提取包名（忽略版本号）
                        pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0]
                        declared_dependencies.add(pkg_name)
    
    # 识别未使用的依赖
    unused_dependencies = []
    total_unused_size = 0
    
    for pkg in installed_packages:
        pkg_name = pkg.key
        
        # 检查包是否被导入
        if pkg_name not in imported_packages:
            # 检查包是否是其他已使用包的依赖
            is_dependency = False
            for used_pkg in imported_packages:
                if pkg_name in get_package_dependencies(used_pkg):
                    is_dependency = True
                    break
            
            if not is_dependency:
                # 计算包大小
                pkg_size = get_package_size(pkg_name)
                total_unused_size += pkg_size
                
                unused_dependencies.append({
                    'name': pkg_name,
                    'version': pkg.version,
                    'size': pkg_size,
                    'size_human': f"{pkg_size / 1024:.2f} KB" if pkg_size < 1024*1024 else f"{pkg_size / (1024*1024):.2f} MB"
                })
    
    # 按大小排序
    unused_dependencies.sort(key=lambda x: x['size'], reverse=True)
    
    # 生成分析报告
    report = {
        'total_installed_packages': len(installed_packages),
        'total_imported_packages': len(imported_packages),
        'total_declared_dependencies': len(declared_dependencies),
        'total_unused_dependencies': len(unused_dependencies),
        'total_unused_size': total_unused_size,
        'total_unused_size_human': f"{total_unused_size / 1024:.2f} KB" if total_unused_size < 1024*1024 else f"{total_unused_size / (1024*1024):.2f} MB",
        'unused_dependencies': unused_dependencies,
        'imported_packages': sorted(list(imported_packages)),
        'declared_dependencies': sorted(list(declared_dependencies))
    }
    
    return report


def main():
    """
    主函数
    """
    # 设置路径
    codebase_path = os.path.dirname(os.path.abspath(__file__))
    venv_path = os.path.join(codebase_path, '.venv')
    
    print("=" * 60)
    print("          依赖分析工具")
    print("=" * 60)
    print(f"代码库路径: {codebase_path}")
    print(f"虚拟环境路径: {venv_path}")
    print("=" * 60)
    
    # 分析依赖
    report = analyze_dependencies(codebase_path, venv_path)
    
    # 输出分析结果
    print(f"\n已安装的包总数: {report['total_installed_packages']}")
    print(f"代码中导入的包数: {report['total_imported_packages']}")
    print(f"声明的依赖数: {report['total_declared_dependencies']}")
    print(f"未使用的依赖数: {report['total_unused_dependencies']}")
    print(f"未使用依赖的总大小: {report['total_unused_size_human']}")
    
    print("\n" + "=" * 60)
    print("          未使用的依赖列表")
    print("=" * 60)
    print(f"{'包名':<30} {'版本':<15} {'大小':<10}")
    print("-" * 60)
    
    for dep in report['unused_dependencies']:
        print(f"{dep['name']:<30} {dep['version']:<15} {dep['size_human']:<10}")
    
    # 保存报告到文件
    report_file = os.path.join(codebase_path, 'dependency_analysis_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"分析报告已保存到: {report_file}")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
