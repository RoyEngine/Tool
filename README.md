# Starsector Mod 源码本地化工具（V0 / CLI）

本工具用于对 **Starsector Mod 的 Java/Kotlin 源码（仅 src/**）**做字符串提取与回填替换：
- Extract：从源码提取字符串，生成/更新规则文件（YAML）
- Apply：把已翻译的规则写回英文源码，输出翻译后的源码树
- Extend：用 EN+ZH 基线对齐，自动填充已翻译条目（加速迭代）

V0 约束：
- 翻译由人工填写，不做机器翻译
- **V0 不做 jar 反编译/解包**：请先准备好 `src/`（反编译如需支持，必须作为独立预处理步骤）

---

## 1. 仓库固定目录（方案 B）

工具代码（不要改动位置）：
- `legacy/Localization_Tool/src/`

输入源码（两种语言、多 Mod；每个 Mod 必须包含 `src/`）：
- `legacy/Localization_File/source/English/<ModFolder>/src/**`
- `legacy/Localization_File/source/Chinese/<ModFolder>/src/**`

输出根目录：
- `legacy/Localization_File/output/`

---

## 2. Quick Start（V0）

从仓库根目录执行。

### 2.1 Extract（按语言递归提取所有 Mod）
```bat
python legacy/Localization_Tool/src/main.py extract ^
  --lang English ^
  --source-root legacy/Localization_File/source/English ^
  --out-root legacy/Localization_File/output
