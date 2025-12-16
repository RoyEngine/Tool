## 1. 问题分析
- **当前行为**：`move_to_complete`函数使用`shutil.move()`将源文件夹移动到`Extract_Complete`目录，导致原始文件夹位置改变
- **用户需求**：
  - 执行文件提取操作时，无需移动原始文件夹位置
  - 提取出的文件应保留在原目录中
  - 完成文件映射操作后，相关文件同样需要保持在原始位置
  - 整个操作过程中所有文件的物理存储位置维持不变

## 2. 解决方案
修改`move_to_complete`函数，将**移动**操作改为**复制**操作，这样可以：
- 保持原始文件夹在其原始位置
- 同时在`Extract_Complete`目录中创建副本
- 不影响其他功能的正常运行

## 3. 实现步骤
1. **修改`move_to_complete`函数**：
   - 文件：`c:\Users\Roki\Documents\GitHub\Tool\legacy\Localization_Tool\src\common\file_utils.py`
   - 函数：`move_to_complete`（第865行）
   - 将`shutil.move()`替换为`shutil.copytree()`，并添加`dirs_exist_ok=True`参数以支持覆盖

2. **验证Extend模式**：
   - 已检查`src/extend_mode`目录，确认没有使用`move_to_complete`函数
   - 没有其他移动文件的操作（`shutil.move`或`os.rename`）
   - 因此Extend模式不需要修改

## 4. 预期效果
- 原始文件夹保持在`Localization_File/source/{language}/`位置
- `Extract_Complete`目录中会创建包含时间戳的文件夹副本
- 整个操作过程中所有文件的物理存储位置维持不变
- 不影响其他功能的正常运行

## 5. 实现代码
将第890行的`shutil.move()`替换为`shutil.copytree()`：
```python
# 原代码
shutil.move(source_path, os.path.join(target_path, source_folder_name))

# 修改后代码
shutil.copytree(source_path, os.path.join(target_path, source_folder_name), dirs_exist_ok=True)
```