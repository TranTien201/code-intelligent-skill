#ifndef ECO_MODE_H
#define ECO_MODE_H
enum {
    TONER_SAVE_OFF = 0,
    TONER_SAVE_LOW = 1,
    TONER_SAVE_HIGH = 2
};

int EcoMode_GetLevel(void);
int EcoMode_ApplyDensity(int density);
int EcoMode_MenuHandler(int key);
int EcoMode_PjlSet(const char *arg);
#endif
