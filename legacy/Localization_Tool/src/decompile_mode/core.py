#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
反编译模式核心模块

该模块提供完整的JAR文件反编译和提取API，包括：
1. decompile_single_jar - 反编译单个JAR文件
2. decompile_all_jars - 反编译目录中所有JAR文件
3. extract_single_jar - 提取单个JAR文件内容
4. extract_all_jars - 提取目录中所有JAR文件内容
5. run_decompile_sub_flow - 执行反编译子流程

所有API均返回FlowResult对象，包含执行状态、结果数据和错误信息
"""

import os
from typing import Any, Dict, List

from src.common import (generate_report,  # noqa: E402, E501
                        get_timestamp,
                        setup_logger, get_logger)
from src.common.jar_utils import (
    decompile_jar,
    decompile_all_jars_in_dir,
    extract_jar,
    find_jar_files,
    check_java_environment,
    check_decompiler_tools
)
from src.common.config_utils import get_directory
from src.common.flow_executor import FlowManager, FlowResult

# 设置日志记录器
logger = setup_logger("decompile_mode")


def run_decompile_sub_flow(sub_flow: str, base_path: str = None) -> Dict[str, Any]:
    """
    执行反编译指定子流程

    Args:
        sub_flow: 子流程类型，可选值：
            - 反编译单个JAR文件
            - 反编译目录中所有JAR文件
            - 提取单个JAR文件内容
            - 提取目录中所有JAR文件内容
        base_path: 基础路径，默认从配置获取

    Returns:
        Dict[str, Any]: 执行结果，包含output_path、mode和language
    """
    # 如果没有提供base_path，使用当前脚本的项目根目录
    if base_path is None:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 检查Java环境和反编译工具
    if not check_java_environment():
        return generate_report(
            process_id=f"{get_timestamp()}_decompile",
            mode="Decompile",
            sub_flow=sub_flow,
            status="fail",
            data={
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": ["Java环境不可用"],
            }
        )
    
    if not check_decompiler_tools():
        return generate_report(
            process_id=f"{get_timestamp()}_decompile",
            mode="Decompile",
            sub_flow=sub_flow,
            status="fail",
            data={
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": ["反编译工具不可用"],
            }
        )
    
    # 根据子流程类型执行不同的逻辑
    def flow_func() -> FlowResult:
        # 从配置中获取JAR文件路径和输出路径
        mod_root = get_directory("mod_root")
        if not mod_root:
            return FlowResult(
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["未找到mod_root配置"],
                    "output_path": ""
                },
                message="未找到mod_root配置"
            )
        
        # 构建输入和输出路径
        source_dir = os.path.join(mod_root, "source")
        decompile_output_dir = os.path.join(mod_root, "output", "Decompile")
        extract_output_dir = os.path.join(mod_root, "output", "Extract")
        
        if sub_flow == "反编译单个JAR文件":
            # 实现反编译单个JAR文件的逻辑
            jar_files = find_jar_files(source_dir)
            if not jar_files:
                return FlowResult(
                    status="fail",
                    data={
                        "total_count": 0,
                        "success_count": 0,
                        "fail_count": 1,
                        "fail_reasons": ["未找到JAR文件"],
                        "output_path": ""
                    },
                    message="未找到JAR文件"
                )
            jar_path = jar_files[0]
            jar_name = os.path.basename(jar_path).replace(".jar", "")
            jar_output_dir = os.path.join(decompile_output_dir, jar_name)
            return decompile_single_jar(jar_path, jar_output_dir)
        elif sub_flow == "反编译目录中所有JAR文件":
            # 实现反编译目录中所有JAR文件的逻辑
            return decompile_all_jars(source_dir, decompile_output_dir)
        elif sub_flow == "提取单个JAR文件内容":
            # 实现提取单个JAR文件内容的逻辑
            jar_files = find_jar_files(source_dir)
            if not jar_files:
                return FlowResult(
                    status="fail",
                    data={
                        "total_count": 0,
                        "success_count": 0,
                        "fail_count": 1,
                        "fail_reasons": ["未找到JAR文件"],
                        "output_path": ""
                    },
                    message="未找到JAR文件"
                )
            jar_path = jar_files[0]
            jar_name = os.path.basename(jar_path).replace(".jar", "")
            jar_output_dir = os.path.join(extract_output_dir, jar_name)
            return extract_single_jar(jar_path, jar_output_dir)
        elif sub_flow == "提取目录中所有JAR文件内容":
            # 实现提取目录中所有JAR文件内容的逻辑
            return extract_all_jars(source_dir, extract_output_dir)
        else:
            return FlowResult(
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": [f"未知子流程: {sub_flow}"],
                },
                message=f"未知子流程: {sub_flow}"
            )
    
    # 使用FlowManager执行流程
    result = FlowManager.execute_flow(
        mode="Decompile",
        sub_flow=sub_flow,
        base_path=base_path,
        flow_func=flow_func,
        require_folders=False,
        require_renaming=False,
        require_restoring=False
    )
    
    # 添加mode字段到结果中
    result["mode"] = "Decompile"
    
    # 如果结果中没有output_path，尝试从data中获取
    if "output_path" not in result:
        result["output_path"] = result.get("data", {}).get("output_path", "")
    
    return result


def decompile_single_jar(jar_path: str, output_dir: str, decompiler: str = "cfr") -> FlowResult:
    """
    反编译单个JAR文件
    
    Args:
        jar_path: JAR文件路径
        output_dir: 输出目录
        decompiler: 反编译工具，可选值：cfr或procyon
    
    Returns:
        FlowResult: 执行结果
    """
    try:
        # 执行反编译
        success = decompile_jar(jar_path, output_dir, decompiler)
        
        # 生成结果
        status = "success" if success else "fail"
        return FlowResult(
            status=status,
            data={
                "total_count": 1,
                "success_count": 1 if success else 0,
                "fail_count": 0 if success else 1,
                "fail_reasons": [] if success else ["反编译失败"],
                "output_path": output_dir
            },
            message=f"{status} 反编译单个JAR文件",
            output_path=output_dir
        )
    except Exception as e:
        return FlowResult(
            status="fail",
            data={
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": [f"执行过程中发生异常: {str(e)}"],
                "output_path": ""
            },
            message=f"执行过程中发生异常: {str(e)}",
            error_details=str(e)
        )


def decompile_all_jars(input_dir: str, output_dir: str, max_workers: int = 4, decompiler: str = "cfr") -> FlowResult:
    """
    反编译目录中所有JAR文件
    
    Args:
        input_dir: 包含JAR文件的输入目录
        output_dir: 输出目录
        max_workers: 并行工作线程数
        decompiler: 反编译工具，可选值：cfr或procyon
    
    Returns:
        FlowResult: 执行结果
    """
    try:
        # 执行批量反编译，使用并行处理
        results = decompile_all_jars_in_dir(input_dir, output_dir, max_workers=max_workers, decompiler=decompiler)
        
        # 统计结果
        total_count = len(results)
        success_count = sum(1 for r in results if r["success"])
        fail_count = total_count - success_count
        fail_reasons = []
        
        for result in results:
            if not result["success"]:
                fail_reasons.append(f"反编译失败: {os.path.basename(result['jar_file'])}")
        
        # 生成结果
        status = "success" if success_count > 0 else "fail"
        return FlowResult(
            status=status,
            data={
                "total_count": total_count,
                "success_count": success_count,
                "fail_count": fail_count,
                "fail_reasons": fail_reasons,
                "output_path": output_dir
            },
            message=f"{status} 反编译目录中所有JAR文件",
            output_path=output_dir
        )
    except Exception as e:
        return FlowResult(
            status="fail",
            data={
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": [f"执行过程中发生异常: {str(e)}"],
                "output_path": ""
            },
            message=f"执行过程中发生异常: {str(e)}",
            error_details=str(e)
        )


def extract_single_jar(jar_path: str, output_dir: str) -> FlowResult:
    """
    提取单个JAR文件内容
    
    Args:
        jar_path: JAR文件路径
        output_dir: 输出目录
    
    Returns:
        FlowResult: 执行结果
    """
    try:
        # 执行提取
        success = extract_jar(jar_path, output_dir)
        
        # 生成结果
        status = "success" if success else "fail"
        return FlowResult(
            status=status,
            data={
                "total_count": 1,
                "success_count": 1 if success else 0,
                "fail_count": 0 if success else 1,
                "fail_reasons": [] if success else ["提取失败"],
                "output_path": output_dir
            },
            message=f"{status} 提取单个JAR文件内容",
            output_path=output_dir
        )
    except Exception as e:
        return FlowResult(
            status="fail",
            data={
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": [f"执行过程中发生异常: {str(e)}"],
                "output_path": ""
            },
            message=f"执行过程中发生异常: {str(e)}",
            error_details=str(e)
        )


def extract_all_jars(input_dir: str, output_dir: str) -> FlowResult:
    """
    提取目录中所有JAR文件内容
    
    Args:
        input_dir: 包含JAR文件的输入目录
        output_dir: 输出目录
    
    Returns:
        FlowResult: 执行结果
    """
    try:
        # 查找JAR文件
        jar_files = find_jar_files(input_dir)
        if not jar_files:
            return FlowResult(
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["未找到JAR文件"],
                    "output_path": ""
                },
                message="未找到JAR文件"
            )
        
        # 执行批量提取
        success_count = 0
        fail_count = 0
        fail_reasons = []
        
        for jar_path in jar_files:
            jar_name = os.path.basename(jar_path).replace(".jar", "")
            jar_output_dir = os.path.join(output_dir, jar_name)
            
            if extract_jar(jar_path, jar_output_dir):
                success_count += 1
            else:
                fail_count += 1
                fail_reasons.append(f"提取失败: {os.path.basename(jar_path)}")
        
        # 生成结果
        status = "success" if success_count > 0 else "fail"
        return FlowResult(
            status=status,
            data={
                "total_count": len(jar_files),
                "success_count": success_count,
                "fail_count": fail_count,
                "fail_reasons": fail_reasons,
                "output_path": output_dir
            },
            message=f"{status} 提取目录中所有JAR文件内容",
            output_path=output_dir
        )
    except Exception as e:
        return FlowResult(
            status="fail",
            data={
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": [f"执行过程中发生异常: {str(e)}"],
                "output_path": ""
            },
            message=f"执行过程中发生异常: {str(e)}",
            error_details=str(e)
        )


def decompile_and_extract(jar_path: str, output_dir: str, decompiler: str = "cfr") -> bool:
    """
    反编译并提取JAR文件
    
    Args:
        jar_path: JAR文件路径
        output_dir: 输出目录
        decompiler: 反编译工具，可选值：cfr或procyon
    
    Returns:
        bool: 是否成功
    """
    return decompile_jar(jar_path, output_dir, decompiler)


def extract_jar_content(jar_path: str, output_dir: str) -> bool:
    """
    提取JAR文件内容，不进行反编译
    
    Args:
        jar_path: JAR文件路径
        output_dir: 输出目录
    
    Returns:
        bool: 是否成功
    """
    return extract_jar(jar_path, output_dir)


def find_jar_files_in_mod(mod_dir: str) -> List[str]:
    """
    在mod目录中查找JAR文件
    
    Args:
        mod_dir: mod目录路径
    
    Returns:
        List[str]: JAR文件路径列表
    """
    return find_jar_files(mod_dir)


def check_decompile_environment() -> bool:
    """
    检查反编译环境
    
    Returns:
        bool: 环境是否可用
    """
    return check_java_environment() and check_decompiler_tools()

