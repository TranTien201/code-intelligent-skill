"""Sinh bộ dữ liệu giả lập firmware máy in để thử nghiệm việc port feature A -> B.

Sinh ra 4 input đúng như bài toán thật:
  data/A_latest/        source mới nhất của máy A
  data/B_latest/        source mới nhất của máy B
  data/feature_before/  các file của A TRƯỚC khi làm feature "Toner Save"
  data/feature_after/   các file đó SAU khi làm feature
và data/expected.json  = đáp án (do "dev" xác định) để chấm điểm công cụ.

Cú pháp template: dòng bắt đầu bằng "@X " chỉ giữ lại khi cờ X bật.
  A = model A, B = model B
  F = đã có feature Toner Save
  D = drift: bug-fix trên feature, làm SAU commit feature (chỉ có ở A_latest)
  E = feature Eco Report, làm SAU, phụ thuộc vào Toner Save (chỉ có ở A_latest)

Các "bẫy" được cài sẵn (giống thực tế):
  1. Phụ thuộc ẩn: toner_save.c dùng Density_Scale (src/print/density.*) - file này
     KHÔNG nằm trong diff feature, và B chưa có  -> phải tự lần ra.
  2. Chuỗi phụ thuộc nhiều tầng: Density_Scale -> DENSITY_MAX, Clamp.
  3. Xung đột: Clamp() có ở B nhưng khác chữ ký (2 tham số thay vì 3).
  4. Drift: A_latest đã fix bug trong TonerSave_ApplyDensity (thêm gọi Clamp) - diff
     before/after không thấy.
  5. #ifdef: code nằm trong SUPPORT_TONER_SAVE; B chưa define -> copy xong vẫn không chạy.
  6. Bảng đăng ký (function pointer): menu table, PJL table.
  7. Hàm static trùng tên: is_valid() ở toner_save.c và ở panel/menu.c.
  8. Phụ thuộc chiều vào: Eco Report (A-only) gọi TonerSave_GetLevel -> chỉ báo cáo, KHÔNG copy.
  9. File dùng chung đã bị B sửa riêng (FAX...) -> không được ghi đè cả file, phải merge.
 10. Nhiễu: Menu_Quality khác nhau giữa A và B nhưng không liên quan feature.
 11. Struct lưu NVRAM bị thêm field -> ảnh hưởng cao.
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# (path, điều kiện tồn tại file, template)
FILES = [
    ("Makefile", None, """\
@A MODEL ?= A
@B MODEL ?= B
@A SRCS = src/main.c src/core/log.c src/util/math_util.c src/print/density.c \\
@B SRCS = src/main.c src/core/log.c src/util/math_util.c \\
       src/settings/nv_settings.c src/print/render.c \\
       src/panel/menu.c src/panel/menu_table.c \\
       src/cmd/pjl_commands.c src/resources/strings_en.c
@F SRCS += src/features/toner_save/toner_save.c
@E SRCS += src/features/eco_report/eco_report.c

all:
\t$(CC) -Wall -DMODEL_$(MODEL) -o printer_$(MODEL) $(SRCS)
"""),
    ("config/model_config.h", None, """\
#ifndef MODEL_CONFIG_H
#define MODEL_CONFIG_H
#if defined(MODEL_A)
#include "model_a.h"
#elif defined(MODEL_B)
#include "model_b.h"
#endif
#endif
"""),
    ("config/model_a.h", "A", """\
#define MODEL_NAME "Printer-A"
#define SUPPORT_DUPLEX 1
@F #define SUPPORT_TONER_SAVE 1
@E #define SUPPORT_ECO_REPORT 1
"""),
    ("config/model_b.h", "B", """\
#define MODEL_NAME "Printer-B"
#define SUPPORT_DUPLEX 1
#define SUPPORT_FAX 1
"""),
    ("src/main.c", None, """\
#include <stdio.h>
#include "settings/nv_settings.h"
#include "print/render.h"
#include "panel/menu.h"
#include "cmd/pjl_commands.h"

int main(void)
{
    NV_LoadDefaults();
    printf("copies=%d\\n", Menu_Dispatch("COPIES", 2));
    printf("toner_save=%d\\n", Menu_Dispatch("TONER_SAVE", 2));
    printf("pjl=%d\\n", Pjl_Dispatch("ECONOMODE", "1"));
    printf("density=%d\\n", Render_Page(10));
    return 0;
}
"""),
    ("src/core/log.h", None, """\
#ifndef LOG_H
#define LOG_H
void Log_Info(const char *msg);
#endif
"""),
    ("src/core/log.c", None, """\
#include <stdio.h>
#include "log.h"

void Log_Info(const char *msg)
{
    printf("[INFO] %s\\n", msg);
}
"""),
    ("src/util/math_util.h", None, """\
