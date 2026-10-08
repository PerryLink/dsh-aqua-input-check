# dsh-aqua-input-check — 水产养殖投入品记录齐备与休药期日期核对

`dsh-aqua-input-check` 读取一份水产养殖投入品记录——养殖场表头加每条投入品记录一行——核对这份记录自身的齐备与日期算术：每条记录是否写明塘口与养殖品种、写了名称的投入品是否记录了投入量与使用日期、使用日期是否晚于核对日、起捕是否满足记录自己写的休药期、投苗记录是否写了苗种来源与检疫证号、投入品类型是否取自你配置的取值口径、批次编号是否唯一。
它不判定养殖过程是否合规、水产品是否安全可食、用药是否恰当，也不判定是否应当处罚。

## 它回答什么问题

| 你会问 | 它怎么答 |
|---|---|
| 某条记录写了投入品名称，塘口与养殖品种两栏都空着。 | `AQ-001` 要求每条记录的 `pondNo` 与 `species` 至少填一个。它只核对两栏里填了一栏，不判断该投入品是否适用于该品种。 |
| 投入品名称填了，投入量与使用日期空着。 | `AQ-002` 在 `inputName` 已填写时要求 `inputQty` 与 `usedAt`。它只核对这两栏是否记录，不判断用量是否恰当、用药是否对症。 |
| 使用日期写成 `15/03/2026`，还有一行填的是下个月的日期。 | `AQ-003` 识别 `2026-03-15` 与 `2026-03-15 09:30` 两种写法；解析不了的 `usedAt` 按无法解析报出，晚于核对日的按未来日期报出。它不碰休药期——本规则库不内置任何休药期天数。 |
| 6 月 1 日用药、休药期栏写 20 天，6 月 15 日就起捕了，查得出来吗？ | 查得出来。`AQ-004` 拿 `usedAt`、`harvestAt` 与记录自己写的 `withdrawalDays` 相比，差多少天就报多少天。命中的含义是「按你填的休药期算，起捕早了」，不表示水产品不安全——残留是否超标需要检测结果，本插件看不到。三个字段没有都填且可解析时，本条报告 `skipped`，不会假定任何天数。 |
| 我们用的投入品类型不在清单里，也没见报出来。 | `AQ-006` 报告 `skipped`，因为本规则库不带任何投入品类型清单：`values` 出厂为空，配好之后才生效。配置之后它核对所填的 `inputType` 是否在你给的取值里。它不判断该投入品是否允许使用——那要查禁用药品清单与产品批准文号。 |
| 同一个批次编号在两行里各出现一次。 | `AQ-007` 报出重复，并指明是哪两行。比较时忽略空白字符；同一批次的多笔投入品记录各占一行是正常的，只要共用批次编号——不要把行号栏当批次编号用。没有批次编号栏时，本条报告无法执行，而不是静默通过。 |

## 依据的标准

| 文件 | 文号 | 引用它的规则 |
|---|---|---|
| 《水产养殖质量安全管理规定》 | 农业部令（现行令号与条号本次未核实） | AQ-001, AQ-002, AQ-005, AQ-007 |
| 《绿色食品 渔药使用准则》 | NY/T 755—2022（2022-07-11 发布、2022-10-01 实施；全部代替已废止的 NY/T 755—2013；属绿色食品系列标准；条号本次未取得） | AQ-003, AQ-004 |
| 本机构养殖生产管理口径（本机构配置） | 无统一标准（本条依据为本机构配置的类型口径） | AQ-006 |

**Boundary:** this plugin checks an **水产养殖投入品记录** for completeness and date arithmetic — that each record
names its pond and species, that a named input records its quantity and use date, that the use date is not in the
future, that harvesting respects the withdrawal period the record states, that stocking records its source and
quarantine certificate, that the input type comes from your vocabulary, and that batch numbers are unique. It does
**not** decide whether farming practice is compliant, whether the product is safe to eat, whether medication was
appropriate, or whether a penalty applies.

