#!/usr/bin/env python3
"""Build tests/cases/T1-rename-multi from T0-toner-save.

REQ (Before/After) and B_latest are copied unchanged: the request is history, B never had the feature.
A_latest and golden/After get the SAME later evolution (the manual porter copies A_latest code):
  1. file moved + renamed   src/features/toner_save/toner_save.{c,h} -> src/features/eco/eco_mode.{c,h}
  2. function prefix rename TonerSave_*  -> EcoMode_*
  3. field rename           toner_save_level -> eco_level
  4. header guard rename    TONER_SAVE_H -> ECO_MODE_H
  5. split                  EcoMode_ApplyDensity -> EcoMode_ApplyDensity + static eco_effective_level()
Stable things kept on purpose (anchors): STR_TONER_SAVE, "Toner Save", menu key "TONER_SAVE", PJL "ECONOMODE",
SUPPORT_TONER_SAVE, enum TONER_SAVE_*, k_percent literals, the "fix #1234" comment.
Usage: python3 tests/tools/make_t1_rename_multi.py   (overwrites tests/cases/T1-rename-multi)
"""
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'cases', 'T0-toner-save')
DST = os.path.join(ROOT, 'cases', 'T1-rename-multi')

OLD_DIR, NEW_DIR = 'src/features/toner_save', 'src/features/eco'
MOVES = {OLD_DIR + '/toner_save.c': NEW_DIR + '/eco_mode.c', OLD_DIR + '/toner_save.h': NEW_DIR + '/eco_mode.h'}

TEXT_SUBS = [  # applied in order, whole text of every text file of the evolved trees
    ('features/toner_save/toner_save.c', 'features/eco/eco_mode.c'),   # Makefile
    ('features/toner_save/toner_save.h', 'features/eco/eco_mode.h'),   # includes from src/<dir>/
    ('"../toner_save/toner_save.h"', '"../eco/eco_mode.h"'),           # include from src/features/<x>/
    ('#include "toner_save.h"', '#include "eco_mode.h"'),
]
WORD_SUBS = [(r'\bTonerSave_', 'EcoMode_'), (r'\btoner_save_level\b', 'eco_level'), (r'\bTONER_SAVE_H\b', 'ECO_MODE_H')]

OLD_APPLY = """int EcoMode_ApplyDensity(int density)
{
    int level = EcoMode_GetLevel();
    level = Clamp(level, TONER_SAVE_OFF, TONER_SAVE_HIGH); /* fix #1234: NV value hong */
    if (!is_valid(level))
        return density;
    return Density_Scale(density, k_percent[level]);
}
"""
NEW_APPLY = """static int eco_effective_level(void)
{
    int level = EcoMode_GetLevel();
    level = Clamp(level, TONER_SAVE_OFF, TONER_SAVE_HIGH); /* fix #1234: NV value hong */
    return is_valid(level) ? level : -1;
}

int EcoMode_ApplyDensity(int density)
{
    int level = eco_effective_level();
    if (level < 0)
        return density;
    return Density_Scale(density, k_percent[level]);
}
"""


def evolve(tree):
    for old, new in MOVES.items():
        o, n = os.path.join(tree, old), os.path.join(tree, new)
        if os.path.exists(o):
            os.makedirs(os.path.dirname(n), exist_ok=True)
            shutil.move(o, n)
    old_dir = os.path.join(tree, OLD_DIR)
    if os.path.isdir(old_dir) and not os.listdir(old_dir):
        os.rmdir(old_dir)
    for d, _, fs in os.walk(tree):
        for f in fs:
            p = os.path.join(d, f)
            data = open(p, 'rb').read()
            try:
                t = data.decode('utf-8')
            except UnicodeDecodeError:
                continue
            u = t
            for a, b in TEXT_SUBS:
                u = u.replace(a, b)
            for a, b in WORD_SUBS:
                u = re.sub(a, b, u)
            if p.endswith(NEW_DIR.replace('/', os.sep) + os.sep + 'eco_mode.c'):
                assert OLD_APPLY in u, 'split anchor not found in ' + p
                u = u.replace(OLD_APPLY, NEW_APPLY)
            if u != t:
                open(p, 'wb').write(u.encode('utf-8'))


def main():
    if os.path.exists(DST):
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST, ignore=shutil.ignore_patterns('.DS_Store'))
    evolve(os.path.join(DST, 'input', 'A_latest'))
    evolve(os.path.join(DST, 'golden', 'After'))
    # B_latest must not contain any renamed token (sanity: the evolution only touched ported lines)
    for d, _, fs in os.walk(os.path.join(DST, 'input', 'B_latest')):
        for f in fs:
            t = open(os.path.join(d, f), 'rb').read()
            assert b'TonerSave_' not in t and b'toner_save_level' not in t, f
    print('built', DST)


if __name__ == '__main__':
    main()
