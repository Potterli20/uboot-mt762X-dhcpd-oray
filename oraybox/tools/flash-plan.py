#!/usr/bin/env python3
"""按板输出"备份 → 编译 → 刷写 → 校验"的具体命令，数字全部取自该板自己的分区表与 env。

    python3 flash-plan.py X3A_1233            # MT7621（走 uboot-mt7621-dhcpd 那条线）
    python3 flash-plan.py X4C_3131G           # MT7628/MT7620（走 mainline）
    python3 flash-plan.py --list

分区表优先取 board-params.csv 的 mtdparts（那本来就是从固件里解出来的，带 mtdparts_src 溯源），
defconfig 只作交叉校验；两边对不上就报错，不猜。
"""
import csv
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dtsread

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)


SUPPORTED = ("MT7621", "MT7628", "MT7620")


def load_board(name):
    for row in csv.DictReader(open(os.path.join(DATA, "board-params.csv"))):
        if f"{row['model']}_{row['hwid']}".upper() == name.upper():
            return row
    return None


def parse_cells(spec):
    """'192k(u-boot),64k(u-boot-env),64k(factory),-(firmware)' -> [{label,offset,size}]，size=None 表示剩余全部"""
    out = []
    for cell in spec.split(","):
        cell = cell.strip()
        prev = sum(p["size"] for p in out if p["size"] is not None)
        mm = re.match(r"^(\d+)([kKmM])\(([^)]+)\)$", cell)
        if mm:
            n = int(mm.group(1)) * (1024 if mm.group(2).lower() == "k" else 1048576)
            out.append({"label": mm.group(3), "offset": prev, "size": n})
            continue
        mt = re.match(r"^-\(([^)]+)\)$", cell)
        if mt:
            out.append({"label": mt.group(1), "offset": prev, "size": None})
    return out


def up_to_fw(labels):
    """csv 的 mtdparts 按原厂约定在 -(firmware) 处收尾，dts 会把 firmware 之后的 bdinfo/reserve 也列出来：
    两边只能比到 firmware 为止，多出来的尾部不算冲突。"""
    return labels[: labels.index("firmware") + 1] if "firmware" in labels else labels


def donor_dts(row):
    """该板解包出来的内核 dts；同型号多版本时优先用 row['firmware'] 里那个版本号"""
    cands = sorted(glob.glob(os.path.join(DATA, "dts", f"{row['model']}_{row['hwid']}_*.dts")))
    if not cands:
        cands = sorted(glob.glob(os.path.join(DATA, "dts", f"{row['model']}_*.dts")))
    ver = (re.search(r"_(\d+\.\d+\.\d+)", row["firmware"] or "") or ["", ""])[1]
    if ver:
        hit = [c for c in cands if f"_{ver}.dts" in c]
        if hit:
            return hit
    return cands


def mac_evidence(row):
    """内核 dts 里 mtd-mac-address 指向的分区+偏移。这是 ethaddr 该从哪儿取的唯一依据。"""
    res = set()
    exact = sorted(glob.glob(os.path.join(DATA, "dts", f"{row['model']}_{row['hwid']}_*.dts")))
    for f in donor_dts(row):
        hits, _ = dtsread.mac_cells(open(f).read())
        for props, off in hits:
            src = os.path.basename(f) + ("" if f in exact else "（同型号借用，非本硬件版本）")
            res.add((props.get("label", "?"), tuple(props.get("reg") or ()), off, src))
    return sorted(res, key=lambda r: (str(r[0]), r[2]))


def dts_parts(dts):
    t = open(dts).read()
    return [
        {"label": lab, "offset": int(o, 16), "size": int(s, 16)}
        for lab, o, s in re.findall(r'label = "([^"]+)";\s*\n\s*reg = <0x([0-9a-f]+) 0x([0-9a-f]+)>', t)
    ]


def mtdparts_of(row):
    return row["mtdparts"].strip().strip('"')


def find_mt7621_cfg(name, row):
    """oray_x3a_1233 / oray_a500 —— hwid 为空时不能留尾下划线，否则查不到文件"""
    cands = []
    mdl, hw = row["model"].lower(), row["hwid"].lower()
    if hw:
        cands.append(f"oray_{mdl}_{hw}")
    cands.append(f"oray_{mdl}")
    for c in cands:
        f = os.path.join(REPO, "configs-mt7621", c + "_defconfig")
        if os.path.isfile(f):
            return c, f
    return cands[0], None


