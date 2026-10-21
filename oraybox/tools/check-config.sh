#!/usr/bin/env bash
# 校验我们的 u-boot defconfig 里每个 CONFIG_ 符号在当前源码树里真实存在。
# 没交叉编译器时也能跑，避免把不存在的符号塞进 defconfig（make 只会警告 unknown symbol 然后静默丢弃）。
# 用法：check-config.sh <u-boot 源码目录> <defconfig...>
set -uo pipefail
SRC="${1:-}"; shift || true
[ -n "$SRC" ] && [ -d "$SRC" ] || { echo "用法: $0 <u-boot 源码目录> <defconfig...>"; exit 2; }
shift 0
targets=("$@")
if [ "${#targets[@]}" -eq 0 ]; then
  shopt -s nullglob
  here=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
  targets=("$here"/mt7628/oraybox-x4c/*_defconfig "$here"/mt7628/boards/*/*_defconfig)
  shopt -u nullglob
fi

# Kconfig 里声明的符号（config 名字后面跟换行/冒号）
klist=$(mktemp); trap 'rm -f "$klist"' EXIT
grep -rhoE '^\s*(menu)?config [A-Z0-9_]+[[:space:]]*$' "$SRC" --include=Kconfig\* --include=Kconfig 2>/dev/null \
  | awk '{print $2}' | sort -u > "$klist"
# 另外有些符号是 Makefile/defconfig 生成的（如 DEFAULT_DEVICE_TREE），也一并收录
grep -rhoE '^\s*config [A-Z0-9_]+' "$SRC/arch" "$SRC/board" 2>/dev/null | awk '{print $2}' | sort -u >> "$klist"
sort -u -o "$klist" "$klist"

rc=0
for f in "${targets[@]}"; do
  [ -f "$f" ] || { echo "!! 找不到 $f"; rc=1; continue; }
  name=$(basename "$f")
  miss=""
  while read -r sym; do
    grep -qx "$sym" "$klist" || miss="$miss $sym"
  done < <(grep -oE '^CONFIG_[A-Z0-9_]+' "$f" | sed 's/^CONFIG_//' | sort -u)
  n=$(grep -cE '^CONFIG_' "$f")
  if [ -n "$miss" ]; then
    printf 'FAIL %-46s %s 个符号里有未知项:%s\n' "$name" "$n" "$miss"; rc=1
  else
    printf 'PASS %-46s %s 个符号全部存在于 %s\n' "$name" "$n" "$(git -C "$SRC" describe --tags 2>/dev/null || echo "$SRC")"
  fi
done
exit $rc
