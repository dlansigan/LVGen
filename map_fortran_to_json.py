
import json
import sys

# 1. Paste Fortran values here
# From initial_values.f: tZeroX array
tZeroX = {
    "p_LV_0":      7.794860,     # mmHg
    "p_RV_0":      5.391475,     # mmHg
    "p_LV_cap_0":  7.794860,     # mmHg
    "p_RV_cap_0":  5.391475,     # mmHg
    "V_LA_0":      52.197569,    # mL
    "V_RA_0":      120.82212,    # mL
    "p_AR_SYS_0":  57.558015,    # mmHg
    "p_VEN_SYS_0": 37.934602,   # mmHg
    "p_AR_PUL_0":  26.526068,   # mmHg
    "p_VEN_PUL_0": 24.122322,   # mmHg
    "Q_AR_SYS_0":  62.030373,   # mL/s
    "Q_VEN_SYS_0": 129.672957,  # mL/s
    "Q_AR_PUL_0":  69.77572,    # mL/s
    "Q_VEN_PUL_0": 373.197717,  # mL/s
}

# From parameters.f
params = {
    # Timing
    "BPM":          84.0,
    "T_HB":         60.0 / 84.0,   # derived from BPM

    # Left atrium timing
    "time_C_LA":    0.80,
    "T_C_LA":       0.15,
    "T_R_LA":       0.80,

    # Right atrium timing
    "time_C_RA":    0.85,
    "T_C_RA":       0.10,
    "T_R_RA":       0.70,

    # Left ventricle timing
    "time_C_LV":    0.05,
    "T_C_LV":       0.25,
    "T_R_LV":       0.40,

    # Right ventricle timing
    "time_C_RV":    0.05,
    "T_C_RV":       0.25,
    "T_R_RV":       0.40,

    # Ventricular elastances
    "E_LV_act":     3.91643063,  
    "E_LV_pas":     0.09,         
    "E_RV_act":     0.42024988,
    "E_RV_pas":     0.04,

    # Atrial elastances
    "E_LA_act":     0.0,
    "E_LA_pas":     0.15,
    "E_RA_act":     0.0,
    "E_RA_pas":     0.05,

    # Rest volumes
    "V0_LA":        4.0,
    "V0_RA":        4.0,
    "V0_LV":        16.0,         
    "V0_RV":        16.0,

    # Systemic circulation
    "R_AR_SYS":     0.32878621,
    "C_AR_SYS":     1.24526319,
    "L_AR_SYS":     0.005,
    "R_VEN_SYS":    0.2348528,
    "C_VEN_SYS":    60.0,
    "L_VEN_SYS":    0.0005,

    # Pulmonary circulation
    "R_AR_PUL":     0.032,
    "C_AR_PUL":     10.0,
    "L_AR_PUL":     0.0005,
    "R_VEN_PUL":    0.035,
    "C_VEN_PUL":    16.0,
    "L_VEN_PUL":    0.0005,

    # Valve resistances
    "R_min":        0.0075,
    "R_max":        7.5,
}


# 2 Unit Scaling

def get_scaling_factors():
    print("Unit Scaling Factors")
    print("Enter 1.0 for each if no conversion is needed.")

    M = float(input("Mass scaling factor (M): ") or "1.0")
    L = float(input("Length scaling factor (L): ") or "1.0")
    T = float(input("Time scaling factor (T): ") or "1.0")

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

def build_json(scales):
    #Build the svZeroDSolver JSON config from Fortran parameters

    s = scales 

    # Simulation parameters
    simulation_parameters = {
        "coupled_simulation": True,
        "number_of_time_pts": 1000,
        "external_step_size": 0.001,
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

    # Initial conditions
    # Mapping from tZeroX Fortran variables to JSON keys
    # Some JSON keys share the same Fortran value
    p = lambda key: tZeroX[key] * s["pressure"]
    v = lambda key: tZeroX[key] * s["volume"]
    q = lambda key: tZeroX[key] * s["flow"]

    initial_condition = {
        # Chamber volumes
        "Vc:LA":                        v("V_LA_0"),
        "Vc:RA":                        v("V_RA_0"),
        "Vc:RV":                        v("V_RA_0"),  # using RV initial from tZeroX

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

        # Flows
        "flow:ART_SYS:J3":              q("Q_AR_SYS_0"),
        "flow:J3:VEN_SYS":              q("Q_AR_SYS_0"),
        "flow:VEN_SYS:J2":              q("Q_VEN_SYS_0"),
        "flow:ART_PUL:J1":              q("Q_AR_PUL_0"),
        "flow:J1:VEN_PUL":              q("Q_AR_PUL_0"),
        "flow:VEN_PUL:J0":              q("Q_VEN_PUL_0"),
    }

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
    print("Fortran genBC to svZeroDSolver JSON Mapper")


    # Get scaling factors
    scales = get_scaling_factors()

    # Build the JSON
    config = build_json(scales)

    # Write output
    output_file = "svzerod_3Dcoupling_converted.json"
    with open(output_file, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Output written to: {output_file}")
    print("Finished.")


if __name__ == "__main__":
    main()
