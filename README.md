# OrayBox (蒲公英) board data for custom U-Boot

板级参数、解包工具与 MT7628 移植配方，全部逆向自 [web1n/oraybox-firmwares](https://github.com/web1n/oraybox-firmwares) 的官方固件。
Board-level data, unpacking tools and an MT7628 port recipe, all derived from the official OrayBox firmware collection.

## 覆盖情况 / coverage

52 个型号/硬件组合（127 个固件），按 SoC 分流：

| SoC | 型号数 | 现状 |
|---|---|---|
| MT7621 | 17 | `configs-mt7621/` 已出 17 份 defconfig，可直接喂 [uboot-mt7621-dhcpd](https://github.com/Yuzhii0718/uboot-mt7621-dhcpd) |
| MT7628 | 14 | 与 MT7621 仓库无关，需 mainline `mach-mtmips`；X4C 配方见 `uboot-mt7628/` |
| MT7620 | 10 | 待做（mainline v2023.01 起有 mt7620 支持） |
| x86_64 | 7 | G100Pro / V1000 / V2000 等软路由，不涉及 u-boot |
| 未定 | 4 | A20 / G300 / X5-7256 / X5PRO，rootfs 非 squashfs，待补 |

## 目录 / layout

```
configs-mt7621/            build.sh 参数文件，命名 oray_<型号>_<硬件id>_defconfig
uboot-mt7628/oraybox-x4c/  X4C 的 board DTS + defconfig + 构建/刷写配方
tools/orayfw.py            固件解包与索引（list / unpack / summary / dts / boards）
tools/dramid.py            用参考仓库 dramc 表匹配原厂 u-boot，反推 DDR 参数
tools/serial_probe.py      抓串口开机横幅，补 cpufreq / ramfreq / ddrparam
data/                      board-params.csv、SUMMARY.md、index.csv、ddr-probe.json、dts/
```

## MT7621 用法

```bash
git clone https://github.com/Yuzhii0718/uboot-mt7621-dhcpd
cp configs-mt7621/oray_x3a_1233_defconfig uboot-mt7621-dhcpd/configs-mt7621/
cd uboot-mt7621-dhcpd && BOARD=oray_x3a_1233 ./build.sh
```

`--cpufreq` / `--ddrparam` 固件里取不到（原厂 u-boot 运行时自动探测，factory 镜像里的 uenv 是空的），
需要跑一次 `tools/serial_probe.py` 抓横幅补齐；缺值时 build.sh 会直接报 Invalid CPU Frequency。

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
python3 tools/orayfw.py list
python3 tools/orayfw.py unpack --jobs 3
python3 tools/orayfw.py boards
```
