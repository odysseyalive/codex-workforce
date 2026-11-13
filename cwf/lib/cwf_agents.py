"""Codex custom-agent TOML: parse a handbook, render it, and prove the render parses back.

One writer for every `.codex/agents/*.toml` this package produces. `scripts/build-skills`
renders the package's own agents with it, and `cwf/bin/cwf-org` renders a project's
employees with it, so an escaping rule fixed here is fixed for both.

A handbook is markdown with a `---` frontmatter block (`name`, `description`, and optionally
`model`, `effort` / `model_reasoning_effort`, `tools`, `disallowedTools`), the shape upstream's
`AGENT.md` files and `cwf/agents/cwf-implementer.md` already have. The body is carried into
`developer_instructions` byte for byte: backslashes, triple quotes and control characters are
escaped for TOML and come back unchanged when Codex parses the file.
"""
import json
import re
import tomllib

# The effort values Codex accepts for `model_reasoning_effort`.
EFFORTS = ("minimal", "low", "medium", "high", "xhigh")


class AgentError(ValueError):
    """A handbook or a render that must not become a registration."""


def split_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise AgentError("no frontmatter")
    return m.group(1), text[m.end():]


# One frontmatter line: a top-level key, a colon, and the value on the same line.
KEY_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:[ \t]+(.*?))?[ \t]*$")


def frontmatter_value(key, raw):
    """One value, read the way YAML reads a one-line scalar, or AgentError. Anything this
    reader could get wrong (a block or flow value, broken quoting, a comment) is refused,
    never truncated."""
    if not raw:
        return ""
    if raw[0] == '"':
        try:
            return json.loads(raw)
        except ValueError:
            raise AgentError(f"{key}: malformed double-quoted value {raw!r}") from None
    if raw[0] == "'":
        inner = raw[1:-1]
        if len(raw) < 2 or raw[-1] != "'" or "'" in inner.replace("''", ""):
            raise AgentError(f"{key}: malformed single-quoted value {raw!r}")
        return inner.replace("''", "'")
    if raw[0] in ">|":
        raise AgentError(f"{key}: block value ({raw[0]}) is not supported; "
                         "put the value on one line")
    if (raw[0] in "[{&*!%@`#" or raw[:2] in ("- ", "? ") or " #" in raw or ": " in raw
            or raw.endswith(":")):
        raise AgentError(f"{key}: value {raw!r} needs quoting (YAML would not read it "
                         "as plain text)")
    return raw


def parse_frontmatter(text):
    """{key: value} from one-line `key: value` frontmatter, plus the body. Multi-line values,
    duplicate keys and malformed quoting raise AgentError rather than being guessed at."""
    head, body = split_frontmatter(text)
    fields = {}
    for n, line in enumerate(head.splitlines(), 2):
        if not line.strip() or line.startswith("#"):
            continue
        if line[0] in " \t":
            raise AgentError(f"frontmatter line {n} is indented: multi-line values are not "
                             "supported")
        m = KEY_LINE.match(line)
        if not m:
            raise AgentError(f"frontmatter line {n} is not `key: value`: {line!r}")
        key = m.group(1)
        if key in fields:
            raise AgentError(f"frontmatter key {key!r} appears twice")
        fields[key] = frontmatter_value(key, m.group(2) or "")
    return fields, body


def _astral(m):
    hi, lo = int(m.group(1), 16), int(m.group(2), 16)
    return "\\U%08X" % (0x10000 + ((hi - 0xD800) << 10) + (lo - 0xDC00))


def toml_string(value):
    """A TOML basic string. json.dumps gives the same escapes for the BMP; TOML has no
    surrogate escapes, so a JSON surrogate pair becomes one \\U escape, and DEL, which
    JSON leaves bare, is escaped."""
    out = json.dumps(value).replace("\x7f", "\\u007f")
    return re.sub(r"\\u(d[89ab][0-9a-f]{2})\\u(d[c-f][0-9a-f]{2})", _astral, out)


def toml_multiline(value):
    """A TOML multi-line basic string whose parsed value is `value` + a newline."""
    s = value.replace("\\", "\\\\")
    s = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", lambda m: "\\u%04x" % ord(m.group()), s)
    s = s.replace('"""', '""\\"')
    return '"""\n' + s + '\n"""'


def host_limits(tools, disallowed, origin="upstream definition"):
    """The first paragraph of every generated agent: Codex has no per-agent tool limit."""
    return ("Host limits: Codex custom agents cannot enforce a per-agent tool allowlist or "
            f"`disallowedTools:`. The {origin} named `{tools or '(none)'}` and "
            f"`{disallowed or '(none)'}`; treat those as instructions and detection, never as "
            "host enforcement.")


def render_agent_toml(name, description, instructions, model=None, effort=None, header=()):
    """The TOML text for one custom agent. Raises AgentError unless it parses back to
    exactly these values, so nothing unparseable or altered is ever returned."""
    if effort and effort not in EFFORTS:
        raise AgentError(f"effort {effort!r} is not one Codex accepts ({', '.join(EFFORTS)})")
    lines = [f"# {line}" for line in header]
    lines += [f"name = {toml_string(name)}", f"description = {toml_string(description)}"]
    if model:
        lines.append(f"model = {toml_string(model)}")
    if effort:
        lines.append(f'model_reasoning_effort = {toml_string(effort)}')
    lines.append("developer_instructions = " + toml_multiline(instructions))
    text = "\n".join(lines) + "\n"
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise AgentError(f"{name}: rendered TOML does not parse: {exc}") from None
    want = {"name": name, "description": description, "developer_instructions": instructions + "\n"}
    if model:
        want["model"] = model
    if effort:
        want["model_reasoning_effort"] = effort
    if data != want:
        raise AgentError(f"{name}: rendered TOML does not round-trip")
    return text
