#ifndef STRINGS_H
#define STRINGS_H
typedef enum {
    STR_COPIES,
    STR_DUPLEX,
    STR_QUALITY,
    STR_COUNT
} StrId_t;

const char *Str_Get(StrId_t id);
#endif
