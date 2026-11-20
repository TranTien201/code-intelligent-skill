#!/usr/bin/env python3
"""Shared helpers for port-changelog (standard library only).

Text model
----------
Files are read as latin-1 so every byte maps 1:1 to a char: Shift-JIS / UTF-8 bytes survive a
read -> write round trip unchanged, and comparisons stay byte-exact. Line endings are normalised
to '\n' in memory; the original style is remembered and restored on write.

Line numbers in this module are 1-based and inclusive unless a name says otherwise.
"""
import difflib
import os
import re
import subprocess
from dataclasses import dataclass, field

CODE_EXT = {'.c', '.h', '.cc', '.cpp', '.cxx', '.hpp', '.hh', '.hxx', '.inc', '.ipp'}
SKIP_DIRS = {'.git', 'build', 'out', '_work', '.port_changelog'}

C_KEYWORDS = set("""
auto break case char const continue default do double else enum extern float for goto if inline int long
register restrict return short signed sizeof static struct switch typedef union unsigned void volatile while
_Bool bool true false NULL nullptr class namespace template typename public private protected virtual override
new delete this operator using try catch throw constexpr noexcept static_cast const_cast reinterpret_cast
dynamic_cast explicit friend mutable defined include define ifdef ifndef endif elif undef pragma error
int8_t int16_t int32_t int64_t uint8_t uint16_t uint32_t uint64_t size_t ssize_t uintptr_t intptr_t
BOOL BYTE WORD DWORD UCHAR USHORT ULONG UINT INT CHAR VOID TRUE FALSE
""".split())

IDENT_RE = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')


# ----------------------------------------------------------------------------------------------
# File IO
# ----------------------------------------------------------------------------------------------
@dataclass
class SrcFile:
    path: str
    text: str            # '\n' line endings
    eol: str = '\n'      # original line ending ('\r\n' or '\n')
    final_newline: bool = True

    @property
    def lines(self):
        """Lines without terminators."""
        return split_lines(self.text)


def split_lines(text):
    if not text:
        return []
    lines = text.split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    return lines


def join_lines(lines, final_newline=True):
    s = '\n'.join(lines)
    return s + '\n' if (final_newline and lines) else s


def read_src(path):
    with open(path, 'rb') as f:
        data = f.read()
    raw = data.decode('latin-1')
    eol = '\r\n' if '\r\n' in raw else '\n'
    text = raw.replace('\r\n', '\n').replace('\r', '\n')
    return SrcFile(path=path, text=text, eol=eol, final_newline=text.endswith('\n') or not text)


def write_src(path, text, eol='\n', final_newline=True):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    if final_newline and text and not text.endswith('\n'):
        text += '\n'
    if not final_newline:
        text = text.rstrip('\n')
    data = text.replace('\n', eol).encode('latin-1')
    with open(path, 'wb') as f:
        f.write(data)


