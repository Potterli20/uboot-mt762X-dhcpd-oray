# OrayBox (蒲公英) board data for custom U-Boot

板级参数、解包工具与 MT7628 移植配方，全部逆向自 [web1n/oraybox-firmwares](https://github.com/web1n/oraybox-firmwares) 的官方固件。
Board-level data, unpacking tools and an MT7628 port recipe, all derived from the official OrayBox firmware collection.

## 覆盖情况 / coverage

52 个型号/硬件组合（127 个固件），按 SoC 分流：

| SoC | 型号数 | 现状 |
|---|---|---|
| MT7621 | 19 | `configs-mt7621/` 已出 19 份 defconfig，可直接喂 [uboot-mt7621-dhcpd](https://github.com/Yuzhii0718/uboot-mt7621-dhcpd) |
| MT7628 | 14 | 与 MT7621 仓库无关，需 mainline `mach-mtmips`；X4C 配方见 `oraybox/mt7628/` |
| MT7620 | 10 | 待做（mainline v2023.01 起有 mt7620 支持） |
| x86_64 | 7 | G100Pro / V1000 / V2000 等软路由，不涉及 u-boot |
| ARM64 | 2 | G300-42120 = RK3568、X5PRO-1258 = ARM64 OrayOS FIT，均与 MTK u-boot 无关 |

A20-1226 与 X5-7256 是新解析出来的 MT7621（前者靠 FIT 内 DTB、后者靠 tar 子镜像的 UBI 分区表）；
这两块板的 `--ddrparam` 还缺实测（DTB 里没有 memory 节点、板名也没 `-Sxxx/-Nxxx` 后缀），
批量 workflow 会自动跳过含 TODO 的板子并在 summary 里列出。

## 目录 / layout

```
configs-mt7621/                 build.sh 参数文件（上游板子旁边并排放 oray_*_defconfig）
oraybox/mt7628/oraybox-x4c/     X4C 的 board DTS + defconfig + 构建/刷写配方
oraybox/tools/orayfw.py         固件解包与索引（list / unpack / summary / dts / boards）
oraybox/tools/dramid.py         用 dramc-legacy 表匹配原厂 u-boot，反推 DDR 参数
oraybox/tools/serial_probe.py   抓串口开机横幅，补 cpufreq / ramfreq / ddrparam
oraybox/data/                   board-params.csv、SUMMARY.md、index.csv、ddr-probe.json、dts/
```

仓库根就是 MTK U-Boot v2018.09（fork 自 [Yuzhii0718/uboot-mt7621-dhcpd](https://github.com/Yuzhii0718/uboot-mt7621-dhcpd)
/ [DragonBluep/uboot-mt7621](https://github.com/DragonBluep/uboot-mt7621)），许可证见 `Licenses/gpl-2.0.txt`。

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

`factory` 分区（MAC + 无线校准）永远不要写。刷 bootloader 前先备份原厂 0x0 起的前 192KB/256KB；
原厂 u-boot 带 failsafe httpd + TFTP（按住 reset 上电，`192.168.1.119`，默认 `ipaddr/serverip` 见 `data/board-params.csv`），可救砖。

## 复现

```bash
git clone --depth 1 https://github.com/web1n/oraybox-firmwares.git upstream
python3 oraybox/tools/orayfw.py list          # 需在仓库根之外建工作目录，orayfw.py 假设 upstream/ 与 data/ 同级
python3 oraybox/tools/orayfw.py unpack --jobs 3
python3 oraybox/tools/orayfw.py summary && python3 oraybox/tools/orayfw.py boards
python3 oraybox/tools/dramid.py ref-uboot oraybox/data/models --json oraybox/data/ddr-probe.json
```
