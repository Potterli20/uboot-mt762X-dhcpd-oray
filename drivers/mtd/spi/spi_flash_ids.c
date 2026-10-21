// SPDX-License-Identifier: GPL-2.0+
/*
 * SPI Flash ID's.
 *
 * Copyright (C) 2016 Jagan Teki <jagan@openedev.com>
 * Copyright (C) 2013 Jagannadha Sutradharudu Teki, Xilinx Inc.
 */

#include <common.h>
#include <spi.h>
#include <spi_flash.h>

#include "sf_internal.h"

/* Used when the "_ext_id" is two bytes at most */
#define INFO(_jedec_id, _ext_id, _sector_size, _n_sectors, _flags)	\
		.id = {							\
			((_jedec_id) >> 16) & 0xff,			\
			((_jedec_id) >> 8) & 0xff,			\
			(_jedec_id) & 0xff,				\
			((_ext_id) >> 8) & 0xff,			\
			(_ext_id) & 0xff,				\
			},						\
		.id_len = (!(_jedec_id) ? 0 : (3 + ((_ext_id) ? 2 : 0))),	\
		.sector_size = (_sector_size),				\
		.n_sectors = (_n_sectors),				\
		.page_size = 256,					\
		.flags = (_flags),

#define INFO6(_jedec_id, _ext_id, _sector_size, _n_sectors, _flags)	\
		.id = {							\
			((_jedec_id) >> 16) & 0xff,			\
			((_jedec_id) >> 8) & 0xff,			\
			(_jedec_id) & 0xff,				\
			((_ext_id) >> 16) & 0xff,			\
			((_ext_id) >> 8) & 0xff,			\
			(_ext_id) & 0xff,				\
			},						\
		.id_len = 6,						\
		.sector_size = (_sector_size),				\
		.n_sectors = (_n_sectors),				\
		.page_size = 256,					\
		.flags = (_flags),