def iter_code_files(root):
    """Yield paths (relative to root, '/' separators) of C/C++ files, sorted."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in CODE_EXT:
                out.append(os.path.relpath(os.path.join(dirpath, fn), root).replace(os.sep, '/'))
    return sorted(out)


def grep_files(root, word, files=None):
    """Relative paths under root whose content contains `word` as a whole word.

    Uses `grep -rlw` (fast, does not load files into Python). Falls back to Python if grep fails.
    """
    try:
        # -a: treat Shift-JIS files as text (never skipped as binary); LC_ALL=C: byte semantics
        cmd = ['grep', '-rlwa', '--', word]
        if files is not None:
            if not files:
                return []
            cmd += [os.path.join(root, f) for f in files]
        else:
            cmd += [root]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='latin-1',
                           env=dict(os.environ, LC_ALL='C'))
        if r.returncode in (0, 1):
            res = []
            for line in r.stdout.splitlines():
                rel = os.path.relpath(line, root).replace(os.sep, '/')
                if os.path.splitext(rel)[1].lower() in CODE_EXT and not any(
                        p in SKIP_DIRS for p in rel.split('/')):
                    res.append(rel)
            return sorted(set(res))
    except OSError:
        pass
    pat = re.compile(r'\b%s\b' % re.escape(word))
    cand = files if files is not None else iter_code_files(root)
    return sorted(f for f in cand if pat.search(read_src(os.path.join(root, f)).text))


# ----------------------------------------------------------------------------------------------
# C lexing helpers
# ----------------------------------------------------------------------------------------------
def mask_comments_strings(text):
    """Return text of identical length/line layout with comments and string/char literals
    replaced by spaces (newlines kept). Safe base for brace counting and identifier scans."""
    out = list(text)
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == '/' and i + 1 < n and text[i + 1] == '*':
            j = text.find('*/', i + 2)
            j = n if j < 0 else j + 2
            for k in range(i, j):
                if out[k] != '\n':
                    out[k] = ' '
            i = j
        elif c == '/' and i + 1 < n and text[i + 1] == '/':
            j = text.find('\n', i)
            j = n if j < 0 else j
            for k in range(i, j):
                out[k] = ' '
            i = j
        elif c in '"\'':
            j = i + 1
            while j < n and text[j] != c and text[j] != '\n':
                j += 2 if text[j] == '\\' else 1
            j = min(j + 1, n)
            for k in range(i + 1, j - 1):
                if out[k] != '\n':
                    out[k] = ' '
            i = j
        else:
            i += 1
    return ''.join(out)


def strip_comments(line):
    """Remove /* */ (same line) and // comments from a single line."""
    line = re.sub(r'/\*.*?\*/', ' ', line)
    line = re.sub(r'/\*.*$', ' ', line)
    line = re.sub(r'^.*?\*/', ' ', line) if '*/' in line and '/*' not in line else line
    return re.sub(r'//.*$', '', line)


def norm_line(line):
    """Whitespace/comment-insensitive key for one line ('' for blank or comment-only lines)."""
    return re.sub(r'\s+', ' ', strip_comments(line)).strip()


def identifiers(text, drop_keywords=True):
    """Set of identifiers in code (comments/strings ignored)."""
    ids = set(IDENT_RE.findall(mask_comments_strings(text)))
    if drop_keywords:
        ids -= C_KEYWORDS
    return ids


# ----------------------------------------------------------------------------------------------
# Top-level units (functions, declarations, macros)
# ----------------------------------------------------------------------------------------------
@dataclass
class Unit:
    kind: str            # 'func' | 'decl' | 'macro'
    name: str
    start: int           # 1-based first line of the declaration itself
    end: int             # 1-based last line (inclusive)
    doc_start: int = 0   # 1-based first line incl. directly preceding comment block (== start if none)
    lines: list = field(default_factory=list)   # source lines start..end

    @property
    def body(self):
        return '\n'.join(self.lines)


_DECL_NAME_SKIP = C_KEYWORDS | {'extern', 'static', 'const', 'volatile', 'register'}


def _decl_name(stmt_masked):
    """Best-effort name of a top-level declaration statement (masked text, ends with ';')."""
    s = stmt_masked.strip()
    if s.startswith('#'):
        return None
    # typedef ... NAME;   /   typedef struct {...} NAME;
    if re.match(r'\s*typedef\b', s):
        ids = [x for x in IDENT_RE.findall(re.sub(r'\{.*\}', ' ', s, flags=re.S)) if x not in _DECL_NAME_SKIP]
        m = re.search(r'\(\s*\*\s*([A-Za-z_]\w*)\s*\)', s)   # function pointer typedef
        if m:
            return m.group(1)
        return ids[-1] if ids else None
    # struct/enum/union TAG { ... };  (no declarator)
    m = re.match(r'\s*(struct|enum|union)\s+([A-Za-z_]\w*)\s*\{.*\}\s*;\s*$', s, re.S)
    if m:
        return m.group(2)
    # drop initializer and bodies, then take identifier before [ ( or end
    head = s.split('=', 1)[0]
    head = re.sub(r'\{.*\}', ' ', head, flags=re.S)
    m = re.search(r'([A-Za-z_]\w*)\s*(\[[^;]*)?\s*;?\s*$', head.rstrip(';').rstrip())
    if m and m.group(1) not in _DECL_NAME_SKIP:
        return m.group(1)
    # prototype: NAME(...)
    m = re.search(r'([A-Za-z_]\w*)\s*\([^()]*(\([^()]*\)[^()]*)*\)\s*;?\s*$', head.rstrip(';'))
    if m and m.group(1) not in _DECL_NAME_SKIP:
        return m.group(1)
    return None