def mainline_dir(name):
    return next(iter(sorted(glob.glob(os.path.join(ROOT, "mt76*/boards", name)))), None)


def fmt_sz(n):
    return f"{n} 字节（{n // 1024}K）" if n is not None else "剩余全部"


def read_cmd(media, label, out, size, dev="N"):
    """读一块分区。绝不能对 /dev/mtdN 用 skip 去找别的分区——mtd0 只是引导区那一段，skip 过尾只会得到空文件。"""
    where = f"{size} 字节（{size // 1024}K）" if size else "大小见 /proc/mtd"
    if media == "nand":
        return f"   nanddump -f {out} /dev/mtd{dev}      # {dev} = {label} 那块（{where}）；NAND 用 nanddump，别用 dd 跳偏移"
    return f"   dd if=/dev/mtd{dev} of={out} bs=64k   # {dev} = {label} 那块（{where}）"


def plan(name):
    row = load_board(name)
    if not row:
        print(f"!! board-params.csv 里没有 {name}；--list 看可用板名")
        return 1
    media = row["media"]
    if row["soc"] not in SUPPORTED:
        print(f"!! {name} 是 {row['soc']}，本仓库只出 MT7621/MT7628/MT7620 的 u-boot；"
              "这条线的板级配置和刷写步骤都不适用于它，别照着做")
        return 1
    spec = mtdparts_of(row)
    if not spec:
        print(f"!! {name} 在 csv 里没有 mtdparts，给不出安全的偏移，先跑 orayfw.py boards 补齐")
        return 1
    parts = parse_cells(spec)

    md = mainline_dir(name)
    env_off = env_size = dtb = warn = ""
    cfg_note = ""
    if md:
        dts = glob.glob(os.path.join(md, "*.dts"))[0]
        cfg = glob.glob(os.path.join(md, "*_defconfig"))[0]
        c = open(cfg).read()
        env_off = (re.search(r"CONFIG_ENV_OFFSET=(\S+)", c) or ["", ""])[1]
        env_size = (re.search(r"CONFIG_ENV_SIZE=(\S+)", c) or ["", ""])[1]
        dtb = (re.search(r'CONFIG_DEFAULT_DEVICE_TREE="([^"]+)"', c) or ["", ""])[1]
        dp = dts_parts(dts)
        csv_pre, dts_pre = up_to_fw([p["label"] for p in parts]), up_to_fw([p["label"] for p in dp])
        if [p["offset"] for p in parts] != [p["offset"] for p in dp][: len(parts)]:
            print(f"!! {name}: firmware 之前的分区偏移/大小对不上 —— csv {'/'.join(csv_pre)} vs dts "
                  f"{'/'.join(dts_pre)}，先对齐再刷")
            return 1
        warn = ""
        if csv_pre != dts_pre:
            # 同名槽位在不同硬件版本里被叫作 kpanic 或 u-boot-env，偏移和大小是一样的：
            # 只影响下面备份时的分区名，不影响 env 落在哪儿，所以提醒但不拦
            warn = f"（注意：同一槽位在 csv 里叫 {'/'.join(csv_pre)}，在 dts 里叫 {'/'.join(dts_pre)}，" \
                   f"备份时按 /proc/mtd 的大小认领，别按名字硬套）"
        line = "mainline u-boot（mach-mtmips）：make O=build $DEFCONFIG && make O=build u-boot-with-spl.bin"
        artifact = "build/u-boot-with-spl.bin"
        cfg_note = f"板目录 {os.path.relpath(md, ROOT)}（dts 分区表与 csv 一致）"
    else:
        board, f = find_mt7621_cfg(name, row)
        if not f:
            print(f"!! 找不到 configs-mt7621/{board}_defconfig")
            return 1
        line = f"MT7621 分支：BOARD={board} ./build.sh（板级文件 configs-mt7621/{board}_defconfig）"
        artifact = "archive/u-boot-mt7621_*.bin"
        mm = re.search(r'--mtdparts "([^"]+)"', open(f).read())
        if mm and mm.group(1) != spec:
            print(f"!! {name}: defconfig 的 mtdparts({mm.group(1)}) 与 csv({spec}) 不一致，先对齐再刷")
            return 1
        cfg_note = f"板级文件 configs-mt7621/{board}_defconfig"

    ub = next((p for p in parts if p["label"] == "u-boot"), None)
    if not ub or ub["size"] is None:
        print(f"!! {name}: 分区表里没有带确定大小的 u-boot 分区，不敢给刷写上限")
        return 1
    fac = next((p for p in parts if p["label"] == "factory"), None)
    nxt = next((p for p in parts if p["offset"] > ub["offset"]), None)
    macs = mac_evidence(row)
    uniq = {(l, o) for l, _r, o, _f in macs}
    mac = macs[0] if len(uniq) == 1 else None

    print(f"# {row['model']}-{row['hwid']}  ({row['soc']}, {media}, RAM {row['ram_mb'] or '?'}MB)")
    print("# 分区: " + "  ".join(
        f"{p['label']}@{hex(p['offset'])}" + (f"+{hex(p['size'])}" if p["size"] is not None else "+剩余全部")
        for p in parts))
    print(f"# 分区表来源: {row['mtdparts_src'] or '?'}   {cfg_note}")
    if warn:
        print(f"# {warn}")
    if dtb:
        print(f"# env: {env_off}+{env_size}   board dtb: {dtb}")
    print(f"# 原厂 u-boot: {row['boot_banner'] or '（该板固件未内嵌引导区）'}  版本戳 {row['boot_stamp'] or '-'}")
    print()
    print("1) 先备份，别省这一步")
    print("   # 每块 /dev/mtdN 只是一个分区，不是整片 flash：不要用 skip 从 mtd0 越界去读别的分区，")
    print("   # 那样只会读出一个空文件/全零文件，等真出问题就没有校准数据可回了。")
    print("   cat /proc/mtd                                  # 按大小认领：u-boot="
          f"{ub['size'] // 1024}K" + (f"，factory={fac['size'] // 1024}K" if fac and fac["size"] else "")
          + (f"，{mac[0]}={(mac[1][1] if len(mac[1]) > 1 else 0) // 1024}K" if mac else ""))
    bak = [f"uboot-{name}.bin"]
    print(read_cmd(media, "u-boot", bak[0], ub["size"], "N"))
    if fac:
        fn = f"factory-{name}.bin"
        bak.append(fn)
        print(read_cmd(media, "factory", fn, fac["size"], "M")
              + "   # 无线校准：只读只备份，任何情况下都不要往这块写")
    if mac:
        lab, reg, off, src = mac
        size = reg[1] if len(reg) > 1 else None
        fn = f"{lab}-{name}.bin"
        bak.append(fn)
        print(read_cmd(media, lab, fn, size, "K")
              + f"   # 原厂 ethaddr 就在这块里（{src}）")
    print(f"   md5sum {' '.join(bak)} > backup.md5   # 存远一点，回滚前用来比对")
    if mac:
        lab, _reg, off, src = mac
        print(f"   xxd -s {off} -l 6 {lab}-{name}.bin"
              f"          # 内核 dts: mtd-mac-address = <&{lab} {hex(off)}>，这 6 字节就是 ethaddr")
    elif uniq:
        print(f"   # !! MAC 来源在本板有几个版本对不上（{uniq}），先整片备份再人工确认，别照抄别人的偏移")
    else:
        print("   # !! 该板的固件 dts 里解不出 mtd-mac-address，MAC 位置没有证据：整片备份后自己找，别乱设 ethaddr")
    print(f"   # 更稳：{'编程器夹 SPI 整片读' if media != 'nand' else 'nanddump 整片读'}一次拿全，串口 failsafe 也可回滚")
    print()
    print("2) 编译")
    print(f"   {line}")
    print()
    print("3) 刷写（只动 u-boot 分区，范围 0x0 起）")
    print(f"   # 上限 {fmt_sz(ub['size'])}；超出会盖到后面的 {nxt['label'] if nxt else '未知区域'}——"
          "编完先量大小，超了别刷")
    print(f"   ls -l {artifact}")
    if media == "nand":
        print(f"   nand erase 0 {hex(ub['size'])} ; nand write $loadaddr 0x0 ${{filesize}}   # u-boot 里；参数顺序是 addr off len")
    else:
        print(f"   mtd write {artifact} u-boot        # Linux 侧（OpenWrt mtd 工具按分区名写，不会写错偏移）")
        print("   # 或 u-boot 里：sf probe 0 50000000; tftp $loadaddr u-boot.bin;"
              " sf update $loadaddr 0x0 ${filesize}   # 顺序是 addr off len，别写反")
    print()
    print("4) 刷完第一次进 u-boot 要做的")
    if mac:
        lab, _reg, off, _src = mac
        print(f"   env set ethaddr <上面 xxd 从 {lab} 偏移 {hex(off)} 取出的 6 字节>")
        print("   # 不设的话 CONFIG_NET_RANDOM_ETHADDR 每次开机换随机 MAC：蒲公英是按 MAC 认设备的，云上的身份会变")
    else:
        print("   # 没确认 MAC 来源前别 env set ethaddr：写错成校准区里的字节会得到无效地址，env 里改回来还得擦一次")
    print("   env set bootdelay 3 ; env save      # env 落在自己的槽里，别改偏移")
    print("   mtd list                            # 确认分区名与偏移跟上面一致")
    print("   # 回滚：把第 1 步的 uboot-*.bin 原样写回 0x0，再比对 md5")
    return 0


