#!/usr/bin/env python3
"""End-to-end test for the port-changelog skill on fixture tests/fixtures/rt2486.

Run:  python3 -I tests/test_pipeline.py [--keep] [--fixture NAME]

Flow: copy the fixture to a temp dir -> run.py init -> loop `run.py all` (max 10 rounds); on exit 2
answer every open question from expected/answers.json via `run.py answer` -> compare W/target_out with
expected/target_out byte-for-byte. Exit 1 on any mismatch.

expected/answers.json: {"<question id>": "Y" | {"answer": "Y", "optional": bool, "note": str}}
  - optional=true: the question MAY be asked (not reported if it never is).
  - An asked id that is not a key but has a key as prefix (key + ':' ...) is matched to that key.
"""
import difflib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN_PY = os.path.join(ROOT, '.claude', 'skills', 'port-changelog', 'scripts', 'run.py')
MAX_ROUNDS = 10


def run(args, quiet=False):
    cmd = [sys.executable, '-I', RUN_PY] + args
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if not quiet or r.returncode not in (0, 2):
        print('$ run.py %s  -> exit %d' % (' '.join(args[:1]), r.returncode))
        for stream in (r.stdout, r.stderr):
            if stream.strip():
                print('  | ' + '\n  | '.join(stream.rstrip().splitlines()[-40:]))
    return r.returncode


def load_expected_answers(path):
    with open(path, encoding='utf-8') as f:
        raw = json.load(f)
    out = {}
    for k, v in raw.items():
        if isinstance(v, str):
            v = {'answer': v}
        out[k] = {'answer': v['answer'], 'optional': bool(v.get('optional')), 'note': v.get('note', '')}
    return out


def match_expected(qid, expected):
    if qid in expected:
        return qid
    for k in sorted(expected, key=len, reverse=True):
        if qid.startswith(k + ':'):
            return k
    return None


def list_files(root):
    res = set()
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if not d.startswith('.')]
        for fn in fns:
            res.add(os.path.relpath(os.path.join(dp, fn), root).replace(os.sep, '/'))
    return res


def show_eol(s):
    return s.replace('\r\n', '<CRLF>\n')


def compare_trees(exp_root, got_root):
    problems = []
    exp_files, got_files = list_files(exp_root), list_files(got_root) if os.path.isdir(got_root) else set()
    for rel in sorted(exp_files - got_files):
        problems.append('MISSING in target_out: %s' % rel)
    for rel in sorted(got_files - exp_files):
        problems.append('EXTRA in target_out: %s' % rel)
    for rel in sorted(exp_files & got_files):
        with open(os.path.join(exp_root, rel), 'rb') as f:
            e = f.read()
        with open(os.path.join(got_root, rel), 'rb') as f:
            g = f.read()
        if e == g:
            continue
        et, gt = e.decode('latin-1'), g.decode('latin-1')
        if et.replace('\r\n', '\n') == gt.replace('\r\n', '\n'):
            problems.append('EOL ONLY differs: %s (expected %s, got %s)' % (
                rel, 'CRLF' if '\r\n' in et else 'LF', 'CRLF' if '\r\n' in gt else 'LF/mixed'))
            continue
        diff = difflib.unified_diff(show_eol(et).splitlines(True), show_eol(gt).splitlines(True),
                                    'expected/' + rel, 'got/' + rel, n=2)
        problems.append('CONTENT differs: %s\n%s' % (rel, ''.join(diff).rstrip()))
    return problems


