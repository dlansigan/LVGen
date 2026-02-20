# From https://github.com/aabrown100-git/cardiac-fsi-project/blob/main/0D_models/regazzoni_monolithic_0D/
# Parameters from Salvador 2023 code 
# For time-varying elastance chamber model 

# Conversions
kPa_to_mmHg = 7.50062

# ECG parameters
BPM = 87.0 # beats per minute
P_zero_to_peak = 0.040 # seconds
PR_interval = 0.182 # seconds
QRS_duration = 0.088 # seconds
QT_interval = 0.384 # seconds

# Electromechanical delay
EMD = 0.025 # seconds

# Contraction systole ratio:
C_S_ratio = 1./4.

# Intermediate timing parameters
t_start_A = EMD
t_end_A = PR_interval + QRS_duration
t_start_V = PR_interval + EMD
t_end_V = PR_interval + QT_interval

T_sys_A = t_end_A - t_start_A
T_sys_V = t_end_V - t_start_V

# Heart beat duration
T_HB = 60./BPM # seconds

parameters = {
    # ECG related parameters
    "BPM": BPM,  # beats per minute
    "P_zero_to_peak": P_zero_to_peak,  # seconds
    "PR_interval": PR_interval,  # seconds
    "QRS_duration": QRS_duration,  # seconds
    "QT_interval": QT_interval,  # seconds
    "EMD": EMD,  # seconds
    "C_S_ratio": C_S_ratio,  # dimensionless
    "T_HB": T_HB,    # seconds; Heart beat duration.       (MOD)
    
    # Timing parameters (for double_cosine model)
    "timing_parameters_double_cosine": {
        "t_C_LA": t_start_A,                # seconds; LA contraction start time  (Modified from ECG)
        "T_C_LA": C_S_ratio*T_sys_A,        # seconds; LA contraction duration    (Modified from ECG)
        "T_R_LA": (1-C_S_ratio)*T_sys_A,    # seconds; LA relaxation duration     (Modified from ECG)

        "t_C_RA": t_start_A,                # seconds; RA contraction start time  (Modified from ECG)
        "T_C_RA": C_S_ratio*T_sys_A,      # seconds; RA contraction duration    (Modified from ECG)
        "T_R_RA": (1-C_S_ratio)*T_sys_A,      # seconds; RA relaxation duration     (Modified from ECG)

        "t_C_LV": t_start_V,     # seconds; LV contraction start time  (Modified from ECG)
        "T_C_LV": C_S_ratio*T_sys_V,     # seconds; LV contraction duration    (Modified from ECG)
        "T_R_LV": (1-C_S_ratio)*T_sys_V,     # seconds; LV relaxation duration     (Modified from ECG)

        "t_C_RV": t_start_V,     # seconds; RV contraction start time  (Modified from ECG)
        "T_C_RV": C_S_ratio*T_sys_V,     # seconds; RV contraction duration    (Modified from ECG)
        "T_R_RV": (1-C_S_ratio)*T_sys_V,     # seconds; RV relaxation duration     (Modified from ECG)
    },

    # Timing parameters (for double_Hill model) (from Mynard_2012 Table 1)
    "timing_parameters_double_Hill": {
        "m1_LA": 1.32,  # dimensionless; LA contraction rate constant
        "m2_LA": 13.1,  # dimensionless; LA relaxation rate constant
        "tau1_LA": 0.110 * T_HB,  # seconds; LA systolic time constant
        "tau2_LA": 0.180 * T_HB,  # seconds; LA diastolic time constant
        "t_C_LA": t_start_A,  # seconds; LA contraction start time

        "m1_RA": 1.32,  # dimensionless; RA contraction rate constant
        "m2_RA": 13.1,  # dimensionless; RA relaxation rate constant
        "tau1_RA": 0.110 * T_HB,  # seconds; RA systolic time constant
        "tau2_RA": 0.180 * T_HB,  # seconds; RA diastolic time constant
        "t_C_RA": t_start_A,  # seconds; RA contraction start time

        "m1_LV": 1.32,  # dimensionless; LV contraction rate constant
        "m2_LV": 27.4,  # dimensionless; LV relaxation rate constant
        "tau1_LV": 0.269 * T_HB,  # seconds; LV systolic time constant
        "tau2_LV": 0.452 * T_HB,  # seconds; LV diastolic time constant
        "t_C_LV": t_start_V,  # seconds; LV contraction start time

        "m1_RV": 1.32,  # dimensionless; RV contraction rate constant
        "m2_RV": 27.4,  # dimensionless; RV relaxation rate constant
        "tau1_RV": 0.269 * T_HB,  # seconds; RV systolic time constant
        "tau2_RV": 0.452 * T_HB,  # seconds; RV diastolic time constant
        "t_C_RV": t_start_V,  # seconds; RV contraction start time
    },

     # Linear elastance chamber model
    "chamber_model_linear" : {
        # Ventricular elastances 
        "E_LV_act": 2.749, # mmHg mL^-1; LV elastance amplitude    (Blanco 2010 Table 5)
        "E_LV_pas": 0.09,  # mmHg mL^-1; LV elastance baseline     (Blanco 2010 Table 5)

        "E_RV_act": 0.55,  # mmHg mL^-1; RV elastance amplitude  
        "E_RV_pas": 0.05,  # mmHg mL^-1; RV elastance baseline     

        # Atrial elastances (for time-varying elastance model)
        "E_LA_act": 0.20,  # mmHg mL^-1; LA elastance amplitude     (Discrepany between Salvador 2023 paper and code. From Blanco 2010 Table 5, LA elastance should be slightly greater than RA)
        "E_LA_pas": 0.15,  # mmHg mL^-1; LA elastance baseline 

        "E_RA_act": 0.06,  # mmHg mL^-1; RA elastance amplitude     (Discrepany between Salvador 2023 paper and code)
        "E_RA_pas": 0.05,  # mmHg mL^-1; RA elastance baseline     

        # Atrial rest volumes
        "V0_LA": 4.0,   # mL
        "V0_RA": 4.0,   # mL

        # Ventricular rest volumes
        "V0_LV": 16.0,  # mL                                        (Same as LV)
        "V0_RV": 16.0,  # mL
    },


    # Systemic circulation
    "R_AR_SYS": 0.64,       # mmHg s mL^-1
    "C_AR_SYS": 1.2,        # mL mmHg^-1
    "L_AR_SYS": 0.005,      # mmHg s^2 mL^-1
    "Z_AR_SYS": 0.0,        # 
    "R_VEN_SYS": 0.32,      # mmHg s mL^-1
    "C_VEN_SYS": 60.0,      # mL mmHg^-1
    "L_VEN_SYS": 0.0005,    # mmHg s^2 mL^-1

    # Pulmonary circulation
    "R_AR_PUL": 0.032,      # mmHg s mL^-1
    "C_AR_PUL": 10.0,       # mL mmHg^-1
    "L_AR_PUL": 0.0005,     # mmHg s^2 mL^-1
    "Z_AR_PUL": 0.0,        #
    "R_VEN_PUL": 0.035,     # mmHg s mL^-1
    "C_VEN_PUL": 16.0,      # mL mmHg^-1
    "L_VEN_PUL": 0.0005,    # mmHg s^2 mL^-1

    # Valve resistances
    "R_min": 0.005,  # mmHg s mL^-1
    "R_max": 50, # mmHg s mL^-1

    # Initial conditions
    "V_LA_0": 75.60953203763704,  # mL
    "V_LV_0": 140.87115100000003, # mL
    "V_RA_0": 75.10614460364727,  # mL
    "V_RV_0": 125.16916470360742, # mL
    #"p_LA": 23.221669413038278,
    #"p_LV": 23.106673019492554,
    #"p_RA": 7.66863076513064,
    #"p_RV": 5.443734052059726,
    "p_AR_SYS_0": 99.4852044191942,       # mmHg
    "p_VEN_SYS_0": 37.02342293326058,     # mmHg
    "p_AR_PUL_0": 26.25170013422248,      # mmHg
    "p_VEN_PUL_0": 24.828991656015358,    # mmHg
    "Q_AR_SYS_0": 74.80159179163725,      # mL s^-1
    "Q_VEN_SYS_0": 91.7823852744552,      # mL s^-1
    "Q_AR_PUL_0": 47.001257211873614,     # mL s^-1
    "Q_VEN_PUL_0": 46.21258343525287      # mL s^-1
}

