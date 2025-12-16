# 整合计划

## 1. 需求分析
将extend_mode和extract_mode模块中实现的文件夹重命名功能与恢复备份功能整合到init_mode模块中，确保这些功能在软件启动时自动加载并可用。

## 2. 实现步骤

### 2.1 修改init_mode/core.py文件

#### 2.1.1 添加导入语句
在现有的导入语句中添加`rename_mod_folders`和`restore_backup`函数：
```python
from src.common import (
    create_folders, generate_report, get_timestamp, save_report,
    setup_logger, get_logger, log_progress, log_result,
    rename_mod_folders, restore_backup  # 添加这两个函数
)
```

#### 2.1.2 扩展初始化任务
在`run_init_tasks`函数中添加新的初始化任务：

1. **文件夹重命名任务**：调用`rename_mod_folders`函数处理source目录下的所有mod文件夹
2. **备份恢复任务**：调用`restore_backup`函数从备份恢复文件

### 2.2 具体实现细节

#### 2.2.1 文件夹重命名任务
- 对`Localization_File/source/Chinese`和`Localization_File/source/English`目录下的mod文件夹进行重命名
- 利用现有的`rename_mod_folders`函数，该函数已经实现了根据mod_info.json重命名模组文件夹的功能

#### 2.2.2 备份恢复任务
- 从`Localization_File/source_backup`恢复到`Localization_File/source`目录
- 利用现有的`restore_backup`函数，该函数已经实现了基于mod_id匹配恢复备份的功能

### 2.3 修改run_init_tasks函数

更新`run_init_tasks`函数，添加新的初始化任务：

```python
def run_init_tasks(base_path: str) -> Dict[str, Any]:
    # 现有的初始化任务...
    
    # 3. 重命名source目录下的mod文件夹
    source_dirs = [
        os.path.join(base_path, "Localization_File/source/Chinese"),
        os.path.join(base_path, "Localization_File/source/English")
    ]
    for source_dir in source_dirs:
        if os.path.exists(source_dir):
            rename_mod_folders(source_dir)
    
    # 4. 从备份恢复文件
    backup_path = os.path.join(base_path, "Localization_File/source_backup")
    target_path = os.path.join(base_path, "Localization_File/source")
    restore_backup(backup_path, target_path)
    
    # 合并结果...
```

## 3. 预期效果

1. 软件启动时，init_mode模块会自动执行以下任务：
   - 创建必要的文件夹结构
   - 自动重命名文件/文件夹
   - 重命名source目录下的mod文件夹
   - 从备份恢复文件

2. 这些功能将与原模块保持相同的功能逻辑和用户体验

3. 代码将保持良好的可维护性和可扩展性，遵循现有代码风格和架构

## 4. 测试计划

在整合完成后，需要测试以下内容：

1. 确保软件启动时所有初始化任务都能正常执行
2. 确保文件夹重命名功能正常工作
3. 确保备份恢复功能正常工作
4. 确保没有破坏现有功能

## 5. 代码质量

- 遵循PEP 8代码风格
- 添加必要的类型注解
- 保持清晰的代码结构和注释
- 确保与现有代码的兼容性

## 6. 依赖关系

- 依赖现有的common模块中的`rename_mod_folders`和`restore_backup`函数
- 不需要引入新的外部依赖

## 7. 风险评估

- 低风险：所有功能都已经在其他模块中实现并测试过
- 低风险：修改仅涉及添加功能调用，不修改现有功能逻辑
- 低风险：遵循现有代码架构和风格

通过以上步骤，我们可以将文件夹重命名功能和恢复备份功能成功整合到init_mode模块中，确保它们在软件启动时自动执行。