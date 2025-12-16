1. 在main.py中导入decompile\_mode的核心函数
2. 在select\_main\_mode函数中添加Decompile模式选项
3. 添加select\_decompile\_sub\_flow函数，用于选择反编译子流程
4. 在argparse中添加decompile子命令
5. 在main函数中添加处理decompile模式的逻辑
6. 更新帮助文档和示例

具体修改点：

* 在import部分添加：from src.decompile\_mode.core import run\_decompile\_sub\_flow

* 在select\_main\_mode函数中添加选项4：Decompile模式

* 添加select\_decompile\_sub\_flow函数，显示反编译子流程选择菜单

* 在argparse中添加decompile子命令，支持四种子流程

* 在main函数中添加args.mode == "decompile"的处理分支

* 在帮助文档中添加Decompile模式说明和示例