chambers = ["LA","RA","LV","RV"]
for chamber in chambers:
    print(chamber)
    print("\"Emax\": {},"\
        .format(parameters["chamber_model_linear"]["E_{}_act".format(chamber)]))
    print("\"Epass\": {},"\
        .format(parameters["chamber_model_linear"]["E_{}_pas".format(chamber)]))
    print("\"Vrest\": {},"\
        .format(parameters["chamber_model_linear"]["V0_{}".format(chamber)]))
    print("\"contract_start\": {},"\
        .format(parameters["timing_parameters_double_cosine"]["t_C_{}".format(chamber)]))
    print("\"contract_duration\": {},"\
        .format(parameters["timing_parameters_double_cosine"]["T_C_{}".format(chamber)]))
    print("\"relax_duration\": {},"\
        .format(parameters["timing_parameters_double_cosine"]["T_R_{}".format(chamber)]))
    print("\"T_HB\": {},"\
        .format(T_HB))
vessels = ["AR_SYS","VEN_SYS","AR_PUL","VEN_PUL"]
for vessel in vessels:
    print(vessel)
    print("\"C\": {},"\
        .format(parameters["C_{}".format(vessel)]))
    print("\"L\": {},"\
        .format(parameters["L_{}".format(vessel)]))
    print("\"R_poiseuille\": {},"\
        .format(parameters["R_{}".format(vessel)]))