# Main mapping
INP_TO_XML_MAP = {

    # Top-level scalars  →  GeneralSimulationParameters children
    "Number of spatial dimensions":          "GeneralSimulationParameters/Number_of_spatial_dimensions",
    "Number of time steps":                  "GeneralSimulationParameters/Number_of_time_steps",
    "Time step size":                        "GeneralSimulationParameters/Time_step_size",
    "Continue previous simulation":          "GeneralSimulationParameters/Continue_previous_simulation",
    "Save results in folder":                "GeneralSimulationParameters/Save_results_in_folder",
    "Save results to VTK format":            "GeneralSimulationParameters/Save_results_to_VTK_format",
    "Increment in saving restart files":     "GeneralSimulationParameters/Increment_in_saving_restart_files",
    "Name prefix of saved VTK files":        "GeneralSimulationParameters/Name_prefix_of_saved_VTK_files",
    "Increment in saving VTK files":         "GeneralSimulationParameters/Increment_in_saving_VTK_files",
    "Start saving after time step":          "GeneralSimulationParameters/Start_saving_after_time_step",
    "Save averaged results":                 "GeneralSimulationParameters/Save_averaged_results",
    "Spectral radius of infinite time step": "GeneralSimulationParameters/Spectral_radius_of_infinite_time_step",
    "Searched file name to trigger stop":    "GeneralSimulationParameters/Searched_file_name_to_trigger_stop",
    "Simulation requires remeshing":         "GeneralSimulationParameters/Simulation_requires_remeshing",
    "Verbose":                               "GeneralSimulationParameters/Verbose",
    "Warning":                               "GeneralSimulationParameters/Warning",
    "Debug":                                 "GeneralSimulationParameters/Debug",

    # Add_mesh block
    "Add mesh": {
        "_xml_tag":  "Add_mesh",
        "_xml_attr": ("name", "_value"),   # <Add_mesh name="ventricle">

        "Mesh file path":    "Mesh_file_path",
        "Mesh scale factor": "Mesh_scale_factor",
        "Domain":            "Domain",       # integer domain-id leaf

        # Add_face sub-block
        "Add face": {
            "_xml_tag":  "Add_face",
            "_xml_attr": ("name", "_value"),   # <Add_face name="wall">

            "Face file path": "Face_file_path",
        },
    },

    # Add_URIS_mesh block  (one per valve; both MV and AV follow this schema)
    "Add URIS mesh": {
        "_xml_tag":  "Add_URIS_mesh",
        "_xml_attr": ("name", "_value"),   # <Add_URIS_mesh name="MV">

        "Mesh scale factor":         "Mesh_scale_factor",
        "Thickness":                 "Thickness",
        "Resistance":                "Resistance",
        # Closed_thickness and Closed_resistance have no .inp counterpart;
        # injected from XML_ONLY_DEFAULTS in the converter.
        "Positive flow normal file": "Positive_flow_normal_file_path",   # name change

        # Add_URIS_face sub-block
        "Add URIS face": {
            "_xml_tag":  "Add_URIS_face",
            "_xml_attr": ("name", "_value"),   # <Add_URIS_face name="CylinderValve">

            # NOTE: .inp calls this "Mesh file path" inside URIS face; XML uses
            # "Face_file_path" (same tag as regular Add_face children).
            "Mesh file path":        "Face_file_path",   # key rename

            "Open motion file path":  "Open_motion_file_path",
            "Close motion file path": "Close_motion_file_path",
        },
    },

    # Add_equation block  (repeated for FSI equation and mesh equation)
    "Add equation": {
        "_xml_tag":  "Add_equation",
        "_xml_attr": ("type", "_value"),   # <Add_equation type="FSI"> / type="mesh"

        # Equation-level solver settings
        "Coupled":        "Coupled",
        "Min iterations": "Min_iterations",
        "Max iterations": "Max_iterations",
        "Tolerance":      "Tolerance",
        "Poisson ratio":  "Poisson_ratio",   # mesh equation only

        # Domain sub-block (FSI equation only)
        # .inp: Domain: 1 { Equation: fluid  Density: ...  Viscosity: ... }
        # XML:  <Domain id="1"> <Equation>fluid</Equation> ... </Domain>
        "Domain": {
            "_xml_tag":  "Domain",
            "_xml_attr": ("id", "_value"),   # <Domain id="1">

            "Equation": "Equation",          # e.g. "fluid"
            "Density":  "Density",
            "Backflow stabilization coefficient": "Backflow_stabilization_coefficient",

            # Viscosity sub-block
            # .inp:  Viscosity: Newtonian { Value: 0.4 }
            # XML:   <Viscosity model="Constant"> <Value>0.4</Value> </Viscosity>
            # REVIEW: "Newtonian" in .inp → "Constant" in XML (svMultiPhysics rename)
            "Viscosity": {
                "_xml_tag":  "Viscosity",
                "_xml_attr": ("model", "_value"),   # model= gets "Newtonian"→"Constant"

                "Value": "Value",
            },
        },

        # Output sub-block
        # .inp:  Output: Spatial { Velocity: t  ... }
        # XML:   <Output type="Spatial"> <Velocity>true</Velocity> ... </Output>
        "Output": {
            "_xml_tag":  "Output",
            "_xml_attr": ("type", "_value"),   # <Output type="Spatial">

            "Displacement":    "Displacement",
            "Velocity":        "Velocity",
            "Pressure":        "Pressure",
            "WSS":             "WSS",
            "Vorticity":       "Vorticity",
            "Absolute_velocity": "Absolute_velocity",   # REVIEW: underscore in .inp key
            # Traction and Divergence appear in the XML reference but not in .inp —
            # omit or inject false by default in converter.
        },

        # LS (linear solver) sub-block
        # .inp:  LS type: GMRES { Max iterations: 100  Tolerance: ... }
        # XML:   <LS type="GMRES"> <Max_iterations>100</Max_iterations> ... </LS>
        # NOTE: The XML reference also includes a nested <Linear_algebra type="fsils">
        #       block with no .inp counterpart — inject with defaults in converter.
        "LS type": {
            "_xml_tag":  "LS",
            "_xml_attr": ("type", "_value"),   # <LS type="GMRES">

            "Max iterations":         "Max_iterations",
            "Tolerance":              "Tolerance",
            "Absolute tolerance":     "Absolute_tolerance",
            "Krylov space dimension": "Krylov_space_dimension",
        },

        # Couple_to_genBC sub-block
        # .inp:  Couple to genBC: I { 0D code file path: genBC.exe }
        # XML:   <Couple_to_genBC type="I"> <ZeroD_code_file_path>...</ZeroD_code_file_path>
        "Couple to genBC": {
            "_xml_tag":  "Couple_to_genBC",
            "_xml_attr": ("type", "_value"),   # <Couple_to_genBC type="I">

            "0D code file path": "ZeroD_code_file_path",   # leading digit removed
        },

        # Add_BC sub-block
        # .inp:  Add BC: inlet { Type: Neu  Time dependence: Coupled }
        # XML:   <Add_BC name="inlet"> <Type>Neu</Type> ... </Add_BC>
        "Add BC": {
            "_xml_tag":  "Add_BC",
            "_xml_attr": ("name", "_value"),   # <Add_BC name="inlet">

            "Type":            "Type",         # "Neu"/"Dir"/"Rob" — values unchanged
            "Time dependence": "Time_dependence",

            # "Temporal and spatial values file path" maps to one of two XML tags
            # depending on whether the data is spatial (nodal .dat) or time-only:
            # spatial .dat to Temporal_and_spatial_values_file_path
            # 1-D flow file to Temporal_values_file_path
            # This .inp always supplies nodal .dat files, so use the spatial version.
            "Temporal and spatial values file path": "Temporal_and_spatial_values_file_path",

            "Value":                              "Value",
            "Profile":                            "Profile",      # "Flat"/"Parabolic"
            "Zero out perimeter":                 "Zero_out_perimeter",
            "Impose flux":                        "Impose_flux",
            "Impose on state variable integral":  "Impose_on_state_variable_integral",
        },
    },
}

