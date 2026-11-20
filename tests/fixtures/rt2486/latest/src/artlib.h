#ifndef ARTLIB_H
#define ARTLIB_H

/* artlib.h : Recipe / OSF data library */

#define ART_OK              (0)
#define ART_NG              (-1)

#define ART_NAME_LEN        (32)
#define ART_HIST_MAX        (16)
#define ART_RECIPE_MAX      (64)
#define ART_FLAG_RECOVERED  (0x0001)
#define ART_CSTEMP_DEFAULT  (250)
#define ART_OSF_VALUE_MAX   (9999)

#define WAVMACH_VER0700_0000    (700)
#define WAVMACH_VER0800_0000    (800)

/* recipe data */
typedef struct {
    int   id;
    int   ver;
    char  name[ART_NAME_LEN];
    long  date;
    int   temp;
    int   csTemp;
    int   flags;
} ArtRecipe_t;

typedef struct {
    int   count;
    long  stamp[ART_HIST_MAX];
    int   value[ART_HIST_MAX];
} ArtOsfHist_t;

typedef struct {
    int   kind;
    int   size;
    long  date;
} ArtInfo_t;

extern int  ArtLibGetRecipeData(int id, ArtRecipe_t *rec);
extern int  ArtLibPutOsfData(const ArtRecipe_t *rec, ArtOsfHist_t *hist);
extern int  ArtLibRecoverOsfHistoryData(ArtRecipe_t *rec, ArtOsfHist_t *hist);
extern int  artLibMakeArtInfo(const ArtRecipe_t *rec, ArtInfo_t *info);
extern int  ArtLibEntryRecipeName(ArtRecipe_t *rec, const char *name);
extern int  ArtLibCopyRecipeName(ArtRecipe_t *dst, const ArtRecipe_t *src);
extern int  artLibAdjustOsfData(ArtOsfHist_t *hist);
extern int  artLibSetVarDate(ArtRecipe_t *rec, long date);
extern int  artLibSetCsTempToVar(ArtRecipe_t *rec);
extern void artLibLinkOnVarSet(ArtRecipe_t *rec);
extern int  ArtLibJudgeRecipeConvV700(const ArtRecipe_t *rec);
extern int  artLibConvVariApc(ArtRecipe_t *rec);

#endif /* ARTLIB_H */
