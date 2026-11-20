/*#*************************************************************************#*/
/*#     File Name   : artlib.c                                              #*/
/*#     Function    : Recipe / OSF data library                             #*/
/*#*************************************************************************#*/
/*#     Modification:                                                       #*/
/*#         2018/08/31  Y.Kaneko (TTS-X)     RT2486                         #*/
/*#                     Add. artLibSetVarDate()                             #*/
/*#                          artLibSetCsTempToVar()                         #*/
/*#                     Mod. ArtLibGetRecipeData()                          #*/
/*#                          ArtLibPutOsfData()                             #*/
/*#                          ArtLibRecoverOsfHistoryData()                  #*/
/*#                          artLibMakeArtInfo()                            #*/
/*#                          ArtLibEntryRecipeName()                        #*/
/*#                          ArtLibCopyRecipeName()                         #*/
/*#         2022/03/15  R.Ito (TTS)          RT3105                         #*/
/*#                     Mod. ArtLibRecoverOsfHistoryData()                  #*/
/*#                          ArtLibFomularCheckRecipe()                     #*/
/*#                     履歴データ復旧処理をFOMULAR向けに変更               #*/
/*# -------------------------------------------- From here FOMULAR V2.01R0  #*/
/*#         2020/09/10  R.Ito (TTS)          RT2950                         #*/
/*#                     Add. ART_CSTEMP_DEFAULT                             #*/
/*# -------------------------------------------- From here FOMULAR V2.00R0  #*/
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

    if (rec == NULL) {
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

    if (hist == NULL) {
        return ART_NG;
    }
    for (i = 0; i < hist->count; i++) {
        if (hist->value[i] < 0) {
            hist->value[i] = 0;
        }
    }
    return ART_OK;
}

int ArtLibRecoverOsfHistoryData(ArtRecipe_t *rec, ArtOsfHist_t *hist)
{
    int idx = 0;

    /* 履歴データの復旧処理 (FOMULAR) */
    if (rec == NULL || hist == NULL) return (ART_NG);

    while (idx < hist->count) {
        if (rec->date < hist->stamp[idx]) {
            rec->date = hist->stamp[idx];
            rec->temp = (int)hist->value[idx];
        }
        idx++;
    }
    (void)artLibSetVarDate(rec, rec->date);
    (void)artLibSetCsTempToVar(rec);
    rec->flags = (rec->flags | ART_FLAG_RECOVERED);
    return (ART_OK);
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
    rec->csTemp = ART_CSTEMP_DEFAULT;
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

int ArtLibFomularCheckRecipe(const ArtRecipe_t *rec)
{
    /* レシピ名の空チェック */
    if (rec == NULL) {
        return ART_NG;
    }
    if (rec->name[0] == '\0') {
        return ART_NG;
    }
    return ART_OK;
}
