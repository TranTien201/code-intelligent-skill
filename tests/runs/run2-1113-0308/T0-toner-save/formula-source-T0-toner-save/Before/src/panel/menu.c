#include "menu.h"
#include "../core/log.h"

static int is_valid(int key)
{
    return key >= 0 && key < 100;
}

int Menu_Copies(int key)
{
    return is_valid(key) ? key : 1;
}

int Menu_Duplex(int key)
{
    return key ? 1 : 0;
}

int Menu_Quality(int key)
{
    Log_Info("quality");
    return key;
}

int Menu_Language(int key)
{
    return key;
}

int Menu_Fax(int key)
{
    Log_Info("fax menu");
    return key;
}
