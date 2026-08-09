# YAML Dependency Debugger

Finds circular dependencies in a YAML rules file. Part of the validation engine for the credit risk scoring project.

## Why

Business rules for the scoring model change a lot as things evolve, and they're not owned by devs - a business analyst edits the YAML directly. That's fine for individual field rules, but once you let non-devs define relations between fields (`relation.field`), it's easy for two or more rules to end up depending on each other in a loop, which has no valid resolution order. This script lets the analyst run a quick check on their own before the ruleset actually gets used, without needing a dev to review it first.

## Files

```
src/
  debugger_dependencias_yaml.py   # graph + DFS cycle detection
  formateador_reporte.py          # readable report
  exportar_pdf.py                 # PDF export
  wrapper_debugger.py             # CLI
tests/
  test_debugger.py
  test_formateador.py
  test_exportador_pdf.py
```

`debugger_dependencias_yaml.py` builds a graph from `relation.field` and runs DFS cycle detection (visited / in_progress / path stack) over all components. Back-edges = cycles. `eliminar_conflictos_repetidos` rotates each cycle to start at its min element so the same cycle found from different entry points doesn't get reported twice.

## Usage

From `src/`:

```bash
python wrapper_debugger.py reglas_validacion.yaml
```

No conflicts: prints `todo ok, no hay conflictos detectados`.
Conflicts: prints the report and also exports it as PDF, so the analyst can see exactly which fields are looping on each other and fix the YAML.

## Testing

From the `debugger/` root (so `src` resolves as a package):

```bash
python -m pytest
```

- `test_debugger.py` - cycle detection: no relations, linear chains, disconnected components, a simple 2-node cycle, a 3-node cycle, a node feeding into a cycle without being part of it, two independent cycles at once.
- `test_formateador.py` - report text has one "Conflicto" entry per cycle and mentions every field involved.
- `test_exportador_pdf.py` - PDF gets written to disk and isn't empty.

**Unit testing over property-based testing here:** other parts of this portfolio use Hypothesis, but the graph topologies this module needs to cover are small and easy to enumerate by hand (empty, linear, disconnected components, simple cycle, longer cycle, node feeding into a cycle, multiple independent cycles) - property-based testing doesn't add much when the input space is that constrained, and generating random graphs at scale is unnecessary CPU cost for a rule set that's never going to be huge.

## Rule format

```yaml
fields:
  campo_a:
    dtype: int
    relation:
      type: menor_o_igual
      field: campo_b
      offset: -16
```

Only `relation.field` matters for the graph, `type`/`offset` are just rule metadata.