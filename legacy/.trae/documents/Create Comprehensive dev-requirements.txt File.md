# 创建完整的dev-requirements.txt文件

## 1. 项目分析

### 1.1 现有开发依赖
从当前的requirements.txt文件中，以下是与开发相关的包：
- `flake8==7.3.0`（代码 linting）
- `iniconfig==2.3.0`（pytest 配置）
- `mccabe==0.7.0`（圈复杂度检查）
- `packaging==25.0`（版本处理）
- `pluggy==1.6.0`（pytest 插件系统）
- `pycodestyle==2.14.0`（代码风格检查）
- `pyflakes==3.4.0`（语法错误检查）
- `Pygments==2.19.2`（语法高亮）
- `pytest==9.0.2`（测试框架）
- `six==1.17.0`（Python 2/3 兼容性）

### 1.2 所需的额外开发工具
根据项目需求和最佳实践，我们应该添加以下工具：
- **测试工具**：pytest-cov（覆盖率报告）、pytest-mock（模拟测试）
- **代码检查**：mypy（类型检查）、bandit（安全检查）
- **代码格式化**：black（代码格式化）、isort（导入排序）、docformatter（文档字符串格式化）
- **文档生成**：sphinx（文档生成）、sphinx-rtd-theme（readthedocs 主题）、sphinx-autodoc-typehints（类型提示支持）
- **Git 钩子**：pre-commit（Git 钩子管理）

## 2. 文件结构

### 2.1 dev-requirements.txt 内容
```txt
# Localization_Tool 开发依赖
# 此文件列出了项目的所有开发依赖

# =====================================
# 测试工具
# =====================================
pytest==9.0.2
pytest-cov==5.0.0
pytest-mock==3.14.0
iniconfig==2.3.0
pluggy==1.6.0

# =====================================
# 代码检查工具
# =====================================
flake8==7.3.0
pycodestyle==2.14.0
pyflakes==3.4.0
mccabe==0.7.0
bandit==1.7.8
mypy==1.13.0

# =====================================
# 代码格式化工具
# =====================================
black==24.10.0
isort==5.13.2
docformatter==1.8.3

# =====================================
# 文档生成工具
# =====================================
sphinx==7.4.0
sphinx-rtd-theme==2.0.0
sphinx-autodoc-typehints==2.3.0
Pygments==2.19.2

# =====================================
# Git 钩子工具
# =====================================
pre-commit==3.8.0

# =====================================
# 实用库
# =====================================
packaging==25.0
six==1.17.0
typing_extensions==4.12.0
```

## 3. 实施步骤

### 3.1 创建 dev-requirements.txt 文件
- **路径**：`c:\Users\Roki\Documents\GitHub\Tool\legacy\Localization_Tool\dev-requirements.txt`
- **内容**：按照上述草稿，包含适当的分组和版本规范

### 3.2 更新 main requirements.txt
- 从主 requirements.txt 中移除开发依赖
- 只保留核心依赖：colorama、requests、PyYAML、tree-sitter、tree-sitter-java、tree-sitter-kotlin

### 3.3 验证安装
- 运行 `pip install -r dev-requirements.txt` 确保所有包正确安装
- 运行 `pip check` 验证没有依赖冲突

## 4. 预期收益

### 4.1 一致的开发环境
- 所有开发者使用相同版本的开发工具
- 减少 "在我机器上可以运行" 的问题

### 4.2 改进的开发工作流
- 全面的工具集，用于测试、代码检查、格式化和文档生成
- 支持现代 Python 开发最佳实践

### 4.3 更好的代码质量
- 使用 black、isort 和 docformatter 强制一致的代码风格
- 使用 flake8、bandit 和 mypy 检测潜在问题
- 使用 pytest-cov 确保适当的测试覆盖率

### 4.4 增强的文档
- Sphinx 设置用于生成专业文档
- 文档中适当的类型提示支持

## 5. 使用指南

### 5.1 安装
```bash
# 安装所有开发依赖
pip install -r dev-requirements.txt

# 只安装生产依赖
pip install -r requirements.txt
```

### 5.2 运行工具
```bash
# 运行带覆盖率的测试
pytest --cov=src

# 检查代码
flake8 src

# 检查类型
mypy src

# 格式化代码
black src
isort src
docformatter -i src/**/*.py

# 生成文档
cd docs && make html
```

### 5.3 设置 Git 钩子
```bash
pre-commit install
```

## 6. 最终验证

### 6.1 文件验证
- 确保 dev-requirements.txt 格式正确
- 检查是否有重复的包
- 验证所有版本规范是否正确

### 6.2 安装测试
- 运行 `pip install -r dev-requirements.txt` 确认没有错误
- 运行 `pip check` 确保没有依赖冲突

### 6.3 集成测试
- 使用 pytest 运行现有测试，确保兼容性
- 使用 flake8 检查代码库，验证代码检查工作正常

通过实现这个全面的 dev-requirements.txt 文件，我们将确保项目有一个一致、高质量的开发环境。