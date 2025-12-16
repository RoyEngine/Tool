# Tree-sitter 初始化修复方案

## 问题分析

1. **测试结果显示**：Tree-sitter 相关包（tree_sitter、tree_sitter_java、tree_sitter_kotlin）可以正常导入和使用
2. **语言对象类型**：从 tree_sitter_java.language() 和 tree_sitter_kotlin.language() 返回的是 PyCapsule 对象
3. **初始化函数设计**：initialize_languages 函数已经设计了多种方法来处理 PyCapsule 对象，但可能在某些情况下无法正确初始化
4. **导入路径问题**：当直接导入 tree_sitter_utils.py 模块时，遇到了导入路径问题，主要是因为其他模块依赖于它

## 修复方案

### 1. 修复 tree_sitter_utils.py 中的导入路径问题

**问题**：当直接导入 tree_sitter_utils.py 模块时，其他依赖它的模块（如 yaml_utils.py）可能会遇到导入路径问题

**修复**：修改 tree_sitter_utils.py 文件，确保它可以独立运行，不依赖于其他模块的导入路径设置

### 2. 优化 initialize_languages 函数

**问题**：当前的 initialize_languages 函数已经设计了多种方法来处理 PyCapsule 对象，但可能在某些情况下无法正确初始化

**修复**：
- 确保正确处理 Tree-sitter 0.25.2 版本的 API
- 优化错误处理，提供更详细的错误信息
- 确保在 Windows 系统上正常工作

### 3. 添加调试日志

**问题**：当前的初始化过程缺少足够的调试信息，难以定位问题

**修复**：添加更详细的调试日志，包括每个步骤的执行结果和错误信息

### 4. 修复 tree_sitter_utils.py 中的环境变量设置

**问题**：当前的 tree_sitter_utils.py 文件中设置了虚拟环境的 site-packages 目录，但路径可能不正确

**修复**：修改虚拟环境的 site-packages 目录路径，确保它指向正确的位置

## 修复步骤

1. **修改 tree_sitter_utils.py 文件**：
   - 修复虚拟环境的 site-packages 目录路径
   - 优化 initialize_languages 函数
   - 添加更详细的调试日志
   - 确保可以独立运行

2. **测试修复后的代码**：
   - 编写一个简单的测试脚本，直接测试 tree_sitter_utils.py 模块
   - 确保它可以正确初始化 Tree-sitter 语言解析器
   - 确保它可以正确提取字符串

3. **验证修复效果**：
   - 通过 main.py 启动工具，确保 Tree-sitter 初始化成功
   - 运行 Extract 模式，确保可以正确提取字符串

## 预期效果

1. **Tree-sitter 初始化成功**：修复后，tree_sitter_utils.py 应该可以正确初始化 Tree-sitter 语言解析器
2. **独立运行**：修复后，tree_sitter_utils.py 应该可以独立运行，不依赖于其他模块的导入路径设置
3. **详细调试日志**：修复后，初始化过程应该提供更详细的调试信息，便于定位问题
4. **跨平台兼容**：修复后，应该可以在 Windows 和其他平台上正常工作

## 修复后的代码结构

```python
# tree_sitter_utils.py

# 修复虚拟环境的 site-packages 目录路径
venv_site_packages = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    ".venv", "Lib", "site-packages"
)
sys.path.insert(0, venv_site_packages)

# 优化 initialize_languages 函数
def initialize_languages():
    """
    初始化Tree-sitter语言解析器
    增强兼容性处理，支持多种Tree-sitter版本
    针对Tree-sitter 0.25.2版本优化，添加Windows支持
    """
    # 详细的调试日志
    # 优化的初始化逻辑
    # 更好的错误处理
```