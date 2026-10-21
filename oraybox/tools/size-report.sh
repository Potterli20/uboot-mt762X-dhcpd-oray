#!/usr/bin/env bash
# 全量交叉编译 oraybox 的 mainline 板子（MT7628 + MT7620），产出一张体积对照表。
# 前提：已用 oraybox/tools/get-toolchain.sh 拿到 OpenWrt 交叉工具链，且有 u-boot 源码树。
set -uo pipefail
SRC="${1:?用法: $0 <u-boot 源码树> [输出文件]}"
OUT="${2:-sdk/all-sizes.txt}"
TC="$(cd "${3:-$PWD/sdk}/staging_dir" 2>/dev/null && echo $PWD/toolchain-*/ | head -1)"
if [ -z "$TC" ]; then
  TC=$(ls -d "$PWD"/sdk/*/staging_dir/toolchain-*/ | head -1)
fi
export PATH="$TC/bin:$PATH"
mkdir -p "$(dirname "$OUT")"
: >"$OUT"
for d in repo/oraybox/mt7628/oraybox-x4c repo/oraybox/mt7628/boards/*/ repo/oraybox/mt7620/boards/*/; do
  b=$(basename "$d")
  dc=$(basename "$(ls "$d"*_defconfig | head -1)" .defconfig)
  cp "$d"*.dts "$SRC/arch/mips/dts/" 2>/dev/null
  cp "$d"*_defconfig "$SRC/configs/" 2>/dev/null
  if (cd "$SRC" && make O="sz-$b" CROSS_COMPILE=mipsel-openwrt-linux- STAGING_DIR="$TC" "$dc" >/dev/null 2>&1 \
      && make O="sz-$b" CROSS_COMPILE=mipsel-openwrt-linux- STAGING_DIR="$TC" -j"$(nproc)" u-boot-with-spl.bin >/dev/null 2>&1); then
    n=$(stat -c%s "$SRC/sz-$b/u-boot-with-spl.bin")
    lim=$(grep -A2 'label = "u-boot";' "$d"*.dts | grep -oE 'reg = <0x[0-9a-f]+ 0x[0-9a-f]+' | grep -oE '0x[0-9a-f]+$' | head -1)
    verdict=$([ "$n" -le "$((lim))" ] && echo "OK" || echo "超出")
    printf '%-18s %8d / %6d 字节  %s  %s\n' "$b" "$n" "$((lim))" "$verdict" "$dc" >>"$OUT"
  else
    printf '%-18s 编译失败  %s\n' "$b" "$dc" >>"$OUT"
  fi
done
sort -k3 -n "$OUT" -o "$OUT"
echo "共 $(wc -l <"$OUT") 块板，超出分区 $(grep -c 超出 "$OUT" || true) 块，失败 $(grep -c 失败 "$OUT" || true) 块"
echo "-> $OUT"
