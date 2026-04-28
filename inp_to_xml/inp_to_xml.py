#!/usr/bin/env python3
"""
inp_to_xml.py
Convert a svFSI solver.inp file to a svMultiPhysics solver.xml file.

Usage:
    python inp_to_xml.py input.inp output.xml
"""

import sys
import xml.etree.ElementTree as ET

from parse_inp import parse_inp
from inp_to_xml_map import (
    INP_TO_XML_MAP,
    VALUE_TRANSFORMS,
    XML_ONLY_DEFAULTS,
    build_uris_element,
)

BOOL_MAP    = VALUE_TRANSFORMS["bool"]
VISC_MAP    = VALUE_TRANSFORMS["viscosity_model"]
BC_TYPE_MAP = VALUE_TRANSFORMS["bc_type"]

# XML tags whose text content is truly boolean.
# Only these get the "1"/"T"/"t" → "true" / "0"/"F"/"f" → "false" transform.
# Integer and string tags (e.g. Min_iterations, Domain, Increment_in_saving_VTK_files)
# must not be transformed even though their values may be "0" or "1".
BOOL_TAGS = {
    # GeneralSimulationParameters
    "Continue_previous_simulation",
    "Save_results_to_VTK_format",
    "Convert_BIN_to_VTK_format",
    "Save_averaged_results",
    "Simulation_requires_remeshing",
    "Verbose", "Warning", "Debug",
    # Add_equation
    "Coupled",
    # Output fields
    "Velocity", "Pressure", "Traction", "Vorticity", "Divergence",
    "WSS", "Displacement", "Absolute_velocity",
    # Add_BC
    "Impose_flux", "Zero_out_perimeter", "Impose_on_state_variable_integral",
}

_stats = {"mapped": 0, "warnings": 0}


# Helpers

def _warn(msg: str) -> None:
    print(f"WARNING: unmapped .inp key: {msg}", file=sys.stderr)
    _stats["warnings"] += 1


def _transform(val: str, xml_tag: str = "") -> str:
    """Apply value-level transforms in priority order."""
    if xml_tag in BOOL_TAGS and val in BOOL_MAP:
        return BOOL_MAP[val]
    if xml_tag == "Type" and val in BC_TYPE_MAP:
        return BC_TYPE_MAP[val]
    return val


def _sub(parent: ET.Element, tag: str, val: str, xml_tag: str = "") -> ET.Element:
    """Create a child element with transformed, space-padded text."""
    el = ET.SubElement(parent, tag)
    el.text = f" {_transform(val, xml_tag or tag)} "
    _stats["mapped"] += 1
    return el



# Generic recursive builder

def build_element(parent_el: ET.Element, inp_block: dict, schema: dict) -> None:
    """
    Walk inp_block and schema simultaneously, appending child elements to
    parent_el.

    Rules
    -----
    - Scalar entry  (schema value is a str)  → create leaf element.
    - Block entry   (schema value is a dict) → create container element,
      set identifying attribute, recurse.
    - Keys starting with '_' in the schema are structural — skipped.
    - .inp keys absent from the schema trigger a WARNING.
    - .inp keys absent from inp_block are silently skipped.
    """
    if not isinstance(inp_block, dict):
        return

    # Warn about any .inp keys the schema doesn't cover
    schema_keys = {k for k in schema if not k.startswith("_")}
    for inp_key in inp_block:
        if inp_key == "_value":
            continue
        if inp_key not in schema_keys:
            _warn(f"'{inp_key}' — skipping")

    for inp_key, xml_target in schema.items():
        if inp_key.startswith("_"):
            continue

        val = inp_block.get(inp_key)
        if val is None:
            continue

        if isinstance(xml_target, str):
            # Scalar leaf
            items = val if isinstance(val, list) else [val]
            for item in items:
                _sub(parent_el, xml_target, item)

        elif isinstance(xml_target, dict):
            # Container block
            xml_tag       = xml_target["_xml_tag"]
            xml_attr_spec = xml_target.get("_xml_attr")

            items = val if isinstance(val, list) else [val]
            for item in items:
                attrs = {}
                if xml_attr_spec:
                    attr_name, attr_source = xml_attr_spec
                    attr_val = (item.get("_value", "")
                                if attr_source == "_value" else attr_source)
                    if attr_name == "model":
                        attr_val = VISC_MAP.get(attr_val, attr_val)
                    attrs[attr_name] = attr_val

                child_el = ET.SubElement(parent_el, xml_tag, **attrs)
                _stats["mapped"] += 1
                build_element(child_el, item, xml_target)



# Section builders


def build_general_params(root: ET.Element, inp_dict: dict) -> None:
    """Create <GeneralSimulationParameters> from all top-level scalar keys."""
    gp = ET.SubElement(root, "GeneralSimulationParameters")
    for inp_key, path in INP_TO_XML_MAP.items():
        if not isinstance(path, str):
            continue
        if not path.startswith("GeneralSimulationParameters/"):
            continue
        val = inp_dict.get(inp_key)
        if val is None:
            continue
        xml_tag = path.split("/", 1)[1]
        _sub(gp, xml_tag, val)


def build_mesh_block(root: ET.Element, mesh_block: dict) -> None:
    """Create <Add_mesh name="..."> with Add_face and scalar children."""
    schema  = INP_TO_XML_MAP["Add mesh"]
    mesh_el = ET.SubElement(root, "Add_mesh", name=mesh_block.get("_value", ""))
    _stats["mapped"] += 1

    # Add_face children first (matches reference XML ordering)
    faces = mesh_block.get("Add face", [])
    if isinstance(faces, dict):
        faces = [faces]
    face_schema = schema["Add face"]
    for face in faces:
        face_el = ET.SubElement(mesh_el, "Add_face", name=face.get("_value", ""))
        _stats["mapped"] += 1
        build_element(face_el, face, face_schema)

    # Scalar children
    for inp_key in ("Mesh file path", "Mesh scale factor", "Domain"):
        val = mesh_block.get(inp_key)
        if val is not None:
            _sub(mesh_el, schema[inp_key], val)

    # Warn about anything else
    handled = {"_value", "Add face", "Mesh file path", "Mesh scale factor", "Domain"}
    for k in mesh_block:
        if k not in handled:
            _warn(f"'{k}' in mesh block — skipping")


