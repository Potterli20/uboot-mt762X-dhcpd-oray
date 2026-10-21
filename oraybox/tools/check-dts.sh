#!/usr/bin/env bash
# 离线校验 OrayBox 的 mainline board dts 能否编成 DTB（纯 cpp+dtc，不需要交叉编译器）。
#
#   check-dts.sh                          # 扫 mt7628/mt7620 两条线全部板子
#   check-dts.sh path/to/xx.dts ...       # 只校验指定文件
#   UBOOT_SRC=/path/to/u-boot check-dts.sh  # 用本地 mainline 树的 dtsi/dt-bindings
#   UBOOT_REF=v2026.07 check-dts.sh         # 从镜像拉依赖（默认 v2026.07）
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"          # oraybox/

if [ "$#" -gt 0 ]; then
  targets=("$@")
else
  shopt -s nullglob
  targets=("$ROOT"/mt7628/oraybox-x4c/*.dts "$ROOT"/mt7628/boards/*/*.dts "$ROOT"/mt7620/boards/*/*.dts)
  shopt -u nullglob
fi
[ "${#targets[@]}" -gt 0 ] || { echo "!! 没找到任何 .dts"; exit 2; }
command -v dtc >/dev/null || { echo "!! 需要 device-tree-compiler"; exit 2; }

soc_of() { case "$1" in *mt7620*) echo mt7620 ;; *) echo mt7628 ;; esac; }
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/include/dt-bindings/clock" "$TMP/include/dt-bindings/reset"

get_dep() {   # $1 = 源码树内的相对路径
  local f="$1" dest
  case "$f" in
    arch/mips/dts/*) dest="$TMP/${f##*/}" ;;      # dtsi 平铺：#include "mt7628a.dtsi" 按当前目录解析
    *)               dest="$TMP/$f"; mkdir -p "$(dirname "$dest")" ;;
  esac
  [ -f "$dest" ] && return 0
  if [ -n "${UBOOT_SRC:-}" ]; then
    cp "$UBOOT_SRC/$f" "$dest" && return 0
    echo "!! 本地树缺 $f"; return 1
  fi
  local B="https://cdn.jsdelivr.net/gh/u-boot/u-boot@${UBOOT_REF:-v2026.07}"
  for i in 1 2 3 4 5; do
    curl -sSfL --max-time 40 -o "$dest" "$B/$f" && return 0
    sleep 3
  done
  echo "!! 取不到 $f（可用 UBOOT_SRC 指向本地 mainline 树）"; return 1
}

rc=0
for soc in $(for t in "${targets[@]}"; do soc_of "$(basename "$t")"; done | sort -u); do
  for f in "arch/mips/dts/${soc}a.dtsi" "arch/mips/dts/${soc}.dtsi" \
           "include/dt-bindings/clock/${soc}-clk.h" "include/dt-bindings/reset/${soc}-reset.h"; do
    # mt7620 的 dtsi 叫 mt7620.dtsi、mt7628 的叫 mt7628a.dtsi，两个名字都试，取存在的那个
    if [ -n "${UBOOT_SRC:-}" ]; then
      [ -f "$UBOOT_SRC/$f" ] || continue
    else
      case "$f" in
        "arch/mips/dts/${soc}a.dtsi") ;;
        "arch/mips/dts/${soc}.dtsi") [ -f "$TMP/${soc}a.dtsi" ] && continue ;;
      esac
    fi
    get_dep "$f" || rc=1
  done
done

for dts in "${targets[@]}"; do
  [ -f "$dts" ] || { echo "!! 找不到 $dts"; rc=1; continue; }
  n=$(basename "$dts" .dts)
  cp "$dts" "$TMP/$n.dts"
  if cpp -nostdinc -I"$TMP" -I"$TMP/include" -D__DTS__ -x assembler-with-cpp "$TMP/$n.dts" -o "$TMP/$n.pp" 2>"$TMP/$n.cpp.log" \
     && dtc -I dts -O dtb -o "$TMP/$n.dtb" "$TMP/$n.pp" 2>"$TMP/$n.dtc.log"; then
    printf 'PASS %-42s %s 字节 DTB\n' "$n" "$(wc -c <"$TMP/$n.dtb")"
  else
    printf 'FAIL %-42s\n' "$n"; sed 's/^/     /' "$TMP/$n.cpp.log" "$TMP/$n.dtc.log" | head -8; rc=1
  fi
done
exit $rc
