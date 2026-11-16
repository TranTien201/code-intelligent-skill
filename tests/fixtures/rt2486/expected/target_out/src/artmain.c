/*#*************************************************************************#*/
/*#     File Name   : artmain.c                                             #*/
/*#     Function    : Recipe main control                                   #*/
/*#*************************************************************************#*/
/*#     Modification:                                                       #*/
/*#         2021/01/12  R.Ito (TTS)          RT2999                         #*/
/*#                     Mod. ArtMainInit()                                  #*/
/*# -------------------------------------------- From here FOMULAR V2.00R0  #*/
/*#         2019/06/05  H.Nakazawa           RT2402                         #*/
/*#                     Mod. ArtMainInit()                                  #*/
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
    if (ArtLibGetRecipeData(1, &rec) != ART_OK) {
        return ART_NG;
    }
    (void)artLibMakeArtInfo(&rec, &info);
    (void)ArtLibFomularCheckRecipe(&rec);
    return ART_OK;
}
