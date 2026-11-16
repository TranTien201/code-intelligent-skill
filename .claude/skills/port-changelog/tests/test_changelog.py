#!/usr/bin/env python3
"""Self-test for scripts/changelog.py. Run: python3 -I tests/test_changelog.py"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
import changelog as cl  # noqa: E402


def L(s):
    """Pad a changelog content line to the fixed-width '/*# ... #*/' form."""
    return '/*#' + s.ljust(73) + '#*/'


STAR = '/*#' + '*' * 73 + '#*/'
MOD = L('     Modification:')
RT2486 = [L('         2018/08/31  Y.Kaneko (TTS-X)     RT2486'),
          L('                     Add. artLibSetVarDate()'),
          L('                          artLibSetCsTempToVar()'),
          L('                     Mod. ArtLibGetRecipeData()'),
          L('                          ArtLibCopyRecipeName()')]
NEWER = [L('         2021/08/02  S.Kinoshita V8.14R000 RT2707'),
         L('                     Add. artLibLinkOnVarSet()'),
         L('                     Mod. ArtLibCopyRecipeName()'),
         L(' ------------------------------------------ From here TELINDY V8.14R000'),
         L('         2020/04/01  K.Ohtake (TTS)       RT2611'),
         L('                     Add. WAVMACH_VER0800_0000'),
         L('                          WAVMACH_ONLY_VER'),
         L('                          artLibConvVariApc()'),
         L('                     Mod. ArtLibEntryRecipeName()'),
         L(' -------------------------------------------- From here TELINDY V8.10R0'),
         L('         2019/11/07  H.Nakazawa V8.08R000 RT2343'),
         L('                     Mod. ArtLibGetRecipeData()'),
         L('         2019/11/01  K.Ohtake (TTS)       RT2343'),
         L('                     Add. WAVMACH_VER0700_0000'),
         L('                     Mod. ArtLibJudgeRecipeConvV700()'),
         L(' -------------------------------------------- From here TELINDY V8.08R0'),
         L('         2019/07/12  Y.Kaneko (TTS-X)     RT2586'),
         L('                     Mod. artLibAdjustOsfData()'),
         L(' -------------------------------------------- From here TELINDY V8.07R0'),
         L('         2018/10/05  Y.Kaneko (TTS-X)     RT2486:V806-0001'),
         L('                     Mod. ArtLibGetRecipeData()'),
         L(' -------------------------------------------- From here TELINDY V8.06R0')]
OLDER = [L(' -------------------------------------------- From here TELINDY V8.03R1'),
         L('         2018/04/19  Y.Kaneko (TTS-X)     RT2283:V803-0001'),
         L('                     Mod. ArtLibTempProcessGdId[][]'),
         L(' -------------------------------------------- From here TELINDY V8.03R0')]
CODE = ['#include "artlib.h"', '', 'int ArtLibGetRecipeData(void)', '{', '    return 0;', '}']
LATEST_C = [STAR, MOD] + NEWER + RT2486 + OLDER + [STAR] + CODE


def hunk(rows, start, section=''):
    o = sum(1 for t, _ in rows if t in ' -')
    n = sum(1 for t, _ in rows if t in ' +')
    return ['@@ -%d,%d +%d,%d @@ %s' % (start, o, start, n, section)] + [t + x for t, x in rows]


def write(root, rel, lines):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='latin-1', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')


def main():
    # --- parse_entries -------------------------------------------------------------------
    blk = cl.find_mod_block(LATEST_C)
    assert blk == (1, 2 + len(NEWER) + len(RT2486) + len(OLDER)), blk
    ents = cl.parse_entries(LATEST_C[blk[0]:blk[1]])
    got = [(e['rt_full'], e['date'], e['author'], e['version']) for e in ents]
    assert got == [('RT2707', '2021/08/02', 'S.Kinoshita', 'V8.14R000'),
                   ('RT2611', '2020/04/01', 'K.Ohtake (TTS)', 'V8.10R0'),
                   ('RT2343', '2019/11/07', 'H.Nakazawa', 'V8.08R000'),
                   ('RT2343', '2019/11/01', 'K.Ohtake (TTS)', 'V8.08R0'),
                   ('RT2586', '2019/07/12', 'Y.Kaneko (TTS-X)', 'V8.07R0'),
                   ('RT2486:V806-0001', '2018/10/05', 'Y.Kaneko (TTS-X)', 'V8.06R0'),
                   ('RT2486', '2018/08/31', 'Y.Kaneko (TTS-X)', 'V8.03R1'),
                   ('RT2283:V803-0001', '2018/04/19', 'Y.Kaneko (TTS-X)', 'V8.03R0')], got
    assert ents[1]['items'] == {'Add': ['WAVMACH_VER0800_0000', 'WAVMACH_ONLY_VER', 'artLibConvVariApc'],
                                'Mod': ['ArtLibEntryRecipeName']}, ents[1]['items']
    assert ents[7]['rt'] == 'RT2283' and ents[7]['items'] == {'Mod': ['ArtLibTempProcessGdId']}
    assert ents[6]['raw'] == RT2486 and cl.norm_name('X[][]') == 'X'
    assert cl.blank_mod_block(LATEST_C)[1:blk[1]] == [''] * (blk[1] - 1)

    # --- build_scope ---------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        latest = os.path.join(tmp, 'latest')
        write(latest, 'src/artlib.c', LATEST_C)
        # RT token in code but not in the Modification block -> must be out of scope
        write(latest, 'src/other.c', [STAR, MOD, NEWER[0], STAR, '/* RT2486 workaround */', 'int x;'])
        # Entry present in Latest but file not in diff -> in scope, warning
        write(latest, 'src/extra.c', [STAR, MOD] + RT2486[:2] + [STAR, 'int y;'])
        write(latest, 'inc/artlib.h', ['#define WAVMACH_ONLY_VER 1'])
        diff = ['--- a/src/artlib.c', '+++ b/src/artlib.c']
        diff += hunk([(' ', MOD)] + [('+', x) for x in RT2486] + [(' ', OLDER[0])], 2)
        diff += hunk([(' ', '{'), ('-', '    return 1;'), ('+', '    return 0;'), (' ', '}')], 20,
                     'int ArtLibGetRecipeData(void)')
        diff += hunk([(' ', '}'), ('+', 'static void artLibHelper(void) {}')], 30, 'ArtLibCopyRecipeName')
        diff += ['--- a/inc/artlib.h', '+++ b/inc/artlib.h']
        diff += hunk([('+', '#define WAVMACH_ONLY_VER 1')], 1)
        dpath = os.path.join(tmp, 'feature.diff')
        write(tmp, 'feature.diff', diff)

        fps = cl.fingerprint_from_diff(cl.parse_diff('\n'.join(diff) + '\n')[1])
        assert [f['entry']['rt'] for f in fps] == ['RT2486'], fps
        sc = cl.build_scope(dpath, latest)
        assert sc == cl.build_scope(dpath, latest, 'RT2486')
        fp = sc['fingerprint']
        assert sc['rt'] == 'RT2486' and fp['date'] == '2018/08/31' and fp['author'] == 'Y.Kaneko (TTS-X)'
        assert fp['version'] == 'V8.03R1' and fp['raw'] == RT2486 and 'offset' not in fp
        files = {f['path']: f for f in sc['files']}
        assert set(files) == {'src/artlib.c', 'inc/artlib.h', 'src/extra.c'}, files
        assert files['src/artlib.c']['has_entry'] and files['src/artlib.c']['warning'] is None
        assert files['inc/artlib.h']['in_diff'] and not files['inc/artlib.h']['has_entry']
        assert '.h' in files['inc/artlib.h']['warning']
        assert not files['src/extra.c']['in_diff'] and files['src/extra.c']['warning']

        rel = [(e['file'], e['rt'], e['date'], e['relation'], e['touches']) for e in sc['later_entries']]
        assert rel == [('src/artlib.c', 'RT2707', '2021/08/02', 'suspect', ['ArtLibCopyRecipeName']),
                       ('src/artlib.c', 'RT2611', '2020/04/01', 'symbol_source', []),
                       ('src/artlib.c', 'RT2343', '2019/11/07', 'suspect', ['ArtLibGetRecipeData']),
                       ('src/artlib.c', 'RT2343', '2019/11/01', 'symbol_source', []),
                       ('src/artlib.c', 'RT2586', '2019/07/12', 'unrelated', [])], rel
        assert [(f['rt_full'], f['touches']) for f in sc['followups']] == \
            [('RT2486:V806-0001', ['ArtLibGetRecipeData'])], sc['followups']
        assert sc['suspects'] == {'ArtLibCopyRecipeName': ['RT2707'], 'ArtLibGetRecipeData': ['RT2343']}
        ss = sc['symbol_sources']
        assert ss['artLibLinkOnVarSet'] == {'rt': 'RT2707', 'version': 'V8.14R000', 'date': '2021/08/02',
                                            'file': 'src/artlib.c', 'action': 'Add'}, ss
        assert ss['WAVMACH_VER0700_0000']['rt'] == 'RT2343' and ss['WAVMACH_ONLY_VER']['action'] == 'Add'
        assert ss['artLibAdjustOsfData']['action'] == 'Mod' and 'ArtLibTempProcessGdId' not in ss
        assert sc['rt_items'] == {'Add': ['artLibSetVarDate', 'artLibSetCsTempToVar'],
                                  'Mod': ['ArtLibGetRecipeData', 'ArtLibCopyRecipeName']}
        assert sc['diff_units'] == ['ArtLibGetRecipeData', 'ArtLibCopyRecipeName'], sc['diff_units']
        assert sc['coverage'] == {'missing_in_diff': ['artLibSetVarDate', 'artLibSetCsTempToVar'],
                                  'extra_in_diff': []}, sc['coverage']
        assert cl.main(['scope', '--diff', dpath, '--latest', latest, '--out',
                        os.path.join(tmp, 'w', 'scope.json')]) == 0

    # --- insert_entry --------------------------------------------------------------------
    target = [STAR, MOD, OLDER[0], STAR, 'int z;']
    new = cl.insert_entry(target, RT2486)
    assert new == [STAR, MOD] + RT2486 + [OLDER[0], STAR, 'int z;'], new
    assert cl.insert_entry(['int z;'], RT2486) == ['int z;']
    print('test_changelog: OK')


if __name__ == '__main__':
    main()
