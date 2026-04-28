#!/usr/bin/env python3
"""
validate_translation.py
Structural and content validation for a svMultiPhysics solver.xml file.

Usage:
    python validate_translation.py solver_translated.xml
"""

import sys
import xml.etree.ElementTree as ET

# Result tracking

_results = {"checks": 0, "pass": 0, "missing": 0, "invalid": 0, "warnings": 0}


def _pass(msg: str) -> None:
    print(f"  PASS    {msg}")
    _results["checks"] += 1
    _results["pass"] += 1


def _missing(msg: str) -> None:
    print(f"  MISSING {msg}")
    _results["checks"] += 1
    _results["missing"] += 1


def _invalid(msg: str) -> None:
    print(f"  INVALID {msg}")
    _results["checks"] += 1
    _results["invalid"] += 1


def _warning(msg: str) -> None:
    print(f"  WARNING {msg}")
    _results["warnings"] += 1


def _child_text(el: ET.Element, tag: str) -> str | None:
    """Return stripped text of a direct child, or None if absent/empty."""
    child = el.find(tag)
    if child is None or not child.text:
        return None
    return child.text.strip()



# CHECK 1 — Required URIS tags

REQUIRED_URIS_TAGS = [
    "Mesh_scale_factor",
    "Thickness",
    "Resistance",
    "Positive_flow_normal_file_path",
]


def check_uris_required_tags(root: ET.Element) -> None:
    print("\n CHECK 1: Required URIS tags")
    uris_meshes = root.findall("Add_URIS_mesh")
    if not uris_meshes:
        _missing("No <Add_URIS_mesh> elements found in file")
        return
    for uris in uris_meshes:
        name = uris.get("name", "<unnamed>")
        for tag in REQUIRED_URIS_TAGS:
            if uris.find(tag) is None:
                _missing(f"<Add_URIS_mesh name='{name}'> is missing <{tag}>")
            else:
                _pass(f"<Add_URIS_mesh name='{name}'> has <{tag}>")



# CHECK 2 — Required BC tags

REQUIRED_BC_TAGS = ["Type", "Time_dependence"]


def check_bc_required_tags(root: ET.Element) -> None:
    print("\n CHECK 2: Required BC tags")
    for eq in root.findall("Add_equation"):
        eq_type = eq.get("type", "<unknown>")
        for bc in eq.findall("Add_BC"):
            bc_name = bc.get("name", "<unnamed>")
            for tag in REQUIRED_BC_TAGS:
                if bc.find(tag) is None:
                    _missing(f"<Add_equation type='{eq_type}'> / "
                             f"<Add_BC name='{bc_name}'> is missing <{tag}>")
                else:
                    _pass(f"<Add_equation type='{eq_type}'> / "
                          f"<Add_BC name='{bc_name}'> has <{tag}>")



# CHECK 3 — Boolean field values

BOOL_TAGS = {
    "Coupled", "Verbose", "Warning", "Debug",
    "Continue_previous_simulation", "Save_results_to_VTK_format",
    "Save_averaged_results", "Simulation_requires_remeshing",
    "Zero_out_perimeter", "Impose_flux",
    "Impose_on_state_variable_integral", "Displacement",
    "Velocity", "Pressure", "WSS", "Vorticity", "Absolute_velocity",
}

VALID_BOOLS = {"true", "false"}


def check_bool_fields(root: ET.Element) -> None:
    print("\n CHECK 3: Boolean field values")
    for el in root.iter():
        if el.tag not in BOOL_TAGS:
            continue
        text = (el.text or "").strip()
        # Build a breadcrumb path for context
        if text in VALID_BOOLS:
            _pass(f"<{el.tag}> = '{text}'")
        else:
            _invalid(f"<{el.tag}> has non-boolean value: '{text}'")



# CHECK 4 — Numeric field values

NUMERIC_TAGS = {
    "Time_step_size", "Spectral_radius_of_infinite_time_step",
    "Density", "Tolerance", "Absolute_tolerance", "Value",
    "Mesh_scale_factor", "Thickness", "Resistance",
    "Closed_thickness", "Closed_resistance", "Poisson_ratio",
}


