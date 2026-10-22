# OrayBox (蒲公英) board data for custom U-Boot

板级参数、解包工具与 MT7628 移植配方，全部逆向自 [web1n/oraybox-firmwares](https://github.com/web1n/oraybox-firmwares) 的官方固件。
Board-level data, unpacking tools and an MT7628 port recipe, all derived from the official OrayBox firmware collection.

## 覆盖情况 / coverage

52 个型号/硬件组合（127 个固件），按 SoC 分流：

| SoC | 型号数 | 现状 |
|---|---|---|
| MT7621 | 19 | `configs-mt7621/` 已出 19 份 defconfig，可直接喂 [uboot-mt7621-dhcpd](https://github.com/Yuzhii0718/uboot-mt7621-dhcpd) |
| MT7628 | 14 | 与 MT7621 仓库无关，需 mainline `mach-mtmips`；14 块板的 board dts + defconfig 见 `oraybox/mt7628/boards/`，X4C 手工版在 `oraybox/mt7628/oraybox-x4c/` |
| MT7620 | 10 | `oraybox/mt7620/boards/` 已出 10 份 board dts + defconfig（base 在 `oraybox/mt7620/oraybox-r300a/`） |
| x86_64 | 7 | G100Pro / V1000 / V2000 等软路由，不涉及 u-boot |
| ARM64 | 2 | G300-42120 = RK3568、X5PRO-1258 = ARM64 OrayOS FIT，均与 MTK u-boot 无关 |

A20-1226 与 X5-7256 是新解析出来的 MT7621（前者靠 FIT 内 DTB、后者靠 tar 子镜像的 UBI 分区表）；
这两块板的 `--ddrparam` 还缺实测（DTB 里没有 memory 节点、板名也没 `-Sxxx/-Nxxx` 后缀），
批量 workflow 会自动跳过含 TODO 的板子并在 summary 里列出。

改板级文件会触发 `check-boards.yml`（跑上面两个校验，不编译），批量出包用 `build-oraybox-all.yml`。

## 目录 / layout

```
configs-mt7621/                 build.sh 参数文件（上游板子旁边并排放 oray_*_defconfig）
oraybox/mt7628/oraybox-x4c/     X4C 的 board DTS + defconfig + 构建/刷写配方
oraybox/tools/orayfw.py         固件解包与索引（list / unpack / summary / dts / boards）
oraybox/tools/dramid.py         用 dramc-legacy 表匹配原厂 u-boot，反推 DDR 参数
oraybox/tools/serial_probe.py   抓串口开机横幅，补 cpufreq / ramfreq / ddrparam
oraybox/data/                   board-params.csv、SUMMARY.md、index.csv、ddr-probe.json、dts/
oraybox/tools/check-boards.sh      stub 掉 customize.sh 后跑真实 build.sh 解析+validate（不编译）
oraybox/mt7628/oraybox-x4c/check-dts.sh  cpp+dtc 把 X4C 的 dts 编成 DTB，验证 &label 引用
```

仓库根就是 MTK U-Boot v2018.09（fork 自 [Yuzhii0718/uboot-mt7621-dhcpd](https://github.com/Yuzhii0718/uboot-mt7621-dhcpd)
/ [DragonBluep/uboot-mt7621](https://github.com/DragonBluep/uboot-mt7621)），许可证见 `Licenses/gpl-2.0.txt`。

## MT7628 / MT7620 用法

全部 25 份板级配置都用 OpenWrt 工具链真编过一遍，尺寸见 `data/mainline-sizes.txt`
（MT7628 约 163.8K、MT7620 约 165.7K，上限 196,608）。
MT7620 的 rfb 默认配置直接编出来 **218,082 字节，装不进蒲公英 192K 的 u-boot 分区**；
关掉板子上没有/用不到的东西（MMC、USB、DOS/文件系统、FIT）后是 **165,715 字节**，进得去。
MT7628 那边本来就 ~163.8K，同一批瘦身项是空操作，只当留余量。
CI 的 `build-mainline.yml` 里有体积守卫：产物超出该板 dts 里 u-boot 分区大小就直接 fail。

本地免 root 复现编译（OpenWrt SDK 里抠工具链，三个坑写在脚本头注释里）：

```bash
bash oraybox/tools/get-toolchain.sh .toolchain        # 约 170MB 下载
eval "$(bash oraybox/tools/get-toolchain.sh .toolchain --env)"
make O=build $CROSS_COMPILE_PREFIX mt7628_oraybox_x4c_3131g_defconfig
make O=build CROSS_COMPILE=mipsel-openwrt-linux- -j$(nproc) u-boot-with-spl.bin
bash oraybox/tools/size-report.sh <u-boot 树>          # 全板体积对照表
```

`oraybox/tools/gen-7628-dts.py` 从解包出的内核 DTB 派生 mainline 的 board dts（分区表、复位键/LED、
MAC 来源、console），没有 DTB 的老固件板按同 SoC/同型号前缀找供体，文件头写明来源与"未实测"。
派生完用 `check-dts.sh` 编译校验（依赖 mainline 的 dtsi 与 dt-bindings，可走镜像或 `UBOOT_SRC`）：

```bash
python3 oraybox/tools/gen-mtmips-dts.py            # MT7628 + MT7620 一起
bash oraybox/tools/check-dts.sh                    # 默认扫两条线全部板子
```

当前 15 份 dts 全部能编成 DTB，15 份 defconfig 的 CONFIG 符号也全部在 v2024.07 里存在
（`bash oraybox/tools/check-config.sh <u-boot 源码> ...`，没交叉编译器也能跑）。
两个版本都扫过：v2026.07 与 v2024.07 的唯一差别就是 `ENV_RELOC_GD_ENV_ADDR`。。
这些文件只保证"语法与 label 正确 + 分区表来自固件"，刷之前仍需实测。

X4C 的 defconfig 已含：env 在 0x30000（kpanic 区）、`sf probe; sf read 0x83000000 0x50000 0x400000; bootm`、
bootmenu/TFTP/DHCP/ping 恢复命令、LZMA。刻意没写死 `CONFIG_MTDPARTS_DEFAULT`——dm-spi 下的 mtd id
要第一次开机 `mtd list` 才知道。

出包（MT7621 之外的 14 块板走这条）：

```bash
# Actions → "Build OrayBox MT7628 boards"，默认 uboot_ref=v2026.07
# （ENV_RELOC_GD_ENV_ADDR 是 v2026.01 引入的；要退回 v2024.07 就删掉那一行，别的符号两版都认）
# 本地等价命令：
git clone --depth 1 -b v2026.07 https://source.denx.de/u-boot/u-boot.git
cp oraybox/mt7628/boards/X4C_3131G/* u-boot/arch/mips/dts/ # dts
cp oraybox/mt7628/boards/X4C_3131G/*_defconfig u-boot/configs/
make O=build mt7628_oraybox_x4c_3131g_defconfig
make O=build CROSS_COMPILE=mipsel-linux-gnu- -j$(nproc)   # 产物 build/u-boot-with-spl.bin
```

上机前的已知风险：mainline 没有原厂 1.1.3 的 failsafe httpd，恢复只能靠 bootmenu+TFTP；
3.10 老内核那批还要 cmdline 里的 `board=WT6271`，直接 `bootm` 原厂内核不一定起得来，
先拿 RAM/串口确认再刷，且务必先备份 0x0–0x50000。

## MT7621 用法

```bash
./build.sh --flash NOR --mtdparts "192k(u-boot),64k(u-boot-env),64k(factory),-(firmware)" \
  --model "OrayBox_X3A-1233" --kernel-offset 0x50000 --reset-pin 13 --sysled-pin 5 \
  --cpufreq 880 --ramfreq 1200 --ddrparam DDR3-128MiB --baudrate 115200
# 或者直接复用板级文件（把 TODO 换掉）
BOARD=oray_x3a_1233 ./build.sh
```

`--cpufreq` / `--ddrparam` 固件里取不到（原厂 u-boot 运行时自动探测，factory 镜像里的 uenv 是空的），
需要跑一次 `oraybox/tools/serial_probe.py` 抓横幅补齐；缺值时 build.sh 会直接报 Invalid CPU Frequency。

## 已知实机待验证项

- GPIO 编号：从 DTB 读的是 (bank, pin)，落到 `--reset-pin/--sysled-pin` 按 a=0-15 / b=16-31 / c=32-47 折算，需串口实测
- X4C 控制台：mainline `mt7628a.dtsi` 只建模 uart0，原厂 Linux cmdline 写的是 `ttyS1`
- 原厂 1.1.3 二进制里只嵌了 `DDR2_512M` 那张 SDK 基线表（运行时按实际颗粒改写），不能当 `--ddrparam` 直接照搬

## 安全提醒

刷 bootloader 前先备份原厂 0x0 起的前 192KB/256KB；
原厂 u-boot 带 failsafe httpd + TFTP（按住 reset 上电，`192.168.1.119`，默认 `ipaddr/serverip` 见 `data/board-params.csv`），可救砖。
`oraybox/tools/flash-plan.py <板名>` 会按该板自己的分区表打印备份/编译/刷写/校验命令，NAND 用 `nanddump` 而不是 `dd skip`。

## MAC 到底在哪块分区（影响 ethaddr）

解包出来的内核 dts 里，`mtd-mac-address` 基本都指向 **`bdinfo` 偏移 0x9**（SPI-NOR 上是 `0xfe0000`，
NAND 上是 `0x21c0000`，A20 是 `0x20000`——所以不能硬编一个偏移到处用）；只有 X5-6256 5.5.0 例外，写的是
`factory + 0xe006`。`factory` 主要是无线校准，往它里面找 LAN MAC 会取到无效地址。

```bash
python3 oraybox/tools/flash-plan.py --check    # CI 里也跑：MAC 证据必须落在本板 dts 的分区表内
```

为什么不在 dts 里用内核那套 `nvmem-cells = <&macaddr_bdinfo_9>`：u-boot v2026.07 的 nvmem 是
`drivers/misc/nvmem.c` 这个 meta-uclass，只接 I2C_EEPROM / MISC / RTC 三种后端，**没有 MTD/SPI-NOR 实现**，
所以 `nvmem_cell_get_by_name(dev,"mac-address")` 在这类板子上取不到值。u-boot 侧剩下的路子是
`mac-address`/`local-mac-address` 字面量（共享镜像不能用）或者刷完第一次手动 `env set ethaddr`，
否则 `CONFIG_NET_RANDOM_ETHADDR` 每次开机换一个 MAC，而蒲公英是按 MAC 认设备身份的。

## 一个原厂笔误

`X3A_1233_5.5.1` 的内核 DTB 里那个分区节点名是 `artition@fe0000`（少了个 p）。fixed-partitions 只认
`label`/`reg`，所以原厂 Linux 不受影响，但按 `partition@<hex>` 名字匹配的提取器会整块漏掉 bdinfo。
`gen-mtmips-dts.py` 现在走缩进栈解析（`tools/dtsread.py`），不再依赖节点名和制表符层数——
之前 NAND 板（A500/P5/X5-6256/7256）的分区表就是因为 4 层缩进写死而读成空表，只能靠"继承"别的板。


## 复现

```bash
git clone --depth 1 https://github.com/web1n/oraybox-firmwares.git upstream
python3 oraybox/tools/orayfw.py list          # 需在仓库根之外建工作目录，orayfw.py 假设 upstream/ 与 data/ 同级
python3 oraybox/tools/orayfw.py unpack --jobs 3
python3 oraybox/tools/orayfw.py summary && python3 oraybox/tools/orayfw.py boards
python3 oraybox/tools/dramid.py ref-uboot oraybox/data/models --json oraybox/data/ddr-probe.json
```
