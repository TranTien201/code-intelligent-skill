#include <string.h>
#include "menu.h"
#include "../../config/model_config.h"
#ifdef SUPPORT_TONER_SAVE
#include "../features/toner_save/toner_save.h"
#endif

static const MenuEntry_t g_menu_table[] = {
    { "COPIES",   Menu_Copies },
    { "DUPLEX",   Menu_Duplex },
#ifdef SUPPORT_TONER_SAVE
    { "TONER_SAVE", TonerSave_MenuHandler },
#endif
    { "QUALITY",  Menu_Quality },
    { "LANGUAGE", Menu_Language },
};

int Menu_Dispatch(const char *name, int key)
{
    unsigned i;
    for (i = 0; i < sizeof(g_menu_table) / sizeof(g_menu_table[0]); i++) {
        if (strcmp(g_menu_table[i].name, name) == 0)
            return g_menu_table[i].handler(key);
    }
    return -1;
}