def build_equation_block(root: ET.Element, eq_block: dict) -> None:
    """Create <Add_equation type="..."> with all sub-blocks."""
    schema  = INP_TO_XML_MAP["Add equation"]
    eq_type = eq_block.get("_value", "")
    eq_el   = ET.SubElement(root, "Add_equation", type=eq_type)
    _stats["mapped"] += 1

    # Simple scalars 
    for inp_key in ("Coupled", "Min iterations", "Max iterations",
                    "Tolerance", "Poisson ratio"):
        val = eq_block.get(inp_key)
        if val is not None:
            _sub(eq_el, schema[inp_key], val)

    # Domain sub-block (present in FSI equation)
    # .inp: Domain: 1 { Equation: fluid  Density: ...  Viscosity: ... }
    # XML:  <Domain id="1"> <Density>...</Density> ... </Domain>
    if "Domain" in eq_block:
        domain_schema = schema["Domain"]
        items = eq_block["Domain"]
        if isinstance(items, dict):
            items = [items]
        for item in items:
            domain_el = ET.SubElement(eq_el, "Domain", id=item.get("_value", ""))
            _stats["mapped"] += 1
            build_element(domain_el, item, domain_schema)

    # Output sub-block
    if "Output" in eq_block:
        output_schema = schema["Output"]
        items = eq_block["Output"]
        if isinstance(items, dict):
            items = [items]
        for item in items:
            out_el = ET.SubElement(eq_el, "Output", type=item.get("_value", ""))
            _stats["mapped"] += 1
            build_element(out_el, item, output_schema)

    # LS sub-block 
    # .inp: LS type: GMRES { ... }
    # XML:  <LS type="GMRES"> <Linear_algebra type="fsils">...</Linear_algebra> ... </LS>
    if "LS type" in eq_block:
        ls_schema = schema["LS type"]
        ls_block  = eq_block["LS type"]
        ls_el     = ET.SubElement(eq_el, "LS", type=ls_block.get("_value", ""))
        _stats["mapped"] += 1

        # Inject Linear_algebra default — no .inp counterpart
        la_def = XML_ONLY_DEFAULTS["Add_equation/LS/Linear_algebra"]
        la_el  = ET.SubElement(ls_el, "Linear_algebra",
                               type=la_def["_xml_attr"][1])
        ET.SubElement(la_el, "Preconditioner").text = f" {la_def['Preconditioner']} "

        build_element(ls_el, ls_block, ls_schema)

    # Couple_to_genBC sub-block
    if "Couple to genBC" in eq_block:
        genbc_schema = schema["Couple to genBC"]
        genbc_block  = eq_block["Couple to genBC"]
        genbc_el = ET.SubElement(eq_el, "Couple_to_genBC",
                                 type=genbc_block.get("_value", ""))
        _stats["mapped"] += 1
        build_element(genbc_el, genbc_block, genbc_schema)

    # Add_BC sub-blocks
    bcs = eq_block.get("Add BC", [])
    if isinstance(bcs, dict):
        bcs = [bcs]
    bc_schema = schema["Add BC"]
    for bc in bcs:
        bc_el = ET.SubElement(eq_el, "Add_BC", name=bc.get("_value", ""))
        _stats["mapped"] += 1
        build_element(bc_el, bc, bc_schema)

    # Warn about anything not handled above
    handled = {
        "_value", "Coupled", "Min iterations", "Max iterations",
        "Tolerance", "Poisson ratio", "Domain", "Output",
        "LS type", "Couple to genBC", "Add BC",
    }
    for k in eq_block:
        if k not in handled:
            _warn(f"'{k}' in equation block — skipping")



# Main


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python inp_to_xml.py input.inp output.xml")
        sys.exit(1)

    inp_path, xml_path = sys.argv[1], sys.argv[2]
    inp_dict = parse_inp(inp_path)

    # Root element
    root = ET.Element("svMultiPhysicsFile", version="0.1")

    # Sections
    build_general_params(root, inp_dict)

    meshes = inp_dict.get("Add mesh", [])
    if isinstance(meshes, dict):
        meshes = [meshes]
    for mesh in meshes:
        build_mesh_block(root, mesh)

    # Add_URIS_mesh elements are siblings of Add_mesh in the XML
    uris_meshes = inp_dict.get("Add URIS mesh", [])
    if isinstance(uris_meshes, dict):
        uris_meshes = [uris_meshes]
    for uris_block in uris_meshes:
        root.append(build_uris_element(uris_block))

    equations = inp_dict.get("Add equation", [])
    if isinstance(equations, dict):
        equations = [equations]
    for eq in equations:
        build_equation_block(root, eq)

    # Pretty-print and write 
    ET.indent(root, space="  ")
    xml_decl = '<?xml version="1.0" encoding="UTF-8" ?>\n'
    body     = ET.tostring(root, encoding="unicode")
    with open(xml_path, "w", encoding="utf-8") as fh:
        fh.write(xml_decl + body + "\n")

    # Summary 
    print(f"\nWrote: {xml_path}")
    print(f"  {_stats['mapped']} parameters mapped")
    print(f"  {_stats['warnings']} warnings issued")


if __name__ == "__main__":
    main()
