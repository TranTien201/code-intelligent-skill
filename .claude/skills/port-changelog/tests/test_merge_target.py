#!/usr/bin/env python3
"""Tests for scripts/merge_target.py (step 2) and scripts/verify.py (step 3).

Run: python3 -I tests/test_merge_target.py   (plain asserts, no pytest)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), 'scripts')
PY = sys.executable

SJIS = b'\x83\x65\x83\x58\x83\x67'   # "テスト" in Shift-JIS

TARGET_A = [
    b'/*#*************************************************#*/',
    b'/*#     Modification:                               #*/',
    b'/*#         2017/01/01  X.Old       RT1000          #*/',
    b'/*#                     Mod. foo()                  #*/',
    b'/*#*************************************************#*/',
    b'#include "a.h"',
    b'',
    b'/* ' + SJIS + b' counter */',
    b'static int gCount;',
    b'',
    b'int foo(int a)',
    b'{',
    b'    int r = 0, s = 0;   /* FOMULAR init */',
    b'    if (a > 0)   {',
    b'        r = a * 2;',
    b'    }',
    b'    return r;',
    b'}',
    b'',
    b'int bar(int b)',
    b'{',
    b'    b = b + 2;',
    b'    return b;',
    b'}',
    b'',
    b'int baz(int v)',
    b'{',
    b'    unsigned long k;',
    b'    for (k = 0; k < 10; k++) {',
    b'        v ^= (int)(k << 3);',
    b'    }',
    b'    return v;',
    b'}',
    b'',
    b'int qux(int d)',
    b'{',
    b'    d = d * 3 + 11;',
    b'    return d;',
    b'}',
]

LATEST_A = '''/*#*************************************************#*/
/*#     Modification:                               #*/
/*#         2018/08/31  Y.Kaneko    RT2486          #*/
/*#                     Add. newFn()                #*/
/*#                     Mod. foo()                  #*/
/*#         2017/01/01  X.Old       RT1000          #*/
/*#                     Mod. foo()                  #*/
/*#*************************************************#*/
#include "a.h"

static int gCount;

int foo(int a)
{
    int r = 0;
    if (a > 0) {
        r = a * 3;
        gCount++;
    }
    return r;
}

int bar(int b)
{
    b = b + 2;
    return b;
}

int newFn(int x)
{
    gCount += x;
    return gCount;
}

int baz(int c)
{
    c = c - 1;
    c = c - 2;
    return c;
}

int qux(int d)
{
    d = d * 3 + 11;
    return d;
}
'''

FEATURE = '''# port-changelog rt=RT2486
# port-changelog stage=latest
# unit=foo kind=func change=mod status=CHANGED | test
# unit=bar kind=func change=mod status=UNCHANGED | test
# unit=newFn kind=func change=add status=TAKEN after=bar | test
# unit=baz kind=func change=mod status=CHANGED | test
--- a/src/a.c
+++ b/src/a.c
@@ -13,7 +13,8 @@ foo
 {
     int r = 0;
     if (a > 0) {
-        r = a * 2;
+        r = a * 3;
+        gCount++;
     }
     return r;
 }
@@ -22,4 +23,4 @@ bar
 int bar(int b)
 {
-    b = b + 1;
+    b = b + 2;
     return b;
@@ -26,3 +27,9 @@ newFn
 }

+int newFn(int x)
+{
+    gCount += x;
+    return gCount;
+}
+
 int baz(int c)
@@ -32,3 +39,3 @@ baz
     c = c - 1;
-    c = c * 5 + 1;
+    c = c - 2;
     return c;
'''

ENTRY = ['/*#         2018/08/31  Y.Kaneko    RT2486          #*/',
         '/*#                     Add. newFn()                #*/',
         '/*#                     Mod. foo()                  #*/']


def setup(tmp):
    latest = os.path.join(tmp, 'latest')
    target = os.path.join(tmp, 'target')
    work = os.path.join(tmp, 'work')
    os.makedirs(os.path.join(latest, 'src'))
    os.makedirs(os.path.join(target, 'src'))
    os.makedirs(os.path.join(work, '.port_changelog'))
    with open(os.path.join(latest, 'src', 'a.c'), 'w', newline='\n') as f:
        f.write(LATEST_A)
    with open(os.path.join(target, 'src', 'a.c'), 'wb') as f:
        f.write(b'\r\n'.join(TARGET_A) + b'\r\n')
    with open(os.path.join(target, 'src', 'other.c'), 'wb') as f:
        f.write(b'int other(void) { return 0; }\r\n')
    with open(os.path.join(work, 'feature.diff'), 'w', newline='\n') as f:
        f.write(FEATURE)
    st = os.path.join(work, '.port_changelog')
    json.dump({'latest': latest, 'target': target, 'rt': 'RT2486', 'k': 3, 'hi': 0.9, 'lo': 0.6},
              open(os.path.join(st, 'config.json'), 'w'))
    json.dump({'rt': 'RT2486',
               'fingerprint': {'rt': 'RT2486', 'raw': ENTRY,
                               'items': {'Add': ['newFn'], 'Mod': ['foo', 'bar', 'baz']}},
               'rt_items': {'Add': ['newFn'], 'Mod': ['foo()', 'bar', 'baz']}, 'suspects': {}},
              open(os.path.join(st, 'scope.json'), 'w'))
    return latest, target, work


def run(script, work, *extra):
    r = subprocess.run([PY, '-I', os.path.join(SCRIPTS, script), '--work', work] + list(extra),
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def jload(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def answer(work, qid, ans):
    p = os.path.join(work, '.port_changelog', 'answers.json')
    d = jload(p) if os.path.exists(p) else {}
    d[qid] = {'answer': ans, 'by': 'user', 'note': ''}
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(d, f)


def out_bytes(work):
    with open(os.path.join(work, 'target_out', 'src', 'a.c'), 'rb') as f:
        return f.read()


def step2_lines(work):
    with open(os.path.join(work, 'feature.diff'), encoding='latin-1') as f:
        return [l.rstrip('\n') for l in f if l.startswith('# step2 ')]


def stage(work):
    with open(os.path.join(work, 'feature.diff'), encoding='latin-1') as f:
        for l in f:
            if l.startswith('# port-changelog stage='):
                return l.strip().split('=', 1)[1]


def main():
    tmp = tempfile.mkdtemp(prefix='pc_merge_')
    try:
        latest, target, work = setup(tmp)
        orig = open(os.path.join(target, 'src', 'a.c'), 'rb').read()

        # ---- run 1: baz is a mismatch -> question, exit 2 -----------------------------------
        rc, out = run('merge_target.py', work)
        assert rc == 2, out
        qs = jload(os.path.join(work, '.port_changelog', 'questions.json'))
        assert qs['step'] == 2
        kinds = {q["unit"]: q["kind"] for q in qs["questions"]}
        assert kinds == {'baz': 'target_mismatch'}, kinds
        q = qs['questions'][0]
        assert q['who'] == 'user' and q['id'].startswith('s2:src/a.c:baz:target_mismatch'), q
        assert stage(work) == 'latest'
        notes = step2_lines(work)
        assert any('unit=baz result=ASK' in l for l in notes), notes
        data = out_bytes(work)
        # target_out written with what is decided already
        assert b'        r = a * 3;\r\n        gCount++;\r\n' in data, data

        # AUTO: target's own context lines kept (comment + spacing), '-' line dropped
        assert b'    int r = 0, s = 0;   /* FOMULAR init */\r\n' in data
        assert b'    if (a > 0)   {\r\n        r = a * 3;\r\n' in data, data
        assert b'r = a * 2;' not in data
        assert any('unit=foo result=AUTO' in l for l in notes), notes
        # SKIP: bar already has '+' line
        assert any('unit=bar result=SKIP' in l for l in notes), notes
        assert data.count(b'b = b + 2;') == 1
        # new function inserted after bar, blank separators
        assert b'    return b;\r\n}\r\n\r\nint newFn(int x)\r\n{\r\n    gCount += x;\r\n    return gCount;\r\n}\r\n\r\nint baz' \
            in data, data
        assert any('unit=newFn result=AUTO' in l for l in notes), notes
        # CRLF + Shift-JIS preserved, no bare LF
        assert b'/* ' + SJIS + b' counter */\r\n' in data
        assert data.count(b'\n') == data.count(b'\r\n')
        # changelog entry inserted right after Modification:
        assert data.count(b'RT2486') == 1, data
        lines = data.split(b'\r\n')
        assert lines[1].startswith(b'/*#     Modification:') and b'RT2486' in lines[2], lines[:5]
        # untouched file stays byte-identical
        assert open(os.path.join(work, 'target_out', 'src', 'other.c'), 'rb').read() == \
            open(os.path.join(target, 'src', 'other.c'), 'rb').read()
        # input target never modified
        assert open(os.path.join(target, 'src', 'a.c'), 'rb').read() == orig

        # verify must fail while a question is pending
        rc, vout = run('verify.py', work)
        assert rc == 1, vout

        # ---- answer N -> skipped, stage=merged, exit 0 ------------------------------------------
        answer(work, q['id'], 'N')
        rc, out = run('merge_target.py', work)
        assert rc == 0, out
        assert stage(work) == 'merged'
        notes = step2_lines(work)
        assert any('unit=baz result=USER_N' in l for l in notes), notes
        assert len([l for l in notes if 'unit=foo ' in l]) == 1, notes   # step2 notes replaced, not added
        data = out_bytes(work)
        assert b'c = c - 2;' not in data
        assert data.count(b'RT2486') == 1
        assert jload(os.path.join(work, '.port_changelog', 'questions.json'))['questions'] == []
        rc, vout = run('verify.py', work)
        assert rc == 0, vout
        assert 'bỏ qua theo người dùng: baz' not in vout   # baz still exists in target (only hunk skipped)

        # ---- answer Y -> applied at best candidate (re-run from stage=merged) -------------------
        answer(work, q['id'], 'Y')
        rc, out = run('merge_target.py', work)
        assert rc == 0, out
        notes = step2_lines(work)
        assert any('unit=baz result=USER_Y' in l for l in notes), notes
        data = out_bytes(work)
        assert b'    c = c - 2;\r\n' in data, data
        assert data.count(b'RT2486') == 1           # still inserted only once
        assert data.count(b'\n') == data.count(b'\r\n')
        assert b'/* ' + SJIS + b' counter */\r\n' in data
        # hunks themselves unchanged in feature.diff
        with open(os.path.join(work, 'feature.diff'), encoding='latin-1') as f:
            fd_text = f.read()
        strip = lambda t: '\n'.join(l.rstrip() for l in t.split('\n'))   # noqa: E731
        assert strip(FEATURE.split('--- a/src/a.c', 1)[1]) in strip(fd_text)

        rc, vout = run('verify.py', work)
        assert rc == 0, vout
        rc, vout = run('verify.py', work, '--build-cmd', 'exit 3')
        assert rc == 1 and 'mã trả về 3' in vout, vout

        # ---- verify catches a stray edit outside the diff ---------------------------------------
        p = os.path.join(work, 'target_out', 'src', 'a.c')
        with open(p, 'wb') as f:
            f.write(data.replace(b'    d = d * 3 + 11;', b'    d = d * 4;'))
        rc, vout = run('verify.py', work)
        assert rc == 1 and 'd = d * 4;' in vout, vout

        # ---- stage=original is refused ------------------------------------------------------------
        with open(os.path.join(work, 'feature.diff'), 'w', newline='\n') as f:
            f.write(FEATURE.replace('stage=latest', 'stage=original'))
        rc, out = run('merge_target.py', work)
        assert rc == 1, out
        print('test_merge_target: OK')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
