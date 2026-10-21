# 蒲公英固件解包报告（oraybox-firmwares）

- 固件 127 个，型号/硬件组合 52 个；提取到 DTS 49 份，含引导区 91 份，按内容去重的引导区 88 个，按 banner+版本戳去重的原厂 u-boot 构建 46 种。

## 型号对照表

| 型号 | 硬件 | 介质 | SoC/板名 | DTB model | u-boot banner | 版本戳 | uImage@ | squashfs@ | DTS |
|---|---|---|---|---|---|---|---|---|---|
| A20 | 1226 | ? |  |  |  |  | 0x0 | - | - |
| A500 |  | nand | HCMT7621 | MTK Wireless HCMT7621 N512 Board | U-Boot 1.1.3 (Aug 21 2020 - 18:57:47) | U_BOOT 00000100 | 0x140000 | 0x381000 | Y |
| E3 | 1141 | spi-nor |  |  | U-Boot 1.1.3 (Nov 15 2018 - 16:25:22) | U_BOOT 00000001 | 0x50000 | 0x160000 | - |
| G100PRO |  | spi-nor |  |  |  |  | - | 0xa80000 | - |
| G100PRO | 1240 | spi-nor |  |  |  |  | - | 0xa80000 | - |
| G100PRO | 2240 | spi-nor |  |  |  |  | - | 0xa80000 | - |
| G100PRO | 3260 | spi-nor |  |  |  |  | - | 0xa80000 | - |
| G300 | 42120 | nand |  |  |  |  | - | - | - |
| G300PRO |  | spi-nor |  |  |  |  | - | 0xa80000 | - |
| G5 | 1250 | spi-nor | HCMT7621 |  | U-Boot 1.1.3 (Feb 27 2020 - 18:46:51) | U_BOOT 00000009 | 0x50000 | 0x1c0000 | - |
| G5 | 2250 | nand | HCMT7621 |  | U-Boot 1.1.3 (Apr  6 2021 - 21:54:24) | U_BOOT 00000013 | 0x140000 | 0x2c0000 | - |
| ORG | 220 | spi-nor | HCMT7621 |  | U-Boot 1.1.3 (Aug 29 2019 - 10:58:58) | U_BOOT 00000009 | 0x50000 | 0x1c0000 | - |
| ORH | 180 | spi-nor | HCMT7628 |  | U-Boot 1.1.3 (Aug 29 2019 - 09:45:51) | U_BOOT 00000007 | 0x50000 | 0x190000 | - |
| ORH | 260 | spi-nor | HCMT7621 | HC-WT6704 | U-Boot 1.1.3 (Aug 21 2020 - 18:57:47) | U_BOOT 00000100 | 0x50000 | 0x1d0000 | Y |
| P5 | 1210 | nand | HCMT7621 |  | U-Boot 1.1.3 (Jul 19 2021 - 20:00:53) | U_BOOT 00000013 | 0x140000 | 0x2c0000 | - |
| P5 | 2210 | nand | HCMT7621 | HC-WT6718 | U-Boot 1.1.3 (Aug 21 2020 - 18:57:47) | U_BOOT 00000100 | 0x140000 | 0x381000 | Y |
| R300 | 1121G | spi-nor | HCMT7620 |  | U-Boot 1.1.3 (Jun 29 2016 - 02:00:11) | U_BOOT 00000007 | 0x50000 | 0x190000 | - |
| R300 | 2121G | spi-nor | HCMT7620 | HC-WT6304 | U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | 0x50000 | 0x1a0000 | Y |
| R300A | 1121G | spi-nor | HCMT7620 | HC-WT6304 | U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | 0x50000 | 0x1a0000 | Y |
| R300A | 2151G | spi-nor | HCMT7620 | HC-WT6313 | U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | 0x50000 | 0x1a0000 | Y |
| R300A | 3151G | spi-nor | oraybox | OrayBox-R300A-3151G |  |  | 0x0 | 0x14fb96 | Y |
| R300A | 4151G | ? | oraybox | OrayBox-R300A-4151G |  |  | 0x0 | - | Y |
| R300C | 1121G | spi-nor | HCMT7620 | HC-WT6302 | U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | 0x50000 | 0x1a0000 | Y |
| R300PRO | 1153G | spi-nor | HCMT7620 | HC-WT6306 | U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | 0x50000 | 0x190000 | Y |
| R300S | 1151G | spi-nor | WT6320 | HC-WT6320 | U-Boot 1.1.3 (Mar  8 2021 - 15:41:48) |  | 0x50000 | 0x1a0000 | Y |
| R300S | 2151GP | spi-nor | oraybox-r300s-2151gp | OrayBox-R300S-2151GP |  |  | 0x0 | 0x150fa6 | Y |
| V1000 | GK00600X | spi-nor |  |  |  |  | - | 0xa80000 | - |
| V2000 | 1260 | spi-nor |  |  |  |  | - | 0xa80000 | - |
| X1 | 1111 | spi-nor |  |  | U-Boot 1.1.3 (May 13 2019 - 15:14:52) | U_BOOT 00000001 | 0x50000 | 0x160000 | - |
| X1 | 2111 | spi-nor |  |  | U-Boot 1.1.3 (Aug 19 2020 - 17:12:08) | U_BOOT 00000001 | 0x50000 | 0x190000 | - |
| X1 | 3111 | spi-nor | WT6271-128 | HC-WT6271-128 | U-Boot 1.1.3 (May 12 2022 - 17:34:39) | U_BOOT 00000010 | 0x50000 | 0x190000 | Y |
| X1 | 4111 | ? | oraybox | OrayBox-X1-4111 |  |  | 0x0 | - | Y |
| X3 | 2151 | spi-nor | HCMT7628 |  | U-Boot 1.1.3 (May 29 2019 - 15:39:34) | U_BOOT 00000007 | 0x50000 | 0x190000 | - |
| X3 | 3251 | spi-nor | HCMT7628 | HC-WT6503 | U-Boot 1.1.3 (Aug 27 2020 - 14:04:05) | U_BOOT 00000100 | 0x50000 | 0x190000 | Y |
| X3 | D1509 | spi-nor | HCMT7620 |  | U-Boot 1.1.3 (Aug 13 2015 - 15:32:11) | U_BOOT 00000003 | 0x50000 | 0x150000 | - |
| X3 | D1509A | spi-nor | HCMT7628 |  | U-Boot 1.1.3 (Sep 19 2018 - 10:29:01) | U_BOOT 00000007 | 0x50000 | 0x160000 | - |
| X3A | 1233 | spi-nor | mediatek | OrayBox-X3A | U-Boot 2018.11 (Dec 28 2022 - 06:04:04 +0000) |  | 0x3fec0 | 0x23fec0 | Y |
| X3PRO | 1153 | spi-nor | HCMT7628 |  | U-Boot 1.1.3 (Feb  5 2021 - 18:44:28) | U_BOOT 00000007 | 0x50000 | 0x190000 | - |
| X4 | 1123G | spi-nor | HCMT7620 |  | U-Boot 1.1.3 (Jun 29 2016 - 02:00:11) | U_BOOT 00000007 | 0x50000 | 0x190000 | - |
| X4C | 1141G | spi-nor |  |  | U-Boot 1.1.3 (May 20 2020 - 13:57:00) | U_BOOT 00000001 | 0x50000 | 0x160000 | - |
| X4C | 3131G | spi-nor | WT6271-128 | HC-WT6271 | U-Boot 1.1.3 (May 12 2022 - 17:34:39) | U_BOOT 00000010 | 0x50000 | 0x190000 | Y |
| X5 | 1253 | spi-nor | HCMT7621 |  | U-Boot 1.1.3 (May 30 2019 - 16:54:16) | U_BOOT 00000009 | 0x50000 | 0x1c0000 | - |
| X5 | 2253 | spi-nor | HCMT7621 |  | U-Boot 1.1.3 (May 27 2019 - 16:36:06) | U_BOOT 00000009 | 0x50000 | 0x1c0000 | - |
| X5 | 3353 | spi-nor | HCMT7621 |  | U-Boot 1.1.3 (Feb 17 2020 - 14:59:39) | U_BOOT 00000009 | 0x50000 | 0x1c0000 | - |
| X5 | 4253 | nand | HCMT7621 |  | U-Boot 1.1.3 (Jan 12 2021 - 17:42:57) | U_BOOT 00000013 | 0x140000 | 0x2c0000 | - |
| X5 | 5255 | nand | HCMT7621 |  | U-Boot 1.1.3 (Dec 30 2020 - 12:38:16) | U_BOOT 00000013 | 0x140000 | 0x2c0000 | - |
| X5 | 6256 | nand | HCMT7620|HCMT7621 | HC-WT6708 | U-Boot 1.1.3 (Nov 30 2021 - 16:22:52) | U_BOOT 00000101 | 0x140000 | 0x381000 | Y |
| X5 | 7256 | ? |  |  |  |  | 0x400 | - | - |
| X5PRO | 1258 | ? |  |  |  |  | - | - | - |
| X6 | 1293P | spi-nor | HCMT7621 |  | U-Boot 1.1.3 (May 27 2019 - 09:25:34) | U_BOOT 00000003 | 0x50000 | 0x190000 | - |
| X6 | 2293P | spi-nor | HCMT7621 |  | U-Boot 1.1.3 (May 23 2019 - 19:04:48) | U_BOOT 00000003 | 0x50000 | 0x190000 | - |
| X6 | 3293P | nand | HCMT7621 |  | U-Boot 1.1.3 (Apr 23 2021 - 17:45:52) | U_BOOT 00000014 | 0x140000 | 0x2e0000 | - |