def find_units(text):
    """Split C source into top-level units.

    - func : a top-level `{...}` whose head ends with `)` (optionally followed by K&R decls / qualifiers)
    - decl : a top-level statement ending with `;` (globals, arrays, typedefs, struct defs, prototypes)
    - macro: `#define NAME` (with backslash continuations)
    Lines not covered by any unit (includes, #if, comments, blank) are not returned.
    """
    lines = split_lines(text)
    masked = split_lines(mask_comments_strings(text))
    while len(masked) < len(lines):
        masked.append('')
    units = []
    n = len(lines)
    i = 0
    stmt_start = None      # index where current top-level statement started
    stmt_buf = []
    depth = 0
    in_pp = False

    def doc_start_of(idx):
        k = idx - 1
        # attach a directly preceding comment block (no blank line between)
        if k >= 0 and lines[k].strip().endswith('*/'):
            while k >= 0 and '/*' not in lines[k]:
                k -= 1
            if k >= 0:
                return k
        while k >= 0 and lines[k].strip().startswith('//'):
            k -= 1
        return k + 1 if k + 1 < idx else idx

    while i < n:
        m = masked[i]
        stripped = m.strip()
        if depth == 0 and stmt_start is None and (stripped.startswith('#') or in_pp):
            # preprocessor line(s)
            j = i
            while j < n and masked[j].rstrip().endswith('\\'):
                j += 1
            mm = re.match(r'\s*#\s*define\s+([A-Za-z_]\w*)', masked[i])
            if mm and not in_pp:
                units.append(Unit('macro', mm.group(1), i + 1, j + 1, doc_start_of(i) + 1, lines[i:j + 1]))
            i = j + 1
            continue
        if depth == 0 and stmt_start is None:
            if not stripped:
                i += 1
                continue
            stmt_start = i
            stmt_buf = []
        # scan chars of this line
        for ch in m:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth = max(0, depth - 1)
        stmt_buf.append(m)
        joined = '\n'.join(stmt_buf)
        if depth == 0:
            js = joined.rstrip()
            if js.endswith('}') and not js.endswith(';'):
                # function body closed? head must contain ')' before the first '{'
                head = joined[:joined.find('{')] if '{' in joined else joined
                if ')' in head and not re.match(r'\s*(typedef|struct|enum|union)\b', head) and '=' not in head:
                    hm = re.search(r'([A-Za-z_]\w*)\s*\((?:[^()]|\([^()]*\))*\)\s*(?:[^(){};]*;\s*)*[^(){};]*$', head)
                    name = hm.group(1) if hm else None
                    if name:
                        units.append(Unit('func', name, stmt_start + 1, i + 1,
                                          doc_start_of(stmt_start) + 1, lines[stmt_start:i + 1]))
                    stmt_start = None
                    i += 1
                    continue
                # struct/enum/initializer without ';' yet -> keep collecting
            if js.endswith(';'):
                name = _decl_name(joined)
                if name:
                    units.append(Unit('decl', name, stmt_start + 1, i + 1,
                                      doc_start_of(stmt_start) + 1, lines[stmt_start:i + 1]))
                stmt_start = None
            elif not js:
                stmt_start = None
        i += 1
    return units


def unit_index(units):
    """{name: [units...]} (a name can repeat, e.g. prototype decl + func)."""
    idx = {}
    for u in units:
        idx.setdefault(u.name, []).append(u)
    return idx


def best_unit(units, name, kind=None):
    """Prefer func over decl over macro for the same name; None if absent."""
    cands = [u for u in units if u.name == name and (kind is None or u.kind == kind)]
    if not cands:
        return None
    order = {'func': 0, 'macro': 1, 'decl': 2}
    if kind is None:
        # a prototype decl and a func: take func
        cands.sort(key=lambda u: (order.get(u.kind, 9), -(u.end - u.start)))
    return cands[0]


