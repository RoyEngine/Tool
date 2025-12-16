# 实现新的mod_info.json解析方式

## 1. 目标
- 仅在软件启动阶段读取mod_info.json文件，获取必要信息
- 后续操作中读取的JSON文件应为规则文件
- 所有规则文件开头包含id字段，用于唯一标识
- 建立id到mod信息的映射关系

## 2. 实现步骤

### 2.1 增强初始化阶段的mod_info.json读取
**文件：`init_mode/core.py`**
- 修改`id_to_folder_mapping`为全局可用的映射表，包含id到完整mod信息的映射
- 扩展`ModInfo`类，增加对规则文件id字段的支持
- 在`auto_rename_files_folders`函数中，完善id到mod信息的映射关系

### 2.2 修改规则文件生成逻辑
**文件：`extract_mode/core.py`**
- 在生成映射规则文件（JSON/YAML）时，在文件开头添加id字段
- 确保id字段值与对应mod_info.json中的id保持一致

### 2.3 修改规则文件加载逻辑
**文件：`common/file_utils.py`**
- 增强`load_mapping_rules`函数，检查规则文件是否包含id字段
- 建立规则文件id到mod信息的关联
- 支持通过id字段获取对应的mod信息

### 2.4 更新extend_mode中的规则使用
**文件：`extend_mode/core.py`**
- 修改映射逻辑，不再直接读取mod_info.json
- 通过规则文件中的id字段获取mod信息
- 利用映射关系进行规则匹配和应用

### 2.5 实现缓存机制
- 在`init_mode/core.py`中实现mod信息的缓存
- 提供全局访问接口，供其他模块获取mod信息
- 确保缓存只在启动阶段更新

## 3. 关键技术点

### 3.1 映射关系设计
- 全局映射表格式：`{mod_id: mod_info_object}`
- 规则文件格式：`{"id": "mod_id", "rules": [...], ...}`

### 3.2 规则文件验证
- 检查规则文件是否包含有效的id字段
- 验证id是否存在于映射表中
- 处理无效规则文件的情况

### 3.3 缓存管理
- 确保缓存只在启动阶段初始化
- 提供线程安全的访问方式
- 支持缓存的刷新机制（可选）

## 4. 预期效果

- 减少对mod_info.json的重复读取
- 提高规则文件的独立性和可移植性
- 实现id字段作为mod的唯一标识
- 建立清晰的mod信息和规则文件关联
- 优化程序启动和运行时性能

## 5. 测试计划

- 验证启动阶段是否正确读取所有mod_info.json
- 检查生成的规则文件是否包含id字段
- 测试extend_mode是否能通过id字段获取正确的mod信息
- 验证映射关系的准确性和完整性
- 测试异常情况处理（无效id、缺失id等）