const struct spi_flash_info spi_flash_ids[] = {
#ifdef CONFIG_SPI_FLASH_ATMEL		/* ATMEL */
	{"at45db011d",	   INFO(0x1f2200, 0x0, 64 * 1024,     4, SECT_4K) },
	{"at45db021d",	   INFO(0x1f2300, 0x0, 64 * 1024,     8, SECT_4K) },
	{"at45db041d",	   INFO(0x1f2400, 0x0, 64 * 1024,     8, SECT_4K) },
	{"at45db081d",	   INFO(0x1f2500, 0x0, 64 * 1024,    16, SECT_4K) },
	{"at45db161d",	   INFO(0x1f2600, 0x0, 64 * 1024,    32, SECT_4K) },
	{"at45db321d",	   INFO(0x1f2700, 0x0, 64 * 1024,    64, SECT_4K) },
	{"at45db641d",	   INFO(0x1f2800, 0x0, 64 * 1024,   128, SECT_4K) },
	{"at25df321a",     INFO(0x1f4701, 0x0, 64 * 1024,    64, SECT_4K) },
	{"at25df321",      INFO(0x1f4700, 0x0, 64 * 1024,    64, SECT_4K) },
	{"at26df081a",     INFO(0x1f4501, 0x0, 64 * 1024,    16, SECT_4K) },
	{"at26df321",	   INFO(0x1f4700, 0x0, 64 * 1024,    64, SECT_4K) },
	{"at25sl321",      INFO(0x1f4216, 0x0, 64 * 1024,    64, SECT_4K) },
#endif
#ifdef CONFIG_SPI_FLASH_DOSILICON	/* DOSILICON */
	{"ds25m4cb",       INFO(0xe5401a, 0x0, 64 * 1024,  1024, RD_FULL | SECT_4K) },
	{"ds25m4dn",       INFO(0xe5401b, 0x0, 64 * 1024,  2048, RD_FULL | SECT_4K) },
	{"ds25q4cb",       INFO(0xe5301a, 0x0, 64 * 1024,  1024, RD_FULL | SECT_4K) },
	{"ds25q4dn",       INFO(0xe5301b, 0x0, 64 * 1024,  2048, RD_FULL | SECT_4K) },
#endif
#ifdef CONFIG_SPI_FLASH_EON		/* EON */
	{"en25q80b",       INFO(0x1c3014, 0x0, 64 * 1024,    16, SECT_4K) },
	{"en25q32b",	   INFO(0x1c3016, 0x0, 64 * 1024,    64, 0) },
	{"en25q64",	   INFO(0x1c3017, 0x0, 64 * 1024,   128, SECT_4K) },
	{"en25q128b",	   INFO(0x1c3018, 0x0, 64 * 1024,   256, 0) },
	{"en25qh128",	   INFO(0x1c7018, 0x0, 64 * 1024,   256, 0) },
	{"en25s64",	   INFO(0x1c3817, 0x0, 64 * 1024,   128, 0) },
#endif
#ifdef CONFIG_SPI_FLASH_GIGADEVICE	/* GIGADEVICE */
	{"gd25q16c",	   INFO(0xc84015, 0x0, 64 * 1024,    32, RD_FULL | WR_QPP | SECT_4K) },
	{"gd25q64b",	   INFO(0xc84017, 0x0, 64 * 1024,   128, SECT_4K) },
	{"gd25q32b",       INFO(0xc84016, 0x0, 64 * 1024,    64, SECT_4K) },
	{"gd25q128b",	   INFO(0xc84018, 0x0, 64 * 1024,   256, SECT_4K) },
	{"gd25lq32",	   INFO(0xc86016, 0x0, 64 * 1024,    64, SECT_4K) },
	{"gd25lq64c", 	   INFO(0xc86017, 0x0, 64 * 1024,   128, RD_FULL | WR_QPP | SECT_4K) },
	{"gd25q128", 	   INFO(0xc84018, 0x0, 64 * 1024,   256, RD_FULL | WR_QPP | SECT_4K) },
	{"gd25q16",        INFO(0xc84015, 0x0, 64 * 1024,    32, RD_FULL | SECT_4K) },
	{"gd25q32",        INFO(0xc84016, 0x0, 64 * 1024,    64, RD_FULL | SECT_4K) },
	{"gd25q64",        INFO(0xc84017, 0x0, 64 * 1024,   128, RD_FULL | SECT_4K) },
	{"gd25b256",       INFO(0xc84019, 0x0, 64 * 1024,   512, RD_FULL | SECT_4K) },
	{"gd25b512",       INFO(0xc8471a, 0x0, 64 * 1024,  1024, RD_QUAD | SECT_4K) },
	{"gd55b01g",       INFO(0xc8471b, 0x0, 64 * 1024,  2048, RD_QUAD | SECT_4K) },
	{"gd55b02g",       INFO(0xc8471c, 0x0, 64 * 1024,  4096, RD_QUAD | SECT_4K) },
	{"gd25f64",        INFO(0xc84317, 0x0, 64 * 1024,   128, RD_FULL | SECT_4K) },
	{"gd25f128",       INFO(0xc84318, 0x0, 64 * 1024,   256, RD_FULL | SECT_4K) },
	{"gd25f256",       INFO(0xc84319, 0x0, 64 * 1024,   512, RD_FULL | SECT_4K) },
	{"gd55f512",       INFO(0xc8431a, 0x0, 64 * 1024,  1024, RD_FULL | SECT_4K) },
	{"gd25t512",       INFO(0xc8461a, 0x0, 64 * 1024,  1024, RD_QUAD | SECT_4K) },
	{"gd55t01g",       INFO(0xc8461b, 0x0, 64 * 1024,  2048, RD_QUAD | SECT_4K) },
	{"gd55t02g",       INFO(0xc8461c, 0x0, 64 * 1024,  4096, RD_QUAD | SECT_4K) },
	{"gd25x512",       INFO(0xc8481a, 0x0, 64 * 1024,  1024, SECT_4K) },
	{"gd55x01g",       INFO(0xc8481b, 0x0, 64 * 1024,  2048, SECT_4K) },
	{"gd55x02g",       INFO(0xc8481c, 0x0, 64 * 1024,  4096, SECT_4K) },
	{"gd25lq128",      INFO(0xc86018, 0x0, 64 * 1024,   256, RD_FULL | SECT_4K) },
	{"gd25lq256d",     INFO(0xc86019, 0x0, 64 * 1024,   512, RD_FULL | SECT_4K) },
	{"gd25lb256",      INFO(0xc86719, 0x0, 64 * 1024,   512, RD_QUAD | SECT_4K) },
	{"gd25lb512",      INFO(0xc8671a, 0x0, 64 * 1024,  1024, RD_QUAD | SECT_4K) },
	{"gd55lb01g",      INFO(0xc8671b, 0x0, 64 * 1024,  2048, RD_QUAD | SECT_4K) },
	{"gd55lb02g",      INFO(0xc8671c, 0x0, 64 * 1024,  4096, RD_QUAD | SECT_4K) },
	{"gd55lb02ge",     INFO(0xc8671c, 0x0, 64 * 1024,  4096, RD_QUAD | SECT_4K) },
	{"gd25lf80",       INFO(0xc86314, 0x0, 64 * 1024,    16, RD_FULL | SECT_4K) },
	{"gd25lf16",       INFO(0xc86315, 0x0, 64 * 1024,    32, RD_FULL | SECT_4K) },
	{"gd25lf32",       INFO(0xc86316, 0x0, 64 * 1024,    64, RD_FULL | SECT_4K) },
	{"gd25lf64",       INFO(0xc86317, 0x0, 64 * 1024,   128, RD_FULL | SECT_4K) },
	{"gd25lf128",      INFO(0xc86318, 0x0, 64 * 1024,   256, RD_FULL | SECT_4K) },
	{"gd25lf255",      INFO(0xc86319, 0x0, 64 * 1024,   512, RD_FULL | SECT_4K) },
	{"gd25lf511",      INFO(0xc8631a, 0x0, 64 * 1024,  1024, RD_FULL | SECT_4K) },
	{"gd25lt256",      INFO(0xc86619, 0x0, 64 * 1024,   512, RD_QUAD | SECT_4K) },
	{"gd25lt512",      INFO(0xc8661a, 0x0, 64 * 1024,  1024, RD_QUAD | SECT_4K) },
	{"gd55lt01g",      INFO(0xc8661b, 0x0, 64 * 1024,  2048, RD_QUAD | SECT_4K) },
	{"gd55lt02g",      INFO(0xc8661c, 0x0, 64 * 1024,  4096, RD_QUAD | SECT_4K) },
	{"gd25lx128j",     INFO(0xc86818, 0x0, 64 * 1024,   256, SECT_4K) },
	{"gd25lx256e",     INFO(0xc86819, 0x0, 64 * 1024,   512, SECT_4K) },
	{"gd25lx512",      INFO(0xc8681a, 0x0, 64 * 1024,  1024, SECT_4K) },
	{"gd55lx01g",      INFO(0xc8681b, 0x0, 64 * 1024,  2048, SECT_4K) },
	{"gd55lx02g",      INFO(0xc8681c, 0x0, 64 * 1024,  4096, SECT_4K) },
#endif
#ifdef CONFIG_SPI_FLASH_ISSI		/* ISSI */
	{"is25lq040b",	   INFO(0x9d4013, 0x0, 64 * 1024,    8, RD_FULL | SECT_4K) },
	{"is25lp008",      INFO(0x9d6014, 0x0, 64 * 1024,   16, RD_QUAD) },
	{"is25lp016",      INFO(0x9d6015, 0x0, 64 * 1024,   32, RD_QUAD) },
	{"is25lp032",	   INFO(0x9d6016, 0x0, 64 * 1024,    64, 0) },
	{"is25lp064",	   INFO(0x9d6017, 0x0, 64 * 1024,   128, 0) },
	{"is25lp128",	   INFO(0x9d6018, 0x0, 64 * 1024,   256, RD_DUAL | SECT_4K) },
	{"is25lp256",	   INFO(0x9d6019, 0x0, 64 * 1024,   512, RD_DUAL | SECT_4K) },
	{"is25lp512",      INFO(0x9d601a, 0x0, 64 * 1024,  1024, RD_FULL | SECT_4K) },
	{"is25lp512mj",    INFO(0x9d6020, 0x0, 64 * 1024,  1024, RD_FULL | SECT_4K) },
	{"is25lp01g",      INFO(0x9d601b, 0x0, 64 * 1024,  2048, RD_FULL | SECT_4K) },
	{"is25lp01gg",     INFO(0x9d6021, 0x0, 64 * 1024,  2048, RD_FULL | SECT_4K) },
	{"is25lp01gj",     INFO(0x9d6021, 0x0, 64 * 1024,  2048, RD_FULL | SECT_4K) },
	{"is25lp02gg",     INFO(0x9d6022, 0x0, 64 * 1024,  4096, RD_FULL | SECT_4K) },
	{"is25lp02gj",     INFO(0x9d6022, 0x0, 64 * 1024,  4096, RD_FULL | SECT_4K) },
	{"is25lp010e",     INFO(0x9d4011, 0x0, 64 * 1024,     2, RD_FULL | SECT_4K) },
	{"is25lp020e",     INFO(0x9d4012, 0x0, 64 * 1024,     4, RD_FULL | SECT_4K) },
	{"is25wp008",      INFO(0x9d7014, 0x0, 64 * 1024,   16, RD_QUAD) },
	{"is25wp016",      INFO(0x9d7015, 0x0, 64 * 1024,   32, RD_QUAD) },
	{"is25wp032",	   INFO(0x9d7016, 0x0, 64 * 1024,    64, RD_FULL | SECT_4K) },
	{"is25wp064",	   INFO(0x9d7017, 0x0, 64 * 1024,   128, RD_FULL | SECT_4K) },
	{"is25wp128",	   INFO(0x9d7018, 0x0, 64 * 1024,   256, RD_FULL | SECT_4K) },
	{"is25wp256",	   INFO(0x9d7019, 0x0, 64 * 1024,   512, RD_FULL | SECT_4K) },
	{"is25wp512",      INFO(0x9d701a, 0x0, 64 * 1024,  1024, RD_FULL | SECT_4K) },
	{"is25wp512mj",    INFO(0x9d7020, 0x0, 64 * 1024,  1024, RD_FULL | SECT_4K) },
	{"is25wp01g",      INFO(0x9d701b, 0x0, 64 * 1024,  2048, RD_FULL | SECT_4K) },
	{"is25wp01gg",     INFO(0x9d7021, 0x0, 64 * 1024,  2048, RD_FULL | SECT_4K) },
	{"is25wp01gj",     INFO(0x9d7021, 0x0, 64 * 1024,  2048, RD_FULL | SECT_4K) },
	{"is25wp02gg",     INFO(0x9d7022, 0x0, 64 * 1024,  4096, RD_FULL | SECT_4K) },
	{"is25wp02gj",     INFO(0x9d7022, 0x0, 64 * 1024,  4096, RD_FULL | SECT_4K) },
	{"is25wj128f",     INFO(0x9d7118, 0x0, 64 * 1024,   256, RD_FULL | SECT_4K) },
	{"is25wx256",	   INFO(0x9d5b19, 0x0, 128 * 1024,  256, RD_FULL | SECT_4K) },
	{"is25wx128",      INFO(0x9d5b18, 0x0, 64 * 1024,   256, SECT_4K) },
	{"is25lx128",      INFO(0x9d5a18, 0x0, 64 * 1024,   256, SECT_4K) },
	{"is25lx512",      INFO(0x9d5a1a, 0x0, 64 * 1024,  1024, SECT_4K) },
#endif
#ifdef CONFIG_SPI_FLASH_MACRONIX	/* MACRONIX */
	{"mx25l2006e",	   INFO(0xc22012, 0x0, 64 * 1024,     4, 0) },
	{"mx25l4005",	   INFO(0xc22013, 0x0, 64 * 1024,     8, 0) },
	{"mx25l8005",	   INFO(0xc22014, 0x0, 64 * 1024,    16, 0) },
	{"mx25l1605d",	   INFO(0xc22015, 0x0, 64 * 1024,    32, 0) },
	{"mx25l3205d",	   INFO(0xc22016, 0x0, 64 * 1024,    64, 0) },
	{"mx25l6405d",	   INFO(0xc22017, 0x0, 64 * 1024,   128, 0) },
	{"mx25l12805",	   INFO(0xc22018, 0x0, 64 * 1024,   256, RD_FULL | WR_QPP) },
	{"mx25l25635f",	   INFO(0xc22019, 0x0, 64 * 1024,   512, RD_FULL | WR_QPP) },
	{"mx25l51235f",	   INFO(0xc2201a, 0x0, 64 * 1024,  1024, RD_FULL | WR_QPP) },
	{"mx25l1633e",	   INFO(0xc22415, 0x0, 64 * 1024,    32, RD_FULL | WR_QPP | SECT_4K) },
	{"mx25u6435f",	   INFO(0xc22537, 0x0, 64 * 1024,   128, RD_FULL | WR_QPP) },
	{"mx25l12855e",	   INFO(0xc22618, 0x0, 64 * 1024,   256, RD_FULL | WR_QPP) },
	{"mx25u1635e",     INFO(0xc22535, 0x0, 64 * 1024,  32, SECT_4K) },
	{"mx25u12835f",    INFO(0xc22538, 0x0, 64 * 1024, 256, SECT_4K) },
	{"mx25u25635f",    INFO(0xc22539, 0x0, 64 * 1024,   512, RD_FULL | WR_QPP) },
	{"mx25l25655e",    INFO(0xc22619, 0x0, 64 * 1024,   512, 0) },
	{"mx66u51235f",    INFO(0xc2253a, 0x0, 64 * 1024,  1024, RD_FULL | WR_QPP) },
	{"mx66l1g45g",     INFO(0xc2201b, 0x0, 64 * 1024,  2048, RD_FULL | WR_QPP) },
	{"mx25l2005a",     INFO(0xc22012, 0x0, 64 * 1024,     4, SECT_4K) },
	{"mx25l4005a",     INFO(0xc22013, 0x0, 64 * 1024,     8, SECT_4K) },
	{"mx25l1606e",     INFO(0xc22015, 0x0, 64 * 1024,    32, SECT_4K) },
	{"mx25u2033e",     INFO(0xc22532, 0x0, 64 * 1024,     4, SECT_4K) },
	{"mx25u3235f",     INFO(0xc22536, 0x0,  4 * 1024,  1024, SECT_4K) },
	{"mx25l12805d",    INFO(0xc22018, 0x0, 64 * 1024,   256, SECT_4K) },
	{"mx25u51245f",    INFO(0xc2953a, 0x0, 64 * 1024,  1024, RD_FULL | SECT_4K) },
	{"mx25v8035f",     INFO(0xc22314, 0x0, 64 * 1024,    16, RD_FULL | SECT_4K) },
	{"mx25r1635f",     INFO(0xc22815, 0x0, 64 * 1024,    32, RD_FULL | SECT_4K) },
	{"mx66u1g45g",     INFO(0xc2253b, 0x0, 64 * 1024,  2048, RD_FULL | SECT_4K) },
	{"mx66u2g45g",     INFO(0xc2253c, 0x0, 64 * 1024,  4096, RD_FULL | SECT_4K) },
	{"mx66l2g45g",     INFO(0xc2201c, 0x0, 64 * 1024,  4096, RD_FULL | SECT_4K) },
	{"mx25r6435f",     INFO(0xc22817, 0x0, 64 * 1024,   128, SECT_4K) },
	{"mx66uw2g345gx0", INFO(0xc2943c, 0x0, 64 * 1024,  4096, SECT_4K) },
	{"mx66lm1g45g",    INFO(0xc2853b, 0x0, 64 * 1024,  2048, SECT_4K) },
	{"mx25lm51245g",   INFO(0xc2853a, 0x0, 64 * 1024,  1024, SECT_4K) },
	{"mx25lw51245g",   INFO(0xc2863a, 0x0, 64 * 1024,  1024, SECT_4K) },
	{"mx25lm25645g",   INFO(0xc28539, 0x0, 64 * 1024,   512, SECT_4K) },
	{"mx66uw2g345g",   INFO(0xc2843c, 0x0, 64 * 1024,  4096, SECT_4K) },
	{"mx66um1g45g",    INFO(0xc2803b, 0x0, 64 * 1024,  2048, SECT_4K) },
	{"mx66uw1g45g",    INFO(0xc2813b, 0x0, 64 * 1024,  2048, SECT_4K) },
	{"mx25uw51245g",   INFO(0xc2813a, 0x0, 64 * 1024,  1024, SECT_4K) },
	{"mx25uw51345g",   INFO(0xc2843a, 0x0, 64 * 1024,  1024, SECT_4K) },
	{"mx25um25645g",   INFO(0xc28039, 0x0, 64 * 1024,   512, SECT_4K) },
	{"mx25uw25645g",   INFO(0xc28139, 0x0, 64 * 1024,   512, SECT_4K) },
	{"mx25um25345g",   INFO(0xc28339, 0x0, 64 * 1024,   512, SECT_4K) },
	{"mx25uw25345g",   INFO(0xc28439, 0x0, 64 * 1024,   512, SECT_4K) },
	{"mx25uw12845g",   INFO(0xc28138, 0x0, 64 * 1024,   256, SECT_4K) },
	{"mx25uw12345g",   INFO(0xc28438, 0x0, 64 * 1024,   256, SECT_4K) },
	{"mx25uw6445g",    INFO(0xc28137, 0x0, 64 * 1024,   128, SECT_4K) },
	{"mx25uw6345g",    INFO(0xc28437, 0x0, 64 * 1024,   128, SECT_4K) },
#endif
#ifdef CONFIG_SPI_FLASH_PUYA		/* PUYA */
	{"p25q05h",        INFO(0x856010, 0x0, 64 * 1024,     1, RD_FULL | SECT_4K) },
	{"p25q10h",        INFO(0x856011, 0x0, 64 * 1024,     2, RD_FULL | SECT_4K) },
	{"p25q20h",        INFO(0x856012, 0x0, 64 * 1024,     4, RD_FULL | SECT_4K) },
	{"p25q40h",        INFO(0x856013, 0x0, 64 * 1024,     8, RD_FULL | SECT_4K) },
	{"p25q80h",        INFO(0x856014, 0x0, 64 * 1024,    16, RD_FULL | SECT_4K) },
	{"p25q16h",        INFO(0x856015, 0x0, 64 * 1024,    32, RD_FULL | SECT_4K) },
	{"p25q32h",        INFO(0x856016, 0x0, 64 * 1024,    64, RD_FULL | SECT_4K) },
	{"p25q64h",        INFO(0x856017, 0x0, 64 * 1024,   128, RD_FULL | SECT_4K) },
	{"p25q128h",       INFO(0x856018, 0x0, 64 * 1024,   256, RD_FULL | SECT_4K) },
	{"py25f512hb",     INFO(0x85231a, 0x0, 64 * 1024,  1024, RD_FULL | SECT_4K) },
	{"py25f01ghb",     INFO(0x85231b, 0x0, 64 * 1024,  2048, RD_FULL | SECT_4K) },
	{"py25f512lc",     INFO(0x85631a, 0x0, 64 * 1024,  1024, RD_FULL | SECT_4K) },
	{"py25f01glc",     INFO(0x85631b, 0x0, 64 * 1024,  2048, RD_FULL | SECT_4K) },
#endif
#ifdef CONFIG_SPI_FLASH_SILICONKAISER	/* SILICONKAISER */
	{"sk25lp128",      INFO(0x257018, 0x0, 64 * 1024,   256, RD_FULL | SECT_4K) },
#endif
#ifdef CONFIG_SPI_FLASH_SPANSION	/* SPANSION */
	{"s25fl008a",	   INFO(0x010213, 0x0, 64 * 1024,    16, 0) },
	{"s25fl016a",	   INFO(0x010214, 0x0, 64 * 1024,    32, 0) },
	{"s25fl032a",	   INFO(0x010215, 0x0, 64 * 1024,    64, 0) },
	{"s25fl064a",	   INFO(0x010216, 0x0, 64 * 1024,   128, 0) },
	{"s25fl208k",	   INFO(0x014014, 0x0, 64 * 1024,    16, 0) },
	{"s25fl116k",	   INFO(0x014015, 0x0, 64 * 1024,    32, 0) },
	{"s25fl164k",	   INFO(0x014017, 0x0,  64 * 1024,   128, 0) },
	{"s25fl128p_256k", INFO(0x012018, 0x0300, 256 * 1024,    64, RD_FULL | WR_QPP) },
	{"s25fl128p_64k",  INFO(0x012018, 0x0301,  64 * 1024,   256, RD_FULL | WR_QPP) },
	{"s25fl032p",	   INFO(0x010215, 0x4d00,  64 * 1024,    64, RD_FULL | WR_QPP) },
	{"s25fl064p",	   INFO(0x010216, 0x4d00,  64 * 1024,   128, RD_FULL | WR_QPP) },
	{"s25fl128s_256k", INFO(0x012018, 0x4d00, 256 * 1024,    64, RD_FULL | WR_QPP) },
	{"s25fl128s_64k",  INFO(0x012018, 0x4d01,  64 * 1024,   256, RD_FULL | WR_QPP) },
	{"s25fl128l",      INFO(0x016018, 0, 64 * 1024,    256, RD_FULL | WR_QPP) },
	{"s25fl256s_256k", INFO(0x010219, 0x4d00, 256 * 1024,   128, RD_FULL | WR_QPP) },
	{"s25fs256s_64k",  INFO6(0x010219, 0x4d0181, 64 * 1024, 512, RD_FULL | WR_QPP | SECT_4K) },
	{"s25fl256s_64k",  INFO(0x010219, 0x4d01,  64 * 1024,   512, RD_FULL | WR_QPP) },
	{"s25fs512s",      INFO6(0x010220, 0x4d0081, 256 * 1024, 256, RD_FULL | WR_QPP | SECT_4K) },
	{"s25fl512s_256k", INFO(0x010220, 0x4d00, 256 * 1024,   256, RD_FULL | WR_QPP) },
	{"s25fl512s_64k",  INFO(0x010220, 0x4d01,  64 * 1024,  1024, RD_FULL | WR_QPP) },
	{"s25fl512s_512k", INFO(0x010220, 0x4f00, 256 * 1024,   256, RD_FULL | WR_QPP) },
	{"s25fl256s0",     INFO6(0x010219, 0x4d0080, 256 * 1024, 128, RD_FULL) },
	{"s25fl256s1",     INFO6(0x010219, 0x4d0180,  64 * 1024, 512, RD_FULL) },
	{"s25fl512s",      INFO6(0x010220, 0x4d0080, 256 * 1024, 256, RD_FULL) },
	{"s25fs064s",      INFO6(0x010217, 0x4d0181,  64 * 1024, 128, RD_FULL) },
	{"s25fs128s",      INFO6(0x012018, 0x4d0181,  64 * 1024, 256, RD_FULL) },
	{"s25fl128s",      INFO6(0x012018, 0x4d0180,  64 * 1024, 256, RD_FULL) },
	{"s25fl129p0",     INFO(0x012018, 0x4d00, 256 * 1024,    64, RD_FULL) },
	{"s25fl129p1",     INFO(0x012018, 0x4d01,  64 * 1024,   256, RD_FULL) },
	{"s70fs01gs_256k", INFO(0x010221, 0x4d00, 256 * 1024,   512, RD_FULL) },
	{"s25fl064l",      INFO(0x016017, 0x0,   64 * 1024,   128, RD_FULL | SECT_4K) },
	{"s25fl256l",      INFO(0x016019, 0x0,   64 * 1024,   512, RD_FULL | SECT_4K) },
	{"s25hl512t",      INFO6(0x342a1a, 0x0f0390, 256 * 1024, 256, RD_FULL) },
	{"s25hl01gt",      INFO6(0x342a1b, 0x0f0390, 256 * 1024, 512, RD_FULL) },
	{"s25hl02gt",      INFO6(0x342a1c, 0x0f0090, 256 * 1024, 1024, RD_FULL) },
	{"s25hs512t",      INFO6(0x342b1a, 0x0f0390, 256 * 1024, 256, RD_FULL) },
	{"s25hs01gt",      INFO6(0x342b1b, 0x0f0390, 256 * 1024, 512, RD_FULL) },
	{"s25hs02gt",      INFO6(0x342b1c, 0x0f0090, 256 * 1024, 1024, RD_FULL) },
	{"s25fs256t",      INFO6(0x342b19, 0x0f0890, 128 * 1024, 256, RD_QUAD) },
#ifdef CONFIG_SPI_FLASH_S28HX_T
	{"s28hl256t",      INFO(0x345a19, 0x0, 256 * 1024,   128, 0) },
	{"s28hl512t",      INFO(0x345a1a, 0x0, 256 * 1024,   256, 0) },
	{"s28hl01gt",      INFO(0x345a1b, 0x0, 256 * 1024,   512, 0) },
	{"s28hl02gt",      INFO(0x345a1c, 0x0, 256 * 1024,  1024, 0) },
	{"s28hs256t",      INFO(0x345b19, 0x0, 256 * 1024,   128, 0) },
	{"s28hs512t",      INFO(0x345b1a, 0x0, 256 * 1024,   256, 0) },
	{"s28hs01gt",      INFO(0x345b1b, 0x0, 256 * 1024,   512, 0) },
	{"s28hs02gt",      INFO(0x345b1c, 0x0, 256 * 1024,  1024, 0) },
#endif
#endif
#ifdef CONFIG_SPI_FLASH_STMICRO		/* STMICRO */
	{"m25p10",	   INFO(0x202011, 0x0, 32 * 1024,     4, 0) },
	{"m25p20",	   INFO(0x202012, 0x0, 64 * 1024,     4, 0) },
	{"m25p40",	   INFO(0x202013, 0x0, 64 * 1024,     8, 0) },
	{"m25p80",	   INFO(0x202014, 0x0, 64 * 1024,    16, 0) },
	{"m25p16",	   INFO(0x202015, 0x0, 64 * 1024,    32, 0) },
	{"m25pE16",	   INFO(0x208015, 0x1000, 64 * 1024, 32, 0) },
	{"m25pX16",	   INFO(0x207115, 0x1000, 64 * 1024, 32, RD_QUAD | RD_DUAL) },
	{"m25p32",	   INFO(0x202016, 0x0,  64 * 1024,    64, 0) },
	{"m25p64",	   INFO(0x202017, 0x0,  64 * 1024,   128, 0) },
	{"m25p128",	   INFO(0x202018, 0x0, 256 * 1024,    64, 0) },
	{"m25pX64",	   INFO(0x207117, 0x0,  64 * 1024,   128, SECT_4K) },
	{"n25q016a",       INFO(0x20bb15, 0x0,	64 * 1024,    32, SECT_4K) },
	{"n25q32",	   INFO(0x20ba16, 0x0,  64 * 1024,    64, RD_FULL | WR_QPP | SECT_4K) },
	{"n25q32a",	   INFO(0x20bb16, 0x0,  64 * 1024,    64, RD_FULL | WR_QPP | SECT_4K) },
	{"n25q64",	   INFO(0x20ba17, 0x0,  64 * 1024,   128, RD_FULL | WR_QPP | SECT_4K) },
	{"n25q64a",	   INFO(0x20bb17, 0x0,  64 * 1024,   128, RD_FULL | WR_QPP | SECT_4K) },
	{"n25q128",	   INFO(0x20ba18, 0x0,  64 * 1024,   256, RD_FULL | WR_QPP) },
	{"n25q128a",	   INFO(0x20bb18, 0x0,  64 * 1024,   256, RD_FULL | WR_QPP) },
	{"n25q256",	   INFO(0x20ba19, 0x0,  64 * 1024,   512, RD_FULL | WR_QPP | E_FSR | SECT_4K) },
	{"n25q256a",	   INFO(0x20bb19, 0x0,  64 * 1024,   512, RD_FULL | WR_QPP | E_FSR | SECT_4K) },
	{"n25q512",	   INFO(0x20ba20, 0x0,  64 * 1024,  1024, RD_FULL | WR_QPP | E_FSR | SECT_4K) },
	{"n25q512a",	   INFO(0x20bb20, 0x0,  64 * 1024,  1024, RD_FULL | WR_QPP | E_FSR | SECT_4K) },
	{"n25q1024",	   INFO(0x20ba21, 0x0,  64 * 1024,  2048, RD_FULL | WR_QPP | E_FSR | SECT_4K) },
	{"n25q1024a",	   INFO(0x20bb21, 0x0,  64 * 1024,  2048, RD_FULL | WR_QPP | E_FSR | SECT_4K) },
	{"mt25qu02g",	   INFO(0x20bb22, 0x0,  64 * 1024,  4096, RD_FULL | WR_QPP | E_FSR | SECT_4K) },
	{"mt25ql02g",	   INFO(0x20ba22, 0x0,  64 * 1024,  4096, RD_FULL | WR_QPP | E_FSR | SECT_4K) },
	{"mt35xu512g",	   INFO6(0x2c5b1a, 0x104100,  128 * 1024,  512, E_FSR | SECT_4K) },
	{"mt25ql256a",     INFO6(0x20ba19, 0x104400,  64 * 1024,  512, RD_FULL | E_FSR | SECT_4K) },
	{"mt25qu256a",     INFO6(0x20bb19, 0x104400,  64 * 1024,  512, RD_QUAD | E_FSR | SECT_4K) },
	{"mt25qu128ab",    INFO(0x20bb18, 0x0,   64 * 1024,  256, RD_QUAD | E_FSR | SECT_4K) },
	{"mt25qu512a",     INFO6(0x20bb20, 0x104400,  64 * 1024, 1024, RD_FULL | E_FSR | SECT_4K) },
	{"mt25ql512a",     INFO6(0x20ba20, 0x104400,  64 * 1024, 1024, RD_QUAD | E_FSR | SECT_4K) },
	{"mt25ql01g",      INFO(0x21ba20, 0x0,   64 * 1024, 2048, RD_QUAD | E_FSR | SECT_4K) },
	{"mt25qu01g",      INFO6(0x20bb21, 0x104400,  64 * 1024, 2048, RD_QUAD | E_FSR | SECT_4K) },
#ifdef CONFIG_SPI_FLASH_MT35XU
	{"mt35xl512aba",   INFO(0x2c5a1a, 0x0,   128 * 1024,  512, E_FSR | SECT_4K) },
	{"mt35xu512aba",   INFO(0x2c5b1a, 0x0,   128 * 1024,  512, E_FSR | SECT_4K) },
	{"mt35xu01gaba",   INFO(0x2c5b1b, 0x0,   128 * 1024, 1024, E_FSR | SECT_4K) },
#endif
	{"mt35xu01g",      INFO6(0x2c5b1b, 0x104100,  128 * 1024, 1024, E_FSR | SECT_4K) },
	{"mt35xu02g",      INFO(0x2c5b1c, 0x0,   128 * 1024, 2048, E_FSR | SECT_4K) },
	{"m25pe16",        INFO(0x208015, 0x0,   64 * 1024,   32, SECT_4K) },
	{"m25px16",        INFO(0x207115, 0x0,   64 * 1024,   32, RD_FULL | SECT_4K) },
#endif
#ifdef CONFIG_SPI_FLASH_SST		/* SST */
	{"sst25vf040b",	   INFO(0xbf258d, 0x0,	64 * 1024,     8, SECT_4K | SST_WR) },
	{"sst25vf080b",	   INFO(0xbf258e, 0x0,	64 * 1024,    16, SECT_4K | SST_WR) },
	{"sst25vf016b",	   INFO(0xbf2541, 0x0,	64 * 1024,    32, SECT_4K | SST_WR) },
	{"sst25vf032b",	   INFO(0xbf254a, 0x0,	64 * 1024,    64, SECT_4K | SST_WR) },
	{"sst25vf064c",	   INFO(0xbf254b, 0x0,	64 * 1024,   128, SECT_4K) },
	{"sst25wf512",	   INFO(0xbf2501, 0x0,	64 * 1024,     1, SECT_4K | SST_WR) },
	{"sst25wf010",	   INFO(0xbf2502, 0x0,	64 * 1024,     2, SECT_4K | SST_WR) },
	{"sst25wf020",	   INFO(0xbf2503, 0x0,	64 * 1024,     4, SECT_4K | SST_WR) },
	{"sst25wf040",	   INFO(0xbf2504, 0x0,	64 * 1024,     8, SECT_4K | SST_WR) },
	{"sst25wf040b",	   INFO(0x621613, 0x0,	64 * 1024,     8, SECT_4K) },
	{"sst25wf080",	   INFO(0xbf2505, 0x0,	64 * 1024,    16, SECT_4K | SST_WR) },
	{"sst26wf016",	   INFO(0xbf2651, 0x0,	64 * 1024,    32, SECT_4K) },
	{"sst26wf032",	   INFO(0xbf2622, 0x0,	64 * 1024,    64, SECT_4K) },
	{"sst26wf064",	   INFO(0xbf2643, 0x0,	64 * 1024,   128, SECT_4K) },
	{"sst25wf020a",    INFO(0x621612, 0x0,	64 * 1024,     4, SECT_4K) },
	{"sst26wf016b",    INFO(0xbf2641, 0x0,	64 * 1024,    32, SECT_4K) },
	{"sst26vf064b",    INFO(0xbf2643, 0x0,	64 * 1024,   128, RD_FULL | SECT_4K) },
#endif
#ifdef CONFIG_SPI_FLASH_WINBOND		/* WINBOND */
	{"w25p80",	   INFO(0xef2014, 0x0,	64 * 1024,    16, 0) },
	{"w25p16",	   INFO(0xef2015, 0x0,	64 * 1024,    32, 0) },
	{"w25p32",	   INFO(0xef2016, 0x0,	64 * 1024,    64, 0) },
	{"w25x05",	   INFO(0xef3010, 0x0,	64 * 1024,     1, SECT_4K) },
	{"w25x40",	   INFO(0xef3013, 0x0,	64 * 1024,     8, SECT_4K) },
	{"w25x16",	   INFO(0xef3015, 0x0,	64 * 1024,    32, SECT_4K) },
	{"w25x32",	   INFO(0xef3016, 0x0,	64 * 1024,    64, SECT_4K) },
	{"w25x64",	   INFO(0xef3017, 0x0,	64 * 1024,   128, SECT_4K) },
	{"w25q20cl",	   INFO(0xef4012, 0x0,	64 * 1024,     4, SECT_4K) },
	{"w25q20bw",	   INFO(0xef5012, 0x0,	64 * 1024,     4, SECT_4K) },
	{"w25q20ew",	   INFO(0xef6012, 0x0,	64 * 1024,     4, SECT_4K) },
	{"w25q80",	   INFO(0xef5014, 0x0,	64 * 1024,    16, SECT_4K) },
	{"w25q80bl",	   INFO(0xef4014, 0x0,	64 * 1024,    16, RD_FULL | WR_QPP | SECT_4K) },
	{"w25q16cl",	   INFO(0xef4015, 0x0,	64 * 1024,    32, RD_FULL | WR_QPP | SECT_4K) },
	{"w25q32",	   INFO(0xef4016, 0x0,	64 * 1024,    64, RD_FULL | SECT_4K) },
	{"w25q32bv",	   INFO(0xef4016, 0x0,	64 * 1024,    64, RD_FULL | WR_QPP | SECT_4K) },
	{"w25q64cv",	   INFO(0xef4017, 0x0,	64 * 1024,   128, RD_FULL | WR_QPP | SECT_4K) },
	{"w25q128",	   INFO(0xef4018, 0x0,	64 * 1024,   256, RD_FULL | SECT_4K) },
	{"w25q128bv",	   INFO(0xef4018, 0x0,	64 * 1024,   256, RD_FULL | WR_QPP | SECT_4K) },
	{"w25q256",	   INFO(0xef4019, 0x0,	64 * 1024,   512, RD_FULL | WR_QPP | SECT_4K) },
	{"w25q80bw",	   INFO(0xef5014, 0x0,	64 * 1024,    16, RD_FULL | WR_QPP | SECT_4K) },
	{"w25q16dw",	   INFO(0xef6015, 0x0,	64 * 1024,    32, RD_FULL | WR_QPP | SECT_4K) },
	{"w25q16jv",	   INFO(0xef7015, 0x0,	64 * 1024,    32, RD_FULL | WR_QPP | SECT_4K) },
	{"w25q32dw",	   INFO(0xef6016, 0x0,	64 * 1024,    64, RD_FULL | WR_QPP | SECT_4K) },
	{"w25q32jv",	   INFO(0xef7016, 0x0,	64 * 1024,    64, RD_FULL | WR_QPP | SECT_4K) },
	{"w25q32jwm",	   INFO(0xef8016, 0x0,	64 * 1024,    64, RD_FULL | SECT_4K) },
	{"w25q64dw",	   INFO(0xef6017, 0x0,	64 * 1024,   128, RD_FULL | WR_QPP | SECT_4K) },
	{"w25q64jv",	   INFO(0xef7017, 0x0,	64 * 1024,   128, RD_FULL | WR_QPP | SECT_4K) },
	{"w25q128fw",	   INFO(0xef6018, 0x0,	64 * 1024,   256, RD_FULL | WR_QPP | SECT_4K) },
	{"w25q128jv",	   INFO(0xef7018, 0x0,	64 * 1024,   256, RD_FULL | WR_QPP | SECT_4K) },
	{"w25q128jw",	   INFO(0xef8018, 0x0,	64 * 1024,   256, RD_FULL | WR_QPP | SECT_4K) },
	{"w25q256fw",	   INFO(0xef6019, 0x0,	64 * 1024,   512, RD_FULL | WR_QPP | SECT_4K) },
	{"w25q256jw",	   INFO(0xef7019, 0x0,	64 * 1024,   512, RD_FULL | WR_QPP | SECT_4K) },
	{"w25q256jwm",	   INFO(0xef8019, 0x0,	64 * 1024,   512, RD_FULL | SECT_4K) },
	{"w25q512jvq",	   INFO(0xef4020, 0x0,	64 * 1024,   1024, RD_FULL | WR_QPP | SECT_4K) },
	{"w25q512nwq",	   INFO(0xef6020, 0x0,	64 * 1024,  1024, RD_FULL | SECT_4K) },
	{"w25q512nwm",	   INFO(0xef8020, 0x0,	64 * 1024,  1024, RD_FULL | SECT_4K) },
	{"w25q01jv",	   INFO(0xef4021, 0x0,	64 * 1024,  2048, RD_FULL | SECT_4K) },
	{"w25q01jvfim",	   INFO(0xef7021, 0x0,	64 * 1024,  2048, RD_FULL | SECT_4K) },
	{"w25q02jv",	   INFO(0xef7022, 0x0,	64 * 1024,  4096, RD_FULL | SECT_4K) },
	{"w25m512jw",	   INFO(0xef6119, 0x0,	64 * 1024,  1024, RD_FULL | SECT_4K) },
	{"w25m512jv",	   INFO(0xef7119, 0x0,	64 * 1024,  1024, RD_FULL | SECT_4K) },
	{"w25h02jv",	   INFO(0xef9022, 0x0,	64 * 1024,  4096, RD_FULL | SECT_4K) },
	{"w25h512nw-am",   INFO(0xefa020, 0x0,	64 * 1024,  1024, RD_FULL | SECT_4K) },
	{"w25h01nw-am",	   INFO(0xefa021, 0x0,	64 * 1024,  2048, RD_FULL | SECT_4K) },
	{"w25h02nw-am",	   INFO(0xefa022, 0x0,	64 * 1024,  4096, RD_FULL | SECT_4K) },
	{"w25q01nw-iq",	   INFO(0xef6021, 0x0,	64 * 1024,  2048, RD_FULL | SECT_4K) },
	{"w25q01nw-im",	   INFO(0xef8021, 0x0,	64 * 1024,  2048, RD_FULL | SECT_4K) },
	{"w25q02nw-im",	   INFO(0xef8022, 0x0,	64 * 1024,  4096, RD_FULL | SECT_4K) },
	{"w77q51nw",	   INFO(0xef8a1a, 0x0,	64 * 1024,  1024, RD_FULL | SECT_4K) },
#endif
#ifdef CONFIG_SPI_FLASH_XMC
	/* XMC (Wuhan Xinxin Semiconductor Manufacturing Corp.) */
	{ "XM25QH64A",		INFO(0x207017, 0x0, 64 * 1024, 128, RD_FULL | SECT_4K) },
	{ "XM25QH64C",		INFO(0x204017, 0x0, 64 * 1024, 128, RD_FULL | SECT_4K) },
	{ "XM25QH128A",		INFO(0x207018, 0x0, 64 * 1024, 256, RD_FULL | SECT_4K) },
	{ "XM25QH128C",		INFO(0x204018, 0x0, 64 * 1024, 256, RD_FULL | SECT_4K) },
	{ "XM25QU128C",		INFO(0x204118, 0x0, 64 * 1024, 256, RD_FULL | SECT_4K) },
	{ "XM25QH256C",		INFO(0x204019, 0x0, 64 * 1024, 512, RD_FULL | SECT_4K) },
	{ "XM25QU256C",		INFO(0x204119, 0x0, 64 * 1024, 512, RD_FULL | SECT_4K) },
	{ "XM25QH512C",		INFO(0x204020, 0x0, 64 * 1024, 1024, RD_FULL | SECT_4K) },
	{ "XM25QU512C",		INFO(0x204120, 0x0, 64 * 1024, 1024, RD_FULL | SECT_4K) },
	{ "XM25QH01D",		INFO(0x204021, 0x0, 64 * 1024, 2048, RD_FULL | SECT_4K) },
#endif
#ifdef CONFIG_SPI_FLASH_XTX		/* XTX */
	{"xt25f08",        INFO(0x0b4014, 0x0, 64 * 1024,    16, RD_FULL | SECT_4K) },
	{"xt25f16",        INFO(0x0b4015, 0x0, 64 * 1024,    32, RD_FULL | SECT_4K) },
	{"xt25f32",        INFO(0x0b4016, 0x0, 64 * 1024,    64, RD_FULL | SECT_4K) },
	{"xt25f64",        INFO(0x0b4017, 0x0, 64 * 1024,   128, RD_FULL | SECT_4K) },
	{"xt25f128",       INFO(0x0b4018, 0x0, 64 * 1024,   256, RD_FULL | SECT_4K) },
	{"xt25f256",       INFO(0x0b4019, 0x0, 64 * 1024,   512, RD_FULL | SECT_4K) },
	{"xt25q08",        INFO(0x0b6014, 0x0, 64 * 1024,   16, RD_FULL | SECT_4K) },
	{"xt25q16",        INFO(0x0b6015, 0x0, 64 * 1024,   32, RD_FULL | SECT_4K) },
	{"xt25q32",        INFO(0x0b6016, 0x0, 64 * 1024,   64, RD_FULL | SECT_4K) },
	{"xt25q64",        INFO(0x0b6017, 0x0, 64 * 1024,  128, RD_FULL | SECT_4K) },
	{"xt25q128",       INFO(0x0b6018, 0x0, 64 * 1024,  256, RD_FULL | SECT_4K) },
	{"xt25q256",       INFO(0x0b6019, 0x0, 64 * 1024,  512, RD_FULL | SECT_4K) },
	{"xt25q512",       INFO(0x0b601a, 0x0, 64 * 1024, 1024, RD_FULL | SECT_4K) },
	{"xt25q01g",       INFO(0x0b601b, 0x0, 64 * 1024, 2048, RD_FULL | SECT_4K) },
	{"xt55q02g",       INFO(0x0b601c, 0x0, 64 * 1024, 4096, RD_FULL | SECT_4K) },
	{"xt25w512",       INFO(0x0b651a, 0x0, 64 * 1024, 1024, RD_FULL | SECT_4K) },
	{"xt25w01g",       INFO(0x0b651b, 0x0, 64 * 1024, 2048, RD_FULL | SECT_4K) },
#endif
#ifdef CONFIG_SPI_FLASH_ZBIT		/* ZBIT */
	{"zb25vq128",      INFO(0x5e4018, 0x0, 64 * 1024,   256, RD_FULL | SECT_4K) },
#endif
	{},	/* Empty entry to terminate the list */
	/*
	 * Note:
	 * Below paired flash devices has similar spi_flash params.
	 * (s25fl129p_64k, s25fl128s_64k)
	 * (w25q80bl, w25q80bv)
	 * (w25q16cl, w25q16dv, w25q16jv)
	 * (w25q32bv, w25q32fv_spi)
	 * (w25q64cv, w25q64fv_spi)
	 * (w25q128bv, w25q128fv_spi)
	 * (w25q32dw, w25q32fv_qpi)
	 * (w25q64dw, w25q64fv_qpi)
	 * (w25q128fw, w25q128fv_qpi)
	 * (w25q256fw, w25q256fv_qpi)
	 */
};
