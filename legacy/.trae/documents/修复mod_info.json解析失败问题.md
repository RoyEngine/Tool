# 修复mod_info.json解析失败问题

## 1. 问题分析

### 1.1 现象描述
- 执行命令后，系统提示"读取mod_info.json失败: ... - Expecting property name enclosed in double quotes: line 2 column 31 (char 32)"
- 影响的模组是Second-in-Command系列
- 错误发生在Chinese和English版本的source和source_backup目录下

### 1.2 根本原因
- mod_info.json文件存在格式问题：
  - 第2行有注释（`# For the convenience of troubleshooters...`），标准JSON不支持
  - 第15、19、23、27行对象末尾有逗号
  - 第36行数组末尾有逗号

### 1.3 代码分析
- `ModInfo._read_mod_info`方法实现了基于行的解析，重点处理前6行
- 对于前6行，使用正则表达式提取每行中前两个双引号内的字符串
- 如果基于行的解析失败，尝试使用传统JSON解析，移除注释和修复尾随逗号
- 但实际运行时，基于行的解析没有成功，导致进入传统JSON解析流程，遇到格式问题

## 2. 错误排查步骤

### 2.1 查看mod_info.json文件
- 检查文件内容，特别是第2行和依赖项数组部分
- 识别格式问题：注释、尾随逗号等

### 2.2 分析代码执行流程
- 调试`_read_mod_info`方法，查看基于行的解析是否成功
- 检查正则表达式是否能正确提取字段
- 查看传统JSON解析的错误信息

### 2.3 测试修复效果
- 修改mod_info.json文件，移除格式问题
- 重新运行命令，验证是否能成功读取

## 3. 解决方案

### 3.1 优化基于行的解析逻辑
**文件：`init_mode/core.py`**
- 改进`_read_mod_info`方法，增强基于行的解析能力
- 确保能正确处理带注释的行
- 优化正则表达式，提高字段提取的准确性

### 3.2 增强传统JSON解析的容错能力
- 改进注释移除逻辑，确保能处理所有类型的注释
- 增强尾随逗号修复逻辑，处理更多情况
- 提供更详细的错误信息，便于调试

### 3.3 代码修复建议
```python
def _read_mod_info(self):
    # ... 现有代码 ...
    
    try:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import re
        
        # 移除所有类型的注释
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'#.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'\s*/\*[\s\S]*?\*/\s*', '', content)
        
        # 修复JSON语法错误：移除尾随逗号
        content = re.sub(r',\s*(}|\])', r'\1', content)
        
        # 解析JSON
        data = json.loads(content)
        
        # 提取必要的字段
        self.mod_id = data.get("id", "")
        self.name = data.get("name", "")
        self.version = data.get("version", "unknown")
        self.author = data.get("author", "")
        self.description = data.get("description", "")
        
        self.valid = bool(self.mod_id and self.name and self.version)
        if self.valid:
            logger.info(f"成功读取mod_info.json: {self.file_path}")
        else:
            logger.warning(f"mod_info.json缺少必要字段: {self.file_path}")
    except json.JSONDecodeError as e:
        logger.error(f"解析mod_info.json失败: {self.file_path}, 错误: {e}")
        # 尝试基于行的解析作为最后手段
        self._read_mod_info_line_by_line()
    except Exception as e:
        logger.error(f"读取mod_info.json时发生异常: {self.file_path}, 错误: {e}")

# 新增基于行的解析作为备选方案
def _read_mod_info_line_by_line(self):
    # 现有基于行的解析逻辑
    # ...
```

### 3.4 临时解决方案
- 手动修复mod_info.json文件，移除注释和尾随逗号
- 或者使用第三方工具修复JSON格式

## 4. 优化建议

### 4.1 长期优化
- 考虑使用专门的JSON解析库，支持带注释的JSON（如`commentjson`）
- 增强代码的容错能力，提高对各种格式问题的处理能力
- 提供更详细的错误信息，便于调试

### 4.2 性能优化
- 缓存mod_info.json的解析结果，避免重复解析
- 优化正则表达式，提高解析速度

### 4.3 测试建议
- 增加单元测试，覆盖各种mod_info.json格式
- 测试带注释的JSON、带尾随逗号的JSON等
- 测试不同编码的mod_info.json文件

## 5. 预期效果

- 修复后，系统能成功读取mod_info.json文件
- 不再出现"Expecting property name enclosed in double quotes"错误
- 支持带注释的JSON和带尾随逗号的JSON
- 提高系统的容错能力和稳定性

## 6. 实施步骤

1. 修改`init_mode/core.py`文件，优化`_read_mod_info`方法
2. 测试修复效果，确保能处理各种格式的mod_info.json
3. 部署修复后的代码
4. 验证系统能成功读取所有mod_info.json文件
5. 考虑长期优化建议，提高系统的整体性能和稳定性