## 分区表（来自固件内 DTB 反编译）

| 型号 | 硬件 | 分区 |
|---|---|---|
| A500 |  | `u-boot` 0x00+0x80000 `kpanic` 0x80000+0x80000 `factory` 0x100000+0x40000 `firmware` 0x140000+0x2000000 `debug` 0x2140000+0x80000 `bdinfo` 0x21c0000+0x80000 `reserve` 0x2240000+0x80000 `overlay` 0x22c0000+0x1000000 `opt` 0x52c0000+0x2cc0000 `firmware_backup` 0x32c0000+0x2000000 |
| ORH | 260 | `u-boot` 0x00+0x30000 `kpanic` 0x30000+0x10000 `factory` 0x40000+0x10000 `firmware` 0x50000+0xf90000 `bdinfo` 0xfe0000+0x10000 `reserve` 0xff0000+0x10000 |
| P5 | 2210 | `u-boot` 0x00+0x80000 `kpanic` 0x80000+0x80000 `factory` 0x100000+0x40000 `firmware` 0x140000+0x2000000 `debug` 0x2140000+0x80000 `bdinfo` 0x21c0000+0x80000 `reserve` 0x2240000+0x80000 `overlay` 0x22c0000+0x5cc0000 |
| R300 | 2121G | `u-boot` 0x00+0x30000 `kpanic` 0x30000+0x10000 `factory` 0x40000+0x10000 `firmware` 0x50000+0xf90000 `bdinfo` 0xfe0000+0x10000 `reserve` 0xff0000+0x10000 |
| R300A | 1121G | `u-boot` 0x00+0x30000 `kpanic` 0x30000+0x10000 `factory` 0x40000+0x10000 `firmware` 0x50000+0xf90000 `bdinfo` 0xfe0000+0x10000 `reserve` 0xff0000+0x10000 |
| R300A | 2151G | `u-boot` 0x00+0x30000 `kpanic` 0x30000+0x10000 `factory` 0x40000+0x10000 `firmware` 0x50000+0xf90000 `bdinfo` 0xfe0000+0x10000 `reserve` 0xff0000+0x10000 |
| R300A | 3151G | `u-boot` 0x00+0x30000 `u-boot-env` 0x30000+0x10000 `factory` 0x40000+0x10000 `firmware` 0x50000+0xf90000 `bdinfo` 0xfe0000+0x10000 `reserve` 0xff0000+0x10000 `fullflash` 0x00+0x00 |
| R300A | 4151G | `u-boot` 0x00+0x30000 `u-boot-env` 0x30000+0x10000 `factory` 0x40000+0x10000 `firmware` 0x50000+0xf90000 `bdinfo` 0xfe0000+0x10000 `reserve` 0xff0000+0x10000 `fullflash` 0x00+0x00 |
| R300C | 1121G | `u-boot` 0x00+0x30000 `kpanic` 0x30000+0x10000 `factory` 0x40000+0x10000 `firmware` 0x50000+0xf90000 `bdinfo` 0xfe0000+0x10000 `reserve` 0xff0000+0x10000 |
| R300PRO | 1153G | `u-boot` 0x00+0x30000 `kpanic` 0x30000+0x10000 `factory` 0x40000+0x10000 `firmware` 0x50000+0xf90000 `bdinfo` 0xfe0000+0x10000 `reserve` 0xff0000+0x10000 |
| R300S | 1151G | `u-boot` 0x00+0x30000 `kpanic` 0x30000+0x10000 `factory` 0x40000+0x10000 `firmware` 0x50000+0xf90000 `bdinfo` 0xfe0000+0x10000 `reserve` 0xff0000+0x10000 |
| R300S | 2151GP | `u-boot` 0x00+0x30000 `u-boot-env` 0x30000+0x10000 `factory` 0x40000+0x10000 `firmware` 0x50000+0xf90000 `bdinfo` 0xfe0000+0x10000 `reserve` 0xff0000+0x10000 |
| X1 | 3111 | `u-boot` 0x00+0x30000 `kpanic` 0x30000+0x10000 `factory` 0x40000+0x10000 `firmware` 0x50000+0xf90000 `bdinfo` 0xfe0000+0x10000 `reserve` 0xff0000+0x10000 |
| X1 | 4111 | `u-boot` 0x00+0x30000 `u-boot-env` 0x30000+0x10000 `factory` 0x40000+0x10000 `firmware` 0x50000+0xf90000 `bdinfo` 0xfe0000+0x10000 `reserve` 0xff0000+0x10000 `fullflash` 0x00+0x00 |
| X3 | 3251 | `u-boot` 0x00+0x30000 `kpanic` 0x30000+0x10000 `factory` 0x40000+0x10000 `firmware` 0x50000+0xf90000 `bdinfo` 0xfe0000+0x10000 `reserve` 0xff0000+0x10000 |
| X4C | 3131G | `u-boot` 0x00+0x30000 `kpanic` 0x30000+0x10000 `factory` 0x40000+0x10000 `firmware` 0x50000+0xf90000 `bdinfo` 0xfe0000+0x10000 `reserve` 0xff0000+0x10000 |
| X5 | 6256 | `u-boot` 0x00+0x80000 `kpanic` 0x80000+0x80000 `factory` 0x100000+0x40000 `firmware` 0x140000+0x2000000 `debug` 0x2140000+0x80000 `bdinfo` 0x21c0000+0x80000 `reserve` 0x2240000+0x80000 `overlay` 0x22c0000+0x3000000 `opt` 0x52c0000+0x2cc0000 |

