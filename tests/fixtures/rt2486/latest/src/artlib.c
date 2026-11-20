/*#*************************************************************************#*/
/*#     File Name   : artlib.c                                              #*/
/*#     Function    : Recipe / OSF data library                             #*/
/*#*************************************************************************#*/
/*#     Modification:                                                       #*/
/*#         2021/08/02  S.Kinoshita V8.14R000 RT2707                        #*/
/*#                     Add. artLibLinkOnVarSet()                           #*/
/*#                     Mod. ArtLibCopyRecipeName()                         #*/
/*# ------------------------------------------ From here TELINDY V8.14R000  #*/
/*#         2020/04/01  K.Ohtake (TTS)       RT2611                         #*/
/*#                     Add. WAVMACH_VER0800_0000                           #*/
/*#                          artLibConvVariApc()                            #*/
/*#                     Mod. ArtLibEntryRecipeName()                        #*/
/*# -------------------------------------------- From here TELINDY V8.10R0  #*/
/*#         2019/11/07  H.Nakazawa V8.08R000 RT2343                         #*/
/*#                     Mod. ArtLibGetRecipeData()                          #*/
/*#         2019/11/01  H.Nakazawa V8.08R000 RT2343                         #*/
/*#                     Add. WAVMACH_VER0700_0000                           #*/
/*#                          ArtLibJudgeRecipeConvV700()                    #*/
/*# -------------------------------------------- From here TELINDY V8.08R0  #*/
/*#         2019/02/14  T.Mori (TTS)         RT2586                         #*/
/*#                     Mod. artLibAdjustOsfData()                          #*/
/*# -------------------------------------------- From here TELINDY V8.07R0  #*/
/*#         2018/12/03  T.Mori (TTS)         RT2586                         #*/
/*#                     Mod. artLibAdjustOsfData()                          #*/
/*#         2018/11/20  Y.Kaneko (TTS-X)     RT2486:V806-0001               #*/
/*#                     Mod. artLibSetCsTempToVar()                         #*/
/*#         2018/10/22  T.Mori (TTS)         RT2586                         #*/
/*#                     Mod. artLibAdjustOsfData()                          #*/
/*# -------------------------------------------- From here TELINDY V8.06R0  #*/
/*#         2018/08/31  Y.Kaneko (TTS-X)     RT2486                         #*/
/*#                     Add. artLibSetVarDate()                             #*/
/*#                          artLibSetCsTempToVar()                         #*/
/*#                     Mod. ArtLibGetRecipeData()                          #*/
/*#                          ArtLibPutOsfData()                             #*/
/*#                          ArtLibRecoverOsfHistoryData()                  #*/
/*#                          artLibMakeArtInfo()                            #*/
/*#                          ArtLibEntryRecipeName()                        #*/
/*#                          ArtLibCopyRecipeName()                         #*/
/*# -------------------------------------------- From here TELINDY V8.03R1  #*/
/*#         2018/05/10  M.Sato               RT2283                         #*/
/*#                     Mod. ArtLibPutOsfData()                             #*/
/*# -------------------------------------------- From here TELINDY V8.03R0  #*/
/*#         2017/12/01  M.Sato               RT2201                         #*/
/*#                     New. artlib.c                                       #*/
/*#*************************************************************************#*/

#include <string.h>
#include "artlib.h"

static ArtRecipe_t s_artRecipeTbl[ART_RECIPE_MAX];

static ArtRecipe_t *artLibFindRecipe(int id)
{
    int i;

    for (i = 0; i < ART_RECIPE_MAX; i++) {
        if (s_artRecipeTbl[i].id == id) {
            return &s_artRecipeTbl[i];
        }
    }
    return NULL;
}

int ArtLibGetRecipeData(int id, ArtRecipe_t *rec)
{
    ArtRecipe_t *src;

    if ((rec == NULL) || (id < 0)) {
        return ART_NG;
    }
    src = artLibFindRecipe(id);
    if (src == NULL) {
        return ART_NG;
    }
    rec->id   = src->id;
    rec->ver  = src->ver;
    rec->date = src->date;
    rec->temp = src->temp;
    memcpy(rec->name, src->name, ART_NAME_LEN);
    if ((src->ver >= 600) && (src->csTemp != 0)) {
        rec->csTemp = src->csTemp;
    } else {
        (void)artLibSetCsTempToVar(rec);
    }
    (void)artLibSetVarDate(rec, src->date);
    return ART_OK;
}

