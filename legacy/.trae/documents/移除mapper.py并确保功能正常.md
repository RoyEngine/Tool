# 移除mapper.py并确保功能正常

## 分析结论

1. **功能对比**：
   - `tree_sitter_utils.py`：主要负责字符串提取，提供完整的Tree-sitter初始化和AST遍历功能
   - `mapper.py`：主要负责字符串替换，依赖Tree-sitter进行字符串查找和替换

2. **依赖关系**：
   - `mapper.py`依赖`tree_sitter_utils.py`的Tree-sitter功能
   - 现有代码主要使用`yaml_utils.py`中的`apply_yaml_mapping`函数进行字符串替换

3. **使用情况**：
   - `mapper.py`没有被直接使用，`extend_mode/core.py`使用`yaml_utils.py`的`apply_yaml_mapping`函数
   - `mapper.py`包含与`tree_sitter_utils.py`重复的Tree-sitter初始化逻辑

4. **替代可行性**：
   - ✅ `tree_sitter_utils.py`已经覆盖了字符串提取功能
   - ✅ `yaml_utils.py`已经覆盖了字符串替换功能
   - ✅ `mapper.py`没有被直接使用
   - ✅ 移除后不会影响现有功能

## 实施计划

1. **移除文件**：
   - 删除`src/extend_mode/mapper.py`文件
   - 删除其对应的`.pyc`文件

2. **检查依赖**：
   - 确保没有其他文件直接导入`mapper.py`
   - 检查`extend_mode/__init__.py`是否引用了`mapper.py`

3. **测试功能**：
   - 运行`main.py`确保程序正常启动
   - 测试字符串提取功能
   - 测试字符串替换功能

## 风险评估

1. **低风险**：`mapper.py`没有被直接使用，移除后不会影响现有功能
2. **低风险**：现有功能已经由`tree_sitter_utils.py`和`yaml_utils.py`覆盖
3. **低风险**：移除重复代码有助于简化代码结构

## 预期结果

- 代码结构更简洁，减少重复实现
- 统一使用`tree_sitter_utils.py`进行字符串提取
- 统一使用`yaml_utils.py`进行字符串替换
- 减少维护成本
- 程序功能正常运行