> ### ⚠️ What this plugin deliberately does not know
>
> **It ships no withdrawal periods.** `AQ-004` checks that the harvest date is at least as many days after the use
> date as **the record's own withdrawal-period column says**. So a finding means "**by the withdrawal period you
> recorded, harvest came N days early**" — never "this product is unsafe". Residue safety needs a test result,
> which this plugin cannot see. A record with no harvest date reports itself in `skipped` rather than assuming a
> period.
>
> **It ships no list of permitted or prohibited inputs.** `AQ-006` checks that the input type is one you
> configured; whether a product may lawfully be used requires the prohibited-drug list and the product's approval
> number, and this plugin does not go there.
>
> **Every `excerpt` in the rule pack says, in so many words, that the clause text was not obtained.** The regime
> lives in 《水产养殖质量安全管理规定》, NY 5361, NY/T 755 and GB 13078. The verification pass could not
> retrieve verbatim clause text, so the pack states the gap in the `excerpt` field itself and keeps every rule at
> `warn` or `info`. **When the texts are in hand, replace each `excerpt` with the real clause and raise `kind`
> to `direct`.**

## Compatibility

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-alpha.1`。**刻意不声明 `engines.dsh`**：它没有任何读取者，也无法拒装任何宿主 |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` / `both` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Install

```sh
dsh plugin --profile <name> add dsh-aqua-input-check
dsh --profile <name> --dump-config | grep 'dsh-aqua-input-check'
```

## Configuration

全部可调参数都在 `src/config.ts` 的 Schemastery schema 中，只改 `cordis.yml` 即可生效，无需改代码；逐条阈值在 `rules/` 下的规则库文件里。

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rulesFile` | string | `rules/aqua-input-check.yaml` | 规则库文件路径，相对插件包根目录 |
| `disabledRules` | string[] | `[]` | 要停用的规则 id 列表；每条都会出现在 `skipped` 中 |
| `onlyRules` | string[] | `[]` | 只执行这些规则 id；留空表示执行全部规则 |
| `skipNotes` | string | `""` | 附加到每条 `skipped` 说明后的备注 |
| `timeoutMs` | number | `120000` | 工具协作式超时预算（毫秒） |

## Material format

支持 JSON 与 YAML。完整字段示例见 [README.md](README.md#material-format)（英文主版本）。字段在读取层是可选的，由检查引擎校验，因此部分导出的材料会产生"缺项"类差异，而不是让程序崩溃。

## Rule sources

规则数据与代码分离，每条规则都带文件名、文号、按原文自身编号体系的条款号、逐字摘录与来源地址。加载期强制：摘录必须是真实引文且不少于八个字符；依据仅为原则性条款（`kind: derived-from-principle`，严重级上限 `warn`）或本机构配置（`kind: institutional-configuration`，上限 `info`）的检查不得标为 `error`。夸大依据的规则库会在加载期失败，而不会产出一份看起来很有底气的报告。

核验中确认的边界与"刻意没有作出的结论"见 [README.md](README.md#rule-sources)（英文主版本）与随包的 `rules/evidence/` 目录。

## Troubleshooting

- **插件装上了但工具不出现**：确认 `main` 指向 `lib/index.mjs` 且 `pnpm run build` 已生成该文件；`main` 写错会让加载器静默跳过该条目。
- **`dsh plugin add` 报版本不兼容**：peer 范围覆盖 `0.1.x` 与 `0.2.x`；若运行时在其之外，可显式豁免：`dsh plugin --profile <name> allow-version <包名@版本> --dsh-version <runtime> --accept-risk`
- **某条规则没有执行**：查看 `skipped` 数组，其中写明了规则 id 与原因。
- **`check` 报 `manifest-peers` 失败**：静态检查器比对的是一份早于 0.2 世代的硬编码 peer 范围；安装期的 peer 校验以运行时为准。这是 `dsh-plugin-dev` 的已知上游问题。
- **时间看起来偏移**：全部计算都是对输入字符串做墙上时钟运算，不做时区换算。

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-aqua-input-check
```

第 4 项把 `../_shared` 的共享件同步进 `src/shared/`；每次改动共享件后都要重跑。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-aqua-input-check contributors.
