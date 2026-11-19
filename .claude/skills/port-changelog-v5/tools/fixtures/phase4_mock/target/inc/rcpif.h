/*##########################################################################*/
/*#  File   : rcpif.h                                                     #*/
/*#  Modification:                                                         #*/
/*#         2017/06/01  M.Abe (FML)          RT0900                        #*/
/*#                     Add. RcpIfBckCtlRecDef                             #*/
/*##########################################################################*/
#ifndef RCPIF_H
#define RCPIF_H

#include "eccdef.h"

#define RCP_NAME_LEN            16
#define RCP_NOTLINKEDERROR      (RCP_RECIPE_OFFSET + 15)
#define RCP_MACHINEERROR        (RCP_OTHER_OFFSET + 7)

typedef struct {
    text  className[RCP_NAME_LEN];
    unsl  attrFlag;
} RcpIfAttr;

typedef struct {
    text  className[RCP_NAME_LEN];
    text  recipeName[RCP_NAME_LEN];
    unsl  recNo;
} RcpIfBckCtlRecDef;

extern unsl RcpIfGetAllVari(unsl force, text *className, text *recipeName,
                            unsl *variCount, VariableDef **variable);
extern unsl RcpIfSetAllVari(unsl force, text *className, text *recipeName,
                            unsl variCount, VariableDef *variable);

#endif /* RCPIF_H */
