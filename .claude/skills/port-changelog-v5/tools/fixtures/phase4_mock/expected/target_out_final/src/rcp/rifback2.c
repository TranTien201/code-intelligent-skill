/*##########################################################################*/
/*#  File   : rifback2.c                                                  #*/
/*#  Modification:                                                         #*/
/*#         2026/11/19  (port)               RT9001                        #*/
/*#                     Mod. WavRcpIfEntryOtherFile()                      #*/
/*#         2018/11/20  K.Ito (FML)          RT1105                        #*/
/*#                     Add. WavRcpIfGetOtherData()                        #*/
/*##########################################################################*/
#include "eccdef.h"
#include "rcpif.h"

/*--------------------------------------------------------------------------*/
unsl WavRcpIfEntryOtherFile(RcpIfBckCtlRecDef *rec, unsl variCount,
                            VariableDef *variable)
{
    unsl retCode;
    unsl idx;

    for (idx = 0; idx < variCount; idx++) {
        variable[idx].curVar = variable[idx].defVar;
    }

    if (rec->linkFlag == ON) {
        return wavRcpIfLinkOnVarSet(rec, variCount, variable);
    }

    retCode = RcpIfSetAllVari(ON, rec->className, rec->recipeName,
                              variCount, variable);
    return retCode;
}

/*--------------------------------------------------------------------------*/
static unsl wavRcpIfLinkOnVarSet(RcpIfBckCtlRecDef *rec, unsl variCount,
                                 VariableDef *variable)
{
    return RcpIfSetAllVari(ON, rec->className, rec->recipeName,
                           variCount, variable);
}

/*--------------------------------------------------------------------------*/
unsl WavRcpIfGetOtherData(RcpIfBckCtlRecDef *rec, unsl *variCount,
                          VariableDef **variable)
{
    unsl retCode;

    *variCount = 0;
    *variable  = NULL;

    retCode = RcpIfGetAllVari(ON, rec->className, rec->recipeName,
                              variCount, variable);
    if (retCode != NORMAL_END) {
        CapError(retCode, (text *)"GetOtherData", 0);
    }
    return retCode;
}
