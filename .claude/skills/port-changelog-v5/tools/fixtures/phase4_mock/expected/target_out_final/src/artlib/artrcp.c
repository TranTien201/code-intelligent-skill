/*##########################################################################*/
/*#  File   : artrcp.c                                                    #*/
/*#  Modification:                                                         #*/
/*#         2026/11/19  (port)               RT9001                        #*/
/*#                     Mod. artLibCheckName()                             #*/
/*#         2019/04/02  T.Sato (FML)         RT1200                        #*/
/*#                     Mod. ArtLibCopyRecipeName()                        #*/
/*##########################################################################*/
#include "eccdef.h"
#include "rcpif.h"

static text ArtLibMsg[128];

static unsl artLibFreeFollowData(VariableDef *variable);
static unsl artLibCheckName(text *name);
static void artLibLinkOnVarSet(text *className, text *recipeName,
                               VariableDef *variable);

/*--------------------------------------------------------------------------*/
unsl ArtLibCopyRecipeName(text *classNameOrg, text *recipeNameOrg,
                          text *classNameNew, text *recipeNameNew)
{
    unsl         retCode;
    unsl         variCount;
    VariableDef *variable;
    RcpIfAttr    attr;

    variCount = 0;
    variable  = NULL;

    retCode = artLibCheckName(recipeNameNew);
    if (retCode != NORMAL_END) {
        return retCode;
    }

    retCode = RcpIfGetAllVari(ON, classNameOrg, recipeNameOrg,
                              &variCount, &variable);
    if ((retCode != NORMAL_END) && (retCode != RCP_NOTLINKEDERROR)) {
        CapError(retCode, ArtLibMsg, 0);
        return retCode;
    }

    if (retCode == NORMAL_END) {
        retCode = RcpIfGetAttrClassName(classNameNew, recipeNameNew, &attr);
        if ((retCode == NORMAL_END) && (attr.Linked == ON)) {
            artLibLinkOnVarSet(classNameNew, recipeNameNew, variable);
        } else {
            retCode = RcpIfSetAllVariForce(ON, classNameNew, recipeNameNew,
                                           variCount, variable);
        }
    }

    artLibFreeFollowData(variable);
    return retCode;
}

/*--------------------------------------------------------------------------*/
static unsl artLibFreeFollowData(VariableDef *variable)
{
    if (variable != NULL) {
        MemFree((const intb *)variable);
    }
    return NORMAL_END;
}

/*--------------------------------------------------------------------------*/
static void artLibLinkOnVarSet(text *className, text *recipeName,
                               VariableDef *variable)
{
    unsl retCode;

    retCode = RcpIfSetAllVari(ON, className, recipeName, 1, variable);
    if (retCode != NORMAL_END) {
        CapError(retCode, ArtLibMsg, 0);
    }
}

/*--------------------------------------------------------------------------*/
static unsl artLibCheckName(text *name)
{
    if (name == NULL || name[0] == '\0') {
        return RCP_MACHINEERROR;
    }
    if (strlen(name) < RCP_NAME_MIN) {
        return RCP_LINKEDIDOVER;
    }
    return NORMAL_END;
}
