#include "strings.h"

static const char *g_strings_en[STR_COUNT] = {
    [STR_COPIES] = "Copies",
    [STR_DUPLEX] = "2-Sided",
    [STR_QUALITY] = "Quality",
    [STR_FAX] = "Fax",
};

const char *Str_Get(StrId_t id)
{
    return g_strings_en[id];
}
