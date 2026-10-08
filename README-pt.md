# dsh-aqua-input-check — Completude do registo de insumos de aquicultura e verificação de datas do período de retirada

`dsh-aqua-input-check` lê um registo de insumos de aquicultura —o cabeçalho da exploração mais uma linha por registo de insumo— e verifica a completude e a aritmética de datas desse registo: se cada registo indica o seu tanque e a sua espécie, se um insumo com nome registado indica a sua quantidade e a sua data de utilização, se a data de utilização não é futura, se a colheita respeita o período de retirada que o próprio registo declara, se o registo de povoamento anota a sua origem e o seu número de certificado de quarentena, se o tipo de insumo vem do vocabulário que você configurar e se os números de lote são únicos.
Não decide se a prática de cultivo está em conformidade, se o produto é seguro para consumo, se a medicação foi adequada ou se é devida uma sanção.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| Um registo indica o insumo, mas deixa vazias as colunas do tanque e da espécie. | `AQ-001` exige pelo menos um de `pondNo` e `species` em cada registo. Apenas verifica que um dos dois está preenchido e não julga se esse insumo é adequado a essa espécie. |
| O nome do insumo está preenchido, mas a quantidade e a data de utilização estão vazias. | `AQ-002` exige `inputQty` e `usedAt` sempre que `inputName` esteja preenchido. Verifica que os campos estão registados, não que a dose seja adequada nem que o medicamento corresponda à doença. |
| A data de utilização está escrita como `15/03/2026` e uma linha traz a data do mês seguinte. | `AQ-003` aceita `2026-03-15` e `2026-03-15 09:30`; um `usedAt` que não consegue analisar é reportado como não analisável, e um posterior à data de verificação é reportado como data futura. Não toca no período de retirada: o pacote não inclui qualquer número de dias de retirada. |
| Tratámos a 1 de junho com 20 dias de retirada registados e colhemos a 15 de junho. Isso é detetado? | Sim. `AQ-004` compara `usedAt`, `harvestAt` e o `withdrawalDays` que o próprio registo indica, e reporta a linha com os dias em falta. Um achado significa «segundo o período de retirada que você registou, a colheita chegou antes», não que o produto seja inseguro: isso exige um resultado de resíduos que este plugin não consegue ver. Se os três campos não estiverem todos preenchidos e analisáveis, a regra reporta `skipped` em vez de presumir um período. |
| O tipo de insumo que usamos não está na lista e nada é reportado. | `AQ-006` reporta `skipped` porque o pacote não traz qualquer vocabulário de tipos de insumo: `values` está vazio até você o configurar. Depois de configurado, a regra verifica que o `inputType` registado é um dos seus valores. Não julga se esse insumo pode ser legalmente utilizado: isso exige a lista de medicamentos proibidos e o número de aprovação do produto. |
| O mesmo número de lote aparece em duas linhas. | `AQ-007` reporta a repetição e indica as duas linhas. Compara ignorando os espaços em branco; vários registos de insumo para um mesmo lote são normais desde que partilhem o número de lote: não reutilize para isso a coluna do número de linha. Sem coluna de número de lote, reporta que não pôde ser executada em vez de passar em silêncio. |

## Normas que segue

| Documento | Número | Regras que o citam |
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

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-aqua-input-check
dsh --profile <name> --dump-config | grep 'dsh-aqua-input-check'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/aqua-input-check.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-aqua-input-check
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-aqua-input-check contributors.
