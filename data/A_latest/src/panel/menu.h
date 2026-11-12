#ifndef MENU_H
#define MENU_H
typedef int (*MenuHandler_t)(int key);
typedef struct {
    const char *name;
    MenuHandler_t handler;
} MenuEntry_t;

int Menu_Copies(int key);
int Menu_Duplex(int key);
int Menu_Quality(int key);
int Menu_Language(int key);
int Menu_Dispatch(const char *name, int key);
#endif