int ArtLibPutOsfData(const ArtRecipe_t *rec, ArtOsfHist_t *hist)
{
    int n;

    if ((rec == NULL) || (hist == NULL)) {
        return ART_NG;
    }
    n = hist->count;
    if (n >= ART_HIST_MAX) {
        n = ART_HIST_MAX - 1;
    }
    hist->stamp[n] = rec->date;
    hist->value[n] = rec->csTemp;
    hist->count = n + 1;
    return ART_OK;
}

int artLibAdjustOsfData(ArtOsfHist_t *hist)
{
    int i;

    if ((hist == NULL) || (hist->count > ART_HIST_MAX)) {
        return ART_NG;
    }
    for (i = 0; i < hist->count; i++) {
        if (hist->value[i] < 0) {
            hist->value[i] = 0;
        } else if (hist->value[i] > ART_OSF_VALUE_MAX) {
            hist->value[i] = ART_OSF_VALUE_MAX;
        }
    }
    return ART_OK;
}

int ArtLibRecoverOsfHistoryData(ArtRecipe_t *rec, ArtOsfHist_t *hist)
{
    int i;

    if ((rec == NULL) || (hist == NULL)) {
        return ART_NG;
    }
    for (i = 0; i < hist->count; i++) {
        if (hist->stamp[i] > rec->date) {
            rec->date = hist->stamp[i];
            rec->temp = hist->value[i];
        }
    }
    (void)artLibSetVarDate(rec, rec->date);
    (void)artLibSetCsTempToVar(rec);
    rec->flags |= ART_FLAG_RECOVERED;
    return ART_OK;
}

int artLibMakeArtInfo(const ArtRecipe_t *rec, ArtInfo_t *info)
{
    if ((rec == NULL) || (info == NULL)) {
        return ART_NG;
    }
    info->kind = rec->id;
    info->size = (int)sizeof(ArtRecipe_t);
    info->date = rec->date;
    if (rec->csTemp > ART_CSTEMP_DEFAULT) {
        info->kind += 2000;
    }
    return ART_OK;
}

int ArtLibEntryRecipeName(ArtRecipe_t *rec, const char *name)
{
    if ((rec == NULL) || (name == NULL)) {
        return ART_NG;
    }
    strncpy(rec->name, name, ART_NAME_LEN - 1);
    rec->name[ART_NAME_LEN - 1] = '\0';
    if (rec->ver >= WAVMACH_VER0800_0000) {
        rec->csTemp = ART_CSTEMP_DEFAULT;
    }
    (void)artLibSetVarDate(rec, 0L);
    return ART_OK;
}

int ArtLibCopyRecipeName(ArtRecipe_t *dst, const ArtRecipe_t *src)
{
    if ((dst == NULL) || (src == NULL)) {
        return ART_NG;
    }
    memcpy(dst->name, src->name, ART_NAME_LEN);
    dst->ver = src->ver;
    dst->csTemp = src->csTemp;
    (void)artLibSetVarDate(dst, src->date);
    artLibLinkOnVarSet(dst);
    return ART_OK;
}

int artLibSetVarDate(ArtRecipe_t *rec, long date)
{
    if (rec == NULL) {
        return ART_NG;
    }
    if (date <= 0L) {
        date = rec->date;
    }
    rec->date = date;
    return ART_OK;
}

int artLibSetCsTempToVar(ArtRecipe_t *rec)
{
    if (rec == NULL) {
        return ART_NG;
    }
    if (rec->temp <= 0) {
        rec->csTemp = ART_CSTEMP_DEFAULT;
    } else {
        rec->csTemp = rec->temp * 10;
    }
    return ART_OK;
}

void artLibLinkOnVarSet(ArtRecipe_t *rec)
{
    if (rec == NULL) {
        return;
    }
    if (rec->csTemp != ART_CSTEMP_DEFAULT) {
        rec->flags &= ~ART_FLAG_RECOVERED;
    }
}

int ArtLibJudgeRecipeConvV700(const ArtRecipe_t *rec)
{
    if (rec == NULL) {
        return ART_NG;
    }
    return (rec->ver < WAVMACH_VER0700_0000) ? 1 : 0;
}

int artLibConvVariApc(ArtRecipe_t *rec)
{
    if (rec == NULL) {
        return ART_NG;
    }
    if (rec->ver < WAVMACH_VER0800_0000) {
        rec->ver = WAVMACH_VER0800_0000;
        rec->flags &= ~ART_FLAG_RECOVERED;
    }
    return ART_OK;
}
