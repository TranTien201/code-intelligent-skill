/*##########################################################################*/
/*#  File   : rcpif.h                                                     #*/
/*#  Modification:                                                         #*/
/*#         2026/11/19  (port)               RT9001                        #*/
/*#                     Add. RCP_LINKEDIDOVER                              #*/
/*#                          RCP_NAME_MIN                                  #*/
/*#         2017/06/01  M.Abe (FML)          RT0900                        #*/
/*#                     Add. RcpIfBckCtlRecDef                             #*/
/*##########################################################################*/
#ifndef RCPIF_H
#define RCPIF_H

#include "eccdef.h"

#define RCP_NAME_LEN            16
#define RCP_NOTLINKEDERROR      (RCP_RECIPE_OFFSET + 15)
#define RCP_LINKEDIDOVER        (RCP_RECIPE_OFFSET + 16)
#define RCP_MACHINEERROR        (RCP_OTHER_OFFSET + 7)
#define RCP_NAME_MIN            1

typedef struct {
    text  className[RCP_NAME_LEN];
    unsl  attrFlag;
    unsl  Linked;
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
