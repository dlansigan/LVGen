import re
import sys
import pprint


def parse_inp(filepath):
    """Parse a svFSI solver.inp file into a nested Python dictionary.

    Rules:
    - Lines whose first non-whitespace character is '#' are comments → skipped.
    - 'Key: value' lines become dict entries (key and value are stripped strings).
    - A line ending in '{' (or a bare '{' on the next line) opens a nested block
      that is parsed recursively and stored as a sub-dict.
    - When the same key appears more than once inside the same block (e.g. multiple
      'Add BC' or 'Add face' entries), the values are collected into a list.
    - If a block opener carries both a name AND sub-keys  (e.g. 'Add mesh: ventricle {')
      the name is stored under the special key '_value' inside the sub-dict.
    """
    with open(filepath) as f:
        content = f.read()

    # Remove comment lines (first non-space char is '#')
    content = re.sub(r'^\s*#[^\n]*', '', content, flags=re.MULTILINE)

    # Build a flat token list: key-value strings  |  '{'  |  '}'
    tokens = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        if line == '{':
            tokens.append('{')
        elif line == '}':
            tokens.append('}')
        elif line.endswith('{'):
            body = line[:-1].strip()
            if body:
                tokens.append(body)
            tokens.append('{')
        else:
            tokens.append(line)

    idx = [0]   # mutable so nested functions can advance it

    def add_entry(d, key, val):
        """Insert key→val, converting to list on duplicate keys."""
        if key in d:
            if not isinstance(d[key], list):
                d[key] = [d[key]]
            d[key].append(val)
        else:
            d[key] = val

    def parse_block():
        result = {}
        while idx[0] < len(tokens):
            token = tokens[idx[0]]

            if token == '}':
                idx[0] += 1
                return result

            if token == '{':        # stray brace – skip
                idx[0] += 1
                continue

            # Split on the FIRST colon only
            key, _, value = token.partition(':')
            key   = key.strip()
            value = value.strip()
            idx[0] += 1

            # If the next token opens a sub-block, recurse into it
            if idx[0] < len(tokens) and tokens[idx[0]] == '{':
                idx[0] += 1         # consume '{'
                sub = parse_block()
                entry = {'_value': value, **sub} if value else sub
            else:
                entry = value

            add_entry(result, key, entry)

        return result

    return parse_block()


if __name__ == '__main__':
    path = (sys.argv[1] if len(sys.argv) > 1
            else 'LPN_test_case/solver_lpn_adjusted.inp')
    data = parse_inp(path)
    pprint.pprint(data, sort_dicts=False, width=120)
