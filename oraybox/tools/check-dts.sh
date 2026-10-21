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

fetch_one() {   # $1=仓库相对路径 $2=落地路径；成功 0
  local f="$1" dest="$2" code
  [ -f "$dest" ] && return 0
  mkdir -p "$(dirname "$dest")"
  if [ -n "${UBOOT_SRC:-}" ]; then
    [ -f "$UBOOT_SRC/$f" ] && cp "$UBOOT_SRC/$f" "$dest" && return 0
    return 1
  fi
  local B="https://cdn.jsdelivr.net/gh/u-boot/u-boot@${UBOOT_REF:-v2026.07}"
  for i in 1 2 3 4 5; do
    code=$(curl -sS -o "$dest" -w "%{http_code}" --max-time 40 "$B/$f" 2>/dev/null || echo 000)
    [ "$code" = 200 ] && return 0
    # 404 说明这个候选名不存在，直接换下一个，别浪费重试
    [ "$code" = 404 ] && { rm -f "$dest"; return 1; }
    sleep 3
  done
  rm -f "$dest"; return 1
}

get_soc_deps() {   # $1=soc
  local soc="$1" ok=0 f
  # dtsi 名字两版不一样：mt7628 → mt7628a.dtsi，mt7620 → mt7620.dtsi，两个候选都试
  for f in "arch/mips/dts/${soc}a.dtsi" "arch/mips/dts/${soc}.dtsi"; do
    fetch_one "$f" "$TMP/${f##*/}" && ok=1
  done
  [ "$ok" = 1 ] || { echo "!! 找不到 ${soc} 的 dtsi（镜像和本地树都没有）"; return 1; }
  for f in "include/dt-bindings/clock/${soc}-clk.h" "include/dt-bindings/reset/${soc}-reset.h"; do
    fetch_one "$f" "$TMP/$f" || { echo "!! 缺 $f"; return 1; }
  done
  return 0
}

rc=0
for soc in $(for t in "${targets[@]}"; do soc_of "$(basename "$t")"; done | sort -u); do
  get_soc_deps "$soc" || rc=1
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
