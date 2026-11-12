#include "menu.h"
#include "../core/log.h"
#include "../print/density.h"

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
    return Density_Scale(key, 50);
}

int Menu_Language(int key)
{
    return key;
}
