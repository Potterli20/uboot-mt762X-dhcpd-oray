#!/usr/bin/env python3
"""从原厂 u-boot 二进制反推 uboot-mt7621 需要的 DDR 参数。

做法：解析参考仓库 arch/mips/mach-mt7621/dramc-legacy/dramc.S 里的寄存器表，
拿这些表的字面常量去 blob 里做字节匹配；频率看 PTR_LI 展开后的 lui 立即数，
oldparam 直接读表里 DDR3_TRFC_PARAM 那个字。

    python3 dramid.py <ref-uboot 路径> <blob 或目录>...
"""
import argparse
import json
import os
import re
import struct
import sys

TABLE_LABEL = re.compile(r"dramc_(ddr\d)_ac_timing_parameters:")
CONFIG_BLOCK = re.compile(r"#\s*(if|elif|else|endif) defined\(CONFIG_(MT7621_DRAM_[A-Z0-9_]+)\)")
WORD_LINE = re.compile(r"\.word\s+(.*)")


def parse_tables(dramc_path):
    """返回 {config_name: [u32 或 None...]}（24 字一组）与 {立即数: MHz}。"""
    text = open(dramc_path, errors="replace").read()
    tables = {}
    cur, pending = None, []
    for line in text.splitlines():
        m = CONFIG_BLOCK.search(line)
        if m:
            if m.group(1) in ("if", "elif"):
                cur, pending = m.group(2), []
            else:
                cur = None
            continue
        w = WORD_LINE.search(line)
        if not (w and cur):
            continue
        for tok in w.group(1).split(","):
            tok = tok.strip()
            if not tok:
                continue
            if re.fullmatch(r"0x[0-9a-fA-F]+", tok):
                pending.append(int(tok, 16))
            elif tok == "DDR3_TRFC_PARAM":
                pending.append(None)       # oldparam 决定，匹配时当通配
        if len(pending) >= 24:
            tables[cur] = pending[:24]
            cur = None
    freq_map = {
        int(mm.group(2), 16): int(mm.group(1))
        for mm in re.finditer(
            r"CONFIG_MT7621_DRAM_FREQ_(\d+)_LEGACY\)\n#define DDR_FREQ_PARAM\s+(0x[0-9a-fA-F]+)", text
        )
    }
    return tables, freq_map


def find_table(blob, words):
    """24 字表按小端打包，None 位置当通配，返回命中偏移列表。"""
    pat = b"".join(b"...." if w is None else re.escape(struct.pack("<I", w)) for w in words)
    return [m.start() for m in re.finditer(b"(?=" + pat + b")", blob)]


def lui_values(blob, freq_map):
    """MT7621 是 little-endian MIPS；li t?,0xXX000000 编成 lui（rs=0, rt=t?, imm=0xXX00）。"""
    hit = {}
    for val, mhz in freq_map.items():
        rt = 8  # t0
        for rt in range(1, 26):
            insn = struct.pack("<I", ((0x0F << 26) | (0 << 21) | (rt << 16) | (val >> 16)))
            if insn in blob:
                hit[mhz] = hex(struct.unpack("<I", insn)[0])
                break
    return hit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref", help="参考仓库根目录（含 arch/mips/mach-mt7621）")
    ap.add_argument("targets", nargs="+", help="blob 文件或目录（递归找 uboot.bin / bootloader-*.bin）")
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    dramc = os.path.join(args.ref, "arch/mips/mach-mt7621/dramc-legacy/dramc.S")
    tables, freq_map = parse_tables(dramc)
    print(f"参考表 {len(tables)} 组：{list(tables)}")
    print(f"频率立即数：{freq_map}")

    blobs = []
    for t in args.targets:
        if os.path.isfile(t):
            blobs.append(t)
        else:
            for root, _, files in os.walk(t):
                for f in files:
                    if f == "uboot.bin" or f.startswith("bootloader-"):
                        blobs.append(os.path.join(root, f))

    out = {}
    for b in sorted(blobs):
        blob = open(b, "rb").read()
        rec = {"size": len(blob), "ddr": [], "freq": [], "oldparam": None}
        for cfg, words in tables.items():
            offs = find_table(blob, words)
            if offs:
                trfc = words[20] if len(words) > 20 else None
                rec["ddr"].append({"config": cfg, "offsets": [hex(o) for o in offs[:4]]})
                for o in offs[:1]:
                    w = struct.unpack("<I", blob[o + 20 * 4 : o + 20 * 4 + 4])[0]
                    if w in (0x0A000000, 0x0C000000):
                        rec["oldparam"] = (w == 0x0A000000)
                        rec["trfc_word"] = hex(w)
        for mhz, enc in lui_values(blob, freq_map).items():
            rec["freq"].append({"mhz": mhz, "lui": enc})
        out[b] = rec
        ddr = ", ".join(x["config"].replace("MT7621_DRAM_", "").replace("_LEGACY", "") for x in rec["ddr"]) or "-"
        fr = ", ".join(str(x["mhz"]) for x in rec["freq"]) or "-"
        print(f"{b.replace(args.ref, ''):<70} ddr={ddr:<38} freq={fr:<20} oldparam={rec['oldparam']}")

    if args.json:
        json.dump(out, open(args.json, "w"), ensure_ascii=False, indent=1)
        print(f"-> {args.json}")


if __name__ == "__main__":
    main()
