# Localization_Tool 重构计划

## 1. 执行流程修改：初始化操作集中化

### 1.1 问题分析
- 当前 `create_folders`、`rename_mod_folders` 和 `restore_backup` 三个操作在多个地方重复执行
- `init_mode` 模块已实现了这些操作的集中执行，但其他模块仍在重复执行
- `flow_executor.py` 也包含了这些操作，导致重复执行

### 1.2 解决方案

#### 修改 `init_mode/core.py`
- 确保 `run_init_tasks` 函数在启动时执行所有必要的初始化操作
- 确认 `init_project_structure`、`auto_rename_files_folders`、`rename_mod_folders` 和 `restore_backup` 都正确执行

#### 修改 `common/flow_executor.py`
- 默认关闭 `require_folders`、`require_renaming` 和 `require_restoring` 选项
- 移除或修改 `prepare_folders` 和 `rename_and_restore` 方法，使其只在明确配置时执行
- 修改 `FlowConfig` 默认值：
  ```python
  require_folders: bool = False
  require_renaming: bool = False
  require_restoring: bool = False
  ```

#### 修改 `extract_mode/core.py` 和 `extend_mode/core.py`
- 移除所有对 `create_folders`、`rename_mod_folders` 和 `restore_backup` 的直接调用
- 确保这些模块不再执行初始化操作

## 2. 全面重构建议

### 2.1 模块化设计
- 将各个功能模块进一步拆分，确保单一职责原则
- 明确模块间的依赖关系，减少耦合
- 建立清晰的接口定义

### 2.2 一致的命名约定
- 统一变量、函数和类的命名风格
- 使用有意义的名称，避免缩写和模糊命名
- 遵循 PEP 8 规范

### 2.3 减少代码重复
- 提取通用功能到公共模块
- 使用继承和组合减少重复代码
- 确保所有模块使用相同的工具函数

### 2.4 改进错误处理
- 使用结构化的异常处理
- 提供详细的错误信息
- 实现统一的日志记录机制

### 2.5 明确的职责分离
- 每个模块只负责一个功能领域
- 避免跨模块直接调用内部函数
- 使用接口进行模块间通信

## 3. 代码注释审查与更新

### 3.1 审查范围
- 所有模块的文档字符串
- 函数和方法的注释
- 复杂逻辑块的注释
- 重要算法的注释

### 3.2 更新内容
- 修正过时的注释
- 补充缺失的注释
- 确保注释准确反映当前实现
- 使用清晰、简洁的语言

## 4. 反编译功能架构调整

### 4.1 问题分析
- 当前反编译功能与其他模块耦合较紧
- `extract_mode` 和 `extend_mode` 直接调用反编译相关函数
- 缺乏清晰的接口定义

### 4.2 解决方案

#### 增强 `decompile_mode` 模块
- 提供完整的反编译功能接口
- 实现独立的数据流程
- 增强错误处理机制

#### 移除其他模块对反编译功能的直接依赖
- `extract_mode` 和 `extend_mode` 不再直接调用反编译函数
- 反编译操作只通过 `decompile_mode` 模块提供的接口执行

#### 建立明确的调用关系
- 提取和映射流程需要反编译时，通过 `decompile_mode` 模块的 API 调用
- 反编译结果通过标准接口返回

## 5. 重构步骤

### 步骤 1：执行流程修改
1. 修改 `init_mode/core.py`，确保初始化操作完整
2. 修改 `common/flow_executor.py`，关闭默认的初始化操作
3. 移除 `extract_mode/core.py` 中的初始化操作调用
4. 移除 `extend_mode/core.py` 中的初始化操作调用

### 步骤 2：反编译功能分离
1. 增强 `decompile_mode` 模块，提供完整的 API
2. 移除 `extract_mode` 和 `extend_mode` 中对反编译功能的直接调用
3. 建立新的调用关系

### 步骤 3：代码注释更新
1. 审查所有模块的文档字符串
2. 更新函数和方法注释
3. 补充复杂逻辑块的注释

### 步骤 4：重构建议实施
1. 模块化设计改进
2. 命名约定统一
3. 代码重复减少
4. 错误处理改进
5. 职责分离明确

## 6. 预期效果

- 初始化操作只在启动时执行一次
- 反编译功能独立，与其他模块解耦
- 代码结构清晰，可维护性提高
- 注释准确，便于理解和维护
- 模块间依赖关系明确，降低耦合度

## 7. 测试策略

- 单元测试：测试每个模块的功能
- 集成测试：测试模块间的交互
- 端到端测试：测试完整的工作流程
- 回归测试：确保现有功能不受影响

## 8. 代码质量保证

- 遵循 PEP 8 规范
- 使用类型注解
- 运行静态代码分析
- 确保测试覆盖率

通过以上重构计划，我们将使 Localization_Tool 更加模块化、可维护，同时解决当前存在的执行流程问题和反编译功能耦合问题。