def enclosing_unit(units, line_no):
    for u in units:
        if u.doc_start <= line_no <= u.end or u.start <= line_no <= u.end:
            return u
    return None


# ----------------------------------------------------------------------------------------------
# Unified diff model
# ----------------------------------------------------------------------------------------------
@dataclass
class Hunk:
    old_start: int
    old_len: int
    new_start: int
    new_len: int
    section: str = ''                              # text after the closing '@@' (function name)
    lines: list = field(default_factory=list)      # [(tag, text)] tag in ' ', '-', '+', '\\'

    def old_lines(self):
        return [t for tag, t in self.lines if tag in (' ', '-')]

    def new_lines(self):
        return [t for tag, t in self.lines if tag in (' ', '+')]


@dataclass
class FileDiff:
    old_path: str                                  # path as written after '--- ' (without a/ prefix stripping)
    new_path: str
    preamble: list = field(default_factory=list)   # raw lines before '---' (incl. '# ...' notes, 'diff ...')
    hunks: list = field(default_factory=list)

    @property
    def path(self):
        """Repo-relative path: new side unless /dev/null, a/ b/ prefixes stripped."""
        p = self.new_path if self.new_path != '/dev/null' else self.old_path
        return strip_ab(p)

    def notes(self):
        return [l for l in self.preamble if l.startswith('#')]


def strip_ab(p):
    p = p.split('\t', 1)[0].strip()
    if p.startswith(('a/', 'b/')):
        p = p[2:]
    return p


GLOBAL_NOTE = '# port-changelog '

