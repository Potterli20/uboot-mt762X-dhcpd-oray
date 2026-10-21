#!/usr/bin/env bash
# X4C (MT7628AN) 自定义 u-boot 构建 + 刷写配方。
# 只做准备工作（取源码、放板级文件、配置），编译由你在有 mips 工具链的机器上跑。
set -euo pipefail

UBOOT_TAG="${UBOOT_TAG:-v2024.07}"
MIRROR="${UBOOT_MIRROR:-https://source.denx.de/u-boot/u-boot.git}"
MIRROR_FALLBACK="${UBOOT_MIRROR_FALLBACK:-https://github.com/u-boot/u-boot.git}"
WORK="${WORK:-/tmp/x4c-uboot}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

step() { printf '\n### %s\n' "$*"; }

if [ ! -d "$WORK/u-boot" ]; then
  step "取 u-boot $UBOOT_TAG（mainline 从 v2020.07 起有 mt7628 支持）"
  git clone --depth 1 --branch "$UBOOT_TAG" "$MIRROR" "$WORK/u-boot" \
    || git clone --depth 1 --branch "$UBOOT_TAG" "$MIRROR_FALLBACK" "$WORK/u-boot"
fi

step "先离线校验板级 DTS 能否编成 DTB（有 dtc 就做，省得编到一半才报错）"
if command -v dtc >/dev/null; then
  tmp=$(mktemp -d)
  cp -a "$WORK/u-boot/arch/mips/dts/." "$tmp/" 2>/dev/null || true
  cp -a "$WORK/u-boot/include/dt-bindings" "$tmp/include" 2>/dev/null || mkdir -p "$tmp/include"
  cp "$HERE/mt7628a-oraybox-x4c.dts" "$tmp/"
  ( cd "$tmp" && cpp -nostdinc -I. -Iinclude -D__DTS__ -x assembler-with-cpp \
      mt7628a-oraybox-x4c.dts -o pp.dts && dtc -I dts -O dtb -o out.dtb pp.dts ) \
    && echo "DTB 校验通过" || echo "!! DTS 校验失败，请检查 &label 引用是否存在于 mt7628a.dtsi"
  rm -rf "$tmp"
else
  echo "(没装 dtc，跳过 DTS 预校验)"
fi

cd "$WORK/u-boot"
step "放入 X4C 板级文件"
cp "$HERE/mt7628a-oraybox-x4c.dts" arch/mips/dts/
cp "$HERE/mt7628_oraybox_x4c_defconfig" configs/

step "配置并编译（需要 mips-mti 或 openwrt 的 mipsel 工具链）"
cat <<'EOF'
  make mt7628_oraybox_x4c_defconfig
  make -j$(nproc) u-boot-with-spl.bin
产物：u-boot-with-spl.bin（SPL+u-boot，约 <192KB，正好塞进 u-boot 分区）
EOF

step "刷写（原厂 1.1.3 有 failsafe httpd + tftp，不用拆机）"
cat <<'EOF'
1. 断电，按住 reset 上电，等约 5 秒进恢复模式；串口应打印 "Web failsafe mode"
2. 主机接线并设 192.168.1.88/24，浏览器开 http://192.168.1.119
   或 tftp: put u-boot-with-spl.bin（原厂 bootmenu 选项 2/3 可刷 bootloader）
3. 只写 0x000000-0x030000 这 192KB；0x40000 的 factory 是 MAC+无线校准，碰都别碰
4. 先备份原厂 192KB：恢复模式下把 mtd0 读出来存好，或 CH341A 夹 SPI 读一遍
EOF

step "刷机后第一次进 u-boot 要做的 env"
cat <<'EOF'
  env set ethaddr $(从 factory 偏移 0x09 读出的 MAC)   # 内核 DTB 里 mtd-mac-address = <&factory 0x9>
  env set bootdelay 3
  env save                                      # 落在 kpanic 区 0x30000，与原厂不冲突
EOF
