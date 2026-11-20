#ifndef NV_SETTINGS_H
#define NV_SETTINGS_H

/* Struct nay duoc luu vao NVRAM */
typedef struct {
    int copies;
    int duplex;
    int toner_save_level;
    int language;
    int quality;
    int fax_resolution;
} NvSettings_t;

NvSettings_t *NV_GetSettings(void);
void NV_LoadDefaults(void);
#endif