_HUNK_RE = re.compile(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@ ?(.*)$')


def parse_diff(text):
    """Parse a (possibly multi-file) unified diff. Returns (global_notes, [FileDiff]).

    global_notes: '# port-changelog ...' lines placed before the first file block.
    Every other line before a file's '---' (e.g. 'diff -u ...', '# <unit>: ...' notes) is that
    file's preamble.
    """
    lines = split_lines(text.replace('\r\n', '\n'))
    files = []
    pending = []
    glob_notes = []
    cur = None
    hunk = None
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('--- ') and i + 1 < len(lines) and lines[i + 1].startswith('+++ '):
            if not files:
                glob_notes = [l for l in pending if l.startswith(GLOBAL_NOTE)]
                pending = [l for l in pending if not l.startswith(GLOBAL_NOTE)]
            cur = FileDiff(ln[4:], lines[i + 1][4:], preamble=pending)
            pending = []
            files.append(cur)
            hunk = None
            i += 2
            continue
        m = _HUNK_RE.match(ln)
        if m and cur is not None:
            hunk = Hunk(int(m.group(1)), int(m.group(2) or 1), int(m.group(3)), int(m.group(4) or 1),
                        m.group(5).strip())
            cur.hunks.append(hunk)
            i += 1
            continue
        if hunk is not None and ln[:1] in (' ', '-', '+', '\\') or (hunk is not None and ln == ''):
            # count remaining capacity to decide if line belongs to the hunk
            o = sum(1 for t, _ in hunk.lines if t in (' ', '-'))
            nw = sum(1 for t, _ in hunk.lines if t in (' ', '+'))
            if ln.startswith('\\'):
                hunk.lines.append(('\\', ln[1:]))
                i += 1
                continue
            if o < hunk.old_len or nw < hunk.new_len:
                tag = ln[:1] if ln else ' '
                hunk.lines.append((tag, ln[1:]))
                i += 1
                continue
        # not part of a hunk -> preamble of the next file
        hunk = None
        pending.append(ln)
        i += 1
    if not files:
        glob_notes = [l for l in pending if l.startswith(GLOBAL_NOTE)]
    # trailing non-hunk lines after the last file are dropped (blank lines / junk)
    return glob_notes, files


def render_diff(files, global_preamble=None):
    out = list(global_preamble or [])
    for fd in files:
        out.extend(fd.preamble)
        out.append('--- ' + fd.old_path)
        out.append('+++ ' + fd.new_path)
        for h in fd.hunks:
            out.append('@@ -%s +%s @@%s' % (_rng(h.old_start, h.old_len), _rng(h.new_start, h.new_len),
                                            (' ' + h.section) if h.section else ''))
            for tag, t in h.lines:
                out.append(tag + t)
    return join_lines(out)


def _rng(start, length):
    return '%d' % start if length == 1 else '%d,%d' % (start, length)


def make_hunks(old_lines, new_lines, context=3, old_offset=0, new_offset=0, section=''):
    """Unified-diff hunks between two line lists. Offsets are 0-based line offsets added to numbers."""
    hunks = []
    sm = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    for group in sm.get_grouped_opcodes(context):
        i1, i2, j1, j2 = group[0][1], group[-1][2], group[0][3], group[-1][4]
        h = Hunk(i1 + 1 + old_offset, i2 - i1, j1 + 1 + new_offset, j2 - j1, section)
        if h.old_len == 0:
            h.old_start -= 1
        if h.new_len == 0:
            h.new_start -= 1
        for tag, a1, a2, b1, b2 in group:
            if tag == 'equal':
                h.lines += [(' ', l) for l in old_lines[a1:a2]]
            else:
                h.lines += [('-', l) for l in old_lines[a1:a2]]
                h.lines += [('+', l) for l in new_lines[b1:b2]]
        hunks.append(h)
    return hunks


def apply_hunks_strict(lines, hunks):
    """Apply hunks by exact old-side match at stated positions (used for Before->After reconstruction).
    Returns new line list or raises ValueError."""
    out = list(lines)
    delta = 0
    for h in hunks:
        old = h.old_lines()
        pos = h.old_start - 1 + delta if h.old_len else h.old_start + delta
        if out[pos:pos + len(old)] != old:
            raise ValueError('hunk @@ -%d does not match' % h.old_start)
        new = h.new_lines()
        out[pos:pos + len(old)] = new
        delta += len(new) - len(old)
    return out


def reverse_hunks(hunks):
    res = []
    for h in hunks:
        rh = Hunk(h.new_start, h.new_len, h.old_start, h.old_len, h.section,
                  [({'-': '+', '+': '-'}.get(t, t), x) for t, x in h.lines])
        res.append(rh)
    return res


def diff_dirs(before_dir, after_dir, context=3):
    """Build a unified diff (text) between two folders, with function names in @@ headers."""
    files = []
    rels = sorted(set(iter_code_files(before_dir)) | set(iter_code_files(after_dir)))
    for rel in rels:
        bp, ap = os.path.join(before_dir, rel), os.path.join(after_dir, rel)
        b = read_src(bp).lines if os.path.exists(bp) else []
        a = read_src(ap).lines if os.path.exists(ap) else []
        if b == a:
            continue
        units = find_units(join_lines(a)) if a else find_units(join_lines(b))
        hunks = make_hunks(b, a, context)
        for h in hunks:
            ref = h.new_start if a else h.old_start
            # name of the unit containing the first changed line
            first = ref
            for k, (tag, _) in enumerate(h.lines):
                if tag != ' ':
                    first = ref + sum(1 for t, _ in h.lines[:k] if t in (' ', '+' if a else '-'))
                    break
            u = enclosing_unit(units, first)
            h.section = u.name if u else ''
        files.append(FileDiff('a/' + rel if b else '/dev/null', 'b/' + rel if a else '/dev/null', [], hunks))
    return render_diff(files)


# ----------------------------------------------------------------------------------------------
# Notes inside the diff ('# ' lines before '---')
# ----------------------------------------------------------------------------------------------
NOTE_PREFIX = '# '


def set_header_note(global_preamble, key, value):
    """Set/replace a global '# port-changelog key=value ...' style note line."""
    line = '%sport-changelog %s=%s' % (NOTE_PREFIX, key, value)
    for i, l in enumerate(global_preamble):
        if l.startswith('%sport-changelog %s=' % (NOTE_PREFIX, key)):
            global_preamble[i] = line
            return global_preamble
    global_preamble.append(line)
    return global_preamble