## 原厂 u-boot 构建（按 banner + 版本戳去重）

| banner | 版本戳 | 引导区大小 | 覆盖型号 |
|---|---|---|---|
| U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | 327680 | R300/2121G, R300A/1121G, R300A/2151G, R300C/1121G, R300PRO/1153G |
| U-Boot 1.1.3 (Aug 21 2020 - 18:57:47) | U_BOOT 00000100 | 327680 | A500/, ORH/260, P5/2210, X5/6256 |
| U-Boot 1.1.3 (Jun 29 2016 - 02:00:11) | U_BOOT 00000007 | 327680 | R300/1121G, X4/1123G |
| U-Boot 1.1.3 (Mar  8 2021 - 15:41:48) |  | 327680 | R300S/1151G |
| U-Boot 1.1.3 (May 12 2022 - 17:34:39) | U_BOOT 00000010 | 327680 | X1/3111, X4C/3131G |
| U-Boot 1.1.3 (Aug 27 2020 - 14:04:05) | U_BOOT 00000100 | 327680 | X3/3251 |
| U-Boot 1.1.3 (May 30 2019 - 16:54:16) | U_BOOT 00000009 | 327680 | G5/1250, X5/1253 |
| U-Boot 1.1.3 (Aug 29 2019 - 09:45:51) | U_BOOT 00000007 | 327680 | ORH/180 |
| U-Boot 1.1.3 (Jul 19 2021 - 20:00:53) | U_BOOT 00000013 | 1310720 | P5/1210 |
| U-Boot 1.1.3 (May 29 2019 - 15:39:34) | U_BOOT 00000007 | 327680 | X3/2151 |
| U-Boot 1.1.3 (Feb  5 2021 - 18:44:28) | U_BOOT 00000007 | 327680 | X3PRO/1153 |
| U-Boot 1.1.3 (Mar 15 2021 - 15:36:36) | U_BOOT 00000007 | 327680 | X3/3251 |
| U-Boot 1.1.3 (Aug 13 2015 - 15:32:11) | U_BOOT 00000003 | 327680 | X3/D1509 |
| U-Boot 1.1.3 (May 20 2020 - 13:57:00) | U_BOOT 00000001 | 327680 | X4C/1141G |
| U-Boot 1.1.3 (Jan 12 2021 - 17:42:57) | U_BOOT 00000013 | 1310720 | X5/4253 |
| U-Boot 1.1.3 (May 27 2019 - 09:25:34) | U_BOOT 00000003 | 327680 | X6/1293P, X6/2293P |
| U-Boot 1.1.3 (Apr 23 2021 - 17:45:52) | U_BOOT 00000014 | 1310720 | X6/3293P |
| U-Boot 2018.11 (Dec 28 2022 - 06:04:04 +0000) |  | 67544 | X3A/1233 |
| U-Boot 1.1.3 (Nov 15 2018 - 18:10:55) | U_BOOT 00000001 | 327680 | E3/1141 |
| U-Boot 1.1.3 (Apr  6 2021 - 22:24:37) | U_BOOT 00000013 | 1310720 | G5/2250 |
| U-Boot 1.1.3 (Aug 29 2019 - 11:28:42) | U_BOOT 00000009 | 327680 | ORG/220 |
| U-Boot 1.1.3 (Apr 29 2021 - 21:09:05) | U_BOOT 00000013 | 1310720 | P5/2210 |
| U-Boot 1.1.3 (May 20 2019 - 14:53:51) | U_BOOT 00000001 | 327680 | X1/1111 |
| U-Boot 1.1.3 (Aug 20 2020 - 10:49:19) | U_BOOT 00000001 | 327680 | X1/2111 |
| U-Boot 1.1.3 (Sep 19 2018 - 16:51:45) | U_BOOT 00000007 | 327680 | X3/D1509A |
| U-Boot 1.1.3 (Nov 30 2021 - 16:22:52) | U_BOOT 00000101 | 1310720 | X5/6256 |
| U-Boot 1.1.3 (May 27 2019 - 16:41:38) | U_BOOT 00000009 | 327680 | X5/2253 |
| U-Boot 1.1.3 (Jun  3 2019 - 16:12:06) | U_BOOT 00000009 | 327680 | X5/1253 |
| U-Boot 1.1.3 (Mar 31 2019 - 18:11:32) | U_BOOT 00000009 | 327680 | X5/3353 |
| U-Boot 1.1.3 (Dec 30 2020 - 14:39:13) | U_BOOT 00000013 | 1310720 | X5/5255 |
| U-Boot 2018.11 (Aug 27 2022 - 07:48:00 +0000) |  | 0 | X5/6256 |
| U-Boot 2018.11 (Feb 15 2023 - 08:37:48 +0000) |  | 0 | X5/6256 |
| U-Boot 1.1.3 (Jun 24 2022 - 10:38:20) | U_BOOT 00000101 | 1310720 | X5/6256 |
| U-Boot 1.1.3 (May 27 2019 - 13:19:08) | U_BOOT 00000003 | 327680 | X6/1293P |
| U-Boot 1.1.3 (Nov 15 2018 - 16:25:22) | U_BOOT 00000001 | 327680 | E3/1141 |
| U-Boot 1.1.3 (Feb 27 2020 - 18:46:51) | U_BOOT 00000009 | 327680 | G5/1250 |
| U-Boot 1.1.3 (Apr  6 2021 - 21:54:24) | U_BOOT 00000013 | 1310720 | G5/2250 |
| U-Boot 1.1.3 (Aug 29 2019 - 10:58:58) | U_BOOT 00000009 | 327680 | ORG/220 |
| U-Boot 1.1.3 (Apr 29 2021 - 20:19:53) | U_BOOT 00000013 | 1310720 | P5/2210 |
| U-Boot 1.1.3 (Aug 19 2020 - 17:12:08) | U_BOOT 00000001 | 327680 | X1/2111 |
| U-Boot 1.1.3 (May 13 2019 - 15:14:52) | U_BOOT 00000001 | 327680 | X1/1111 |
| U-Boot 1.1.3 (Sep 19 2018 - 10:29:01) | U_BOOT 00000007 | 327680 | X3/D1509A |
| U-Boot 1.1.3 (Feb 17 2020 - 14:59:39) | U_BOOT 00000009 | 327680 | X5/3353 |
| U-Boot 1.1.3 (May 27 2019 - 16:36:06) | U_BOOT 00000009 | 327680 | X5/2253 |
| U-Boot 1.1.3 (Dec 30 2020 - 12:38:16) | U_BOOT 00000013 | 1310720 | X5/5255 |
| U-Boot 1.1.3 (May 23 2019 - 19:04:48) | U_BOOT 00000003 | 327680 | X6/2293P |

