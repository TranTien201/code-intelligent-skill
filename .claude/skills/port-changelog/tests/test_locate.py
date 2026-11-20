#!/usr/bin/env python3
"""Plain-assert tests for scripts/locate.py. Run: python3 -I tests/test_locate.py"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
import locate  # noqa: E402
from locate import DefIndex, decide, find_unit, line_in, locate_block, similarity  # noqa: E402

FUNC = """\
static int artLibSetVarDate(REC_T *rec, int mode)
{
    int ret = 0;
    if (rec == NULL) {
        return -1;
    }
    rec->year = gSysDate.year;
    rec->month = gSysDate.month;
    rec->day = gSysDate.day;
    if (mode == ART_MODE_EXT) {
        ret = artLibCalcExt(rec, 0x20);
    }
    artLibLog("set var date", ret);
    return ret;
}
""".splitlines()

OTHER = """\
void PanelDrawButtons(PANEL_T *pnl)
{
    int i;
    for (i = 0; i < pnl->count; i++) {
        BUTTON_T *b = &pnl->buttons[i];
        if (!b->visible) {
            continue;
        }
        gfxFillRect(b->x, b->y, b->w, b->h, COLOR_BG);
        gfxDrawText(b->x + 2, b->y + 2, b->label);
    }
    pnl->dirty = 0;
    panelFlush(pnl);
    return;
}
""".splitlines()

FILLER = ["", "/* filler */", "int gCounter = 0;", ""]
SCORES = {}


def file_with(*parts):
    out = []
    for p in parts:
        out += p + [""]
    return out


def test_similarity():
    SCORES['sim identical'] = s = similarity(FUNC, FUNC)
    assert s == 1.0, s
    mod = list(FUNC)
    mod[10] = "        ret = artLibCalcExt2(rec, 0x40, mode);"
    mod[12] = '    artLibLog("set var date ex", ret);'
    SCORES['sim 2 lines changed'] = s = similarity(FUNC, mod)
    assert s >= 0.8, s
    ren = [FUNC[0].replace('artLibSetVarDate', 'ArtLibSetVariableDate')] + FUNC[1:]
    SCORES['sim renamed'] = s = similarity(FUNC, ren)
    assert s >= 0.85, s
    SCORES['sim unrelated'] = s = similarity(FUNC, OTHER)
    assert s < 0.4, s


def test_exact_block():
    lines = file_with(FILLER, OTHER, FUNC)
    block = FUNC[6:9]
    c = locate_block(block, lines)
    assert c and c[0]["method"] == "exact" and c[0]["score"] == 1.0, c
    start = lines.index(FUNC[6]) + 1
    assert (c[0]["start"], c[0]["end"]) == (start, start + 2), c
    assert decide(c) == "auto"


def test_reformatted_block():
    lines = file_with(FILLER, FUNC)
    block = ["  if(mode==ART_MODE_EXT){   /* extended */",
             "", "        ret=artLibCalcExt( rec,0x20 ) ;  // calc", "}"]
    c = locate_block(block, lines)
    assert c and c[0]["method"] == "normalized" and c[0]["score"] == 1.0, c
    start = lines.index(FUNC[9]) + 1
    assert (c[0]["start"], c[0]["end"]) == (start, start + 2), c
    assert decide(c) == "auto"


def test_one_line_modified():
    lines = file_with(FILLER, OTHER, FUNC)
    block = list(FUNC[2:14])
    block[5] = "    rec->month = gSysDate.month + 1;"
    c = locate_block(block, lines)
    SCORES['block 1 line modified'] = c[0]["score"]
    start = lines.index(FUNC[2]) + 1
    assert abs(c[0]["start"] - start) <= 1 and abs(c[0]["end"] - (start + 11)) <= 1, c
    assert decide(c) in ("auto", "llm"), c
    # short (1-line) block with a small edit
    c1 = locate_block(['    ret = artLibCalcExt(rec, 0x21);'], lines)
    SCORES['block 1-line modified'] = c1[0]["score"]
    assert c1[0]["start"] == lines.index(FUNC[10]) + 1, c1
    assert decide(c1) in ("auto", "llm"), c1


def test_not_found():
    lines = file_with(FILLER, OTHER)
    c = locate_block(FUNC[6:13], lines)
    SCORES['block in unrelated code'] = c[0]["score"] if c else 0.0
    assert decide(c) == "ask", c


def test_ambiguous():
    dup = ["    rec->year = gSysDate.year;", "    rec->month = gSysDate.month;"]
    lines = file_with(FILLER, ["void a(REC_T *rec)", "{"] + dup + ["}"],
                      ["void b(REC_T *rec)", "{"] + dup + ["}"])
    c = locate_block(dup, lines)
    assert len(c) == 2 and decide(c) != "auto", c


def test_find_unit_and_index():
    with tempfile.TemporaryDirectory() as root:
        renamed = [FUNC[0].replace('artLibSetVarDate', 'artLibSetVarDateEx')] + FUNC[1:]
        src = ["#include \"art.h\"", "", "#define ART_MAX_REC  (16)", "",
               "typedef enum {", "    ART_MODE_NONE = 0,", "    ART_MODE_EXT,", "} ART_MODE_E;", ""] \
            + renamed + [""] + OTHER
        with open(os.path.join(root, 'art.c'), 'w') as f:
            f.write("\n".join(src) + "\n")
        idx = DefIndex(root)
        assert [u.kind for _, u in idx.defs('ART_MAX_REC')] == ['macro']
        assert [u.name for _, u in idx.defs('PanelDrawButtons')] == ['PanelDrawButtons']
        enum = idx.defs('ART_MODE_EXT')
        assert len(enum) == 1 and enum[0][1].name == 'ART_MODE_E', enum
        assert idx.has('ART_MODE_E') and not idx.has('nope_symbol')
        r = find_unit('PanelDrawButtons', 'func', OTHER, root, index=idx)
        assert r["status"] == "found" and r["method"] == "name" and r["score"] == 1.0, r
        r = find_unit('artLibSetVarDate', 'func', FUNC, root, index=idx)
        SCORES['find_unit renamed'] = r["score"]
        assert r["status"] == "renamed" and r["unit"].name == 'artLibSetVarDateEx', r
        assert r["candidates"][0]["name"] == 'artLibSetVarDateEx' and len(r["candidates"]) <= 3
        r = find_unit('noSuchFunc', 'func', ["int x(void) { return 42 + y * z; }"], root, index=idx)
        assert r["status"] == "missing", r


def test_decide_and_line_in():
    assert decide([]) == "ask"
    assert decide([{"score": 0.95}]) == "auto"
    assert decide([{"score": 0.95}, {"score": 0.9}]) == "llm"
    assert decide([{"score": 0.95}, {"score": 0.8}]) == "auto"
    assert decide([{"score": 0.7}]) == "llm"
    assert decide([{"score": 0.5}]) == "ask"
    assert line_in("  ret=0;  /* x */", ["int a;", "ret=0;"])
    assert not line_in("ret = 1;", ["ret=0;"])


if __name__ == '__main__':
    for name, fn in list(globals().items()):
        if name.startswith('test_') and callable(fn):
            fn()
            print('ok', name)
    for k, v in SCORES.items():
        print('  %-24s %.4f' % (k, v))
    print('ALL OK (locate %s)' % os.path.basename(locate.__file__))