#ifndef MATH_UTIL_H
#define MATH_UTIL_H
@A int Clamp(int v, int lo, int hi);
@B int Clamp(int v, int hi);
#endif
"""),
    ("src/util/math_util.c", None, """\
#include "math_util.h"

@A int Clamp(int v, int lo, int hi)
@B int Clamp(int v, int hi)
{
@A     if (v < lo) return lo;
@B     if (v < 0) return 0;
    if (v > hi) return hi;
    return v;
}
"""),
    ("src/settings/nv_settings.h", None, """\
#ifndef NV_SETTINGS_H
#define NV_SETTINGS_H

/* Struct nay duoc luu vao NVRAM */
typedef struct {
    int copies;
    int duplex;
@F     int toner_save_level;
    int language;
    int quality;
@B     int fax_resolution;
} NvSettings_t;

NvSettings_t *NV_GetSettings(void);
void NV_LoadDefaults(void);
#endif
"""),
    ("src/settings/nv_settings.c", None, """\
#include "nv_settings.h"
@F #include "../features/toner_save/toner_save.h"

static NvSettings_t g_settings;

NvSettings_t *NV_GetSettings(void)
{
    return &g_settings;
}

void NV_LoadDefaults(void)
{
    g_settings.copies = 1;
    g_settings.duplex = 0;
@F     g_settings.toner_save_level = TONER_SAVE_OFF;
    g_settings.language = 0;
    g_settings.quality = 1;
@B     g_settings.fax_resolution = 200;
}
"""),
    ("src/print/density.h", "A", """\
#ifndef DENSITY_H
#define DENSITY_H
#define DENSITY_MAX 15
int Density_Scale(int base, int percent);
#endif
"""),
    ("src/print/density.c", "A", """\
#include "density.h"
#include "../util/math_util.h"

int Density_Scale(int base, int percent)
{
    return Clamp(base * percent / 100, 0, DENSITY_MAX);
}
"""),
    ("src/print/render.h", None, """\
#ifndef RENDER_H
#define RENDER_H
int Render_Page(int density);
#endif
"""),
    ("src/print/render.c", None, """\
#include "../core/log.h"
#include "../../config/model_config.h"
@F #ifdef SUPPORT_TONER_SAVE
@F #include "../features/toner_save/toner_save.h"
@F #endif
#include "render.h"

int Render_Page(int density)
{
    Log_Info("render start");
@F #ifdef SUPPORT_TONER_SAVE
@F     density = TonerSave_ApplyDensity(density);
@F #endif
    Log_Info("render done");
@B #ifdef SUPPORT_FAX
@B     Log_Info("fax header");
@B #endif
    return density;
}
"""),
    ("src/panel/menu.h", None, """\
#ifndef MENU_H
#define MENU_H
typedef int (*MenuHandler_t)(int key);
typedef struct {
    const char *name;
    MenuHandler_t handler;
} MenuEntry_t;

int Menu_Copies(int key);
int Menu_Duplex(int key);
int Menu_Quality(int key);
int Menu_Language(int key);
@B int Menu_Fax(int key);
int Menu_Dispatch(const char *name, int key);
#endif
"""),
    ("src/panel/menu.c", None, """\
#include "menu.h"
#include "../core/log.h"
@A #include "../print/density.h"

static int is_valid(int key)
{
    return key >= 0 && key < 100;
}

int Menu_Copies(int key)
{
    return is_valid(key) ? key : 1;
}

int Menu_Duplex(int key)
{
    return key ? 1 : 0;
}

int Menu_Quality(int key)
{
@A     return Density_Scale(key, 50);
@B     Log_Info("quality");
@B     return key;
}

int Menu_Language(int key)
{
    return key;
}
@B
@B int Menu_Fax(int key)
@B {
@B     Log_Info("fax menu");
@B     return key;
@B }
"""),
    ("src/panel/menu_table.c", None, """\
#include <string.h>
#include "menu.h"
#include "../../config/model_config.h"
@F #ifdef SUPPORT_TONER_SAVE
@F #include "../features/toner_save/toner_save.h"
@F #endif
@E #ifdef SUPPORT_ECO_REPORT
@E #include "../features/eco_report/eco_report.h"
@E #endif

static const MenuEntry_t g_menu_table[] = {
    { "COPIES",   Menu_Copies },
    { "DUPLEX",   Menu_Duplex },
@F #ifdef SUPPORT_TONER_SAVE
@F     { "TONER_SAVE", TonerSave_MenuHandler },
@F #endif
    { "QUALITY",  Menu_Quality },
    { "LANGUAGE", Menu_Language },
@B     { "FAX",      Menu_Fax },
@E #ifdef SUPPORT_ECO_REPORT
@E     { "ECO_REPORT", EcoReport_MenuHandler },
@E #endif
};

