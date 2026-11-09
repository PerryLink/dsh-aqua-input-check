import { describe, expect, it } from 'vitest'
import { needsIngest, readTableDocument } from '../src/ingest.ts'
import { SPEC } from '../src/model.ts'

describe('optional document ingest', () => {
  it('recognises the document extensions the plugin advertises', () => {
    for (const file of ['a.docx', 'a.xlsx', 'a.xlsm', 'a.csv', 'a.tsv', 'A.DOCX']) {
      expect(needsIngest(file), file).toBe(true)
    }
    for (const file of ['a.json', 'a.yaml', 'a.yml', 'a.txt']) {
      expect(needsIngest(file), file).toBe(false)
    }
  })

  it('fails with an install hint, not a YAML error, when dsh-table-ingest is absent', async () => {
    const available = await import('dsh-table-ingest/api').then(() => true, () => false)
    if (available) return // The optional package is installed in this workspace; covered by the docx probe.
    await expect(readTableDocument('/tmp/does-not-exist.docx', SPEC)).rejects.toThrow(/dsh-table-ingest/)
  })
})
