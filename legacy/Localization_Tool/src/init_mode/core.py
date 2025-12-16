#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化模式核心模块

该模块包含程序启动时的所有初始化操作，包括：
1. 自动创建必要的文件夹结构
2. 读取mod_info.json并自动重命名文件/文件夹
3. 对source和source_backup目录下的mod文件夹进行重命名
4. 从备份恢复文件
5. 确保程序执行环境就绪

这些操作只在程序启动阶段执行一次，确保后续的提取、映射和反编译流程能够正常进行
"""

import os
import json
from typing import Any, Dict, List

from src.common import (create_folders, generate_report,  # noqa: E402, E501
                        get_timestamp, save_report,
                        setup_logger, get_logger, log_progress, log_result,
                        rename_mod_folders, restore_backup)  # 添加文件夹重命名和备份恢复功能

# 设置日志记录器
logger = setup_logger("init_mode")

# 全局映射表，用于存储id到mod信息的映射关系
# 格式：{mod_id: mod_info_object}
id_to_mod_info_mapping = {}

# 全局mod映射表，用于存储mod_id到mod_path和mod_info的完整映射
# 格式：{mod_id: {"mod_path": str, "mod_info": ModInfo, "language": str, "source_type": str}}
# source_type: "source" 或 "source_backup"
mod_mappings = {}

# 项目所需的基础文件夹结构
REQUIRED_FOLDERS = [
    "File/source/Chinese",
    "File/source/English",
    "File/source_backup/Chinese",
    "File/source_backup/English",
    "File/output/Extract_Chinese",
    "File/output/Extract_English",
    "File/output/Extend_en2zh",
    "File/output/Extend_zh2en",
    "File/rule/Chinese",
    "File/rule/English",
    "tools/cfr-0.152",
    "tools/procyon-decompiler-0.6.0",
]


class ModInfo:
    """Mod信息类"""
    # 类级别的缓存字典，用于存储已读取的mod_info信息
    _cache = {}
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.mod_id = ""
        self.name = ""
        self.version = ""
        self.author = ""
        self.description = ""
        self.valid = False
        
        # 检查缓存中是否已有该文件的信息
        if file_path in self._cache:
            # 使用缓存的信息
            cached_info = self._cache[file_path]
            self.mod_id = cached_info["mod_id"]
            self.name = cached_info["name"]
            self.version = cached_info["version"]
            self.author = cached_info["author"]
            self.description = cached_info["description"]
            self.valid = cached_info["valid"]
            logger.debug(f"使用缓存的mod_info: {file_path}")
        else:
            # 读取mod_info.json
            self._read_mod_info()
            # 缓存信息
            self._cache[file_path] = {
                "mod_id": self.mod_id,
                "name": self.name,
                "version": self.version,
                "author": self.author,
                "description": self.description,
                "valid": self.valid
            }
    
    def _read_mod_info(self):
        """读取mod_info.json文件，支持带注释的JSON
        
        实现基于行的解析逻辑，重点处理前6行，提取每行中前两个双引号内的字符串
        """
        if not os.path.exists(self.file_path):
            logger.error(f"mod_info.json文件不存在: {self.file_path}")
            return
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            import re
            
            # 重点处理前6行，提取必要信息
            for i, line in enumerate(lines[:6]):
                # 移除注释
                # 移除单行注释 // ...
                line = re.sub(r'//.*$', '', line)
                # 移除#开头的注释
                line = re.sub(r'#.*$', '', line)
                # 移除多行注释 /* ... */ (如果有的话)
                line = re.sub(r'/\*[\s\S]*?\*/', '', line)
                
                # 跳过空行
                line = line.strip()
                if not line:
                    continue
                
                # 使用正则表达式提取每行中前两个双引号内的字符串
                # 改进：支持在一行中包含多个键值对的情况
                matches = re.findall(r'"([^"]+)"\s*:\s*"([^"]+)"', line, re.DOTALL)
                if matches:
                    # 提取所有匹配的键值对
                    for key, value in matches:
                        key = key.strip()
                        value = value.strip()
                        
                        # 确定字段类型
                        if key == "id":
                            self.mod_id = value
                            logger.debug(f"提取到id: {value}")
                        elif key == "name":
                            self.name = value
                            logger.debug(f"提取到name: {value}")
                        elif key == "version":
                            self.version = value
                            logger.debug(f"提取到version: {value}")
                        elif key == "author":
                            self.author = value
                            logger.debug(f"提取到author: {value}")
                        elif key == "description":
                            self.description = value
                            logger.debug(f"提取到description: {value}")
            
            # 检查是否提取到了必要的字段
            if self.mod_id and self.name and self.version:
                self.valid = True
                logger.info(f"基于行的解析成功读取mod_info.json: {self.file_path}")
            else:
                # 如果基于行的解析失败，尝试使用传统的JSON解析
                logger.debug("基于行的解析未提取到所有必要字段，尝试使用传统JSON解析")
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 移除所有类型的注释
                import re
                content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
                content = re.sub(r'#.*$', '', content, flags=re.MULTILINE)
                # 处理多行注释，确保能处理包含换行符的情况
                content = re.sub(r'\s*/\*[\s\S]*?\*/\s*', ' ', content)
                content = content.replace('\t', '    ')
                
                # 修复JSON语法错误：移除尾随逗号
                # 改进：更全面的尾随逗号修复
                # 移除数组末尾的逗号
                content = re.sub(r',\s*\]', r']', content)
                # 移除对象末尾的逗号
                content = re.sub(r',\s*\}', r'}', content)
                # 移除对象属性后的逗号（如果后面跟着}或]）
                content = re.sub(r',\s*(\}|\])', r'\1', content)
                # 移除对象属性后的逗号（如果后面跟着换行和}或]）
                content = re.sub(r',\s*\n\s*(\}|\])', r'\n\1', content)
                
                # 解析JSON
                data = json.loads(content)
                
                # 提取必要的字段
                self.mod_id = data.get("id", self.mod_id)
                self.name = data.get("name", self.name)
                self.version = data.get("version", self.version)
                self.author = data.get("author", self.author)
                self.description = data.get("description", self.description)
                
                self.valid = bool(self.mod_id and self.name and self.version)
                if self.valid:
                    logger.info(f"传统JSON解析成功读取mod_info.json: {self.file_path}")
                else:
                    logger.warning(f"mod_info.json缺少必要字段: {self.file_path}")
        except json.JSONDecodeError as e:
            logger.error(f"解析mod_info.json失败: {self.file_path}, 错误: {e}")
            # 如果JSON解析失败，但基于行的解析已经提取到了一些字段，仍然标记为有效
            if self.mod_id and self.name and self.version:
                self.valid = True
                logger.info(f"基于行的解析成功，成功读取mod_info.json: {self.file_path}")
        except Exception as e:
            logger.error(f"读取mod_info.json时发生异常: {self.file_path}, 错误: {e}")
            # 如果发生异常，但基于行的解析已经提取到了一些字段，仍然标记为有效
            if self.mod_id and self.name and self.version:
                self.valid = True
                logger.info(f"基于行的解析成功，成功读取mod_info.json: {self.file_path}")
            else:
                logger.error(f"无法读取mod_info.json: {self.file_path}, 所有解析方法均失败")
    
    def to_dict(self):
        """将ModInfo对象转换为字典
        
        Returns:
            dict: ModInfo对象的字典表示
        """
        return {
            "id": self.mod_id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "valid": self.valid,
            "file_path": self.file_path
        }


def get_mod_info_by_id(mod_id: str) -> ModInfo:
    """通过mod_id获取mod信息
    
    Args:
        mod_id: mod的唯一标识
        
    Returns:
        ModInfo: mod信息对象，如果不存在则返回None
    """
    return id_to_mod_info_mapping.get(mod_id)


def get_all_mod_info() -> dict:
    """获取所有mod信息
    
    Returns:
        dict: 所有mod信息的字典，格式：{mod_id: mod_info_object}
    """
    return id_to_mod_info_mapping


def init_project_structure(base_path: str) -> Dict[str, Any]:
    """
    自动创建必要的文件夹结构

    Args:
        base_path: 项目基础路径

    Returns:
        Dict[str, Any]: 执行结果
    """
    timestamp = get_timestamp()
    process_id = f"{timestamp}_init_structure"
    
    created_folders = []
    failed_folders = []
    
    logger.info(f"开始初始化项目文件夹结构，基础路径: {base_path}")
    
    for folder_rel_path in REQUIRED_FOLDERS:
        folder_path = os.path.join(base_path, folder_rel_path)
        try:
            # 先检查文件夹是否存在
            if not os.path.exists(folder_path):
                # 只有当文件夹不存在时才创建
                os.makedirs(folder_path, exist_ok=True)
                created_folders.append(folder_rel_path)
                logger.info(f"成功创建文件夹: {folder_rel_path}")
            else:
                # 文件夹已存在，跳过创建
                logger.debug(f"文件夹已存在，跳过创建: {folder_rel_path}")
        except Exception as e:
            failed_folders.append({
                "path": folder_rel_path,
                "error": str(e)
            })
            logger.error(f"创建文件夹失败: {folder_rel_path}, 错误: {e}")
    
    # 生成报告
    total_count = len(REQUIRED_FOLDERS)
    success_count = len(created_folders)
    fail_count = len(failed_folders)
    
    fail_reasons = [f"创建文件夹失败: {item['path']}, 错误: {item['error']}" for item in failed_folders]
    
    report = generate_report(
        process_id=process_id,
        mode="Init",
        sub_flow="初始化项目文件夹结构",
        status="success" if fail_count == 0 else "fail",
        data={
            "total_count": total_count,
            "success_count": success_count,
            "fail_count": fail_count,
            "fail_reasons": fail_reasons,
            "created_folders": created_folders
        }
    )
    
    logger.info(f"项目文件夹结构初始化完成，成功创建: {success_count}/{total_count} 个文件夹")
    
    return report


def auto_rename_files_folders(base_path: str) -> Dict[str, Any]:
    """
    读取mod文件夹中的mod_info.json文件信息，对相关文件或文件夹进行自动重命名

    Args:
        base_path: 项目基础路径

    Returns:
        Dict[str, Any]: 执行结果
    """
    from src.common.config_utils import get_directory
    
    timestamp = get_timestamp()
    process_id = f"{timestamp}_auto_rename"
    
    renamed_items = []
    failed_items = []
    skipped_items = []
    
    # 获取正确的Localization_File路径
    mod_root = get_directory("mod_root")
    if not mod_root:
        logger.error("无法获取mod_root路径，使用base_path作为替代")
        mod_root = os.path.join(base_path, "Localization_File")
    
    logger.info(f"开始自动重命名文件/文件夹，mod_root: {mod_root}")
    
    # 遍历source和source_backup目录下的所有mod文件夹
    source_dirs = [
        # source目录
        os.path.join(mod_root, "source/Chinese"),
        os.path.join(mod_root, "source/English"),
        # source_backup目录
        os.path.join(mod_root, "source_backup/Chinese"),
        os.path.join(mod_root, "source_backup/English")
    ]
    
    for source_dir in source_dirs:
        if not os.path.exists(source_dir):
            logger.warning(f"源目录不存在: {source_dir}")
            continue
        
        # 遍历源目录下的所有文件夹
        for mod_folder in os.listdir(source_dir):
            mod_folder_path = os.path.join(source_dir, mod_folder)
            if not os.path.isdir(mod_folder_path):
                continue
            
            # 检查mod_info.json文件是否存在
            mod_info_path = os.path.join(mod_folder_path, "mod_info.json")
            if not os.path.exists(mod_info_path):
                skipped_items.append({
                    "path": mod_folder_path,
                    "reason": "mod_info.json文件不存在"
                })
                logger.info(f"跳过文件夹: {mod_folder_path}, 原因: mod_info.json文件不存在")
                continue
            
            # 读取mod_info.json
            mod_info = ModInfo(mod_info_path)
            if not mod_info.valid:
                failed_items.append({
                    "path": mod_folder_path,
                    "error": "mod_info.json文件无效"
                })
                logger.error(f"读取mod_info.json失败: {mod_info_path}")
                continue
            
            # 根据mod_info.json中的信息重命名文件夹
            try:
                # 构建新的文件夹名称：name + 空格 + version
                if mod_info.name and mod_info.version:
                    new_folder_name = f"{mod_info.name} {mod_info.version}"
                elif mod_info.name:
                    new_folder_name = mod_info.name
                elif mod_info.version:
                    new_folder_name = f"{mod_info.mod_id if mod_info.mod_id else mod_folder} {mod_info.version}"
                else:
                    new_folder_name = mod_info.mod_id if mod_info.mod_id else mod_folder
                
                new_folder_path = os.path.join(source_dir, new_folder_name)
                
                # 更新id_to_mod_info_mapping映射表
                if mod_info.mod_id:
                    # 直接存储mod_info对象，覆盖已存在的记录
                    id_to_mod_info_mapping[mod_info.mod_id] = mod_info
                
                if new_folder_path != mod_folder_path:
                    # 检查新文件夹名称是否已存在
                    if not os.path.exists(new_folder_path):
                        # 重命名文件夹
                        os.rename(mod_folder_path, new_folder_path)
                        renamed_items.append({
                            "old_path": mod_folder_path,
                            "new_path": new_folder_path
                        })
                        logger.info(f"成功重命名文件夹: {mod_folder} -> {new_folder_name}")
                        
                        # 更新id_to_mod_info_mapping映射表中的文件路径
                        if mod_info.mod_id:
                            # 更新mod_info对象的file_path属性
                            mod_info.file_path = os.path.join(new_folder_path, "mod_info.json")
                            # 重新存储更新后的mod_info对象
                            id_to_mod_info_mapping[mod_info.mod_id] = mod_info
                    else:
                        skipped_items.append({
                            "path": mod_folder_path,
                            "reason": f"新文件夹名称 {new_folder_name} 已存在"
                        })
                        logger.warning(f"跳过文件夹: {mod_folder_path}, 原因: 新文件夹名称 {new_folder_name} 已存在")
                else:
                    skipped_items.append({
                        "path": mod_folder_path,
                        "reason": "文件夹名称已符合要求"
                    })
                    logger.info(f"跳过文件夹: {mod_folder_path}, 原因: 文件夹名称已符合要求")
            except Exception as e:
                failed_items.append({
                    "path": mod_folder_path,
                    "error": str(e)
                })
                logger.error(f"重命名文件夹失败: {mod_folder_path}, 错误: {e}")
    
    # 生成报告
    total_count = len(renamed_items) + len(failed_items) + len(skipped_items)
    success_count = len(renamed_items)
    fail_count = len(failed_items)
    
    fail_reasons = [f"重命名失败: {item['path']}, 错误: {item['error']}" for item in failed_items]
    
    report = generate_report(
        process_id=process_id,
        mode="Init",
        sub_flow="自动重命名文件/文件夹",
        status="success" if fail_count == 0 else "fail",
        data={
            "total_count": total_count,
            "success_count": success_count,
            "fail_count": fail_count,
            "fail_reasons": fail_reasons,
            "renamed_items": renamed_items,
            "skipped_items": skipped_items
        }
    )
    
    logger.info(f"自动重命名完成，成功: {success_count}, 失败: {fail_count}, 跳过: {len(skipped_items)}")
    
    return report


def build_mod_mappings(mod_root: str) -> Dict[str, Any]:
    """
    构建mod映射关系，遍历source和source_backup目录
    
    Args:
        mod_root: Localization_File路径
        
    Returns:
        Dict[str, Any]: 包含映射结果的字典
    """
    timestamp = get_timestamp()
    process_id = f"{timestamp}_build_mod_mappings"
    
    logger.info(f"开始构建mod映射关系，mod_root: {mod_root}")
    
    # 清空全局映射表
    global mod_mappings
    mod_mappings.clear()
    
    success_count = 0
    fail_count = 0
    skipped_count = 0
    
    # 遍历source和source_backup目录
    source_types = ["source", "source_backup"]
    languages = ["Chinese", "English"]
    
    for source_type in source_types:
        for language in languages:
            # 构建当前目录路径
            current_dir = os.path.join(mod_root, source_type, language)
            
            if not os.path.exists(current_dir):
                logger.warning(f"目录不存在，跳过: {current_dir}")
                continue
            
            logger.info(f"处理目录: {current_dir} (source_type: {source_type}, language: {language})")
            
            # 遍历当前目录下的所有mod文件夹
            for mod_folder in os.listdir(current_dir):
                mod_path = os.path.join(current_dir, mod_folder)
                if not os.path.isdir(mod_path):
                    continue
                
                # 检查mod_info.json文件是否存在
                mod_info_path = os.path.join(mod_path, "mod_info.json")
                if not os.path.exists(mod_info_path):
                    logger.info(f"跳过文件夹: {mod_path}, 原因: mod_info.json文件不存在")
                    skipped_count += 1
                    continue
                
                # 读取mod_info.json
                mod_info = ModInfo(mod_info_path)
                if not mod_info.valid:
                    logger.error(f"读取mod_info.json失败: {mod_info_path}")
                    fail_count += 1
                    continue
                
                # 构建mod_id
                mod_id = mod_info.mod_id
                if not mod_id:
                    logger.warning(f"mod文件夹 {mod_path} 缺少id信息，跳过")
                    skipped_count += 1
                    continue
                
                # 更新全局映射表
                mod_mappings[mod_id] = {
                    "mod_path": mod_path,
                    "mod_info": mod_info,
                    "language": language,
                    "source_type": source_type
                }
                
                # 同时更新id_to_mod_info_mapping
                id_to_mod_info_mapping[mod_id] = mod_info
                
                success_count += 1
                logger.debug(f"添加mod映射: {mod_id} -> {mod_path} (language: {language}, source_type: {source_type})")
    
    logger.info(f"mod映射构建完成，成功: {success_count}, 失败: {fail_count}, 跳过: {skipped_count}")
    
    # 生成报告
    report = generate_report(
        process_id=process_id,
        mode="Init",
        sub_flow="构建mod映射关系",
        status="success" if fail_count == 0 else "fail",
        data={
            "total_count": success_count + fail_count + skipped_count,
            "success_count": success_count,
            "fail_count": fail_count,
            "skip_count": skipped_count,
            "mod_ids": list(mod_mappings.keys())
        }
    )
    
    return report


def get_mod_mapping() -> Dict[str, Any]:
    """
    获取完整的mod映射关系
    
    Returns:
        Dict[str, Any]: mod映射字典，格式：{mod_id: {"mod_path": str, "mod_info": ModInfo, "language": str, "source_type": str}}
    """
    return mod_mappings


def get_mod_path_by_id(mod_id: str, source_type: str = "source", language: str = None) -> str:
    """
    根据mod_id获取mod路径
    
    Args:
        mod_id: mod的唯一标识
        source_type: 源类型，可选值："source" 或 "source_backup"，默认"source"
        language: 语言类型，可选值："Chinese" 或 "English"，默认None（任意语言）
        
    Returns:
        str: mod路径，如果没有找到则返回空字符串
    """
    mod_info = mod_mappings.get(mod_id)
    if mod_info and mod_info["source_type"] == source_type:
        if language is None or mod_info["language"] == language:
            return mod_info["mod_path"]
    
    # 如果没有找到，尝试查找其他匹配项
    for mod_info in mod_mappings.values():
        if mod_info["mod_info"].mod_id == mod_id and mod_info["source_type"] == source_type:
            if language is None or mod_info["language"] == language:
                return mod_info["mod_path"]
    
    return ""


def get_mod_info_by_path(mod_path: str) -> Dict[str, Any]:
    """
    根据mod路径获取mod_info
    
    Args:
        mod_path: mod文件夹路径
        
    Returns:
        Dict[str, Any]: mod_info字典，如果没有找到则返回空字典
    """
    for mod_info in mod_mappings.values():
        if mod_info["mod_path"] == mod_path:
            return mod_info
    
    return {}


def run_init_tasks(base_path: str) -> Dict[str, Any]:
    """
    运行所有初始化任务

    Args:
        base_path: 项目基础路径

    Returns:
        Dict[str, Any]: 执行结果
    """
    timestamp = get_timestamp()
    process_id = f"{timestamp}_run_init_tasks"
    
    logger.info(f"开始执行初始化任务，基础路径: {base_path}")
    
    # 1. 创建必要的文件夹结构
    structure_result = init_project_structure(base_path)
    
    # 2. 自动重命名文件/文件夹
    rename_result = auto_rename_files_folders(base_path)
    
    # 3. 对source和source_backup目录下的mod文件夹进行重命名
    logger.info("开始执行文件夹重命名任务", extra={"stage": "RENAME"})
    
    # 获取正确的File路径
    from src.common.config_utils import get_directory
    mod_root = get_directory("mod_root")
    if not mod_root:
        logger.error("无法获取mod_root路径，使用base_path作为替代", extra={"stage": "RENAME"})
        mod_root = os.path.join(base_path, "File")
    
    source_dirs = [
        # source目录
        os.path.join(mod_root, "source/Chinese"),
        os.path.join(mod_root, "source/English"),
        # source_backup目录
        os.path.join(mod_root, "source_backup/Chinese"),
        os.path.join(mod_root, "source_backup/English")
    ]
    
    rename_mod_result = {
        "total_count": len(source_dirs),
        "success_count": 0,
        "fail_count": 0,
        "fail_reasons": []
    }
    
    for source_dir in source_dirs:
        # 提取目录类型和语言信息，用于阶段标记
        parts = source_dir.replace(mod_root + os.sep, "").split(os.sep)
        if len(parts) >= 2:
            dir_type = parts[0].upper()
            language = parts[1].upper()
            stage = f"RENAME_{dir_type}_{language}"
        else:
            stage = "RENAME_UNKNOWN"
        
        logger.info(f"开始重命名 {source_dir} 下的模组文件夹", extra={"stage": stage})
        if os.path.exists(source_dir):
            if rename_mod_folders(source_dir):
                rename_mod_result["success_count"] += 1
                logger.info(f"重命名完成: {source_dir}", extra={"stage": stage})
            else:
                rename_mod_result["fail_count"] += 1
                rename_mod_result["fail_reasons"].append(f"重命名文件夹失败: {source_dir}")
                logger.error(f"重命名文件夹失败: {source_dir}", extra={"stage": stage})
        else:
            rename_mod_result["fail_count"] += 1
            rename_mod_result["fail_reasons"].append(f"目录不存在: {source_dir}")
            logger.warning(f"目录不存在: {source_dir}", extra={"stage": stage})
    
    # 4. 从备份恢复文件
    logger.info("开始执行备份恢复任务", extra={"stage": "BACKUP_RESTORE"})
    backup_path = os.path.join(mod_root, "source_backup")
    target_path = os.path.join(mod_root, "source")
    
    restore_result = {
        "total_count": 1,
        "success_count": 0,
        "fail_count": 0,
        "fail_reasons": []
    }
    
    if restore_backup(backup_path, target_path):
        restore_result["success_count"] += 1
    else:
        restore_result["fail_count"] += 1
        restore_result["fail_reasons"].append("恢复备份失败")
    
    # 5. 构建mod映射关系
    logger.info("开始构建mod映射关系", extra={"stage": "BUILD_MOD_MAPPINGS"})
    mapping_result = build_mod_mappings(mod_root)
    
    # 合并结果
    total_count = (
        structure_result['data']['total_count'] + 
        rename_result['data']['total_count'] +
        rename_mod_result['total_count'] +
        restore_result['total_count'] +
        mapping_result['data']['total_count']
    )
    
    success_count = (
        structure_result['data']['success_count'] + 
        rename_result['data']['success_count'] +
        rename_mod_result['success_count'] +
        restore_result['success_count'] +
        mapping_result['data']['success_count']
    )
    
    fail_count = (
        structure_result['data']['fail_count'] + 
        rename_result['data']['fail_count'] +
        rename_mod_result['fail_count'] +
        restore_result['fail_count'] +
        mapping_result['data']['fail_count']
    )
    
    fail_reasons = (
        structure_result['data']['fail_reasons'] + 
        rename_result['data']['fail_reasons'] +
        rename_mod_result['fail_reasons'] +
        restore_result['fail_reasons'] +
        mapping_result['data'].get('fail_reasons', [])
    )
    
    # 生成综合报告
    report = generate_report(
        process_id=process_id,
        mode="Init",
        sub_flow="运行所有初始化任务",
        status="success" if fail_count == 0 else "fail",
        data={
            "total_count": total_count,
            "success_count": success_count,
            "fail_count": fail_count,
            "fail_reasons": fail_reasons,
            "structure_result": structure_result,
            "rename_result": rename_result,
            "rename_mod_result": rename_mod_result,
            "restore_result": restore_result,
            "mapping_result": mapping_result
        }
    )
    
    logger.info(f"初始化任务执行完成，成功: {success_count}/{total_count}")
    
    return report
