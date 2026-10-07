/**
 * dsh-aqua-input-check — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'aqua_input_check'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  /**
   * The batch identifier.
   *
   * Deliberately **not** aliased to 序号: the reader treats that column as the row's own
   * display number, so mapping it here as well would make the uniqueness check compare row
   * numbers and report every register as duplicated. A register that numbers its batches in
   * the 序号 column can alias it by adding `batchNo` to that column instead.
   */
  batchNo: ['批次编号', '批次号', '编号', 'batchNo'],
  pondNo: ['塘口编号', '塘号', '养殖单元', 'pondNo'],
  species: ['养殖品种', '品种', '物种', 'species'],
  stockingAt: ['投苗日期', '放养日期', '苗种投放日期', 'stockingAt'],
  stockingQty: ['投苗数量', '放养数量', '苗种数量', 'stockingQty'],
  stockingSize: ['苗种规格', '规格', '苗种大小', 'stockingSize'],
  stockSource: ['苗种来源', '苗种场', '来源', 'stockSource'],
  quarantineNo: ['检疫证号', '苗种检疫证明', '检疫编号', 'quarantineNo'],
  inputType: ['投入品类型', '投入品', '类型', 'inputType'],
  inputName: ['投入品名称', '产品名称', '饲料或渔药名称', 'inputName'],
  inputQty: ['投入量', '用量', '使用量', 'inputQty'],
  inputUnit: ['投入量单位', '单位', 'inputUnit'],
  usedAt: ['使用日期', '投喂日期', '用药日期', 'usedAt'],
  withdrawalDays: ['休药期天数', '休药期', '停药期', 'withdrawalDays'],
  harvestAt: ['起捕日期', '收获日期', '出塘日期', 'harvestAt'],
  dischargeAt: ['排水日期', '尾水排放日期', 'dischargeAt'],
  recordKeeper: ['记录人', '填写人', 'recordKeeper'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'items', 'batches', '批次'],
  columns: COLUMNS,
  header: {
  farm: ['farm', '养殖场名称', '生产单位'],
  site: ['site', '场址', '养殖地点'],
  area: ['area', '养殖面积', '水面面积'],
  period: ['period', '记录期间', '统计期间'],
  checkedAt: ['checkedAt', '核对日期'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '投入品名称',
  'inputName',
  '投入品类型',
  'inputType',
  '塘口编号',
  'pondNo',
  '养殖品种',
  'species',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
