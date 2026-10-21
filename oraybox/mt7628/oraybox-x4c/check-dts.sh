#!/usr/bin/env bash
# 离线校验 X4C 的板级 DTS 能否编成 DTB。
#   UBOOT_SRC=/path/to/u-boot  ./check-dts.sh      用本地 mainline 树
#   ./check-dts.sh                                 从 jsDelivr 取 3 个 mainline 文件
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 参数：要校验的 .dts（可传多个）；默认校验本目录 + boards/ 下全部
if [ "$#" -gt 0 ]; then targets=("$@"); else
  targets=("$HERE/mt7628a-oraybox-x4c.dts")
  shopt -s nullglob; targets+=("$HERE"/../boards/*/*.dts); shopt -u nullglob
fi
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
    # dtsi 平铺到 $TMP（#include "mt7628a.dtsi" 是相对当前文件解析的），头文件保持 include/ 层级
    case "$f" in
      arch/mips/dts/*) dest="$TMP/${f##*/}" ;;
      *)               dest="$TMP/$f"; mkdir -p "$(dirname "$dest")" ;;
    esac
    ok=0
    for i in 1 2 3 4 5; do
      curl -sSfL --max-time 40 -o "$dest" "$B/$f" && { ok=1; break; }
      sleep 3
    done
    [ "$ok" = 1 ] || { echo "!! 取不到 $f（jsDelivr 抽风？可用 UBOOT_SRC 指向本地 mainline 树）"; exit 2; }
  done
fi
command -v dtc >/dev/null || { echo "!! 需要 device-tree-compiler"; exit 2; }
rc=0
for dts in "${targets[@]}"; do
  [ -f "$dts" ] || { echo "!! 找不到 $dts"; rc=1; continue; }
  DTS=$(basename "$dts" .dts)
  cp "$dts" "$TMP/$DTS.dts"
  if cpp -nostdinc -I"$TMP" -I"$TMP/include" -D__DTS__ -x assembler-with-cpp \
       "$TMP/$DTS.dts" -o "$TMP/$DTS.pp.dts" 2>"$TMP/cpp.log" \
     && dtc -I dts -O dtb -o "$TMP/$DTS.dtb" "$TMP/$DTS.pp.dts" 2>"$TMP/dtc.log"; then
    printf 'PASS %-40s %s 字节 DTB\n' "$DTS" "$(wc -c <"$TMP/$DTS.dtb")"
  else
    printf 'FAIL %-40s\n' "$DTS"; head -6 "$TMP/cpp.log" "$TMP/dtc.log" | sed 's/^/     /'; rc=1
  fi
done
exit $rc
