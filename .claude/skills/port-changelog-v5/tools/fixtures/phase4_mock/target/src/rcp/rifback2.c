/*##########################################################################*/
/*#  File   : rifback2.c                                                  #*/
/*#  Modification:                                                         #*/
/*#         2018/11/20  K.Ito (FML)          RT1105                        #*/
/*#                     Add. WavRcpIfGetOtherData()                        #*/
/*##########################################################################*/
#include "eccdef.h"
#include "rcpif.h"

static unsl wavRcpIfOldCheck(VariableDef *variable);

/*--------------------------------------------------------------------------*/
unsl WavRcpIfEntryOtherFile(RcpIfBckCtlRecDef *rec, unsl variCount,
                            VariableDef *variable)
{
    unsl retCode;
    unsl idx;

    retCode = wavRcpIfOldCheck(variable);
    if (retCode != NORMAL_END) {
        return retCode;
    }

    for (idx = 0; idx < variCount; idx++) {
        variable[idx].curVar = variable[idx].defVar;
    }

    retCode = RcpIfSetAllVari(ON, rec->className, rec->recipeName,
                              variCount, variable);
    return retCode;
}

/*--------------------------------------------------------------------------*/
static unsl wavRcpIfOldCheck(VariableDef *variable)
{
    if (variable == NULL) {
        return RCP_MACHINEERROR;
    }
    return NORMAL_END;
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
