
import argparse
import json
import sys
import yaml


def load_parameters(yaml_path):
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    return data["tZeroX"], data["params"]


# 2 Unit Scaling

def get_scaling_factors(P, L, T):
    M = P * L * T**2  # back-calculated from pressure scale

    # Derived scales from dimensional analysis
    scales = {
        "pressure":    M / (L * T**2),       # [M / (L * T^2)]
        "volume":      L**3,                  # [L^3]
        "flow":        L**3 / T,              # [L^3 / T]
        "resistance":  M / (L**4 * T),        # [M / (L^4 * T)]
        "compliance":  L**4 * T**2 / M,       # [L^4 * T^2 / M]
        "inductance":  M / L**4,              # [M / L^4]
        "elastance":   M / (L**4 * T**2),     # [M / (L^4 * T^2)]
    }

    print("\nDerived scaling factors:")
    for name, val in scales.items():
        print(f"  {name:15s}: {val:.6e}")
    print()

    return scales


# 3 Build .json

def build_json(scales, n_time_pts, ext_step_size, tZeroX, params):
    #Build the svZeroDSolver JSON config from Fortran parameters

    s = scales

    simulation_parameters = {
        "coupled_simulation": True,
        "number_of_time_pts": n_time_pts,
        "external_step_size": ext_step_size,
        "output_all_cycles": True,
        "output_variable_based": True,
        "steady_initial": False,
    }

    # Boundary conditions (empty for this setup)
    boundary_conditions = []

    # External solver coupling blocks
    external_solver_coupling_blocks = [
        {
            "name": "LPN_inlet",
            "type": "FLOW",
            "location": "inlet",
            "connected_block": "DUMMY_AV",
            "periodic": False,
            "values": {
                "t": [0.0, 1.0],
                "Q": [1.0, 1.0],
            },
        },
        {
            "name": "LPN_outlet",
            "type": "FLOW",
            "location": "outlet",
            "connected_block": "DUMMY_MV",
            "periodic": False,
            "values": {
                "t": [0.0, 1.0],
                "Q": [1.0, 1.0],
            },
        },
    ]

    # Junctions
    junctions = [
        {
            "junction_name": "J0",
            "junction_type": "NORMAL_JUNCTION",
            "inlet_blocks": ["VEN_PUL"],
            "outlet_blocks": ["LA"],
        },
        {
            "junction_name": "J1",
            "junction_type": "NORMAL_JUNCTION",
            "inlet_blocks": ["ART_PUL"],
            "outlet_blocks": ["VEN_PUL"],
        },
        {
            "junction_name": "J2",
            "junction_type": "NORMAL_JUNCTION",
            "inlet_blocks": ["VEN_SYS"],
            "outlet_blocks": ["RA"],
        },
        {
            "junction_name": "J3",
            "junction_type": "NORMAL_JUNCTION",
            "inlet_blocks": ["ART_SYS"],
            "outlet_blocks": ["VEN_SYS"],
        },
    ]

    # Vessels (with unit conversions)
    vessels = [
        {
            "vessel_id": 1,
            "vessel_name": "VEN_PUL",
            "vessel_length": 10.0,
            "zero_d_element_type": "BloodVesselCRL",
            "zero_d_element_values": {
                "C": params["C_VEN_PUL"] * s["compliance"],
                "R_poiseuille": params["R_VEN_PUL"] * s["resistance"],
                "L": params["L_VEN_PUL"] * s["inductance"],
                "stenosis_coefficient": 0,
            },
        },
        {
            "vessel_id": 2,
            "vessel_name": "ART_PUL",
            "vessel_length": 10.0,
            "zero_d_element_type": "BloodVesselCRL",
            "zero_d_element_values": {
                "C": params["C_AR_PUL"] * s["compliance"],
                "R_poiseuille": params["R_AR_PUL"] * s["resistance"],
                "L": params["L_AR_PUL"] * s["inductance"],
                "stenosis_coefficient": 0,
            },
        },
        {
            "vessel_id": 3,
            "vessel_name": "VEN_SYS",
            "vessel_length": 10.0,
            "zero_d_element_type": "BloodVesselCRL",
            "zero_d_element_values": {
                "C": params["C_VEN_SYS"] * s["compliance"],
                "R_poiseuille": params["R_VEN_SYS"] * s["resistance"],
                "L": params["L_VEN_SYS"] * s["inductance"],
                "stenosis_coefficient": 0,
            },
        },
        {
            "vessel_id": 4,
            "vessel_name": "ART_SYS",
            "vessel_length": 10.0,
            "zero_d_element_type": "BloodVesselCRL",
            "zero_d_element_values": {
                "C": params["C_AR_SYS"] * s["compliance"],
                "R_poiseuille": params["R_AR_SYS"] * s["resistance"],
                "L": params["L_AR_SYS"] * s["inductance"],
                "stenosis_coefficient": 0,
            },
        },
        {
            "vessel_id": 5,
            "vessel_name": "DUMMY_AV",
            "vessel_length": 10.0,
            "zero_d_element_type": "BloodVesselCRL",
            "zero_d_element_values": {
                "C": 0.0,
                "R_poiseuille": 0.0,
                "L": 0.0,
                "stenosis_coefficient": 0,
            },
        },
        {
            "vessel_id": 6,
            "vessel_name": "DUMMY_MV",
            "vessel_length": 10.0,
            "zero_d_element_type": "BloodVesselCRL",
            "zero_d_element_values": {
                "C": 0.0,
                "R_poiseuille": 0.0,
                "L": 0.0,
                "stenosis_coefficient": 0,
            },
        },
    ]

    # Chambers (LA, RA, RV — LV is handled by 3D solver)
    T_HB = params["T_HB"]

    chambers = [
        {
            "name": "LA",
            "type": "PiecewiseCosineChamber",
            "values": {
                "Emax": params["E_LA_act"] * s["elastance"],
                "Epass": params["E_LA_pas"] * s["elastance"],
                "Vrest": params["V0_LA"] * s["volume"],
                "contract_start": params["time_C_LA"],
                "contract_duration": params["T_C_LA"],
                "relax_duration": params["T_R_LA"],
                "T_HB": T_HB,
            },
        },
        {
            "name": "RA",
            "type": "PiecewiseCosineChamber",
            "values": {
                "Emax": params["E_RA_act"] * s["elastance"],
                "Epass": params["E_RA_pas"] * s["elastance"],
                "Vrest": params["V0_RA"] * s["volume"],
                "contract_start": params["time_C_RA"],
                "contract_duration": params["T_C_RA"],
                "relax_duration": params["T_R_RA"],
                "T_HB": T_HB,
            },
        },
        {
            "name": "RV",
            "type": "PiecewiseCosineChamber",
            "values": {
                "Emax": params["E_RV_act"] * s["elastance"],
                "Epass": params["E_RV_pas"] * s["elastance"],
                "Vrest": params["V0_RV"] * s["volume"],
                "contract_start": params["time_C_RV"],
                "contract_duration": params["T_C_RV"],
                "relax_duration": params["T_R_RV"],
                "T_HB": T_HB,
            },
        },
    ]

    # Valves
    valves = [
        {
            "type": "PiecewiseValve",
            "name": "PV",
            "params": {
                "Rmax": params["R_max"] * s["resistance"],
                "Rmin": params["R_min"] * s["resistance"],
                "upstream_block": "RV",
                "downstream_block": "ART_PUL",
            },
        },
        {
            "type": "PiecewiseValve",
            "name": "TV",
            "params": {
                "Rmax": params["R_max"] * s["resistance"],
                "Rmin": params["R_min"] * s["resistance"],
                "upstream_block": "RA",
                "downstream_block": "RV",
            },
        },
        {
            "type": "PiecewiseValve",
            "name": "AV",
            "params": {
                "Rmax": params["R_max"] * s["resistance"],
                "Rmin": params["R_min"] * s["resistance"],
                "upstream_block": "DUMMY_AV",
                "downstream_block": "ART_SYS",
            },
        },
        {
            "type": "PiecewiseValve",
            "name": "MV",
            "params": {
                "Rmax": params["R_max"] * s["resistance"],
                "Rmin": params["R_min"] * s["resistance"],
                "upstream_block": "LA",
                "downstream_block": "DUMMY_MV",
            },
        },
    ]

    # Warn about unrecognized keys in tZeroX
    known_keys = {
        "p_LV_0", "p_RV_0", "p_LV_cap_0", "p_RV_cap_0",
        "V_LA_0", "V_RA_0", "V_RV_0",
        "p_AR_SYS_0", "p_VEN_SYS_0", "p_AR_PUL_0", "p_VEN_PUL_0",
        "Q_AR_SYS_0", "Q_VEN_SYS_0", "Q_AR_PUL_0", "Q_VEN_PUL_0",
    }
    for key in tZeroX:
        if key not in known_keys:
            print(f"Warning: unrecognized tZeroX key '{key}' in YAML — ignoring.")

    # Initial conditions
    # Mapping from tZeroX Fortran variables to JSON keys
    # Some JSON keys share the same Fortran value
    p = lambda key: tZeroX[key] * s["pressure"]
    v = lambda key: tZeroX[key] * s["volume"]
    q = lambda key: tZeroX[key] * s["flow"]

    # V_RV_0 was not in the original Fortran tZeroX — fall back to V_RA_0 if not provided
    v_RV = tZeroX.get("V_RV_0", tZeroX["V_RA_0"]) * s["volume"]
    if "V_RV_0" not in tZeroX:
        print("Note: V_RV_0 not found in YAML, using V_RA_0 as fallback for Vc:RV.")

    initial_condition = {
        # Chamber volumes
        "Vc:LA":                        v("V_LA_0"),
        "Vc:RA":                        v("V_RA_0"),
        "Vc:RV":                        v_RV,

        # Pressures through the LV path (inlet = aortic valve side)
        "pressure:LPN_inlet:DUMMY_AV":  p("p_LV_0"),
        "pressure:DUMMY_AV:AV":         p("p_LV_0"),
        "pressure:AV:ART_SYS":          p("p_AR_SYS_0"),
        "pressure:ART_SYS:J3":          p("p_VEN_SYS_0"),
        "pressure:J3:VEN_SYS":          p("p_VEN_SYS_0"),

        # Pressures through the RV path
        "pressure:TV:RV":               p("p_RV_0"),
        "pressure:RV:PV":               p("p_RV_0"),
        "pressure:PV:ART_PUL":          p("p_AR_PUL_0"),
        "pressure:ART_PUL:J1":          p("p_VEN_PUL_0"),
        "pressure:J1:VEN_PUL":          p("p_VEN_PUL_0"),

        # Pressures through the MV (mitral valve) path
        "pressure:MV:DUMMY_MV":         p("p_LV_0"),
        "pressure:DUMMY_MV:LPN_outlet": p("p_LV_0"),
    }

    # Flows are optional — skipped if not defined in YAML
    flow_entries = {
        "flow:ART_SYS:J3":  ("Q_AR_SYS_0",  "Q_AR_SYS_0"),
        "flow:J3:VEN_SYS":  ("Q_AR_SYS_0",  "Q_AR_SYS_0"),
        "flow:VEN_SYS:J2":  ("Q_VEN_SYS_0", "Q_VEN_SYS_0"),
        "flow:ART_PUL:J1":  ("Q_AR_PUL_0",  "Q_AR_PUL_0"),
        "flow:J1:VEN_PUL":  ("Q_AR_PUL_0",  "Q_AR_PUL_0"),
        "flow:VEN_PUL:J0":  ("Q_VEN_PUL_0", "Q_VEN_PUL_0"),
    }
    for json_key, (tZeroX_key, _) in flow_entries.items():
        if tZeroX_key in tZeroX:
            initial_condition[json_key] = q(tZeroX_key)
        else:
            print(f"Note: '{tZeroX_key}' not found in YAML — skipping {json_key}.")

    # assemble full JSON
    config = {
        "simulation_parameters": simulation_parameters,
        "boundary_conditions": boundary_conditions,
        "external_solver_coupling_blocks": external_solver_coupling_blocks,
        "junctions": junctions,
        "vessels": vessels,
        "chambers": chambers,
        "valves": valves,
        "initial condition": initial_condition,
    }

    return config


# 4 Main

def main():
    parser = argparse.ArgumentParser(description="Fortran genBC to svZeroDSolver JSON Mapper")
    parser.add_argument("--params-file", type=str,   default="parameters.yaml", help="Path to YAML parameters file (default: parameters.yaml)")
    parser.add_argument("--pressure",    type=float, default=1.0,               help="Pressure scaling factor (default: 1.0)")
    parser.add_argument("--length",      type=float, default=1.0,               help="Length scaling factor (default: 1.0)")
    parser.add_argument("--time",        type=float, default=1.0,               help="Time scaling factor (default: 1.0)")
    parser.add_argument("--time-pts",    type=int,   default=1000,              help="Number of time points (default: 1000)")
    parser.add_argument("--step-size",   type=float, default=0.001,             help="External step size (default: 0.001)")
    args = parser.parse_args()

    tZeroX, params = load_parameters(args.params_file)
    scales = get_scaling_factors(args.pressure, args.length, args.time)
    config = build_json(scales, args.time_pts, args.step_size, tZeroX, params)

    # Write output
    output_file = "svzerod_3Dcoupling_converted.json"
    with open(output_file, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Output written to: {output_file}")
    print("Finished.")


if __name__ == "__main__":
    main()
