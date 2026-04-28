# svFSI `.inp` → svMultiPhysics `.xml` Converter

Converts a legacy `svFSI` solver configuration file (`solver.inp`) to the `svMultiPhysics` XML format (`solver.xml`), and validates the output.

## Scripts

| Script | Role |
|---|---|
| `inp_to_xml.py` | Main converter — reads `.inp`, writes `.xml` |
| `parse_inp.py` | Parser — tokenises a `.inp` file into a Python dict |
| `inp_to_xml_map.py` | Mapping table — defines key/value translations between formats |
| `validate_translation.py` | Validator — checks the converted `.xml` for structural correctness |

## Requirements

Python 3.9+ (uses `str | None` union syntax). No third-party packages required.

## Usage

### Step 1 — Convert

```bash
python inp_to_xml.py input.inp output.xml
```

Example:

```bash
python inp_to_xml.py solver_lpn_adjusted.inp solver_translated.xml
```

The script prints a summary on completion:

```
Wrote: solver_translated.xml
  84 parameters mapped
  0 warnings issued
```

Any `.inp` keys not covered by the mapping table are printed to stderr as warnings — they are skipped but do not abort conversion.

### Step 2 — Validate

```bash
python validate_translation.py output.xml
```

Example:

```bash
python validate_translation.py solver_translated.xml
```

The validator runs six checks and prints a pass/fail summary:

| Check | What it verifies |
|---|---|
| 1 — Required URIS tags | Each `<Add_URIS_mesh>` has all mandatory child tags |
| 2 — Required BC tags | Each `<Add_BC>` has `<Type>` and `<Time_dependence>` |
| 3 — Boolean fields | All boolean-valued tags contain `true` or `false` |
| 4 — Numeric fields | All numeric-valued tags can be parsed as floats |
| 5 — URIS symmetry | All `<Add_URIS_mesh>` blocks have identical child tag sets |
| 6 — Resistance defaults | Warns if any `<Resistance>` is missing or zero |

Exit code is `0` if all checks pass, `1` if any MISSING or INVALID issues are found.

## Key translations

### Boolean values

`.inp` values `1`, `T`, `t` → XML `true`; `0`, `F`, `f` → XML `false`.

### Viscosity model rename

| `.inp` value | XML `model` attribute |
|---|---|
| `Newtonian` | `Constant` |
| `Carreau-Yasuda` | `Carreau-Yasuda` |
| `Cassons` | `Cassons` |

### BC type aliases

| `.inp` value | XML value |
|---|---|
| `Neumann` | `Neu` |
| `Dirichlet` | `Dir` |
| `Neu` / `Dir` | passed through unchanged |

### XML-only defaults (no `.inp` counterpart)

| XML path | Default value |
|---|---|
| `Add_equation/LS/Linear_algebra[@type]` | `fsils` |
| `Add_equation/LS/Linear_algebra/Preconditioner` | `fsils` |
| `Add_URIS_mesh/Resistance` | `1.0e5` |
| `Add_URIS_mesh/Closed_thickness` | `0.0` |
| `Add_URIS_mesh/Closed_resistance` | `0.0` |

These are injected automatically when the corresponding `.inp` key is absent.

## Inspecting the mapping table

Run `inp_to_xml_map.py` directly to print a structured summary of all key/value mappings:

```bash
python inp_to_xml_map.py
```

Run `parse_inp.py` on a `.inp` file to inspect the parsed dictionary:

```bash
python parse_inp.py solver_lpn_adjusted.inp
```
