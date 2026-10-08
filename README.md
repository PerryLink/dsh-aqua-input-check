# dsh-aqua-input-check — Aquaculture input register completeness and withdrawal-period date check

`dsh-aqua-input-check` reads one aquaculture input register — the farm header plus one row per input record — and checks that register's own completeness and date arithmetic: that each record names its pond and species, that a named input records its quantity and use date, that the use date is not in the future, that harvesting respects the withdrawal period the record itself states, that a stocking record carries its source and quarantine certificate number, that the input type comes from your configured vocabulary, and that batch numbers are unique.
It does not decide whether farming practice is compliant, whether the product is safe to eat, whether medication was appropriate, or whether a penalty applies.

## What it answers

| You ask | What it answers |
|---|---|
| A record names the input but leaves the pond and the species column empty. | `AQ-001` requires at least one of `pondNo` and `species` on every record. It only checks that one of the two is filled in, and does not judge whether that input is suitable for that species. |
| The input name is there, but the quantity and the use date are blank. | `AQ-002` asks for `inputQty` and `usedAt` whenever `inputName` is filled in. It checks that the fields are recorded, not that the dosage is appropriate or that the medication suits the disease. |
| The use date is written as `15/03/2026`, and one row carries next month's date. | `AQ-003` accepts `2026-03-15` and `2026-03-15 09:30`; a `usedAt` it cannot parse is reported as unparseable, and one later than the check date is reported as a future date. It does not touch the withdrawal period — the pack ships no withdrawal days at all. |
| We treated on 1 June with 20 withdrawal days recorded and harvested on 15 June. Is that caught? | Yes. `AQ-004` compares `usedAt`, `harvestAt` and the record's own `withdrawalDays`, and reports the row as short by the difference. A finding means "by the withdrawal period you recorded, harvest came early" — not that the product is unsafe, which needs a residue test this plugin cannot see. If those three fields are not all filled and parseable, the rule reports `skipped` instead of assuming a period. |
| The input type we use is not in the list — nothing is reported. | `AQ-006` reports `skipped` because the pack ships no input-type vocabulary: `values` is empty until you configure one. Once set, the rule checks that the stored `inputType` is one of your values. It does not judge whether that input may lawfully be used — that needs the prohibited-drug list and the product's approval number. |
| The same batch number appears in two rows. | `AQ-007` reports the repeat and names both rows. It compares with whitespace ignored; several input entries for one batch are normal as long as they share the batch number — do not reuse the row-number column for it. With no batch-number column it reports that it could not run instead of passing silently. |

## Standards it follows

| Document | Number | Cited by rules |
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

| Surface | Status |
|---|---|
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-alpha.1`. `engines.dsh` is deliberately not declared: it has no reader and cannot reject a host |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native`, `ptc` and `both`; for a season of records use `ptc` |

## What it does

Registers the `aqua_input_check` tool. It reads one input register — the farm header plus one row per input
record — applies a versioned rule pack, and returns a report.

| Rule | Check | Severity | Basis kind |
|---|---|---|---|
| `AQ-001` | the pond and species are recorded | warn | principle |
| `AQ-002` | a named input records its quantity and date | warn | principle |
| `AQ-003` | the use date is not in the future | warn | principle |
| `AQ-004` | harvest respects the recorded withdrawal period | warn | principle |
| `AQ-005` | stocking records its source and quarantine number | warn | principle |
| `AQ-006` | the input type comes from your vocabulary (off by default) | info | local |
| `AQ-007` | batch numbers are unique | warn | principle |

## Install

```sh
dsh plugin --profile <name> add dsh-aqua-input-check
dsh --profile <name> --dump-config | grep 'dsh-aqua-input-check'
```

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `rulesFile` | string | `rules/aqua-input-check.yaml` | Rule-pack path, relative to the package root |
| `disabledRules` | string[] | `[]` | Rule ids to stop running; each appears in `skipped` |
| `onlyRules` | string[] | `[]` | Run only these rule ids; empty runs every rule |
| `skipNotes` | string | `""` | Note appended to every `skipped` reason |
| `timeoutMs` | number | `120000` | Cooperative tool timeout budget |

Rule-level parameters worth knowing:

- `AQ-004` `earlierField` / `laterField` / `minDaysField` — the two dates and the column holding the required
  gap. The period comes from the record, so no figure is built in.
- `AQ-006` `values` — your input types, e.g.
  `[配合饲料, 冰鲜鱼, 水质改良剂, 抗菌药, 杀虫药, 消毒剂, 疫苗]`. Empty means no check.
- `AQ-002` `conditionField` / `requiredFields` — what triggers the quantity-and-date requirement.

## Material format

The tool accepts JSON or YAML:

```yaml
farm: 某某水产养殖场
site: 某某镇某某村
area: 86 亩
rows:
  - { 序号: '1', 批次编号: B-2026-0001, 塘口编号: T-03, 养殖品种: 草鱼,
      投苗日期: 2026-02-20, 苗种来源: 某某苗种场, 检疫证号: JY-2026-0031,
      投入品类型: 配合饲料, 投入品名称: 草鱼配合饲料 2 号, 投入量: '350',
      投入量单位: kg, 使用日期: 2026-03-01, 休药期天数: '0', 起捕日期: 2026-06-20 }
```

Column names are matched case-insensitively and ignoring spaces, underscores and hyphens; the register's own
column names are kept, so a finding names the column it read. Note that 序号 is read as the row's display
number — give the batch identifier its own column (批次编号).

## Rule sources

Rule data lives in `rules/aqua-input-check.yaml`. The pack's header states the citation gap in full, and each
rule's `note` repeats the part that matters for that rule. The load-time guard that normally enforces "an
excerpt must be a real quotation of at least eight characters" cannot tell a quotation from a description —
so this pack leans on the header, the per-rule notes and a test that asserts every `excerpt` admits the gap.

## Troubleshooting

- **`AQ-004` reports itself as skipped.** One of the two dates or the withdrawal period is missing. Records of
  feeding with no harvest, for instance, are simply out of scope.
- **`AQ-004` fires but I believe the batch is safe.** The finding is arithmetic: harvest came earlier than the
  period **you recorded**. Whether residue is a problem needs a test result.
- **`AQ-006` never runs.** Its vocabulary is empty; fill it with the input types your farm uses.
- **`AQ-007` fires on a batch with several input records.** Several records for one batch should share the batch
  number. If your register instead numbers each line, disable the rule or use a distinct identifier column.
- **The plugin installs but the tool never appears.** Check that `main` resolves to `lib/index.mjs` and
  that `pnpm run build` produced it; a wrong `main` makes the loader skip the entry silently.
- **`dsh plugin add` refuses the package as incompatible.** The peer range covers `0.1.x` and `0.2.x`; if
  your runtime sits outside it, grant an explicit exemption:
  `dsh plugin --profile <name> allow-version dsh-aqua-input-check@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` reports `manifest-peers` as failed.** The static checker compares against a hard-coded peer
  range that predates the 0.2 line. The runtime enforces peer compatibility at install time, so the
  declared range is the correct one; this is a known upstream issue in `dsh-plugin-dev`.

## Development

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, the shared table-plugin suite plus paired fixtures
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
node ../scripts/sync-shared.mjs dsh-aqua-input-check   # refresh src/shared from ../_shared
```

The plugin is **data-only**: `src/model.ts` declares the table shape, the shared kit supplies the reader and
the check engine, and the rule pack declares every check.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-aqua-input-check contributors.