def main():
    keep = '--keep' in sys.argv
    fixture = 'rt2486'
    if '--fixture' in sys.argv:
        fixture = sys.argv[sys.argv.index('--fixture') + 1]
    fx_src = os.path.join(ROOT, 'tests', 'fixtures', fixture)
    if not os.path.isfile(RUN_PY):
        print('FAIL: %s does not exist' % RUN_PY)
        return 1

    tmp = tempfile.mkdtemp(prefix='port_changelog_%s_' % fixture)
    fx = os.path.join(tmp, 'fixture')
    shutil.copytree(fx_src, fx)
    work = os.path.join(tmp, 'work')
    expected = load_expected_answers(os.path.join(fx, 'expected', 'answers.json'))
    print('fixture: %s\nwork:    %s' % (fx_src, work))

    failures = []
    asked = {}          # qid -> round
    unexpected = []     # (qid, who, kind, message)
    llm_defaulted = []
    repeated = []

    rc = run(['init', '--work', work, '--latest', os.path.join(fx, 'latest'),
              '--target', os.path.join(fx, 'target'), '--before', os.path.join(fx, 'before'),
              '--after', os.path.join(fx, 'after'), '--rt', 'RT2486'])
    if rc != 0:
        print('FAIL: init exit %d' % rc)
        return 1

    done = False
    for rnd in range(1, MAX_ROUNDS + 1):
        rc = run(['all', '--work', work], quiet=True)
        if rc == 0:
            done = True
            print('round %d: run.py all -> 0 (done)' % rnd)
            break
        if rc != 2:
            failures.append('run.py all exit %d in round %d' % (rc, rnd))
            break
        qpath = os.path.join(work, '.port_changelog', 'questions.json')
        with open(qpath, encoding='utf-8') as f:
            qs = json.load(f).get('questions', [])
        print('round %d: run.py all -> 2, %d question(s)' % (rnd, len(qs)))
        if not qs:
            failures.append('exit 2 but questions.json is empty (round %d)' % rnd)
            break
        for q in qs:
            qid, who, kind = q.get('id'), q.get('who', 'user'), q.get('kind')
            if qid in asked:
                repeated.append(qid)
            asked[qid] = rnd
            key = match_expected(qid, expected)
            if key is not None:
                ans, by = expected[key]['answer'], ('llm' if who == 'llm' else 'user')
                tag = 'expected' if key == qid else 'expected(prefix %s)' % key
            elif who == 'llm':
                ans, by, tag = 'Y', 'llm', 'LLM-DEFAULT'
                llm_defaulted.append((qid, kind, q.get('message', '')))
            else:
                ans, by, tag = 'Y', 'user', 'UNEXPECTED'
                unexpected.append((qid, who, kind, q.get('message', '')))
            print('  [%s] %s (who=%s) -> %s' % (tag, qid, who, ans))
            arc = run(['answer', '--work', work, '--id', qid, '--answer', ans, '--by', by], quiet=True)
            if arc != 0:
                failures.append('run.py answer exit %d for %s' % (arc, qid))
        if failures:
            break
    if not done and not failures:
        failures.append('pipeline did not finish within %d rounds' % MAX_ROUNDS)

    # target/ must never be modified in place
    tgt_problems = compare_trees(os.path.join(fx_src, 'target'), os.path.join(fx, 'target'))
    for p in tgt_problems:
        failures.append('target/ was modified: ' + p.splitlines()[0])

    out_problems = compare_trees(os.path.join(fx, 'expected', 'target_out'), os.path.join(work, 'target_out'))
    failures.extend(out_problems)

    asked_keys = {match_expected(q, expected) for q in asked}
    never = [k for k, v in expected.items() if not v['optional'] and k not in asked_keys]
    for k in never:
        failures.append('expected question never asked: %s' % k)
    for qid, who, kind, msg in unexpected:
        failures.append('UNEXPECTED question: %s (kind=%s): %s' % (qid, kind, msg))
    for qid in repeated:
        failures.append('question asked twice: %s' % qid)

    print('\n==== summary ====')
    print('questions asked: %d, unexpected(user): %d, llm-defaulted: %d' % (
        len(asked), len(unexpected), len(llm_defaulted)))
    for qid, kind, msg in llm_defaulted:
        print('  note: llm question answered Y by default: %s (%s) %s' % (qid, kind, msg))
    if failures:
        for p in failures:
            print('FAIL: ' + p)
        print('\nRESULT: FAIL (%d problem(s)); work dir kept: %s' % (len(failures), work))
        return 1
    print('RESULT: PASS')
    if not keep:
        shutil.rmtree(tmp, ignore_errors=True)
    else:
        print('work dir kept: %s' % work)
    return 0


if __name__ == '__main__':
    sys.exit(main())
