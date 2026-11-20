import sys, os
RA = sys.argv[1]; W = sys.argv[2]
# (H, file, header, brange, arange, point, symbol, fstatus, file_status, plus_start, plus_end)
P = [
("H001","Makefile","@@ -2,7 +2,8 @@ MODEL ?= A","2,7","2,8","p1","N/A (non-code file)","unknown","modified",6,6),
("H002","config/model_a.h","@@ -1,2 +1,3 @@","1,2","1,3","p1","SUPPORT_TONER_SAVE (macro)","added","modified",3,3),
("H003","src/cmd/pjl_commands.c","@@ -1,6 +1,7 @@","1,6","1,7","p1","file scope (file scope)","modified","modified",4,4),
("H004","src/cmd/pjl_commands.c","@@ -23,6 +24,7 @@","23,6","24,7","p1","g_pjl_table (table)","modified","modified",27,27),
("H005","src/features/toner_save/toner_save.c","@@ -0,0 +1,40 @@","0,0","1,40","p1","file scope (file scope)","added","added",1,7),
("H005","src/features/toner_save/toner_save.c","@@ -0,0 +1,40 @@","0,0","1,40","p2","k_percent (global)","added","added",8,9),
("H005","src/features/toner_save/toner_save.c","@@ -0,0 +1,40 @@","0,0","1,40","p3","is_valid (function)","added","added",10,14),
("H005","src/features/toner_save/toner_save.c","@@ -0,0 +1,40 @@","0,0","1,40","p4","TonerSave_GetLevel (function)","added","added",15,19),
("H005","src/features/toner_save/toner_save.c","@@ -0,0 +1,40 @@","0,0","1,40","p5","TonerSave_ApplyDensity (function)","added","added",20,27),
("H005","src/features/toner_save/toner_save.c","@@ -0,0 +1,40 @@","0,0","1,40","p6","TonerSave_MenuHandler (function)","added","added",28,36),
("H005","src/features/toner_save/toner_save.c","@@ -0,0 +1,40 @@","0,0","1,40","p7","TonerSave_PjlSet (function)","added","added",37,40),
("H006","src/features/toner_save/toner_save.h","@@ -0,0 +1,13 @@","0,0","1,13","p1","TONER_SAVE_H (preprocessor)","added","added",1,2),
("H006","src/features/toner_save/toner_save.h","@@ -0,0 +1,13 @@","0,0","1,13","p2","TONER_SAVE_OFF/LOW/HIGH (enum)","added","added",3,8),
("H006","src/features/toner_save/toner_save.h","@@ -0,0 +1,13 @@","0,0","1,13","p3","TonerSave_GetLevel (prototype)","added","added",9,9),
("H006","src/features/toner_save/toner_save.h","@@ -0,0 +1,13 @@","0,0","1,13","p4","TonerSave_ApplyDensity (prototype)","added","added",10,10),
("H006","src/features/toner_save/toner_save.h","@@ -0,0 +1,13 @@","0,0","1,13","p5","TonerSave_MenuHandler (prototype)","added","added",11,11),
("H006","src/features/toner_save/toner_save.h","@@ -0,0 +1,13 @@","0,0","1,13","p6","TonerSave_PjlSet (prototype)","added","added",12,12),
("H006","src/features/toner_save/toner_save.h","@@ -0,0 +1,13 @@","0,0","1,13","p7","TONER_SAVE_H (preprocessor)","added","added",13,13),
("H007","src/panel/menu_table.c","@@ -1,10 +1,16 @@","1,10","1,16","p1","file scope (file scope)","modified","modified",4,6),
("H007","src/panel/menu_table.c","@@ -1,10 +1,16 @@","1,10","1,16","p2","g_menu_table (table)","modified","modified",11,13),
("H008","src/print/render.c","@@ -1,10 +1,16 @@","1,10","1,16","p1","file scope (file scope)","modified","modified",3,5),
("H008","src/print/render.c","@@ -1,10 +1,16 @@","1,10","1,16","p2","Render_Page (function)","modified","modified",11,13),
("H009","src/resources/strings.h","@@ -3,6 +3,7 @@","3,6","3,7","p1","StrId_t (enum)","modified","modified",6,6),
("H010","src/resources/strings_en.c","@@ -1,8 +1,9 @@","1,8","1,9","p1","g_strings_en (table)","modified","modified",6,6),
("H011","src/settings/nv_settings.c","@@ -1,4 +1,5 @@","1,4","1,5","p1","file scope (file scope)","modified","modified",2,2),
("H012","src/settings/nv_settings.c","@@ -10,7 +11,8 @@","10,7","11,8","p1","NV_LoadDefaults (function)","modified","modified",15,15),
("H013","src/settings/nv_settings.h","@@ -4,7 +4,8 @@","4,7","4,8","p1","NvSettings_t (struct)","modified","modified",8,8),
]
def lines(f): return open(os.path.join(RA,f)).read().split("\n")
def esc(s): return s.replace("|","\\|")
def cell(f,a,b):
    L=lines(f); n=b-a+1
    items=[f"L{i}: `{esc(L[i-1])}`" if L[i-1].strip() else f"L{i}: (blank)" for i in range(a,b+1)]
    if n<=3: return "<br>".join(items)
    return "<br>".join(items[:2])+f"<br>… (+{n-2} lines, {{H}})"
hunks=["| H-id | file | hunk header | before range | after range | point | symbol (kind) | function_status | -lines | +lines | manifest No |","|---|---|---|---|---|---|---|---|---|---|---|"]
man=["| No | file | file_status | function | function_status | Modified_line_before | Modified_line_after |","|---:|---|---|---|---|---|---|"]
no=0
for (h,f,hdr,br,ar,p,sym,fs,fst,a,b) in P:
    no+=1
    hunks.append(f"| {h} | `{f}` | `{esc(hdr)}` | {br} | {ar} | {p} | {sym} | {fs} | 0 | {b-a+1} (L{a}-L{b}) | {no} |")
    if sym.startswith("N/A"):
        man.append(f"| {no} | `{f}` | {fst} | N/A (non-code file) | unknown | N/A | N/A |")
    else:
        man.append(f"| {no} | `{f}` | {fst} | {sym} | {fs} | N/A | {cell(f,a,b).replace('{H}',h)} |")
open(os.path.join(W,"A_hunks.md"),"w").write("# A_hunks\n\n"+"\n".join(hunks)+"\n\nAll points are pure additions (0 `-` lines). Blank `+` lines are attached to the preceding point (H005, H006).\n")
# line-level
ll=[]
cur=None
for (h,f,hdr,br,ar,p,sym,fs,fst,a,b) in P:
    if sym.startswith("N/A"): continue
    if f!=cur:
        cur=f; ll.append(f"\n#### `{f}`\n| H-id | Modified_Before (-) | Modified_After (+) |\n|---|---|---|")
    L=lines(f)
    for i in range(a,b+1):
        t=L[i-1]
        ll.append(f"| {h} |  | L{i}: `{esc(t)}` |" if t.strip() else f"| {h} |  | L{i}: (blank) |")
open(os.path.join(W,"A_manifest.part.md"),"w").write("\n".join(man)+"\n")
open(os.path.join(W,"A_lineLevel.part.md"),"w").write("\n".join(ll).lstrip("\n")+"\n")
print(no,"rows")