## 引导区按内容去重（同一型不同固件版本是否有变化）

| sha16 | 大小 | banner | 版本戳 | 特性 | 型号 |
|---|---|---|---|---|---|
| `b80988b5e4a6d0e2` | 67544 | U-Boot 2018.11 (Dec 28 2022 - 06:04:04 +0000) |  |  | X3A/1233 |
| `7c8bd62388102f4b` | 1310720 | U-Boot 1.1.3 (Aug 21 2020 - 18:57:47) | U_BOOT 00000100 | flash_write_menu,httpd_failsafe,mdio_cmds,nand,tftp_menu,uip_stack | A500/ |
| `06d67b0a3a503857` | 327680 | U-Boot 1.1.3 (Nov 15 2018 - 18:10:55) | U_BOOT 00000001 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | E3/1141 |
| `e77132213924999e` | 327680 | U-Boot 1.1.3 (May 30 2019 - 16:54:16) | U_BOOT 00000009 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | G5/1250 |
| `a97b493d291ca8f8` | 327680 | U-Boot 1.1.3 (Aug 29 2019 - 09:45:51) | U_BOOT 00000007 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | ORH/180 |
| `611a3537d67f18bb` | 1310720 | U-Boot 1.1.3 (Apr  6 2021 - 22:24:37) | U_BOOT 00000013 | flash_write_menu,httpd_failsafe,mdio_cmds,nand,tftp_menu,uip_stack | G5/2250 |
| `cd42f0dc80a0bae5` | 327680 | U-Boot 1.1.3 (Aug 29 2019 - 11:28:42) | U_BOOT 00000009 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | ORG/220 |
| `8863161658a9a1d3` | 1310720 | U-Boot 1.1.3 (Jul 19 2021 - 20:00:53) | U_BOOT 00000013 | flash_write_menu,httpd_failsafe,mdio_cmds,nand,tftp_menu,uip_stack | P5/1210 |
| `523b494119824da1` | 327680 | U-Boot 1.1.3 (Aug 21 2020 - 18:57:47) | U_BOOT 00000100 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | ORH/260 |
| `a61ee5af510ae5e6` | 327680 | U-Boot 1.1.3 (Aug 21 2020 - 18:57:47) | U_BOOT 00000100 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | ORH/260 |
| `f79ec6ba63ffc817` | 1310720 | U-Boot 1.1.3 (Apr 29 2021 - 21:09:05) | U_BOOT 00000013 | flash_write_menu,httpd_failsafe,mdio_cmds,nand,tftp_menu,uip_stack | P5/2210 |
| `ee7708fbb7b57fd7` | 327680 | U-Boot 1.1.3 (Jun 29 2016 - 02:00:11) | U_BOOT 00000007 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300/1121G |
| `8d48ec0186aa486a` | 1310720 | U-Boot 1.1.3 (Aug 21 2020 - 18:57:47) | U_BOOT 00000100 | flash_write_menu,httpd_failsafe,mdio_cmds,nand,tftp_menu,uip_stack | P5/2210 |
| `6e69d25d06deac21` | 327680 | U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300A/1121G |
| `7e5433a44d38d345` | 327680 | U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300A/2151G |
| `aae76e2cec6aa9ec` | 327680 | U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300A/2151G |
| `c5ede189bab18a8c` | 327680 | U-Boot 1.1.3 (Mar  8 2021 - 15:41:48) |  | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300S/1151G |
| `c49c95406daf99ad` | 327680 | U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300C/1121G |
| `9757e313526c57d9` | 327680 | U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300PRO/1153G |
| `406cf3f9b01ad105` | 327680 | U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300/2121G |
| `56d7c0d21af211db` | 327680 | U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300/2121G |
| `e7ede3564922c199` | 327680 | U-Boot 1.1.3 (Mar  8 2021 - 15:41:48) |  | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300S/1151G |
| `e048070ddecd12a6` | 327680 | U-Boot 1.1.3 (May 20 2019 - 14:53:51) | U_BOOT 00000001 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X1/1111 |
| `edcc6fa13c03ac2c` | 327680 | U-Boot 1.1.3 (Aug 20 2020 - 10:49:19) | U_BOOT 00000001 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X1/2111 |
| `efa329a0fa4a5e42` | 327680 | U-Boot 1.1.3 (May 12 2022 - 17:34:39) | U_BOOT 00000010 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X1/3111 |
| `326fe6c2c268b7d1` | 327680 | U-Boot 1.1.3 (May 29 2019 - 15:39:34) | U_BOOT 00000007 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X3/2151 |
| `6cc3096bd5b0f2b6` | 327680 | U-Boot 1.1.3 (Feb  5 2021 - 18:44:28) | U_BOOT 00000007 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X3PRO/1153 |
| `3d3de6465cbf4235` | 327680 | U-Boot 1.1.3 (Mar 15 2021 - 15:36:36) | U_BOOT 00000007 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X3/3251 |
| `f2fc8c97f3a6e067` | 327680 | U-Boot 1.1.3 (Sep 19 2018 - 16:51:45) | U_BOOT 00000007 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X3/D1509A |
| `e31c45d91319baca` | 327680 | U-Boot 1.1.3 (Aug 13 2015 - 15:32:11) | U_BOOT 00000003 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X3/D1509 |
| `6c0e20226caf27b4` | 327680 | U-Boot 1.1.3 (May 20 2020 - 13:57:00) | U_BOOT 00000001 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X4C/1141G |
| `47ba366828dde86f` | 1310720 | U-Boot 1.1.3 (Nov 30 2021 - 16:22:52) | U_BOOT 00000101 | flash_write_menu,httpd_failsafe,mdio_cmds,nand,tftp_menu,uip_stack | X5/6256 |
| `61bd28fa8e79ba71` | 327680 | U-Boot 1.1.3 (Jun 29 2016 - 02:00:11) | U_BOOT 00000007 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X4/1123G |
| `9bba9637d2f72ca8` | 327680 | U-Boot 1.1.3 (May 12 2022 - 17:34:39) | U_BOOT 00000010 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X4C/3131G |
| `8c3b39d5892a251e` | 327680 | U-Boot 1.1.3 (May 27 2019 - 16:41:38) | U_BOOT 00000009 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X5/2253 |
| `c81356c3cfa21d94` | 327680 | U-Boot 1.1.3 (Jun  3 2019 - 16:12:06) | U_BOOT 00000009 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X5/1253 |
| `699d7f48731de708` | 327680 | U-Boot 1.1.3 (Mar 31 2019 - 18:11:32) | U_BOOT 00000009 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X5/3353 |
| `dd342b1e654ad056` | 1310720 | U-Boot 1.1.3 (Dec 30 2020 - 14:39:13) | U_BOOT 00000013 | flash_write_menu,httpd_failsafe,mdio_cmds,nand,tftp_menu,uip_stack | X5/5255 |
| `72faae332db07096` | 1310720 | U-Boot 1.1.3 (Aug 21 2020 - 18:57:47) | U_BOOT 00000100 | flash_write_menu,httpd_failsafe,mdio_cmds,nand,tftp_menu,uip_stack | X5/6256 |
| `a552af55bf037754` | 1310720 | U-Boot 1.1.3 (Jan 12 2021 - 17:42:57) | U_BOOT 00000013 | flash_write_menu,httpd_failsafe,mdio_cmds,nand,tftp_menu,uip_stack | X5/4253 |
| `a2f0c91de11670c7` | 1310720 | U-Boot 1.1.3 (Jun 24 2022 - 10:38:20) | U_BOOT 00000101 | flash_write_menu,httpd_failsafe,mdio_cmds,nand,tftp_menu,uip_stack | X5/6256 |
| `2e6f5a9bb37635f9` | 327680 | U-Boot 1.1.3 (May 27 2019 - 13:19:08) | U_BOOT 00000003 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X6/1293P |
| `7826d1c63b465e0f` | 327680 | U-Boot 1.1.3 (May 27 2019 - 09:25:34) | U_BOOT 00000003 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X6/2293P |
| `44539af91bcd20fc` | 1310720 | U-Boot 1.1.3 (Apr 23 2021 - 17:45:52) | U_BOOT 00000014 | flash_write_menu,httpd_failsafe,mdio_cmds,nand,tftp_menu,uip_stack | X6/3293P |
| `370be1653d8bf975` | 327680 | U-Boot 1.1.3 (Aug 27 2020 - 14:04:05) | U_BOOT 00000100 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X3/3251 |
| `dba82726c2328778` | 327680 | U-Boot 1.1.3 (Aug 27 2020 - 14:04:05) | U_BOOT 00000100 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X3/3251 |
| `5aec223fa013b114` | 327680 | U-Boot 1.1.3 (Nov 15 2018 - 16:25:22) | U_BOOT 00000001 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | E3/1141 |
| `09bec68cf3daed5b` | 1310720 | U-Boot 1.1.3 (Aug 21 2020 - 18:57:47) | U_BOOT 00000100 | flash_write_menu,httpd_failsafe,mdio_cmds,nand,tftp_menu,uip_stack | A500/ |
| `9c39f2ab7f29d67f` | 327680 | U-Boot 1.1.3 (Feb 27 2020 - 18:46:51) | U_BOOT 00000009 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | G5/1250 |
| `33448181633660e5` | 1310720 | U-Boot 1.1.3 (Apr  6 2021 - 21:54:24) | U_BOOT 00000013 | flash_write_menu,httpd_failsafe,mdio_cmds,nand,tftp_menu,uip_stack | G5/2250 |
| `8d0fd5ddb7d24d40` | 327680 | U-Boot 1.1.3 (Aug 29 2019 - 10:58:58) | U_BOOT 00000009 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | ORG/220 |
| `4f49c78a43866521` | 327680 | U-Boot 1.1.3 (Aug 29 2019 - 09:45:51) | U_BOOT 00000007 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | ORH/180 |
| `01fbe3c0b23cd9b7` | 1310720 | U-Boot 1.1.3 (Jul 19 2021 - 20:00:53) | U_BOOT 00000013 | flash_write_menu,httpd_failsafe,mdio_cmds,nand,tftp_menu,uip_stack | P5/1210 |
| `148a756e5236c9b3` | 327680 | U-Boot 1.1.3 (Aug 21 2020 - 18:57:47) | U_BOOT 00000100 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | ORH/260 |
| `9f8705fa4efdfec5` | 327680 | U-Boot 1.1.3 (Aug 21 2020 - 18:57:47) | U_BOOT 00000100 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | ORH/260 |
| `26d9e69471a1c6e0` | 1310720 | U-Boot 1.1.3 (Aug 21 2020 - 18:57:47) | U_BOOT 00000100 | flash_write_menu,httpd_failsafe,mdio_cmds,nand,tftp_menu,uip_stack | P5/2210 |
| `a343e4fdc968ae5a` | 1310720 | U-Boot 1.1.3 (Apr 29 2021 - 20:19:53) | U_BOOT 00000013 | flash_write_menu,httpd_failsafe,mdio_cmds,nand,tftp_menu,uip_stack | P5/2210 |
| `f958dd4a79048cc0` | 327680 | U-Boot 1.1.3 (Jun 29 2016 - 02:00:11) | U_BOOT 00000007 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300/1121G |
| `e31a8c4e9aaade19` | 327680 | U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300A/1121G |
| `99bee8d22042b714` | 327680 | U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300A/2151G |
| `c77a17bfd39c32c0` | 327680 | U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300A/2151G |
| `f23e93ffb4629b9a` | 327680 | U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300PRO/1153G |
| `412fa6efd7124880` | 327680 | U-Boot 1.1.3 (Mar  8 2021 - 15:41:48) |  | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300S/1151G |
| `30d2f26d0a749531` | 327680 | U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300C/1121G |
| `5500b563ebd37ae1` | 327680 | U-Boot 1.1.3 (Mar  8 2021 - 15:41:48) |  | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300S/1151G |
| `5665fc52be3e238c` | 327680 | U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300/2121G |
| `31dd48f1d01ea5b0` | 327680 | U-Boot 1.1.3 (Feb 23 2021 - 11:13:19) |  | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | R300/2121G |
| `3f7db3d947831d5a` | 327680 | U-Boot 1.1.3 (Aug 19 2020 - 17:12:08) | U_BOOT 00000001 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X1/2111 |
| `638b990b9c9fc60f` | 327680 | U-Boot 1.1.3 (May 13 2019 - 15:14:52) | U_BOOT 00000001 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X1/1111 |
| `388b355d399d7511` | 327680 | U-Boot 1.1.3 (May 12 2022 - 17:34:39) | U_BOOT 00000010 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X1/3111 |
| `2191c021d892ca6c` | 327680 | U-Boot 1.1.3 (Feb  5 2021 - 18:44:28) | U_BOOT 00000007 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X3PRO/1153 |
| `f18657a24d84a35d` | 327680 | U-Boot 1.1.3 (May 29 2019 - 15:39:34) | U_BOOT 00000007 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X3/2151 |
| `e06e1d09ee6520c1` | 327680 | U-Boot 1.1.3 (Mar 15 2021 - 15:36:36) | U_BOOT 00000007 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X3/3251 |
| `7b2bf2eef8028cd7` | 327680 | U-Boot 1.1.3 (Aug 13 2015 - 15:32:11) | U_BOOT 00000003 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X3/D1509 |
| `51680dfca9ff595f` | 327680 | U-Boot 1.1.3 (Sep 19 2018 - 10:29:01) | U_BOOT 00000007 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X3/D1509A |
| `b1980bec6851f920` | 327680 | U-Boot 1.1.3 (May 20 2020 - 13:57:00) | U_BOOT 00000001 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X4C/1141G |
| `1b80ed954eec287c` | 327680 | U-Boot 1.1.3 (Jun 29 2016 - 02:00:11) | U_BOOT 00000007 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X4/1123G |
| `59339ec88a033225` | 327680 | U-Boot 1.1.3 (May 30 2019 - 16:54:16) | U_BOOT 00000009 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X5/1253 |
| `5826a24bb728bcf6` | 327680 | U-Boot 1.1.3 (May 12 2022 - 17:34:39) | U_BOOT 00000010 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X4C/3131G |
| `4fd43fb6eeecb48a` | 327680 | U-Boot 1.1.3 (Feb 17 2020 - 14:59:39) | U_BOOT 00000009 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X5/3353 |
| `875d6ee7167f95b7` | 1310720 | U-Boot 1.1.3 (Jan 12 2021 - 17:42:57) | U_BOOT 00000013 | flash_write_menu,httpd_failsafe,mdio_cmds,nand,tftp_menu,uip_stack | X5/4253 |
| `46e391eb23d4108f` | 327680 | U-Boot 1.1.3 (May 27 2019 - 16:36:06) | U_BOOT 00000009 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X5/2253 |
| `f049a7645da2c660` | 1310720 | U-Boot 1.1.3 (Dec 30 2020 - 12:38:16) | U_BOOT 00000013 | flash_write_menu,httpd_failsafe,mdio_cmds,nand,tftp_menu,uip_stack | X5/5255 |
| `6837dd9c9032435e` | 327680 | U-Boot 1.1.3 (May 27 2019 - 09:25:34) | U_BOOT 00000003 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X6/1293P |
| `7cfea23f23891a1d` | 327680 | U-Boot 1.1.3 (May 23 2019 - 19:04:48) | U_BOOT 00000003 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X6/2293P |
| `d8a42e9821b2ced3` | 1310720 | U-Boot 1.1.3 (Apr 23 2021 - 17:45:52) | U_BOOT 00000014 | flash_write_menu,httpd_failsafe,mdio_cmds,nand,tftp_menu,uip_stack | X6/3293P |
| `797f47fc097f7eca` | 327680 | U-Boot 1.1.3 (Aug 27 2020 - 14:04:05) | U_BOOT 00000100 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X3/3251 |
| `39fa92ced86d99d8` | 327680 | U-Boot 1.1.3 (Aug 27 2020 - 14:04:05) | U_BOOT 00000100 | flash_write_menu,httpd_failsafe,mdio_cmds,tftp_menu,uip_stack | X3/3251 |

