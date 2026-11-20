#include <string.h>
#include "pjl_commands.h"
#include "../core/log.h"
#include "../features/toner_save/toner_save.h"

typedef int (*PjlHandler_t)(const char *arg);
typedef struct {
    const char *cmd;
    PjlHandler_t fn;
} PjlEntry_t;

static int Pjl_SetCopies(const char *arg)
{
    Log_Info(arg);
    return 0;
}

static int Pjl_SetDuplex(const char *arg)
{
    Log_Info(arg);
    return 0;
}

static const PjlEntry_t g_pjl_table[] = {
    { "COPIES", Pjl_SetCopies },
    { "DUPLEX", Pjl_SetDuplex },
    { "ECONOMODE", TonerSave_PjlSet },
};

int Pjl_Dispatch(const char *cmd, const char *arg)
{
    unsigned i;
    for (i = 0; i < sizeof(g_pjl_table) / sizeof(g_pjl_table[0]); i++) {
        if (strcmp(g_pjl_table[i].cmd, cmd) == 0)
            return g_pjl_table[i].fn(arg);
    }
    return -1;
}
