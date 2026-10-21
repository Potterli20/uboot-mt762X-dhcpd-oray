#!/usr/bin/env bash
# 离线校验 X4C 的板级 DTS 能否编成 DTB。
#   UBOOT_SRC=/path/to/u-boot  ./check-dts.sh      用本地 mainline 树
#   ./check-dts.sh                                 从 jsDelivr 取 3 个 mainline 文件
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DTS="mt7628a-oraybox-x4c"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/include/dt-bindings/clock" "$TMP/include/dt-bindings/reset"

need=(arch/mips/dts/mt7628a.dtsi include/dt-bindings/clock/mt7628-clk.h include/dt-bindings/reset/mt7628-reset.h)
if [ -n "${UBOOT_SRC:-}" ]; then
  cp "$UBOOT_SRC/arch/mips/dts/mt7628a.dtsi" "$TMP/"
  cp "$UBOOT_SRC/include/dt-bindings/clock/mt7628-clk.h" "$TMP/include/dt-bindings/clock/"
  cp "$UBOOT_SRC/include/dt-bindings/reset/mt7628-reset.h" "$TMP/include/dt-bindings/reset/"
else
  B="https://cdn.jsdelivr.net/gh/u-boot/u-boot@${UBOOT_REF:-master}"
  for f in "${need[@]}"; do
    ok=0
    for i in 1 2 3 4 5; do
      curl -sSfL --max-time 40 -o "$TMP/$f" "$B/$f" && { ok=1; break; }
      sleep 3
    done
    [ "$ok" = 1 ] || { echo "!! 取不到 $f（jsDelivr 抽风？可用 UBOOT_SRC 指向本地 mainline 树）"; exit 2; }
  done
fi
cp "$HERE/$DTS.dts" "$TMP/"
command -v dtc >/dev/null || { echo "!! 需要 device-tree-compiler"; exit 2; }

cpp -nostdinc -I"$TMP" -I"$TMP/include" -D__DTS__ -x assembler-with-cpp \
    "$TMP/$DTS.dts" -o "$TMP/pp.dts" || { echo "!! 预处理失败"; exit 1; }
if dtc -I dts -O dtb -o "$TMP/out.dtb" "$TMP/pp.dts" 2>"$TMP/dtc.log"; then
  echo "DTS 校验通过：$(wc -c <"$TMP/out.dtb") 字节 DTB"
  grep -E "^$(basename "$TMP")/$DTS.dts|error|Warning" "$TMP/dtc.log" | grep -v "also defined at" || true
  exit 0
fi
echo "!! DTS 编译失败："; cat "$TMP/dtc.log"; exit 1
