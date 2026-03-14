import json
import argparse
import os

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=str)
    args = parser.parse_args()

    fn = os.path.join(args.case,"svzerod_3Dcoupling_base.json")
    save_fn = os.path.join(args.case,"svzerod_3Dcoupling.json")
    with open(fn,"r") as file:
        params = json.load(file)

    # Conversion factors: multiply these scales to 0D units to get 3D units
    # i.e., scale: 0D units -> 3D units
    pscale = 1333.22 # mmHg -> dyn/cm^2 
    lscale = 1 # cm -> cm; mL -> mL
    tscale = 1 # s -> s

    ### CHAMBERS ###
    for i,chamber in enumerate(params["chambers"]):
        # Elastance
        chamber["values"]["Emax"] *= pscale/lscale**3 # mmHg/mL
        chamber["values"]["Epass"] *= pscale/lscale**3

        # Volume
        chamber["values"]["Vrest"] *= lscale**3 # mL

        # Activation 
        chamber["activation_function"]["contract_start"] *= tscale # s
        chamber["activation_function"]["relax_start"] *= tscale
        chamber["activation_function"]["contract_duration"] *= tscale
        chamber["activation_function"]["relax_duration"] *= tscale

        params["chambers"][i] = chamber


    ### VESSELS ###
    for i,vessel in enumerate(params["vessels"]):
        # Capacitance
        vessel["zero_d_element_values"]["C"] *= lscale**3/pscale # mL/mmHg
        # Resistance
        vessel["zero_d_element_values"]["R_poiseuille"] *= pscale*tscale/lscale**3 # mmHg-s/mL
        # Inductance
        vessel["zero_d_element_values"]["L"] *= pscale*tscale**2/lscale**3# mmHg-s^2/mL

        params["vessels"][i] = vessel

    ### VALVES ###
    for i,valve in enumerate(params["valves"]):
        # Resistance
        valve["params"]["Rmax"] *= pscale*tscale/lscale**3 # mmHg-s/mL
        valve["params"]["Rmin"] *= pscale*tscale/lscale**3 # mmHg-s/mL

        params["valves"][i] = valve

    ### INITIAL CONDITIONS
    for ic in params["initial_condition"]:
        q = ic.split(":")[0]
        if q == "Vc":
            params["initial_condition"][ic] *= lscale**3 # mL
        elif q == "pressure":
            params["initial_condition"][ic] *= pscale # mmHg
        elif q == "flow":
            params["initial_condition"][ic] *= lscale**3/tscale #mL/s

    # Save new JSON
    with open(save_fn, "w") as f:
        json.dump(params, f, indent=4)