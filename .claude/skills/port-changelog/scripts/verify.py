#!/usr/bin/env python3
"""Step 3 of port-changelog: final checks on W/target_out.

Usage: verify.py --work W [--build-cmd CMD]
Prints a short Vietnamese checklist; exit 1 if any check fails, else 0.
"""
import argparse
import difflib
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import common  # noqa: E402
from common import norm_line, read_src  # noqa: E402

STATE = '.port_changelog'
PAIR_RATIO = 0.8   # same tolerance merge_target uses when it drops a slightly different '-' line


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def raw_lines(path):
    """Lines of a file as latin-1 text WITHOUT EOL normalisation ('\\r' kept)."""
    with open(path, 'rb') as f:
        data = f.read().decode('latin-1')
    lines = data.split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    return lines


def plain_name(s):
    s = s.strip()
    s = re.sub(r'\(.*$', '', s)
    s = re.sub(r'\[.*$', '', s)
    return s.strip()


class Checker:
    def __init__(self, work, build_cmd=None):
        self.work = os.path.abspath(work)
        self.state = os.path.join(self.work, STATE)
        self.cfg = load_json(os.path.join(self.state, 'config.json'), {})
        self.scope = load_json(os.path.join(self.state, 'scope.json'), {})
        self.answers = load_json(os.path.join(self.state, 'answers.json'), {})
        self.target = self.cfg.get('target')
        self.latest = self.cfg.get('latest')
        self.out = os.path.join(self.work, 'target_out')
        self.build_cmd = build_cmd
        self.failed = False
        import locate  # noqa: E402
        self.locate = locate
        dsrc = read_src(os.path.join(self.work, 'feature.diff'))
        self.glob, self.files = common.parse_diff(dsrc.text)

    def report(self, ok, title, details=()):
        print('[%s] %s' % ('OK ' if ok else 'LỖI', title))
        for d in details:
            print('      - ' + d)
        if not ok:
            self.failed = True

    # ------------------------------------------------------------------------------------------
    def user_n_units(self):
        res = set()
        for fd in self.files:
            for l in fd.preamble:
                if l.startswith('# step2 '):
                    m = re.search(r'\bunit=(\S+)', l)
                    if m and re.search(r'\bresult=USER_N\b', l):
                        res.add(m.group(1))
        return res

    def changed_files(self):
        """Relative paths whose bytes differ between target and target_out (incl. new files)."""
        out = []
        for rel in common.iter_code_files(self.out):
            a = os.path.join(self.target, rel)
            b = os.path.join(self.out, rel)
            if not os.path.exists(a):
                out.append(rel)
                continue
            with open(a, 'rb') as fa, open(b, 'rb') as fb:
                if fa.read() != fb.read():
                    out.append(rel)
        return out

    # ------------------------------------------------------------------------------------------
    def check_items(self, out_index):
        items = self.scope.get('rt_items') or {}
        names = []
        for key in ('Add', 'Mod'):
            for n in items.get(key) or []:
                n = plain_name(n)
                if n and n not in names:
                    names.append(n)
        skipped = self.user_n_units()
        missing, by_user = [], []
        for n in names:
            if out_index.has(n):
                continue
            (by_user if n in skipped else missing).append(n)
        det = ['thiếu: %s' % n for n in missing] + ['bỏ qua theo người dùng: %s' % n for n in by_user]
        self.report(not missing, 'Mọi hàm/symbol Add./Mod. của RT có trong target_out (%d mục)' % len(names), det)

    def check_symbols(self, out_index, changed):
        latest_index = self.locate.DefIndex(self.latest)
        needed = set()
        for rel in changed:
            a = os.path.join(self.target, rel)
            old = read_src(a).lines if os.path.exists(a) else []
            new = read_src(os.path.join(self.out, rel)).lines
            sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
            added = []
            for tag, _i1, _i2, j1, j2 in sm.get_opcodes():
                if tag in ('insert', 'replace'):
                    added += new[j1:j2]
            needed |= common.identifiers('\n'.join(added))
        missing = sorted(s for s in needed if latest_index.has(s) and not out_index.has(s))
        self.report(not missing, 'Symbol dùng trong code mới đều có định nghĩa trong target_out',
                    ['chưa có định nghĩa: %s' % s for s in missing])

    def check_state(self):
        qs = load_json(os.path.join(self.state, 'questions.json'), {}).get('questions') or []
        pending = [q['id'] for q in qs if q.get('id') not in self.answers]
        stage = None
        for line in self.glob:
            m = re.search(r'\bstage=(\S+)', line)
            if m:
                stage = m.group(1)
        det = ['câu hỏi chưa trả lời: %s' % q for q in pending]
        if stage != 'merged':
            det.append('feature.diff đang ở stage=%s (cần merged)' % stage)
        self.report(not pending and stage == 'merged', 'Không còn câu hỏi chờ, feature.diff stage=merged', det)

    def check_bytes(self, changed):
        plus = set()
        minus_keys = []
        for fd in self.files:
            for h in fd.hunks:
                for tag, t in h.lines:
                    if tag == '+':
                        plus.add(t)
                    elif tag == '-':
                        minus_keys.append(norm_line(t) or t.strip())
        minus_set = set(minus_keys)
        fp = self.scope.get('fingerprint') or {}
        entry = {l.rstrip('\r') for l in (fp.get('raw') or [])}
        det = []
        for rel in changed:
            a = os.path.join(self.target, rel)
            b = os.path.join(self.out, rel)
            if not os.path.exists(a):
                det.append('%s: file mới (tạo từ Latest)' % rel)
                continue
            sa, sb = read_src(a), read_src(b)
            if sa.eol != sb.eol:
                det.append('%s: kiểu xuống dòng bị đổi (%r -> %r)' % (rel, sa.eol, sb.eol))
            ra, rb = raw_lines(a), raw_lines(b)
            eol_cr = sa.eol == '\r\n'
            sm = difflib.SequenceMatcher(None, ra, rb, autojunk=False)
            bad = []
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag == 'equal':
                    continue
                for ln in rb[j1:j2]:
                    t = ln[:-1] if eol_cr and ln.endswith('\r') else ln
                    if t in plus or t in entry or not t.strip():
                        continue
                    bad.append('dòng lạ được thêm: %s' % t.strip()[:70])
                for ln in ra[i1:i2]:
                    t = ln[:-1] if eol_cr and ln.endswith('\r') else ln
                    k = norm_line(t) or t.strip()
                    if not k or k in minus_set:
                        continue
                    if any(difflib.SequenceMatcher(None, k, m, autojunk=False).ratio() >= PAIR_RATIO
                           for m in minus_keys):
                        continue
                    bad.append('dòng gốc bị xoá/sửa ngoài diff: %s' % t.strip()[:70])
            det += ['%s: %s' % (rel, x) for x in bad[:10]]
            if len(bad) > 10:
                det.append('%s: ... còn %d dòng' % (rel, len(bad) - 10))
        ok = not [d for d in det if 'file mới' not in d]
        self.report(ok, 'Encoding/xuống dòng giữ nguyên, chỉ đổi đúng các dòng của diff (%d file sửa)'
                    % len(changed), det)

    def check_build(self):
        if not self.build_cmd:
            print('[-- ] Không chạy build (không có --build-cmd)')
            return
        r = subprocess.run(self.build_cmd, shell=True, cwd=self.out, capture_output=True, text=True,
                           encoding='latin-1')
        tail = (r.stdout + r.stderr).strip().splitlines()[-5:]
        self.report(r.returncode == 0, 'Build trong target_out: mã trả về %d' % r.returncode, tail)

    def run(self):
        if not os.path.isdir(self.out):
            print('[LỖI] Chưa có target_out — hãy chạy bước 2 trước.')
            return 1
        print('Kiểm tra cuối (bước 3):')
        out_index = self.locate.DefIndex(self.out)
        changed = self.changed_files()
        self.check_items(out_index)
        self.check_symbols(out_index, changed)
        self.check_state()
        self.check_bytes(changed)
        self.check_build()
        print('=> %s' % ('CÓ LỖI, cần xem lại.' if self.failed else 'Tất cả đều đạt.'))
        return 1 if self.failed else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description='port-changelog step 3: kiểm tra cuối')
    ap.add_argument('--work', required=True)
    ap.add_argument('--build-cmd', default=None)
    args = ap.parse_args(argv)
    try:
        return Checker(args.work, args.build_cmd).run()
    except Exception as e:  # noqa: BLE001
        print('Lỗi: %s' % e)
        return 1


if __name__ == '__main__':
    sys.exit(main())
