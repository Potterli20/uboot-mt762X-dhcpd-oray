#!/usr/bin/env bash
# 用 build.sh 的真实解析/校验逻辑跑一遍 configs-mt7621/oray_*，不编译。
# 用法：bash oraybox/tools/check-boards.sh [uboot 源码目录]
set -uo pipefail
SRC="${1:-$(pwd)}"
TMP=$(mktemp -d)
cp "$SRC/build.sh" "$TMP/"
cp -r "$SRC/configs-mt7621" "$TMP/"
cat > "$TMP/customize.sh" <<'STUB'
#!/usr/bin/env bash
echo "ARGS|flash=$1|koff=$3|mtd=$2|cpu=$6|ram=$7|ddr=$8"
STUB
chmod +x "$TMP/customize.sh"
cd "$TMP"
bad=0
for f in configs-mt7621/oray_*_defconfig; do
  b=$(basename "$f" _defconfig)
  out=$(BOARD="$b" bash ./build.sh 2>&1 | grep -E "^ARGS\||^Error|Entering interactive")
  if [[ "$out" == ARGS* ]]; then
    printf 'PASS %-22s %s\n' "$b" "$(echo "$out" | sed 's/ARGS|//')"
    grep -q TODO "$f" && echo "     ↑ $f 仍有 TODO（批量 workflow 会跳过）"
  else
    printf 'FAIL %-22s %s\n' "$b" "${out:0:110}"; bad=1
  fi
done
rm -rf "$TMP"
exit $bad