# Value-level transformations
# Maps .inp raw string values to the correct XML text content.
# Applied after the structural mapping above.

VALUE_TRANSFORMS = {

    # Boolean normalisation
    # .inp uses "1"/"T"/"t" for true, "0"/"F"/"f" for false
    "bool": {
        "1": "true",  "T": "true",  "t": "true",  "true":  "true",
        "0": "false", "F": "false", "f": "false",  "false": "false",
    },

    # Viscosity model rename
    "viscosity_model": {
        "Newtonian": "Constant",
        "Carreau-Yasuda": "Carreau-Yasuda",   # Confirm?
        "Cassons": "Cassons",                 # Confirm?
    },

    # BC type aliases  (values appear unchanged in XML, listed here for reference)
    "bc_type": {
        "Neumann": "Neu",    # .inp long form to XML short form
        "Dirichlet": "Dir",  # .inp long form to XML short form
        "Neu": "Neu",        # .inp short form passthrough
        "Dir": "Dir",        # .inp short form passthrough
    },

    # Time dependence aliases (values appear unchanged in XML)
    "time_dependence": {
        "Steady":   "Steady",
        "Unsteady": "Unsteady",
        "Coupled":  "Coupled",
        "General":  "General",
    },
}

# XML-only fields with no .inp counterpart

