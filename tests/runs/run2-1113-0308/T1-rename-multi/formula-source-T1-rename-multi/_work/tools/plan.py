import json,sys,os
SRC=sys.argv[1]; TGT=sys.argv[2]; W=sys.argv[3]
def sl(p,a,b): return open(os.path.join(SRC,p)).read().split('\n')[a-1:b]
def tl(p,n): return open(os.path.join(TGT,p)).read().split('\n')[n-1]
# P: id, M, file, action, anchor(file,line) or None, srcref, text(lines), adaptation, mode(insert-after|replace|add-file|append)
P=[
("P001","M006","config/model_b.h","add-define",3,"SRC:config/model_a.h:3",sl("config/model_a.h",3,3),"position AUTO-DECIDED: appended after last feature define (TGT:config/model_b.h:3); request also appended at end of model_a.h","insert-after"),
("P002","M005","src/util/math_util.h","replace",3,"SRC:src/util/math_util.h:3",sl("src/util/math_util.h",3,3),"none (REPLACE row 14: target prototype `int Clamp(int v, int hi);` replaced)","replace"),
("P003","M005","src/util/math_util.c","replace",3,"SRC:src/util/math_util.c:3-5",sl("src/util/math_util.c",3,5),"none (REPLACE row 14: target L3-5 replaced; L4 `{` identical)","replace3"),
("P004","M004","src/print/density.h","add-file",None,"SRC:src/print/density.h:1-5",sl("src/print/density.h",1,5),"none","add-file"),
("P005","M004","src/print/density.c","add-file",None,"SRC:src/print/density.c:1-7",sl("src/print/density.c",1,7),"none","add-file"),
("P006","M003","src/features/eco/eco_mode.h","add-file",None,"SRC:src/features/eco/eco_mode.h:1-13",sl("src/features/eco/eco_mode.h",1,13),"none","add-file"),
("P007","M001","src/features/eco/eco_mode.c","add-file",None,"SRC:src/features/eco/eco_mode.c:1-20,28-48",sl("src/features/eco/eco_mode.c",1,20)+sl("src/features/eco/eco_mode.c",28,48),"none (file written together with P008 as SRC:src/features/eco/eco_mode.c:1-48)","add-file"),
("P008","M002","src/features/eco/eco_mode.c","insert",None,"SRC:src/features/eco/eco_mode.c:21-27",sl("src/features/eco/eco_mode.c",21,27),"none; ext (scope beyond request), inserted between EcoMode_GetLevel and EcoMode_ApplyDensity as in source","ext-in-file"),
("P009","M019","src/settings/nv_settings.h","insert",7,"SRC:src/settings/nv_settings.h:8",sl("src/settings/nv_settings.h",8,8),"none; target-only `fax_resolution` kept","insert-after"),
("P010","M015","src/resources/strings.h","insert",5,"SRC:src/resources/strings.h:6",sl("src/resources/strings.h",6,6),"none; target-only `STR_FAX` kept","insert-after"),
("P011","M016","src/resources/strings_en.c","insert",5,"SRC:src/resources/strings_en.c:6",sl("src/resources/strings_en.c",6,6),"none; target-only `[STR_FAX]` kept","insert-after"),
("P012","M017","src/settings/nv_settings.c","add-include",1,"SRC:src/settings/nv_settings.c:2",sl("src/settings/nv_settings.c",2,2),"none","insert-after"),
("P013","M018","src/settings/nv_settings.c","insert",13,"SRC:src/settings/nv_settings.c:15",sl("src/settings/nv_settings.c",15,15),"none; target-only fax default kept","insert-after"),
("P014","M009","src/cmd/pjl_commands.c","add-include",3,"SRC:src/cmd/pjl_commands.c:4",sl("src/cmd/pjl_commands.c",4,4),"none","insert-after"),
("P015","M010","src/cmd/pjl_commands.c","add-registration",25,"SRC:src/cmd/pjl_commands.c:27",sl("src/cmd/pjl_commands.c",27,27),"none","insert-after"),
("P016","M011","src/panel/menu_table.c","add-include",3,"SRC:src/panel/menu_table.c:4-6",sl("src/panel/menu_table.c",4,6),"partial take: SRC:src/panel/menu_table.c:7-9 (eco_report include) excluded","insert-after"),
("P017","M012","src/panel/menu_table.c","add-registration",7,"SRC:src/panel/menu_table.c:14-16",sl("src/panel/menu_table.c",14,16),"partial take: SRC:src/panel/menu_table.c:19-21 (ECO_REPORT entry) excluded; target-only FAX entry kept","insert-after"),
("P018","M013","src/print/render.c","add-include",2,"SRC:src/print/render.c:3-5",sl("src/print/render.c",3,5),"none","insert-after"),
("P019","M014","src/print/render.c","insert",7,"SRC:src/print/render.c:11-13",sl("src/print/render.c",11,13),"none; target-only SUPPORT_FAX block kept after \"render done\"","insert-after"),
("P020","M007","Makefile","add-to-build",5,"SRC:Makefile:6",sl("Makefile",6,6),"partial take: SRC:Makefile:7 (eco_report.c) excluded","insert-after"),
("P021","M008","Makefile","add-to-build",5,"SRC:Makefile:2 (density.c entry)",["SRCS += src/print/density.c"],"AUTO-DECIDED: source lists density.c inside `SRCS =` (SRC:Makefile:2); added as own `SRCS +=` line after P020 so existing target lines stay untouched","insert-after-P020"),
]
out=[]; js=[]
for (pid,m,f,act,ln,src,txt,adp,mode) in P:
    anc = ("TGT:%s:%d `%s`"%(f,ln,tl(f,ln))) if ln else "(new file)"
    if mode=="ext-in-file": anc="P007 file, after SRC line 20 (blank after EcoMode_GetLevel) – new file"
    out.append("### %s (%s) – %s %s\n- anchor: %s\n- mode: %s\n- content source: %s\n- adaptation: %s\n- label: none\n```c\n%s\n```\n"%(pid,m,act,f,anc,mode,src,adp,"\n".join(txt)))
    js.append(dict(pid=pid,m=m,file=f,action=act,anchor_line=ln,anchor_text=(tl(f,ln) if ln else None),mode=mode,src=src,text=txt,adaptation=adp))
open(os.path.join(W,"D_plan.texts.md"),"w").write("\n".join(out))
json.dump(js,open(os.path.join(W,"D_plan.json"),"w"),indent=1)
for (pid,m,f,act,ln,src,txt,adp,mode) in P:
    anc=("TGT:%s:%d `%s`"%(f,ln,tl(f,ln).replace('|','\\|'))) if ln else "(new file)"
    print("| %s | `%s` | %s | %s | %s | %s | none |"%(pid,f,act,anc,src,adp.replace('|','\\|')))