int Menu_Dispatch(const char *name, int key)
{
    unsigned i;
    for (i = 0; i < sizeof(g_menu_table) / sizeof(g_menu_table[0]); i++) {
        if (strcmp(g_menu_table[i].name, name) == 0)
            return g_menu_table[i].handler(key);
    }
    return -1;
}
"""),
    ("src/cmd/pjl_commands.h", None, """\
#ifndef PJL_COMMANDS_H
#define PJL_COMMANDS_H
int Pjl_Dispatch(const char *cmd, const char *arg);
#endif
"""),
    ("src/cmd/pjl_commands.c", None, """\
#include <string.h>
#include "pjl_commands.h"
#include "../core/log.h"
@F #include "../features/toner_save/toner_save.h"

typedef int (*PjlHandler_t)(const char *arg);
typedef struct {
    const char *cmd;
    PjlHandler_t fn;
} PjlEntry_t;

static int Pjl_SetCopies(const char *arg)
{
    Log_Info(arg);
    return 0;
}

static int Pjl_SetDuplex(const char *arg)
{
    Log_Info(arg);
    return 0;
}

static const PjlEntry_t g_pjl_table[] = {
    { "COPIES", Pjl_SetCopies },
    { "DUPLEX", Pjl_SetDuplex },
@F     { "ECONOMODE", TonerSave_PjlSet },
};

int Pjl_Dispatch(const char *cmd, const char *arg)
{
    unsigned i;
    for (i = 0; i < sizeof(g_pjl_table) / sizeof(g_pjl_table[0]); i++) {
        if (strcmp(g_pjl_table[i].cmd, cmd) == 0)
            return g_pjl_table[i].fn(arg);
    }
    return -1;
}
"""),
    ("src/resources/strings.h", None, """\
#ifndef STRINGS_H
#define STRINGS_H
typedef enum {
    STR_COPIES,
    STR_DUPLEX,
@F     STR_TONER_SAVE,
    STR_QUALITY,
@B     STR_FAX,
    STR_COUNT
} StrId_t;

const char *Str_Get(StrId_t id);
#endif
"""),
    ("src/resources/strings_en.c", None, """\
#include "strings.h"

static const char *g_strings_en[STR_COUNT] = {
    [STR_COPIES] = "Copies",
    [STR_DUPLEX] = "2-Sided",
@F     [STR_TONER_SAVE] = "Toner Save",
    [STR_QUALITY] = "Quality",
@B     [STR_FAX] = "Fax",
};

const char *Str_Get(StrId_t id)
{
    return g_strings_en[id];
}
"""),
    ("src/features/toner_save/toner_save.h", "F", """\
#ifndef TONER_SAVE_H
#define TONER_SAVE_H
enum {
    TONER_SAVE_OFF = 0,
    TONER_SAVE_LOW = 1,
    TONER_SAVE_HIGH = 2
};

int TonerSave_GetLevel(void);
int TonerSave_ApplyDensity(int density);
int TonerSave_MenuHandler(int key);
int TonerSave_PjlSet(const char *arg);
#endif
"""),
    ("src/features/toner_save/toner_save.c", "F", """\
#include <stdlib.h>
#include "toner_save.h"
#include "../../settings/nv_settings.h"
#include "../../print/density.h"
#include "../../core/log.h"
#include "../../resources/strings.h"
@D #include "../../util/math_util.h"

static const int k_percent[] = { 100, 80, 60 };

static int is_valid(int level)
{
    return level >= TONER_SAVE_OFF && level <= TONER_SAVE_HIGH;
}

int TonerSave_GetLevel(void)
{
    return NV_GetSettings()->toner_save_level;
}

int TonerSave_ApplyDensity(int density)
{
    int level = TonerSave_GetLevel();
@D     level = Clamp(level, TONER_SAVE_OFF, TONER_SAVE_HIGH); /* fix #1234: NV value hong */
    if (!is_valid(level))
        return density;
    return Density_Scale(density, k_percent[level]);
}

int TonerSave_MenuHandler(int key)
{
    if (!is_valid(key))
        return -1;
    NV_GetSettings()->toner_save_level = key;
    Log_Info(Str_Get(STR_TONER_SAVE));
    return key;
}

int TonerSave_PjlSet(const char *arg)
{
    return TonerSave_MenuHandler(atoi(arg));
}
"""),
    ("src/features/eco_report/eco_report.h", "E", """\
#ifndef ECO_REPORT_H
#define ECO_REPORT_H
void EcoReport_Print(void);
int EcoReport_MenuHandler(int key);
#endif
"""),
    ("src/features/eco_report/eco_report.c", "E", """\
