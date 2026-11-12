MODEL ?= A
SRCS = src/main.c src/core/log.c src/util/math_util.c src/print/density.c \
       src/settings/nv_settings.c src/print/render.c \
       src/panel/menu.c src/panel/menu_table.c \
       src/cmd/pjl_commands.c src/resources/strings_en.c
SRCS += src/features/eco/eco_mode.c
SRCS += src/features/eco_report/eco_report.c

all:
	$(CC) -Wall -DMODEL_$(MODEL) -o printer_$(MODEL) $(SRCS)
