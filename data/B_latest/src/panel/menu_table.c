#include <string.h>
#include "menu.h"
#include "../../config/model_config.h"

static const MenuEntry_t g_menu_table[] = {
    { "COPIES",   Menu_Copies },
    { "DUPLEX",   Menu_Duplex },
    { "QUALITY",  Menu_Quality },
    { "LANGUAGE", Menu_Language },
    { "FAX",      Menu_Fax },
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
