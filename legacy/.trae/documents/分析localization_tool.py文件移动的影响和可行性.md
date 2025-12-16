# 分析localization_tool.py文件移动的影响和可行性

## 1. 文件依赖关系分析

### 1.1 内部依赖
- 该脚本依赖于 `src.common` 模块中的多个工具函数和类
- 具体包括：yaml_utils、tree_sitter_utils等模块
- 这些依赖关系在移动后仍然有效，因为目标目录是 `src/common`，属于同一包结构

### 1.2 外部依赖
- 标准库：os、sys、argparse、typing
- 这些依赖不受文件位置影响

## 2. 导入路径分析

### 2.1 当前导入语句
```python
# 添加项目根目录到Python搜索路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入核心模块
from src.common import (...)
from src.common.tree_sitter_utils import extract_ast_mappings
```

### 2.2 移动后影响
- 移动到 `src/common` 后，`sys.path.append` 语句变得多余，因为脚本已经位于 `src` 包结构中
- 导入语句 `from src.common import (...)` 需要修改，因为脚本现在已经在 `src.common` 包内

## 3. 资源引用分析

### 3.1 当前资源引用
- 脚本中没有直接引用相对于自身位置的资源文件
- 所有文件路径均通过命令行参数或配置获取

### 3.2 移动后影响
- 资源引用不受影响，因为没有硬编码的相对路径

## 4. 命令行功能分析

### 4.1 当前命令行使用
```bash
python scripts/localization_tool.py <command>
```

### 4.2 移动后影响
- 直接运行脚本的命令需要修改
- 脚本将失去作为独立脚本的直接可执行性

## 5. 可行性评估

### 5.1 技术可行性
- ✅ 可以移动，因为主要依赖关系在同一包结构内
- ✅ 导入语句修改后可以正常工作
- ✅ 资源引用不受影响

### 5.2 功能可行性
- ✅ 核心功能可以保持不变
- ✅ 但命令行使用方式需要调整

### 5.3 维护可行性
- ✅ 移动后更符合项目结构，脚本成为核心代码的一部分
- ✅ 便于统一维护和版本控制

## 6. 确保正常使用的必要步骤

### 6.1 代码修改
1. **移除多余的sys.path.append**：
   ```python
   # 删除这行
   sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
   ```

2. **修改导入语句**：
   ```python
   # 原导入
   from src.common import (...)
   from src.common.tree_sitter_utils import extract_ast_mappings
   
   # 修改为
   from .yaml_utils import (...)
   from .tree_sitter_utils import extract_ast_mappings
   ```

3. **添加包导出**：在 `src/common/__init__.py` 中添加导出
   ```python
   from .localization_tool import main
   ```

### 6.2 命令行入口调整
1. **在项目根目录创建入口脚本**：如 `run_localization.py`，内容如下：
   ```python
   #!/usr/bin/env python3
   from src.common.localization_tool import main
   import sys
   
   if __name__ == "__main__":
       sys.exit(main())
   ```

2. **或修改setup.py**：添加console_scripts配置
   ```python
   entry_points={
       'console_scripts': [
           'localization-tool=src.common.localization_tool:main',
       ],
   },
   ```

### 6.3 测试验证
1. 测试所有命令行功能是否正常：
   ```bash
   python run_localization.py extract --help
   python run_localization.py process-unmapped --help
   python run_localization.py conflict --help
   ```

2. 测试实际功能是否正常工作：
   ```bash
   python run_localization.py extract --source-dir ./Localization_File/source/English/src --output-file ./Localization_File/rule/English/test.yaml
   ```

## 7. 注意事项

1. **命令行文档更新**：需要更新脚本中的示例命令，将 `python scripts/localization_tool.py` 替换为新的运行方式

2. **现有脚本兼容性**：如果有其他脚本依赖该脚本的位置，需要同步更新

3. **导入循环问题**：移动后需要确保没有引入循环导入

4. **权限问题**：如果脚本之前有执行权限，移动后需要重新设置

5. **IDE配置**：需要确保IDE能够正确识别移动后的文件

## 8. 结论

将 `localization_tool.py` 从 `scripts` 目录移动到 `src/common` 目录是可行的，但需要进行以下修改：

1. 修改导入语句，移除多余的sys.path.append
2. 添加包导出，确保可以从外部访问
3. 调整命令行入口，保持命令行功能可用
4. 更新文档和示例命令
5. 进行全面测试验证

移动后，脚本将更好地融入项目结构，便于维护和扩展，同时保持原有功能不变。