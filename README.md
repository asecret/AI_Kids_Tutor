# AI Kids Tutor · K12 智能私教与教辅系统

一套给 Agent 用的教辅技能：把「口语化提需求」直接变成**可打印的标准试卷**，
并把批改结果沉淀成**持续滚动的错题本**，错题自动生成变式重练卷。

家长只需要说人话，例如：

> 高小宝，初一，数学人教版
> 按第三章出一套期末卷，中等偏上
> 批改一下这张（附图片）
> 针对最近的错题出一套重练卷

---

## 能做什么

| 能力 | 说明 |
|---|---|
| 学生档案 | 姓名 / 年级 / 科目 / 教材版本 / 当前章节 |
| 卷种识别 | 单元测 / 月考 / 期中 / 期末 / 专项，自动推导考试范围，不确定会先问一句 |
| 按纲出题 | 依据教材版本 + 年级 + 章节，标准 7:2:1 难度配比 |
| 标准卷面 | 卷头三要素、答题框留白、页脚名句 + 页码、答案后置 |
| 分科规则 | 数学（LaTeX 公式、草稿框）/ 英语（禁听力、选项横排）/ 语文（防超纲、默写下划线） |
| 拍照批改 | 识别字迹 → 对比答案 → 标错 + 错因诊断 → 结构化归档 |
| 错题分类 | 统一 `knowledge_tag` 知识点 + `error_type` 错误类型（六类枚举），可跨科归类统计 |
| 错题重练 | 「换汤不换药」变式：换数据与情境，保留底层考点模型 |
| 批量合卷 | 按时间筛选（今天/最近N天/最近一月）、每题出 N 个变式、支持跨科合并成一份卷 |
| 靶向特训 | 卷头与题号显式标注对应的原错题编号 |

---

## 目录结构

```
AI_Kids_Tutor/
├── SKILL.md                                  ← 技能入口（Agent 读这个）
├── README.md                                 ← 本文件
├── LICENSE                                   ← MIT
├── references/                               ← 规则库（按需加载）
│   ├── 00_global_print_rules.md              全局排版铁律
│   ├── math_exam_rules.md                    数学规范
│   ├── english_exam_rules.md                 英语规范
│   ├── chinese_exam_rules.md                 语文规范
│   ├── wrong_question_retry_rule.md          错题变式标准
│   └── textbook_download_guide.md            教材自动下载操作规程
├── scripts/                                  ← 可执行脚本
│   └── fetch_textbook.py                     教材自动下载器
├── assets/                                   ← 数据模板（运行时复制走，勿改）
│   ├── student_profile.template.json
│   ├── wrong_questions.template.json
│   └── textbooks.manifest.template.json
├── textbooks/                                ← 教材 PDF（工作区内，见其 README）
│   └── README.md
├── student_profile.json                      ← 示例数据（给访客看格式）
└── wrong_questions.json                      ← 示例数据（给访客看格式）
```

> `student_profile.json` / `wrong_questions.json` 是**示例数据**（演示用，学生名「高小宝」）。
> 真正运行时，Agent 会在**你的工作区**新建自己的副本，不会改动这两个文件。

---

## 安装

### 方式 A · 手动（通用，最简单）

把整个 `AI_Kids_Tutor` 文件夹拷到对应平台的技能目录，文件夹名建议改为 `ai-kids-tutor`：

| 平台 / Agent | 用户级（全项目可用） | 项目级（仅当前项目） |
|---|---|---|
| WorkBuddy | `~/.workbuddy/skills/` | `<项目>/.workbuddy/skills/` |
| Claude Code | `~/.claude/skills/` | `<项目>/.claude/skills/` |
| OpenCode | `~/.config/opencode/skills/` | `<项目>/.opencode/skills/` |
| Cursor / Codex 等 | 各自主机 skills 目录 | 各自主机 skills 目录 |

放好后重启 / 新开会话即可生效。

### 方式 B · 直接 clone 到技能目录

```bash
# 以 WorkBuddy 为例，其他平台换目录即可
git clone https://github.com/<你的账号>/AI_Kids_Tutor.git \
  ~/.workbuddy/skills/ai-kids-tutor
```

### 方式 C · 豆包 / 扣子 / 元宝（不支持技能文件）

这些平台**不读取 SKILL.md，也没有本地文件系统**。
请改用仓库里的 **`全量提示词_豆包等无文件权限平台.md`**：
整段复制，粘贴到智能体的「系统提示词 / 人设设定」里即可。
该版本已把档案与错题本改为**对话内维护**，并直接输出排版好的卷面。

---

## 快速上手

安装完，直接对 Agent 说：

1. `高小宝，初一，数学人教版` → 建立档案、挂载教材
2. `帮我出套第二单元的数学卷纸` → 单元卷（"第二单元"自动归一化为章节范围）
3. `帮我出套数学期中考试卷纸` → 期中卷（自动推导半册范围，不确定会先确认）
4. 把孩子做好的卷子拍照发过去 → `批改一下` → 自动归档错题
5. `把最近一个月的错题，每个出三道同类型的，所有科目放一起` → 跨科错题合卷

---

## 关于教材

- **默认自动下载**：建档或出题时若 `./textbooks/` 没有对应教材，Agent 会**自动**从开源库
  `TapXWorld/ChinaTextbook` 下载（学段/科目/版本/年级自动匹配，下载后自动重命名并登记索引）。
- 自动下载失败时，Agent 会说明原因并给出手动下载链接，**不会默默降级**。
- 手动放置：教材 PDF 放进**你的工作区** `./textbooks/`，不要放进技能安装目录。
- **命名规范（强制）**：`科目_年级学期_版本.pdf`，科目键为 `math` / `chinese` / `english`。
  例：`math_七上_人教版.pdf`。所有 PDF 平铺在 `textbooks/` 根目录，不建子目录。
- **多科目可以全放一起**。Agent 靠 `textbooks/manifest.json` 索引 + 文件名做
  「科目 + 年级 + 学期 + 版本」四维精确匹配，不会认错书；你也**不用手写**这个索引，
  Agent 首次运行会自动扫描生成。
- 出于性能考虑，Agent **不会把教材 PDF 全文读入**，只在需要时按章节定向检索。
- **没有教材也能出题**：系统会依据「版本 + 年级 + 章节」的通用考点生成，并在卷头标注，不会中断。
- 可选开源教材库：https://github.com/TapXWorld/ChinaTextbook （体积大，建议单本手动下载后重命名）

## 关于导出格式

**零安装。** Agent 会自动探测环境能力，你什么都不用装：

1. 宿主自带文档能力（如 WorkBuddy）→ 直接给你 Word 文件
2. 本机已装 python-docx → 用它生成 Word 文件
3. 以上都没有（默认）→ 给你一份排版好的 Markdown 卷面，**复制进 Word / WPS 直接就能打印**

> 载体不同，**卷面质量完全一样**。Agent 不会为了出 Word 而让你去装 python-docx 或 pandoc。
> 只有你主动说「我要 .docx 文件」时，它才会给你安装命令。

---

## 许可

MIT。随便用、随便改，注明出处即可。


## 支持我

如果您觉得这个项目对您有帮助，您可以扫描以下二维码进行捐赠：
<p align="left">
  <img src=".cache/support-alipay.png" width="20%">
</p>