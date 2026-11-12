#ifndef TONER_SAVE_H
#define TONER_SAVE_H
enum {
    TONER_SAVE_OFF = 0,
    TONER_SAVE_LOW = 1,
    TONER_SAVE_HIGH = 2
};

int TonerSave_GetLevel(void);
int TonerSave_ApplyDensity(int density);
int TonerSave_MenuHandler(int key);
int TonerSave_PjlSet(const char *arg);
#endif
