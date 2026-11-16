#!/usr/bin/env python3
"""port-changelog driver.

  run.py init  --work W --latest L --target T (--diff D | --before B --after A) [--rt RT]
  run.py step0|step1|step2|step3 --work W [--build-cmd CMD]
  run.py all   --work W [--build-cmd CMD]   # from the first unfinished step; stops at exit 2
  run.py answer --work W --id ID --answer A [--by user|llm] [--note TEXT]
  run.py questions --work W

Exit codes: 0 done, 2 questions pending, 1 error.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import diff_dirs, set_header_note, parse_diff, render_diff  # noqa: E402

STATE = '.port_changelog'
STEP_SCRIPTS = {1: 'carry.py', 2: 'merge_target.py', 3: 'verify.py'}


def st(work, name):
    return os.path.join(work, STATE, name)


def load(path, default):
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return default


def save(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def progress(work):
    return load(st(work, 'progress.json'), {'done': []})


def mark(work, step, ok):
    p = progress(work)
    done = [s for s in p['done'] if s < step] if not ok else sorted(set(p['done']) | {step})
    if ok:
        done = [s for s in done if s <= step]     # a re-run step invalidates later ones
    p['done'] = done
    save(st(work, 'progress.json'), p)


# ----------------------------------------------------------------------------------------------
def cmd_init(a):
    work = os.path.abspath(a.work)
    os.makedirs(os.path.join(work, STATE), exist_ok=True)
    if a.diff:
        with open(a.diff, encoding='latin-1') as f:
            text = f.read()
    elif a.before and a.after:
        text = diff_dirs(a.before, a.after)
    else:
        print('Cần --diff hoặc --before/--after', file=sys.stderr)
        return 1
    g, files = parse_diff(text)
    if not files:
        print('File diff rỗng hoặc không đọc được.', file=sys.stderr)
        return 1
    set_header_note(g, 'stage', 'original')
    text = render_diff(files, g)
    for name in ('feature.orig.diff', 'feature.diff'):
        with open(os.path.join(work, name), 'w', encoding='latin-1', newline='\n') as f:
            f.write(text)
    save(st(work, 'config.json'), {'latest': os.path.abspath(a.latest), 'target': os.path.abspath(a.target),
                                   'rt': a.rt, 'k': 3, 'hi': 0.9, 'lo': 0.6})
    if not os.path.exists(st(work, 'answers.json')):
        save(st(work, 'answers.json'), {})
    save(st(work, 'progress.json'), {'done': []})
    save(st(work, 'questions.json'), {'step': 0, 'questions': []})
    print('Đã khởi tạo %s (%d file trong diff). Bản gốc: feature.orig.diff' % (work, len(files)))
    return 0


def cmd_step0(work):
    import changelog
    cfg = load(st(work, 'config.json'), {})
    scope = changelog.build_scope(os.path.join(work, 'feature.orig.diff'), cfg['latest'], cfg.get('rt'))
    save(st(work, 'scope.json'), scope)
    if not cfg.get('rt'):
        cfg['rt'] = scope.get('rt')
        save(st(work, 'config.json'), cfg)
    later = scope.get('later_entries', [])
    print('Bước 0: RT=%s | %d file làm việc | %d thay đổi về sau (%d nghi vấn) | %d bản sửa tiếp cùng RT'
          % (scope.get('rt'), len(scope.get('files', [])), len(later),
             sum(1 for e in later if e.get('relation') == 'suspect'), len(scope.get('followups', []))))
    for f in scope.get('files', []):
        if f.get('warning'):
            print('  ! %s: %s' % (f['path'], f['warning']))
    for name, rts in sorted(scope.get('suspects', {}).items()):
        print('  nghi vấn: %s <- %s' % (name, ', '.join(rts)))
    cov = scope.get('coverage', {})
    if cov.get('missing_in_diff'):
        print('  ! changelog có nhưng diff không có: %s' % ', '.join(cov['missing_in_diff']))
    save(st(work, 'questions.json'), {'step': 0, 'questions': []})
    return 0


def run_script(work, step, extra=()):
    r = subprocess.run([sys.executable, '-I', os.path.join(HERE, STEP_SCRIPTS[step]), '--work', work] + list(extra))
    return r.returncode


def cmd_step(work, step, build_cmd=None):
    if step == 0:
        try:
            rc = cmd_step0(work)
        except Exception as e:
            print('LỖI bước 0: %s' % e, file=sys.stderr)
            rc = 1
    else:
        extra = ['--build-cmd', build_cmd] if (step == 3 and build_cmd) else []
        rc = run_script(work, step, extra)
    mark(work, step, rc == 0)
    if rc == 2:
        print_questions(work)
    return rc


def cmd_all(work, build_cmd=None):
    done = set(progress(work)['done'])
    for step in range(4):
        if step in done:
            continue
        rc = cmd_step(work, step, build_cmd)
        if rc != 0:
            return rc
    print('Hoàn tất: feature.diff (stage=merged) và target_out/.')
    return 0


def cmd_answer(a):
    work = os.path.abspath(a.work)
    ans = load(st(work, 'answers.json'), {})
    ans[a.id] = {'answer': a.answer, 'by': a.by, 'note': a.note or ''}
    save(st(work, 'answers.json'), ans)
    step = int(a.id[1]) if a.id.startswith('s') and a.id[1:2].isdigit() else 1
    p = progress(work)
    p['done'] = [s for s in p['done'] if s < step]
    save(st(work, 'progress.json'), p)
    print('Đã ghi câu trả lời %s = %s' % (a.id, a.answer))
    return 0


def print_questions(work):
    q = load(st(work, 'questions.json'), {'questions': []})
    ans = load(st(work, 'answers.json'), {})
    open_q = [x for x in q.get('questions', []) if x['id'] not in ans]
    if not open_q:
        print('Không có câu hỏi nào đang chờ.')
        return 0
    print('Bước %s — %d câu hỏi đang chờ:' % (q.get('step'), len(open_q)))
    for x in open_q:
        print('- [%s] %s' % ('LLM tự đánh giá' if x.get('who') == 'llm' else 'HỎI NGƯỜI DÙNG', x['id']))
        print('  %s' % x['message'])
        ctx = x.get('context', {})
        if ctx.get('rt_hint'):
            print('  Gợi ý changelog: %s' % ctx['rt_hint'])
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description='port-changelog driver')
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('init')
    p.add_argument('--work', required=True)
    p.add_argument('--latest', required=True)
    p.add_argument('--target', required=True)
    p.add_argument('--diff')
    p.add_argument('--before')
    p.add_argument('--after')
    p.add_argument('--rt')
    for name in ('step0', 'step1', 'step2', 'step3', 'all', 'questions'):
        p = sub.add_parser(name)
        p.add_argument('--work', required=True)
        p.add_argument('--build-cmd')
    p = sub.add_parser('answer')
    p.add_argument('--work', required=True)
    p.add_argument('--id', required=True)
    p.add_argument('--answer', required=True)
    p.add_argument('--by', default='user', choices=['user', 'llm'])
    p.add_argument('--note')
    a = ap.parse_args(argv)
    if a.cmd == 'init':
        return cmd_init(a)
    if a.cmd == 'answer':
        return cmd_answer(a)
    work = os.path.abspath(a.work)
    if not os.path.isdir(os.path.join(work, STATE)):
        print('Chưa init thư mục làm việc: %s' % work, file=sys.stderr)
        return 1
    if a.cmd == 'questions':
        return print_questions(work)
    if a.cmd == 'all':
        return cmd_all(work, a.build_cmd)
    return cmd_step(work, int(a.cmd[-1]), a.build_cmd)


if __name__ == '__main__':
    sys.exit(main())
