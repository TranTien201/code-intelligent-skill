/*#*************************************************************************#*/
/*#     File Name   : artmain.c                                             #*/
/*#     Function    : Recipe main control                                   #*/
/*#*************************************************************************#*/
/*#     Modification:                                                       #*/
/*# -------------------------------------------- From here TELINDY V8.03R1  #*/
/*#         2019/06/05  H.Nakazawa           RT2402                         #*/
/*#                     Mod. ArtMainInit()                                  #*/
/*# -------------------------------------------- From here TELINDY V8.03R0  #*/
/*#         2017/12/01  M.Sato               RT2201                         #*/
/*#                     New. artmain.c                                      #*/
/*#*************************************************************************#*/

#include <string.h>
#include "artlib.h"

int ArtMainInit(void)
{
    ArtRecipe_t rec;
    ArtInfo_t   info;

    memset(&rec, 0, sizeof(rec));
    if (ArtLibGetRecipeData(0, &rec) != ART_OK) {
        return ART_NG;
    }
    (void)artLibMakeArtInfo(&rec, &info);
    return ART_OK;
}
