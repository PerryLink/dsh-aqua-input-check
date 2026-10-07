import { describeTablePlugin } from './table-plugin-suite.ts'
import { Config } from '../src/config.ts'
import { parseMaterial, runCheck, SPEC } from '../src/model.ts'
import { buildView } from '../src/view.ts'
import { inject, name, resolvePackageFile, TOOL_NAME } from '../src/index.ts'

describeTablePlugin({
  name,
  inject,
  TOOL_NAME,
  resolvePackageFile,
  Config,
  rulesFile: 'rules/aqua-input-check.yaml',
  parseMaterial,
  runCheck,
  buildView,
  columnNames: SPEC.columns,
  samples: {
    good: {
          "farm": "某某水产养殖场",
          "site": "某某镇某某村",
          "area": "86 亩",
          "period": "2026 年 2—6 月",
          "rows": [
                {
                      "序号": "1",
                      "塘口编号": "T-03",
                      "养殖品种": "草鱼",
                      "投苗日期": "2026-02-20",
                      "投苗数量": "12000",
                      "苗种规格": "8 cm",
                      "苗种来源": "某某苗种场",
                      "检疫证号": "JY-2026-0031",
                      "投入品类型": "配合饲料",
                      "投入品名称": "草鱼配合饲料 2 号",
                      "投入量": "350",
                      "投入量单位": "kg",
                      "使用日期": "2026-03-01",
                      "休药期天数": "0",
                      "起捕日期": "2026-06-20",
                      "排水日期": "2026-06-25",
                      "记录人": "张工"
                }
          ]
    },
    unknownColumn: { rows: [{ 备注: '甲' }] },
  },
})
