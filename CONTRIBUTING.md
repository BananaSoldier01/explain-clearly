# 参与贡献

谢谢你愿意改进 explain-clearly。本仓库用中文协作。

## 先看边界

- 两条入口保持不变：用户明确要理解；或普通回答里出现可能不熟悉、又影响理解的专业内容。术语按读者背景展开，避免逐词科普。
- 图和交互 HTML 先说明能看清什么，得到对应同意后再生成。只同意图，不等于同意 HTML。
- 改这些规则前，请先开 Issue，附上具体失败例子。不要顺手放宽或收紧。
- 单次观察不能写成跨 Agent 稳定触发或理解增益。已有范围见 [验证记录](VERIFICATION.md)。

## 本地检查

在仓库根运行：

```sh
python3 -B tests/check_package.py
python3 -m unittest discover -s tests -v
```

`examples/interactive.html` 与 `skills/explain-clearly/assets/explainer.html` 须保持内容一致。日常安装包用 `./scripts/pack-skill.sh` 生成，说明见 [USAGE.md](USAGE.md)。

## 反馈

用 Issue 即可：

- [触发失败](https://github.com/BananaSoldier01/explain-clearly/issues/new?template=trigger-failure.md)
- [过度科普](https://github.com/BananaSoldier01/explain-clearly/issues/new?template=over-explanation.md)
- [HTML 授权问题](https://github.com/BananaSoldier01/explain-clearly/issues/new?template=html-authorization.md)

请写下原话、实际回答和宿主名称。一次会话只说明该次观察。