XML_ONLY_DEFAULTS = {
    # Inside <LS type="GMRES">:
    "Add_equation/LS/Linear_algebra": {
        "_xml_tag":  "Linear_algebra",
        "_xml_attr": ("type", "fsils"),    # <Linear_algebra type="fsils">
        "Preconditioner": "fsils",
    },
    # Confirm thickness?
    "Add_URIS_mesh/Closed_thickness":  "0.0",
    # Confirm closed resistance?
    "Add_URIS_mesh/Closed_resistance": "0.0",
    # Confirm resistance?
    "Add_URIS_mesh/Resistance": "1.0e5",
}


# Self-test: print a structured summary when run directly
if __name__ == "__main__":
    import pprint

    def walk(node, depth=0):
        indent = "   " * depth
        if isinstance(node, dict):
            tag  = node.get("_xml_tag", "—")
            attr = node.get("_xml_attr")
            attr_str = f"  [{attr[0]}={attr[1]}]" if attr else ""
            print(f"{indent}<{tag}>{attr_str}")
            for k, v in node.items():
                if k.startswith("_"):
                    continue
                if isinstance(v, dict):
                    print(f"{indent}  .inp '{k}'  →")
                    walk(v, depth + 2)
                else:
                    print(f"{indent}  .inp '{k}'  →  <{v}>")
        else:
            print(f"{indent}{node}")

    print("=== INP_TO_XML_MAP structure ===\n")
    for key, val in INP_TO_XML_MAP.items():
        if isinstance(val, dict):
            print(f"[block]  '{key}'  →")
            walk(val, depth=1)
            print()
        else:
            print(f"[scalar] '{key}'  →  {val}")
    print()

    print("=== VALUE_TRANSFORMS ===")
    pprint.pprint(VALUE_TRANSFORMS, sort_dicts=False)
    print()

    print("=== XML_ONLY_DEFAULTS ===")
    pprint.pprint(XML_ONLY_DEFAULTS, sort_dicts=False)



# build_uris_element
import xml.etree.ElementTree as ET