#include "eco_report.h"
#include "../toner_save/toner_save.h"
#include "../../core/log.h"

void EcoReport_Print(void)
{
    if (TonerSave_GetLevel() != TONER_SAVE_OFF)
        Log_Info("Eco: toner save ON");
}

int EcoReport_MenuHandler(int key)
{
    EcoReport_Print();
    return key;
}
"""),
]

VARIANTS = {
    "A_before": dict(A=True, B=False, F=False, D=False, E=False),
    "A_after":  dict(A=True, B=False, F=True,  D=False, E=False),
    "A_latest": dict(A=True, B=False, F=True,  D=True,  E=True),
    "B_latest": dict(A=False, B=True, F=False, D=False, E=False),
}

TS = "src/features/toner_save/toner_save.c"

# Đáp án: những gì một dev cẩn thận sẽ xác định khi port Toner Save sang B.
EXPECTED = {
    "add_symbols": [
        "TonerSave_GetLevel", "TonerSave_ApplyDensity", "TonerSave_MenuHandler",
        "TonerSave_PjlSet", f"is_valid@{TS}", f"k_percent@{TS}",
        "TONER_SAVE_OFF", "TONER_SAVE_LOW", "TONER_SAVE_HIGH", "STR_TONER_SAVE",
        "Density_Scale", "DENSITY_MAX",            # phụ thuộc ẩn, ngoài diff
    ],
    "merge_symbols": [
        "NvSettings_t", "NV_LoadDefaults", "Render_Page",
        "g_menu_table@src/panel/menu_table.c", "g_pjl_table@src/cmd/pjl_commands.c",
        "StrId_t", "g_strings_en@src/resources/strings_en.c",
    ],
    "conflicts": ["Clamp"],
    "guards": ["SUPPORT_TONER_SAVE"],
    "drift": ["TonerSave_ApplyDensity"],
    "report_only": ["EcoReport_Print"],
    # điểm nối nằm ngoài diff mà B có sẵn: bộ dữ liệu này KHÔNG có -> báo ra là báo động giả
    "glue_review": [],
    "must_not_copy": ["EcoReport_Print", "EcoReport_MenuHandler", "Menu_Quality",
                      "SUPPORT_ECO_REPORT"],
    "new_files": [
        "src/features/toner_save/toner_save.c", "src/features/toner_save/toner_save.h",
        "src/print/density.c", "src/print/density.h",
    ],
    "merge_files": [
        "Makefile", "src/settings/nv_settings.h", "src/settings/nv_settings.c",
        "src/print/render.c", "src/panel/menu_table.c", "src/cmd/pjl_commands.c",
        "src/resources/strings.h", "src/resources/strings_en.c",
    ],
    # NvSettings_t: struct lưu NVRAM bị thêm field. StrId_t: chèn enumerator vào GIỮA
    # danh sách -> giá trị STR_QUALITY... bị dịch, dev cũng phải kiểm tra.
    "high_impact": ["NvSettings_t", "StrId_t"],
}


def render(template: str, flags: dict) -> str:
    out = []
    for line in template.splitlines():
        if line.startswith("@") and len(line) >= 2 and line[1] in flags:
            if not flags[line[1]]:
                continue
            line = line[3:] if len(line) > 2 else ""
        out.append(line)
    return "\n".join(out) + "\n"


def write_tree(dest: Path, flags: dict) -> dict:
    files = {}
    for path, cond, tpl in FILES:
        if cond and not flags[cond]:
            continue
        files[path] = render(tpl, flags)
        p = dest / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(files[path])
    return files


def main():
    if DATA.exists():
        shutil.rmtree(DATA)
    tmp = DATA / "_tmp"
    trees = {name: write_tree(tmp / name, flags) for name, flags in VARIANTS.items()}

    for name in ("A_latest", "B_latest"):
        shutil.copytree(tmp / name, DATA / name)

    # feature_before / feature_after = chỉ các file bị feature commit chạm vào
    before, after = trees["A_before"], trees["A_after"]
    changed = sorted(p for p in set(before) | set(after) if before.get(p) != after.get(p))
    for p in changed:
        for side, tree in (("feature_before", before), ("feature_after", after)):
            if p in tree:
                f = DATA / side / p
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(tree[p])
    shutil.rmtree(tmp)

    (DATA / "expected.json").write_text(json.dumps(EXPECTED, indent=2, ensure_ascii=False))
    print(f"Đã sinh dữ liệu ở {DATA}")
    print("File thuộc feature (before/after):")
    for p in changed:
        tag = "NEW " if p not in before else "MOD "
        print("  ", tag, p)


if __name__ == "__main__":
    sys.exit(main())
