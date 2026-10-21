#!/usr/bin/env python3
"""按板输出"备份 → 编译 → 刷写 → 校验"的具体命令，数字全部取自该板自己的分区表与 env。

    python3 flash-plan.py X3A_1233            # MT7621（走 uboot-mt7621-dhcpd 那条线）
    python3 flash-plan.py X4C_3131G           # MT7628/MT7620（走 mainline）
    python3 flash-plan.py --list
"""
import csv
import glob
import os
import re
import sys

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_board(name):
    for row in csv.DictReader(open(os.path.join(DATA, "board-params.csv"))):
        if f"{row['model']}_{row['hwid']}".upper() == name.upper():
            return row
    return None


def dts_parts(dts):
    t = open(dts).read()
    return [
        {"label": lab, "offset": int(o, 16), "size": int(s, 16)}
        for lab, o, s in re.findall(r'label = "([^"]+)";\s*\n\s*reg = <0x([0-9a-f]+) 0x([0-9a-f]+)>', t)
    ]


def main():
    return plan(sys.argv[1])


def mainline_dir(name):
    return next(iter(glob.glob(os.path.join(ROOT, "mt76*/boards", name)) or []), None)


def plan(name):
    row = load_board(name)
    if not row:
        print(f"!! board-params.csv 里没有 {name}；--list 看可用板名")
        return 1
    md = mainline_dir(name)
    parts, env_off, env_size, dtb = [], "", "", ""
    if md:
        dts = glob.glob(os.path.join(md, "*.dts"))[0]
        cfg = glob.glob(os.path.join(md, "*_defconfig"))[0]
        parts = dts_parts(dts)
        c = open(cfg).read()
        env_off = (re.search(r"CONFIG_ENV_OFFSET=(\S+)", c) or ["", ""])[1]
        env_size = (re.search(r"CONFIG_ENV_SIZE=(\S+)", c) or ["", ""])[1]
        dtb = (re.search(r'CONFIG_DEFAULT_DEVICE_TREE="([^"]+)"', c) or ["", ""])[1]
        line = "mainline u-boot（mach-mtmips）：make O=build $DEFCONFIG && make O=build u-boot-with-spl.bin"
        artifact = "build/u-boot-with-spl.bin"
    else:
        board = f"oray_{name.lower()}"
        f = os.path.join(os.path.dirname(ROOT), "configs-mt7621", board + "_defconfig")
        line = f"MT7621 分支：BOARD={board} ./build.sh（板级文件 configs-mt7621/{board}_defconfig）"
        artifact = "archive/u-boot-mt7621_*.bin"
        mp = re.search(r"--mtdparts \"([^\"]+)\"", open(f).read()) if os.path.isfile(f) else None
        if mp:
            for cell in mp.group(1).split(","):
                prev = sum(p["size"] for p in parts)
                mm = re.match(r"(\d+)([kKmM])\(([^)]+)\)", cell)
                if mm:
                    n = int(mm.group(1)) * (1024 if mm.group(2).lower() == "k" else 1048576)
                    parts.append({"label": mm.group(3), "offset": prev, "size": n})
                    continue
                mt = re.match(r"-\(([^)]+)\)", cell)      # -(firmware) 这种"剩余全部"写法
                if mt:
                    parts.append({"label": mt.group(1), "offset": prev, "size": None})
    ub = next((p for p in parts if p["label"] == "u-boot"), {"offset": 0, "size": 0x30000, "label": "u-boot"})
    fac = next((p for p in parts if p["label"] == "factory"), None)
    nxt = next((p for p in parts if p["offset"] > ub["offset"]), None)
    print(f"# {row['model']}-{row['hwid']}  ({row['soc']}, {row['media']}, RAM {row['ram_mb'] or '?'}MB)")
    print("# 分区: " + "  ".join(
        f"{p['label']}@{hex(p['offset'])}" + (f"+{hex(p['size'])}" if p["size"] is not None else "+剩余全部")
        for p in parts))
    if dtb:
        print(f"# env: {env_off}+{env_size}   board dtb: {dtb}")
    print(f"# 原厂 u-boot: {row['boot_banner'] or '（该板固件未内嵌引导区）'}  版本戳 {row['boot_stamp'] or '-'}")
    print()
    print("1) 先备份，别省这一步")
    print(f"   # 串口 115200；原厂 failsafe：按住 reset 上电，tftp 主机 192.168.1.88，设备 192.168.1.119")
    print(f"   dd if=/dev/mtd0 of=uboot-{name}.bin bs=1 count={ub['size']}   # 或 CH341A 夹 SPI 整片读")
    if fac:
        print(f"   dd if=/dev/mtd0 of=factory-{name}.bin bs=1 skip={fac['offset']} count={fac['size']}   # MAC/无线校准，只备份不写")
    print()
    print("2) 编译")
    print(f"   {line}")
    print()
    print("3) 刷写（只写 u-boot 分区，范围 0x0 起）")
    print(f"   # 允许的最大镜像 {ub['size']} 字节（{ub['size'] // 1024}K）；"
          f"超出就别刷，会盖到后面的 {nxt['label'] if nxt else '未知分区'}")
    print(f"   # mtd write {artifact} u-boot      # 或 failsafe 页上传 / tftp 烧 0x0")
    print()
    print("4) 刷完第一次进 u-boot 要做的")
    if fac:
        print(f"   env set ethaddr <factory 偏移 0x{0x9:x} 起 6 字节>")
    print("   env set bootdelay 3 ; env save      # env 落在自己的槽里，别改偏移")
    print("   mtd list                            # 确认分区名与偏移跟上面一致")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "--list":
        names = sorted({f"{r['model']}_{r['hwid']}" for r in csv.DictReader(open(os.path.join(DATA, "board-params.csv")))} - {""})
        print("可用板名（model_hwid）：\n  " + "\n  ".join(n for n in names if n.strip("_")))
        sys.exit(0)
    sys.exit(main())
