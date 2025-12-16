# 修复Extend模式子目录处理逻辑

## 问题分析

1. **当前问题**：在 `save_report` 函数中，当处理映射规则时，代码尝试从 `report_path` 中提取 Extend 模式的子目录，但逻辑存在错误

2. **错误原因**：
   - 调用 `save_report` 时传递的 `report_path` 参数已经是完整的映射文件夹路径（包含模组名称）
   - `os.path.dirname(report_path)` 返回的是包含模组名称的目录，而不是 Extend 模式的目录
   - `os.path.basename()` 无法正确提取到 Extend 模式的子目录名称

3. **解决方案**：修改 `save_report` 函数中处理映射规则的逻辑，正确识别 Extend 模式的子目录，并根据语言对信息进行处理

## 修复方案

### 1. 修改 `src/common/report_utils.py` 中的 `save_report` 函数

**问题代码**：
```python
elif rule_type == "mapping" and mod_name:
    # 映射规则，保存到对应的映射文件夹
    # 从report_path中提取Extend模式的子目录(如Extend_en2zh)
    extend_mode = os.path.basename(os.path.dirname(report_path))
    final_report_path = os.path.join(report_path, mod_name)
```

**修复后的代码**：
```python
elif rule_type == "mapping" and mod_name:
    # 映射规则，保存到对应的映射文件夹
    # 从report_path中提取完整路径信息
    parts = report_path.split(os.sep)
    
    # 查找包含Extend的目录
    extend_dir = None
    for i, part in enumerate(parts):
        if part.startswith("Extend_"):
            extend_dir = part
            break
    
    if extend_dir:
        # 提取语言对信息(如en2zh)
        lang_pair = extend_dir.split("_")[-1] if "_" in extend_dir else ""
        
        # 根据语言对确定目标目录
        if lang_pair in ["en2zh", "zh2en"]:
            # 使用正确的Extend目录结构
            final_report_path = report_path
        else:
            # 默认处理
            final_report_path = report_path
    else:
        # 如果没有找到Extend目录，使用默认路径
        final_report_path = report_path
```

### 2. 确保逻辑正确性

- 正确识别包含Extend的目录（如Extend_en2zh、Extend_zh2en）
- 提取语言对信息（如en2zh、zh2en）
- 根据语言对确定目标目录
- 确保报告保存到正确的位置

### 3. 测试修复效果

- 运行 `src/main.py` 进行测试
- 确保Extend模式的子目录能够根据语言对信息被准确识别
- 验证报告保存到正确的位置

## 预期效果

- Extend_en2zh目录下的文件会被正确识别为英文到中文的映射
- Extend_zh2en目录下的文件会被正确识别为中文到英文的映射
- 报告文件会保存到正确的位置
- 语言对信息能够被准确提取和使用

## 修复步骤

1. 编辑 `src/common/report_utils.py` 文件
2. 修改 `save_report` 函数中处理映射规则的逻辑
3. 保存文件
4. 测试修复效果

## 注意事项

- 确保代码兼容不同操作系统的路径分隔符
- 保持向后兼容性，确保现有功能不受影响
- 确保错误处理逻辑完善，避免因路径格式问题导致程序崩溃