# Python Portfolio 使用说明

## 这个项目证明什么

它不是单纯展示“会写 Python”，而是展示你能够把语言学问题转化为：

1. 可计算的操作定义；
2. 可复现的数据处理流程；
3. 不猜测身份对应关系的数据审计；
4. 基于语料语言标注、且有质量控制的转换点识别；
5. 对不显著结果也保持透明的统计解释。

## 推荐展示顺序

先在 GitHub 首页展示 `README.md`，然后依次展示四个 notebooks：

1. 数据结构和质量问题；
2. speaker mapping 为什么不能直接合并；
3. 保守的 switch-point identification 如何工作；
4. participant-level rate 如何生成和解释。

招生官不需要运行原始受限数据，也能通过 synthetic demo 检查代码逻辑。

## 本地运行

在项目根目录打开 PowerShell：

```powershell
$env:PYTHONPATH="src"
python -m unittest discover -s tests -v
python -m bangor_miami demo --output-dir results/demo
```

如果需要使用原始 `.xlsx`：

```powershell
python -m pip install -e ".[xlsx]"
```

然后把合法下载的文件放入 `data/raw`，按照 README 的命令运行。不要把
`data/raw` 或 `results/full` 上传到 GitHub。

## 写进申请材料时的准确表述

> I developed a reproducible Python pipeline that parses CHAT metadata,
> conservatively aligns pseudonymised speakers with questionnaire records, and
> quantifies within-utterance Spanish-English transitions while preserving
> ambiguous cases for audit rather than forcing matches.

不要把这一规则流程称为 automatic code-switching detection model：它使用的
`eng`/`spa` 标签由语料提供，并不是项目训练出的自动语言识别结果。

不要写成“我证明了教育程度影响语码转换”，因为目前统计结果并不支持这一结论。