def check_all():
    """一致性自检：dts 头里写的 MAC 来源必须能在同一份 dts 的分区表里找到，
    而且偏移一致。注释漂移（比如照着别的板抄了一半）就在这里拦下。"""
    bad = n = 0
    dirs = sorted(glob.glob(os.path.join(ROOT, "mt76*/boards/*")) + glob.glob(os.path.join(ROOT, "mt76*/oraybox-*")))
    for md in dirs:
        name = os.path.basename(md.rstrip("/"))
        dts = (glob.glob(os.path.join(md, "*.dts")) + [""])[0]
        if not dts:
            continue                      # 模板目录：只放基线 defconfig，没有 dts
        n += 1
        t = open(dts).read()
        note = re.search(r"MAC\s*:\s*([\w-]+)@(0x[0-9a-f]+)\s*\+0x([0-9a-f]+)", t)
        if not note:
            print(f"!! {name}: dts 头里没有 'MAC : <分区>@<偏移> +0x<n>' 形式的证据")
            bad += 1
            continue
        lab, base, off = note.group(1), int(note.group(2), 16), int(note.group(3), 16)
        got = {p["label"]: p["offset"] for p in dts_parts(dts)}
        if lab not in got:
            print(f"!! {name}: MAC 证据指向 {lab}，但本板 dts 分区表里没有这块（只有 {'/'.join(got)}）")
            bad += 1
        elif got[lab] != base:
            print(f"!! {name}: {lab} 在 dts 里是 {hex(got[lab])}，注释写的却是 {hex(base)}")
            bad += 1
        elif not (0 <= off < (dict((p["label"], p["size"]) for p in dts_parts(dts)).get(lab) or 0)):
            print(f"!! {name}: {lab}+{hex(off)} 越出该分区")
            bad += 1
        # dts 头写的容量必须和 csv（含 board-overrides.json）一致，否则"继承"来的数字会一直留着
        ram = re.search(r"RAM\s*:\s*(\d+)MB", t)
        row = load_board(name)
        if ram and row and row["ram_mb"] and int(ram.group(1)) != int(row["ram_mb"]):
            print(f"!! {name}: dts 头写 {ram.group(1)}MB，csv/overrides 是 {row['ram_mb']}MB")
            bad += 1
    print(f"flash-plan --check: 主线上 {n} 块板，问题 {bad} 块")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--check":
        sys.exit(check_all())
    if len(sys.argv) < 2 or sys.argv[1] == "--list":
        rows = list(csv.DictReader(open(os.path.join(DATA, "board-params.csv"))))
        inb = sorted({f"{r['model']}_{r['hwid']}" for r in rows if r["soc"] in SUPPORTED})
        out = sorted({f"{r['model']}_{r['hwid']}" for r in rows if r["soc"] not in SUPPORTED})
        print("可用板名（model_hwid）：\n  " + "\n  ".join(n for n in inb if n.strip("_")))
        if out:
            print("\n不在本项目 u-boot 覆盖范围（非 MIPS）：\n  " + "\n  ".join(n for n in out if n.strip("_")))
        sys.exit(0)
    sys.exit(plan(sys.argv[1]))