def check_numeric_fields(root: ET.Element) -> None:
    print("\n CHECK 4: Numeric field values")
    for el in root.iter():
        if el.tag not in NUMERIC_TAGS:
            continue
        text = (el.text or "").strip()
        try:
            float(text)
            _pass(f"<{el.tag}> = '{text}' (valid float)")
        except ValueError:
            _invalid(f"<{el.tag}> cannot be parsed as float: '{text}'")



# CHECK 5 — URIS symmetry

def check_uris_symmetry(root: ET.Element) -> None:
    print("\n CHECK 5: URIS symmetry")
    uris_meshes = root.findall("Add_URIS_mesh")
    if len(uris_meshes) < 2:
        _warning("Fewer than 2 <Add_URIS_mesh> elements — symmetry check skipped")
        return
    # Compare child tag sets pairwise across all URIS mesh blocks
    tag_sets = [
        (u.get("name", f"index-{i}"), {c.tag for c in u})
        for i, u in enumerate(uris_meshes)
    ]
    ref_name, ref_tags = tag_sets[0]
    all_symmetric = True
    for name, tags in tag_sets[1:]:
        only_in_ref  = ref_tags - tags
        only_in_this = tags - ref_tags
        if only_in_ref or only_in_this:
            all_symmetric = False
            _missing(f"ASYMMETRIC between '{ref_name}' and '{name}': "
                     f"only in {ref_name}={only_in_ref or '{}'}, "
                     f"only in {name}={only_in_this or '{}'}")
        else:
            _pass(f"<Add_URIS_mesh name='{ref_name}'> and "
                  f"<Add_URIS_mesh name='{name}'> have identical child tag sets")
    if all_symmetric and len(tag_sets) > 2:
        # All pairs symmetric
        pass



# CHECK 6 — Resistance default warning

def check_resistance_defaults(root: ET.Element) -> None:
    print("\n CHECK 6: Resistance default warning")
    for uris in root.findall("Add_URIS_mesh"):
        name = uris.get("name", "<unnamed>")
        res_text = _child_text(uris, "Resistance")
        if res_text is None:
            _warning(f"<Add_URIS_mesh name='{name}'> has no <Resistance> value "
                     "— add before running solver")
        else:
            try:
                if float(res_text) == 0.0:
                    _warning(f"<Add_URIS_mesh name='{name}'> has <Resistance> = 0.0 "
                             "— add before running solver")
                else:
                    _pass(f"<Add_URIS_mesh name='{name}'> <Resistance> = '{res_text}'")
            except ValueError:
                _invalid(f"<Add_URIS_mesh name='{name}'> <Resistance> is not numeric: "
                         f"'{res_text}'")
                _results["checks"] += 1



# Main

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python validate_translation.py solver_translated.xml")
        sys.exit(1)

    xml_path = sys.argv[1]
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as exc:
        print(f"ERROR: XML parse failed: {exc}")
        sys.exit(1)

    root = tree.getroot()
    print(f"Validating: {xml_path}")
    print(f"Root element: <{root.tag} {' '.join(f'{k}={v!r}' for k, v in root.attrib.items())}>")

    check_uris_required_tags(root)
    check_bc_required_tags(root)
    check_bool_fields(root)
    check_numeric_fields(root)
    check_uris_symmetry(root)
    check_resistance_defaults(root)

    r = _results
    print("\n" + "─" * 60)
    print(f"  Checks run : {r['checks']}")
    print(f"  PASS       : {r['pass']}")
    print(f"  MISSING    : {r['missing']}")
    print(f"  INVALID    : {r['invalid']}")
    print(f"  WARNINGS   : {r['warnings']}")
    print("─" * 60)

    if r["missing"] + r["invalid"] == 0:
        print("  Result: ALL CHECKS PASSED")
    else:
        print("  Result: ISSUES FOUND — review items above")
    sys.exit(0 if r["missing"] + r["invalid"] == 0 else 1)


if __name__ == "__main__":
    main()
