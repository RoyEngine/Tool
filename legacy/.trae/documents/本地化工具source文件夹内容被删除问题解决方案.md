## 问题调查结果

### 1. 问题根源

#### 1.1 source文件夹内容被删除问题
- **自动化测试脚本清理机制**：`automated_test.py` 脚本的 `prepare_test_environment` 函数在每次测试前会执行以下操作：
  - 清理 `source` 文件夹：`shutil.rmtree(TEST_CONFIG["source_path"])`
  - 创建空的 `source` 文件夹：`os.makedirs(TEST_CONFIG["source_path"])`
  - 从 `source_backup` 复制内容到 `source` 文件夹：`shutil.copytree(source_item, target_item)`

#### 1.2 工具无法自动关闭和返回主页问题
- 工具执行完任务后，没有正确的退出机制
- 操作流程结束后，没有自动返回主页的逻辑
- 可能存在残留进程

#### 1.3 路径寻找机制问题
- Terminal#1-93 `d:\Poki\Tool\Localization_File` 的路径寻找机制有问题
- `d:\Poki\Tool\Localization_File` 与 `d:\Poki\Tool\Localization_Tool` 是平行关系，都在 `D:\Poki\Tool` 下
- 工具配置中可能没有正确处理这种平行目录结构

### 2. 解决方案

#### 2.1 修复source文件夹内容被删除问题
- **修改 `automated_test.py` 脚本**：
  - 修改 `prepare_test_environment` 函数，移除强制清理整个 `source` 文件夹的逻辑
  - 改为仅在 `source_backup` 文件夹存在时，才更新 `source` 文件夹内容
  - 添加日志记录，便于调试和追踪

#### 2.2 修复工具无法自动关闭和返回主页问题
- **修改主程序退出逻辑**：
  - 确保工具在执行完所有指定任务后能够正常退出当前操作界面
  - 优化导航逻辑，使操作流程结束后系统能自动跳转回工具的主页面
  - 确保没有残留进程
- **添加测试用例**：
  - 测试不同操作场景下的自动关闭功能
  - 验证主页返回的准确性

#### 2.3 修复路径寻找机制问题
- **修改目录配置**：
  - 确保 `directory_config.json` 中正确配置了 `tool_root` 和 `mod_root` 路径
  - 修改路径寻找机制，正确处理平行目录结构
  - 测试路径解析功能，确保能正确找到 `Localization_File` 目录

### 3. 实施步骤

#### 3.1 修复自动化测试脚本
1. 修改 `prepare_test_environment` 函数：
   - 移除 `shutil.rmtree(TEST_CONFIG["source_path"])` 行
   - 添加条件判断，仅在需要时更新 `source` 文件夹内容
   - 添加详细日志记录

#### 3.2 修复工具退出和返回逻辑
1. 检查 `main.py` 中的退出逻辑
2. 添加操作完成后返回主页的功能
3. 确保没有残留进程
4. 编写测试用例，验证自动关闭和返回主页功能

#### 3.3 修复路径寻找机制
1. 检查 `directory_config.json` 中的路径配置
2. 修改 `config_utils.py` 中的路径解析逻辑
3. 确保 `tool_root` 和 `mod_root` 路径正确配置
4. 测试路径寻找功能，验证能正确找到 `Localization_File` 目录

#### 3.4 全面测试
1. 测试自动化测试脚本，验证 `source` 文件夹内容不再被意外删除
2. 测试工具的自动关闭和返回主页功能
3. 测试路径寻找机制，确保能正确找到 `Localization_File` 目录
4. 测试不同操作场景下的稳定性

### 4. 预期效果

- 解决 `source\English` 文件夹内容被意外删除的问题
- 工具执行完成后能自动关闭并返回主页
- 路径寻找机制能正确处理平行目录结构
- 提高自动化测试脚本的安全性和可靠性
- 提升用户操作体验

通过以上解决方案，可以有效解决本地化工具存在的问题，提高工具的稳定性和用户体验。