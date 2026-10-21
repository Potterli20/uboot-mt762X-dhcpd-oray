#!/usr/bin/env bash
# 免 root 拿一个能编 u-boot 的 mipsel 交叉工具链（OpenWrt SDK 里抠出来）。
# 三个坑：
#  1) 只解 toolchain 不够：gcc 是 wrapper，运行时要同 SDK 的 staging_dir/host/lib/ld-linux-x86-64.so.2
#     （它是按相对路径找的，所以不用进 PATH，但必须一起解出来）
#  2) 光设 CROSS_COMPILE 不行，要把 toolchain/bin 加进 PATH
#  3) 千万别把 SDK 的 host/bin 也加进 PATH：里面的 bison/flex 数据文件写死了 /builder/... 绝对路径，
#     u-boot 编 scripts/dtc 时会报 "m4sugar.m4: cannot open"（实测踩过）
# 用法：
#   bash get-toolchain.sh [输出目录]      # 默认 ./.toolchain
#   eval "$(bash get-toolchain.sh --env)" # 只打印环境变量
set -uo pipefail

REL="${OPENWRT_REL:-23.05.5}"
TARGET="${OPENWRT_TARGET:-ramips/mt76x8}"          # mt76x8 的 24kc 工具链同样能编 mt7620/mt7621 u-boot
GCC="${OPENWRT_GCC:-12.3.0}"
ARCH="${OPENWRT_ARCH:-x86_64}"
SDK="openwrt-sdk-${REL}-$(echo "$TARGET" | tr '/' '-')_gcc-${GCC}_musl.Linux-${ARCH}"
URL="https://downloads.openwrt.org/releases/${REL}/targets/${TARGET}/${SDK}.tar.xz"
DEST="${1:-$PWD/.toolchain}"

if [ "${1:-}" = "--env" ]; then
  TC="$DEST/${SDK}/staging_dir/toolchain-mipsel_24kc_gcc-${GCC}_musl"
  echo "export PATH=\"$TC/bin:\$PATH\"   # 注意：不要加 staging_dir/host/bin"
  echo "export STAGING_DIR=\"$TC\""
  echo "export CROSS_COMPILE=mipsel-openwrt-linux-"
  exit 0
fi

if [ ! -x "$DEST/$SDK/staging_dir/toolchain-mipsel_24kc_gcc-$GCC-musl/bin/mipsel-openwrt-linux-gcc" ] \
   && ! ls "$DEST/$SDK/staging_dir/toolchain-"*/bin/mipsel-openwrt-linux-gcc >/dev/null 2>&1; then
  echo "下载 ${SDK}.tar.xz（约 170MB）…"
  mkdir -p "$DEST"
  curl -fL --retry 3 -o "$DEST/sdk.tar.xz" "$URL" || { echo "!! 下载失败：$URL"; exit 1; }
  echo "解出 staging_dir/toolchain-* 与 staging_dir/host*（其余不需要）…"
  tar xJf "$DEST/sdk.tar.xz" -C "$DEST" --wildcards "*/staging_dir/toolchain-*" "*/staging_dir/host*"
  rm -f "$DEST/sdk.tar.xz"
fi

TC=$(ls -d "$DEST/$SDK/staging_dir/toolchain-"*/ | head -1)
echo "工具链：$TC"
"$TC/bin/mipsel-openwrt-linux-gcc" --version | head -1
cat <<EOF

接下来（在 u-boot 源码目录里）：
  export PATH="$TC/bin:\$PATH"        # 别加 host/bin，见文件头第 3 个坑
  export STAGING_DIR="$TC"
  make O=build CROSS_COMPILE=mipsel-openwrt-linux- mt7628_oraybox_x4c_defconfig
  make O=build CROSS_COMPILE=mipsel-openwrt-linux- -j\$(nproc) u-boot-with-spl.bin
EOF
