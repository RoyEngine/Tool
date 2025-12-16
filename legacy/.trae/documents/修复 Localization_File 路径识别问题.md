# 问题分析

## 1. 根本原因

通过分析代码和配置，我发现程序错误识别 Localization_File 路径的根本原因是 `config_utils.py` 中存在硬编码的路径计算逻辑，它覆盖了配置文件中的设置：

- 在 `_resolve_directory_config` 方法的第 494 行，有硬编码逻辑：`mod_root = os.path.join(os.path.dirname(tool_root), "Localization_File")`
- 这行代码会忽略配置文件中对 `mod_root` 的配置，强制将其设置为 `tool_root` 上级目录下的 `Localization_File`
- 同时，配置缓存机制可能导致错误的路径被缓存，即使修复了代码也不会立即生效

## 2. 具体问题点

1. **硬编码的路径计算**：第 494 行的硬编码逻辑覆盖了配置文件设置
2. **缓存机制**：如果缓存中的配置数据是错误的，会导致后续计算错误
3. **路径计算顺序**：预替换和硬编码计算之间的顺序问题
4. **缺少路径验证**：计算完成后没有验证路径是否符合预期

## 3. 解决方案

### 3.1 移除硬编码路径计算

删除 `config_utils.py` 中第 494-496 行的硬编码逻辑，让 `mod_root` 完全由配置文件和占位符替换决定：

```python
# 删除这三行硬编码逻辑
# mod_root = os.path.join(os.path.dirname(tool_root), "Localization_File")
# directories["mod_root"] = mod_root
# logger.debug(f"计算得到 mod_root: {mod_root}")
```

### 3.2 修复路径替换逻辑

确保配置文件中的占位符被正确替换：

- 保留预替换 `${current_dir}` 的逻辑
- 正确处理 `tool_root` 和 `mod_root` 的计算顺序
- 确保所有占位符都被正确替换

### 3.3 增强路径验证

在配置加载完成后，添加路径验证逻辑，确保 `mod_root` 指向预期的目录：

```python
# 在 validate_directories 方法中添加验证
if not os.path.exists(mod_root):
    logger.warning(f"mod_root 目录不存在: {mod_root}")
    # 尝试创建目录
    try:
        os.makedirs(mod_root, exist_ok=True)
        logger.info(f"已创建 mod_root 目录: {mod_root}")
    except Exception as e:
        logger.error(f"创建 mod_root 目录失败: {e}")
        return False
```

### 3.4 改进缓存机制

确保在配置文件变化时，缓存被正确更新：

- 在 `load_config` 方法中，确保缓存的 `config_mtime` 和 `settings_mtime` 被正确更新
- 提供清除缓存的机制，以便在需要时强制重新加载配置

### 3.5 添加调试日志

在关键步骤添加日志，以便调试路径计算问题：

```python
logger.debug(f"预替换后 tool_root: {directories['tool_root']}")
logger.debug(f"预替换后 mod_root: {directories['mod_root']}")
logger.debug(f"最终计算的 tool_root: {tool_root}")
logger.debug(f"最终计算的 mod_root: {self.config['directories']['mod_root']}")
```

## 4. 验证方案

1. **运行程序**：启动程序，观察日志中的路径计算过程
2. **检查目录**：验证 `Localization_File` 目录是否被正确识别和操作
3. **测试不同场景**：
   - 正常启动
   - 修改配置文件
   - 清除缓存后启动
4. **检查输出**：验证所有操作是否在正确的 `Localization_File` 目录下进行

## 5. 预期结果

修复后，程序将：

1. 正确识别 `c:\Users\Roki\Documents\GitHub\Tool\legacy\Localization_File` 作为目标目录
2. 不再在 `Localization_Tool` 目录下创建错误的 `Localization_File` 目录
3. 能够持续、准确地定位并操作目标文件夹
4. 配置变化时能够及时更新，避免缓存导致的问题

## 6. 代码修改点

1. **`config_utils.py`**：
   - 删除第 494-496 行的硬编码逻辑
   - 增强路径验证
   - 添加调试日志
   - 改进缓存机制

2. **`main.py`**：
   - 确保在启动时正确加载配置
   - 验证目录结构时检查 `mod_root` 路径

通过以上修改，能够彻底解决路径识别问题，确保程序持续、准确地定位并操作目标文件夹。