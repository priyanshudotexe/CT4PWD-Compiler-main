# eval.py

VALID_LOGIC = {
    "raining": "umbrella",
    "sunny": "sunglasses",
    "snowing": "coat",
    "green": "go",
    "red": "stop",
    # add more valid mappings here
}


def validate_condition(cond: dict) -> str | None:
    """
    Validate a single condition block (if/elseif/else).
    Returns an error string if invalid, otherwise None.

    For an incorrect condition->action mapping, the returned string now
    includes a second line with the corrected mapping:
        incorrect logic: red-go
        correct: red-stop
    """
    # if / elseif must map condition -> expected action
    if "if" in cond or "elseif" in cond:
        key = "if" if "if" in cond else "elseif"
        condition = cond[key]
        action = cond["action"]

        expected_action = VALID_LOGIC.get(condition)
        if expected_action is None:
            return f"unknown condition: {condition}"

        if action != expected_action:
            # Return error + suggested correct mapping on next line (dash-separated as requested)
            return f"incorrect logic: {condition}-{action}\ncorrect: {condition}-{expected_action}"

    # else: check that the else action (if present) is a known action
    elif "else" in cond:
        action = cond["else"]
        # Accept actions that appear in VALID_LOGIC values or keys, or common actions listed explicitly
        known_actions = set(VALID_LOGIC.values()) | set(VALID_LOGIC.keys()) | {"umbrella", "coat", "sunglasses", "go", "stop"}
        if action and action not in known_actions:
            return f"unknown else action: {action}"

    return None


def build_expected_sequence(conditions: list[dict]) -> list[str]:
    """
    Build the expected sequence of tokens from condition blocks.
    Example: [{'if':'red','action':'stop'}, {'elseif':'green','action':'go'}, {'else':'umbrella'}]
    -> ['if','red','stop', 'elseif','green','go', 'else','umbrella']
    """
    expected = []
    for cond in conditions:
        if "if" in cond:
            expected.extend(["if", cond["if"], cond["action"]])
        elif "elseif" in cond:
            expected.extend(["elseif", cond["elseif"], cond["action"]])
        elif "else" in cond:
            expected.append("else")
            if cond["else"]:
                expected.append(cond["else"])
    return expected


def generate_output(parsed_data: dict) -> str:
    """
    Produce final output string from parsed data.

    Behavior:
    - If there are NO condition blocks, treat this as a pattern/loop program and
      return the full expanded 'sequence' (this covers loop repetition of the whole sequence).
    - If there ARE condition blocks:
        1) validate each condition -> action mapping (now returns correction when mismatch)
        2) validate that the control/condition/action tokens appear in the expected order
        3) return the joined sequence (which may include colors and condition tokens)
    """
    sequence = parsed_data.get("sequence", []) or []
    conditions = parsed_data.get("conditions", []) or []
    colors = parsed_data.get("colors", []) or []
    loop_count = parsed_data.get("loop_count", 1) or 1

    # --- Case A: No condition blocks -> pattern/loop output ---
    if not conditions:
        # sequence is already expanded by parse_blocks for loops
        if sequence:
            return f"✓ CORRECT: {' '.join(sequence)}"
        # fallback: if parse only filled colors but not sequence
        if colors:
            return f"✓ CORRECT: {' '.join(colors * loop_count)}"
        return "No valid blocks detected."

    # --- Case B: There are condition blocks -> validate and check order ---
    # 1) Validate condition-action correctness
    for cond in conditions:
        error = validate_condition(cond)
        if error:
            return error  # may contain two lines for incorrect logic (with correction)

    # 2) Validate conditional order (compare only tokens relevant to condition blocks)
    expected_conditional_sequence = build_expected_sequence(conditions)
    if not expected_conditional_sequence:
        # defensive: if build failed somehow
        return "wrong arrangement"

    # Build a filtered list from 'sequence' that contains only tokens that are part of the expected conditional sequence.
    expected_set = set(expected_conditional_sequence)
    conditional_sequence = [tok for tok in sequence if tok in expected_set]

    if conditional_sequence != expected_conditional_sequence:
        return "wrong arrangement"

    # 3) If validation passed, return the human-readable program output (join sequence)
    if sequence:
        return f"✓ CORRECT: {' '.join(sequence)}"

    return "No valid blocks detected."