def build_uris_element(uris_inp_block: dict) -> ET.Element:
    """Convert one parsed 'Add URIS mesh' dict into an ET.Element.

    Parameters:
    uris_inp_block : dict
        One item from parse_inp()'s 'Add URIS mesh' value (or the list
        element if there are multiple valves).  Must contain '_value' for
        the mesh name.

    Returns:
    xml.etree.ElementTree.Element
        A fully-built <Add_URIS_mesh name="..."> element.
    """
    schema     = INP_TO_XML_MAP["Add URIS mesh"]
    face_schema = schema["Add URIS face"]
    bools      = VALUE_TRANSFORMS["bool"]

    # root element
    root = ET.Element("Add_URIS_mesh", name=uris_inp_block.get("_value", ""))

    # Add_URIS_face children
    faces = uris_inp_block.get("Add URIS face", [])
    if isinstance(faces, dict):       # single face — normalise to list
        faces = [faces]
    for face_block in faces:
        face_el = ET.SubElement(root, "Add_URIS_face",
                                name=face_block.get("_value", ""))
        for inp_key, xml_tag in face_schema.items():
            if inp_key.startswith("_"):
                continue
            val = face_block.get(inp_key)
            if val is not None:
                ET.SubElement(face_el, xml_tag).text = val

    # scalar leaf children (order follows the target XML)
    # Leaf keys as (inp_key, xml_tag, is_bool)
    leaf_order = [
        ("Mesh scale factor", "Mesh_scale_factor", False),
        ("Thickness",         "Thickness",          False),
    ]
    for inp_key, xml_tag, is_bool in leaf_order:
        val = uris_inp_block.get(inp_key)
        if val is not None:
            text = bools.get(val, val) if is_bool else val
            ET.SubElement(root, xml_tag).text = text

    # inject XML-only defaults if absent from .inp block
    # Resistance  (between Thickness and Positive_flow_normal_file_path)
    res_val = uris_inp_block.get("Resistance")
    ET.SubElement(root, "Resistance").text = (
        res_val if res_val is not None
        else XML_ONLY_DEFAULTS["Add_URIS_mesh/Resistance"]
    )

    # Positive_flow_normal_file_path
    pfn = uris_inp_block.get("Positive flow normal file")
    if pfn is not None:
        ET.SubElement(root, "Positive_flow_normal_file_path").text = pfn
    # Closed_thickness
    if uris_inp_block.get("Closed thickness") is None:
        ET.SubElement(root, "Closed_thickness").text = \
            XML_ONLY_DEFAULTS["Add_URIS_mesh/Closed_thickness"]
    # Closed_resistance
    if uris_inp_block.get("Closed resistance") is None:
        ET.SubElement(root, "Closed_resistance").text = \
            XML_ONLY_DEFAULTS["Add_URIS_mesh/Closed_resistance"]

    return root

# Test
if __name__ == "__main__":
    # Hardcoded example matching the structure of solver_lpn_adjusted.inp
    example_uris_block = {
        "_value": "MV",
        "Add URIS face": [
            {
                "_value": "LCC",
                "Mesh file path":        "meshes/LCC_mesh.vtu",
                "Open motion file path": "meshes/LCC_motion_open.dat",
                "Close motion file path":"meshes/LCC_motion_close.dat",
            }
        ],
        "Mesh scale factor":         "1.0",
        "Thickness":                 "0.2",
        "Resistance":                "1.0e5",
        "Positive flow normal file": "meshes/normal.dat",
        # Closed_thickness and Closed_resistance intentionally omitted
        # to exercise the XML_ONLY_DEFAULTS injection path.
    }

    elem = build_uris_element(example_uris_block)

    # Pretty-print via minidom
    import xml.dom.minidom as minidom
    raw = ET.tostring(elem, encoding="unicode")
    pretty = minidom.parseString(raw).toprettyxml(indent="  ", newl="\n")
    # Strip the <?xml ...?> declaration line for clarity
    pretty = "\n".join(pretty.splitlines()[1:])
    print("\n=== build_uris_element output ===")
    print(pretty)