## 内嵌引导镜像（NAND BL / u-boot 2018 FIT）

- X5/6256 6.0.0: `MT7621 NAND` @ 0x458 size=72920 load=0x80100000 kind=nand-bl fit=False banner=
- X5/6256 6.0.0: `U-Boot 2018.11 for mt7621_nand_r` @ 0x20458 size=209563 load=0x80200000 kind=bootloader fit=False banner=U-Boot 2018.11 (Aug 27 2022 - 07:48:00 +0000)
- X5/6256 6.3.0: `MT7621 NAND` @ 0x7d8 size=72920 load=0x80100000 kind=nand-bl fit=False banner=
- X5/6256 6.3.0: `U-Boot 2018.11 for mt7621_nand_r` @ 0x207d8 size=209464 load=0x80200000 kind=bootloader fit=False banner=U-Boot 2018.11 (Feb 15 2023 - 08:37:48 +0000)
- X3A/1233 6.3.0: `U-Boot 2018.11 for mt7621_rfb bo` @ 0x107d8 size=128359 load=0x80200000 kind=bootloader fit=False banner=U-Boot 2018.11 (Dec 28 2022 - 06:04:04 +0000)
- X3A/1233 6.3.1: `U-Boot 2018.11 for mt7621_rfb bo` @ 0x107d8 size=128359 load=0x80200000 kind=bootloader fit=False banner=U-Boot 2018.11 (Dec 28 2022 - 06:04:04 +0000)

## 不含引导区的固件（纯 sysupgrade，需从设备 SPI/NAND 读原厂 u-boot）

A20/1226, G100PRO/, G100PRO/1240, G100PRO/2240, G100PRO/3260, G300/42120, G300PRO/, R300A/3151G, R300A/4151G, R300S/2151GP, V1000/GK00600X, V2000/1260, X1/4111, X3A/1233, X5/7256, X5PRO/1258
