# 教材目录 (textbooks)

## 放哪里
运行时读取的是**当前工作区**的 `./textbooks/`。

> ⚠️ 如果你把本技能安装在 `~/.workbuddy/skills/ai-kids-tutor/` 这类技能目录下，
> **不要把教材 PDF 放进技能安装目录** —— 技能升级时该目录会被覆盖。
> 请放在你实际干活的工作区里。

## 怎么放（命名规范，强制）

所有 PDF **平铺**在本目录根目录，**不建子目录**，文件名统一为：

```
科目_年级学期_版本.pdf
```

示例（科目用英文键，和 `student_profile.json` 对齐）：

```
math_七上_人教版.pdf
math_七下_人教版.pdf
chinese_七上_部编版.pdf
english_七上_外研版.pdf
```

科目键只有三个：`math` / `chinese` / `english`。
多科目、多年级、多版本的教材可以**全部堆在这个目录里**，Agent 靠文件名精确匹配，不会认错。

## 索引清单 manifest.json

本目录下应有 `manifest.json`，记录每本教材的科目/年级/学期/版本/章节。

- **你不用手写** —— Agent 首次运行时会扫描目录、按文件名自动生成。
- 手动补充 `chapters`（章节列表）是**可选**的，填了之后你说「第三章」时
  Agent 能直接校验这个章节存不存在、准确叫什么，不用翻 PDF。

## Agent 会自动下载
首次建档或出题时，如果这里没有对应教材，Agent **会自动**去开源教材库
`TapXWorld/ChinaTextbook` 下载，**不需要你手动操作**。
下载后会按上面的命名规范自动重命名并登记索引。

下载细节（目录结构、版本映射、下载通道、校验）见技能内的
`references/textbook_download_guide.md`。

## 下载失败时
Agent 会明确告诉你失败原因（网络不通 / 未检索到 / 下载超时 / 文件损坏），
并给出手动下载链接。此时你可以：

- https://github.com/TapXWorld/ChinaTextbook
  浏览器打开，按「学段 → 科目 → 版本 → 年级」找到 PDF 下载

**下载后记得按上面的规范重命名。**

> 注：小学教材单本可达 50 MB，弱网下可能超时；
> `raw.githubusercontent.com` 在国内常被阻断，Agent 会改走 `api.github.com` 通道。

## 没有教材也能用
未挂载教材时，系统会依据 `student_profile.json` 里的「版本 + 年级 + 当前章节」
及该版本公开教学大纲常识出题，并在卷头标注提示，**不会中断任务**。
