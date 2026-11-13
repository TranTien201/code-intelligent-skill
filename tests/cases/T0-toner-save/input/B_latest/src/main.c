#include <stdio.h>
#include "settings/nv_settings.h"
#include "print/render.h"
#include "panel/menu.h"
#include "cmd/pjl_commands.h"

int main(void)
{
    NV_LoadDefaults();
    printf("copies=%d\n", Menu_Dispatch("COPIES", 2));
    printf("toner_save=%d\n", Menu_Dispatch("TONER_SAVE", 2));
    printf("pjl=%d\n", Pjl_Dispatch("ECONOMODE", "1"));
    printf("density=%d\n", Render_Page(10));
    return 0;
}
