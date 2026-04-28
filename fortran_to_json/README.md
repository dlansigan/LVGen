# Fortran genBC → svZeroDSolver JSON Mapper

Converts Fortran `genBC` LPN parameters into a `svZeroDSolver` JSON configuration file for 0D–3D coupled cardiac simulations.

## Requirements

```
pip install pyyaml
```

## Usage

```bash
python map_fortran_to_json.py [OPTIONS]
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--params-file` | `parameters.yaml` | Path to the YAML parameter file |
| `--pressure` | `1.0` | Pressure scaling factor (P) |
| `--length` | `1.0` | Length scaling factor (L) |
| `--time` | `1.0` | Time scaling factor (T) |
| `--time-pts` | `1000` | Number of time points |
| `--step-size` | `0.001` | External coupling step size |

The script writes its output to `svzerod_3Dcoupling_converted.json` in the current working directory.

### Minimal example (no unit conversion)

```bash
python map_fortran_to_json.py --params-file parameters.yaml
```

### Example with CGS → SI unit scaling

If your Fortran parameters are in CGS units (pressure in mmHg·dyn/cm², length in cm, time in s) and you need SI output, pass the corresponding scaling factors:

```bash
python map_fortran_to_json.py \
  --params-file parameters.yaml \
  --pressure 1333.22 \
  --length 0.01 \
  --time 1.0 \
  --time-pts 2000 \
  --step-size 0.0005
```

## Parameter file format

Edit `parameters.yaml` to match your Fortran simulation. It has two top-level sections:

```yaml
tZeroX:          # Initial conditions (from initial_values.f / tZeroX array)
  p_LV_0: 7.79  # LV pressure at t=0  [mmHg]
  ...

params:          # Model parameters (from parameters.f)
  T_HB: 0.714   # Heartbeat period [s]
  ...
```

See the bundled `parameters.yaml` for all supported keys and their units.

### Notes on `tZeroX` keys

- `V_RV_0` is not present in the original Fortran `tZeroX`. If omitted, the script falls back to `V_RA_0` for the RV initial volume and prints a warning.
- Unrecognized keys are ignored with a warning; they do not cause an error.

## Output

`svzerod_3Dcoupling_converted.json` — a ready-to-use svZeroDSolver config containing:

- Simulation parameters (coupled mode, time stepping)
- External solver coupling blocks (`LPN_inlet`, `LPN_outlet`)
- Junctions, vessels (systemic and pulmonary circuits)
- Chambers (LA, RA, RV — LV is handled by the 3D solver)
- Valves (AV, MV, PV, TV) with `PiecewiseValve` model
- Initial conditions for pressures, volumes, and flows

## Unit scaling

The script derives all physical scales from three base factors P (pressure), L (length), and T (time):

| Quantity | Scale |
|---|---|
| Pressure | P |
| Volume | L³ |
| Flow | L³ / T |
| Resistance | P·T / L³ |
| Compliance | L³ / P |
| Inductance | P·T² / L³ |
| Elastance | P / L³ |

Scaling factors are printed to stdout when the script runs.
