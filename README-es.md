# dsh-aqua-input-check — Completitud del registro de insumos de acuicultura y verificación de fechas del periodo de retiro

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-aqua-input-check` lee un registro de insumos de acuicultura —la cabecera de la granja más una fila por registro de insumo— y comprueba la completitud y la aritmética de fechas de ese registro: que cada registro indique su estanque y su especie, que un insumo con nombre registre su cantidad y su fecha de uso, que la fecha de uso no sea futura, que la cosecha respete el periodo de retiro que el propio registro declara, que el registro de siembra anote su origen y su número de certificado de cuarentena, que el tipo de insumo provenga del vocabulario que usted configure y que los números de lote sean únicos.
No decide si la práctica de cultivo cumple la normativa, ni si el producto es apto para el consumo, ni si la medicación fue adecuada, ni si procede una sanción.

## Cómo se ve la salida

![Terminal demo of dsh-aqua-input-check: real output over its AQ-003 fixture](https://raw.githubusercontent.com/PerryLink/dsh-aqua-input-check/main/docs/assets/dsh-aqua-input-check-demo.png)

Salida real de este plugin sobre su propio fixture de prueba `AQ-003` — no es un montaje. El paquete de reglas no inventa citas, así que cada hallazgo nombra la cláusula aplicada y advierte que su texto no se obtuvo.

## Qué responde

| Usted pregunta | Qué responde |
|---|---|
| Un registro nombra el insumo, pero deja vacías las columnas del estanque y de la especie. | `AQ-001` exige al menos uno de `pondNo` y `species` en cada registro. Solo comprueba que uno de los dos esté relleno y no juzga si ese insumo es adecuado para esa especie. |
| El nombre del insumo está puesto, pero la cantidad y la fecha de uso están vacías. | `AQ-002` pide `inputQty` y `usedAt` siempre que `inputName` esté relleno. Comprueba que los campos estén registrados, no que la dosis sea adecuada ni que el medicamento corresponda a la enfermedad. |
| La fecha de uso figura como `15/03/2026` y una fila lleva la fecha del mes que viene. | `AQ-003` acepta `2026-03-15` y `2026-03-15 09:30`; un `usedAt` que no puede analizar se informa como no analizable, y uno posterior a la fecha de comprobación se informa como fecha futura. No toca el periodo de retiro: el paquete no incluye ningún número de días de retiro. |
| Tratamos el 1 de junio con 20 días de retiro registrados y cosechamos el 15 de junio. ¿Se detecta? | Sí. `AQ-004` compara `usedAt`, `harvestAt` y el `withdrawalDays` que el propio registro indica, e informa de la fila con los días que faltan. Un hallazgo significa «según el periodo de retiro que usted registró, la cosecha llegó antes», no que el producto sea inseguro: eso exige un resultado de residuos que este plugin no puede ver. Si los tres campos no están todos rellenos y analizables, la regla informa de `skipped` en lugar de suponer un periodo. |
| El tipo de insumo que usamos no está en la lista y no se informa de nada. | `AQ-006` informa de `skipped` porque el paquete no trae ningún vocabulario de tipos de insumo: `values` está vacío hasta que usted lo configure. Una vez configurado, la regla comprueba que el `inputType` guardado sea uno de sus valores. No juzga si ese insumo puede usarse legalmente: eso exige la lista de fármacos prohibidos y el número de aprobación del producto. |
| El mismo número de lote aparece en dos filas. | `AQ-007` informa de la repetición e indica las dos filas. Compara ignorando los espacios en blanco; varias entradas de insumo para un mismo lote son normales siempre que compartan el número de lote: no reutilice para ello la columna del número de fila. Si no hay columna de número de lote, informa de que no pudo ejecutarse en lugar de pasar en silencio. |

## Normas que sigue

| Documento | Número | Reglas que lo citan |
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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-aqua-input-check
dsh --profile <name> --dump-config | grep 'dsh-aqua-input-check'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/aqua-input-check.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-aqua-input-check
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-aqua-input-check contributors.
