# -*- coding: utf-8 -*-
"""
并行处理工具模块

该模块提供了并行文件处理的功能，用于加速字符串提取和翻译回写等操作。
"""

import os
import time
from typing import List, Callable, Any, Dict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed


class ParallelProcessor:
    """
    并行处理器类，用于并行处理文件列表
    """
    
    def __init__(self, max_workers: int = None, use_multiprocessing: bool = False):
        """
        初始化并行处理器
        
        Args:
            max_workers: 最大工作线程/进程数，默认为CPU核心数
            use_multiprocessing: 是否使用多进程模式，默认为多线程模式
        """
        self.max_workers = max_workers
        self.use_multiprocessing = use_multiprocessing
    
    def process_files(self, file_paths: List[str], worker_func: Callable[[str], Any]) -> Dict[str, Any]:
        """
        并行处理文件列表
        
        Args:
            file_paths: 要处理的文件路径列表
            worker_func: 处理单个文件的函数
        
        Returns:
            Dict[str, Any]: 处理结果，包含成功、失败和耗时信息
        """
        start_time = time.time()
        results = {
            "success": [],
            "failed": [],
            "time": 0.0
        }
        
        # 根据选择使用不同的执行器
        ExecutorClass = ProcessPoolExecutor if self.use_multiprocessing else ThreadPoolExecutor
        
        with ExecutorClass(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_file = {executor.submit(worker_func, file_path): file_path for file_path in file_paths}
            
            # 处理结果
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    results["success"].append({
                        "file": file_path,
                        "result": result
                    })
                except Exception as e:
                    results["failed"].append({
                        "file": file_path,
                        "error": str(e)
                    })
        
        # 计算耗时
        results["time"] = time.time() - start_time
        
        return results


def get_all_source_files(root_dir: str, extensions: List[str]) -> List[str]:
    """
    获取指定目录下所有符合扩展名要求的文件
    
    Args:
        root_dir: 根目录路径
        extensions: 文件扩展名列表
    
    Returns:
        List[str]: 文件路径列表
    """
    source_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                source_files.append(os.path.join(root, file))
    return source_files


def batch_process_files(
    root_dir: str,
    extensions: List[str],
    worker_func: Callable[[str], Any],
    max_workers: int = None,
    use_multiprocessing: bool = False
) -> Dict[str, Any]:
    """
    批量处理文件的便捷函数
    
    Args:
        root_dir: 根目录路径
        extensions: 文件扩展名列表
        worker_func: 处理单个文件的函数
        max_workers: 最大工作线程/进程数
        use_multiprocessing: 是否使用多进程模式
    
    Returns:
        Dict[str, Any]: 处理结果
    """
    # 获取所有源文件
    source_files = get_all_source_files(root_dir, extensions)
    
    if not source_files:
        return {
            "success": [],
            "failed": [],
            "time": 0.0,
            "message": "没有找到符合条件的文件"
        }
    
    # 创建并行处理器并处理文件
    processor = ParallelProcessor(max_workers=max_workers, use_multiprocessing=use_multiprocessing)
    results = processor.process_files(source_files, worker_func)
    
    return results
