MODEL ?= B
SRCS = src/main.c src/core/log.c src/util/math_util.c \
       src/settings/nv_settings.c src/print/render.c \
       src/panel/menu.c src/panel/menu_table.c \
       src/cmd/pjl_commands.c src/resources/strings_en.c

all:
	$(CC) -Wall -DMODEL_$(MODEL) -o printer_$(MODEL) $(SRCS)
