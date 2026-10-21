#!/usr/bin/env python3
"""从 web1n/oraybox-firmwares 批量解包蒲公英固件，提取原厂 u-boot / 内核 / rootfs 元数据。

前置：git clone --depth 1 https://github.com/web1n/oraybox-firmwares.git upstream

用法:
    python3 orayfw.py list                       # 生成 upstream 文件清单
    python3 orayfw.py unpack --limit 5            # 解包前 5 个
    python3 orayfw.py unpack --model X5 --model R300A
    python3 orayfw.py unpack --jobs 3             # 全量
    python3 orayfw.py summary                     # 汇总 u-boot 去重表
"""
import argparse
import bz2
import csv
import gzip
import hashlib
import json
import lzma
import os
import re
import struct
import subprocess
import sys
import time
import zlib
from concurrent.futures import ThreadPoolExecutor, as_completed

OWNER = "web1n"
REPO = "oraybox-firmwares"
BRANCH = "main"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPSTREAM = os.path.join(ROOT, "upstream")
CACHE = os.path.join(ROOT, "cache")
DATA = os.path.join(ROOT, "data")

# 固件内部结构常量（实测 HCMT7621 系列）
UIMAGE_MAGIC = b"\x27\x05\x19\x56"
SQUASH_MAGIC = b"hsqs"
DTB_MAGIC = b"\xd0\x0d\xfe\xed"

# 只从 squashfs 里取这些板级信息文件，避免解包整个 rootfs 占满磁盘
INTERESTING = [
    "etc/device_info",
    "etc/develop_id",
    "etc/openwrt_release",
    "etc/oraybox_functions.conf",
    "etc/config/system",
    "lib/platform.sh",
    "lib/upgrade/platform.sh",
    "lib/functions/system.sh",
    "lib/functions/oem.sh",
    "lib/oraybox/util.sh",
    "lib/hw/switch.sh",
    "lib/network/switch.sh",
    "etc/rc.button/reset",
    "etc/init.d/orayboxsn_s",
]


def log(msg):
    print(msg, flush=True)


def fetch_listing():
    out = []
    for ch in ("stable", "develop"):
        d = os.path.join(UPSTREAM, ch)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            p = os.path.join(d, name)
            if os.path.isfile(p) and os.path.getsize(p) > 0:
                out.append({"channel": ch, "name": name, "path": f"{ch}/{name}", "size": os.path.getsize(p)})
    return out


def parse_name(fname):
    """OrayBox_X5_1253_3.1.0.bin -> model=X5 hwid=1253 version=3.1.0
    OrayBox_R300A-1121G_5.3.0.bin -> model=R300A hwid=1121G version=5.3.0
    """
    stem = re.sub(r"^OrayBox[._-]?", "", fname, flags=re.I)
    stem = re.sub(r"\.(bin|img|trx|chk)(\.gz)?$", "", stem, flags=re.I)
    tokens = re.split(r"[_-]+", stem)
    model, hwid, version, variant = [], "", "", []
    for t in tokens:
        if not t:
            continue
        if not version and re.fullmatch(r"\d+\.\d+(\.\d+)?", t):
            version = t
        elif model and not hwid and not version and re.fullmatch(r"[A-Z]{0,3}\d{3,6}[A-Z]{0,2}", t, re.I):
            hwid = t
        elif version:
            variant.append(t)
        else:
            model.append(t)
    return {
        "model": "".join(model).upper() or fname,
        "hwid": hwid.upper(),
        "version": version,
        "variant": "-".join(variant).lower(),
    }


def maybe_gunzip(data):
    if data[:2] == b"\x1f\x8b":
        return gzip.decompress(data), True
    return data, False


def try_decompress(payload):
    for name, fn in (
        ("lzma", lambda b: lzma.decompress(b)),
        ("gzip", lambda b: zlib.decompress(b, 16 + zlib.MAX_WBITS)),
        ("zlib", lambda b: zlib.decompress(b)),
        ("xz", lambda b: lzma.decompress(b, format=lzma.FORMAT_XZ)),
        ("bz2", lambda b: bz2.decompress(b)),
        ("raw", lambda b: b),
    ):
        try:
            out = fn(payload)
            if len(out) > 1024:
                return name, out
        except Exception:  # noqa: BLE001
            continue
    return None, None


NAME_HINTS = re.compile(r"(u-boot|linux|hcmt|wt6\d{3}|mt76\d{2}|mips|openwrt|lede)", re.I)


def classify_image(nm):
    low = nm.lower()
    if "u-boot" in low:
        return "bootloader"
    if "linux" in low:
        return "kernel"
    if "nand" in low:
        return "nand-bl"          # MTK NAND 引导器镜像
    return "kernel"


def find_images(data, limit=0x400000):
    """蒲公英固件用 u-boot 1.1.3 时代的 legacy 头：
    magic | crc | time | size | load | ep | dc | os_ld | name[32]，数据从 +64 开始。
    一个 .bin 里可能有多个：NAND BL、u-boot 镜像、内核。
    """
    out = []
    for m in re.finditer(re.escape(UIMAGE_MAGIC), data[: min(len(data), limit)]):
        off = m.start()
        if off + 64 > len(data):
            continue
        _crc, stamp, img_size, load, ep, dc, os_ld = struct.unpack(">7I", data[off + 4 : off + 32])
        name = data[off + 32 : off + 64].split(b"\0")[0]
        if not (0x1000 < img_size < len(data) - off) or not re.fullmatch(rb"[\x20-\x7e]{2,32}", name):
            continue
        nm = name.decode()
        if not NAME_HINTS.search(nm) or not (0x0 <= load <= 0x9FFFFFFF):
            continue
        out.append(
            {
                "offset": off,
                "hdr_size": 64,
                "image_size": img_size,
                "load": hex(load),
                "entry": hex(ep),
                "name": nm,
                "kind": classify_image(nm),
                "timestamp": time.strftime("%Y-%m-%d %H:%M", time.gmtime(stamp)) if 946684800 < stamp < 2 ** 31 else "",
                "fit": data[off + 64 : off + 68] == DTB_MAGIC,
            }
        )
    return out


def parse_partitions(dts_text):
    """从反编译 DTS 里取出 mtd 分区表。"""
    parts = []
    for mm in re.finditer(r"partition@[0-9a-f]+\s*\{(.*?)\};", dts_text, re.S):
        body = mm.group(1)
        lab = re.search(r'label\s*=\s*"([^"]+)"', body)
        reg = re.search(r"reg\s*=\s*<\s*0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)", body)
        if lab and reg:
            parts.append({"label": lab.group(1), "offset": "0x" + reg.group(1), "size": "0x" + reg.group(2)})
    return parts


def find_squashfs(data, start=0):
    m = re.compile(re.escape(SQUASH_MAGIC)).search(data, start)
    return m.start() if m else None


def file_kind(path):
    try:
        return subprocess.run(["file", "-b", path], capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:  # noqa: BLE001
        return ""


def uboot_strings(blob):
    """从 u-boot 区段提取 banner、板名、版本戳、默认 env。"""
    res = {"board_names": [], "banner": "", "boot_stamp": "", "env": {}, "features": []}
    res["board_names"] = sorted({b.decode() for b in re.findall(rb"HCMT[0-9A-Za-z/]+", blob)})
    mb = re.search(rb"U-Boot \d+\.\d+[.\d]* \([^)]{0,120}?\)", blob)
    if mb:
        res["banner"] = mb.group().decode(errors="replace")
    ms = re.search(rb"U_BOOT [0-9A-Za-z._-]{1,16}", blob)
    if ms:
        res["boot_stamp"] = ms.group().decode(errors="replace")
        res["boot_stamp_off"] = hex(ms.start())
    me = re.search(rb"bootcmd=", blob)
    if me:
        seg = blob[me.start() : me.start() + 600].split(b"\xff")[0].split(b"\0\0\0")[0]
        txt = seg.decode("latin1")
        for k in ("bootcmd", "bootdelay", "baudrate", "ethaddr", "ipaddr", "serverip", "netmask", "stdin", "stdout"):
            mk = re.search(rf"{k}=?([^\x00-\x1f=]*)", txt)
            if mk:
                res["env"][k] = mk.group(1).strip()
    feats = {
        "httpd_failsafe": b"start httpd",
        "uip_stack": b"uIP/",
        "tftp_menu": b"System Load UBoot to SDRAM",
        "mdio_cmds": b"mdio.r",
        "flash_write_menu": b"Erase Boot Loader in Flash",
        "nand": b"MT7621-NAND",
    }
    res["features"] = sorted(k for k, v in feats.items() if v in blob)
    return res


def dt_strings(txt, key):
    """读取 dtc 输出里的字符串属性，兼容 "str" 和 [hex] 两种写法。"""
    mm = re.search(rf'\b{key}\s*=\s*(.*?);', txt, re.S)
    if not mm:
        return ""
    vals = []
    for item in re.findall(r'"([^"]*)"|\[([0-9a-fA-F ]+)\]', mm.group(1)):
        s, hx = item
        if s:
            vals.append(s)
        elif hx:
            try:
                vals.append(bytes.fromhex(hx.replace(" ", "")).split(b"\0")[0].decode(errors="replace"))
            except ValueError:
                pass
    return ", ".join(v for v in vals if v)[:160]


def extract_dtbs(buf, out_dir, tag):
    """在原始字节里找 Flattened Device Tree 并反编译成 DTS。返回摘要列表。"""
    found = []
    os.makedirs(out_dir, exist_ok=True)
    for m in re.finditer(re.escape(DTB_MAGIC), buf):
        off = m.start()
        if off + 8 > len(buf):
            continue
        (total,) = struct.unpack(">I", buf[off + 4 : off + 8])
        if not (64 < total < 4 << 20) or off + total > len(buf):
            continue
        dtb = os.path.join(out_dir, f"{tag}-{hex(off)}.dtb")
        dts = os.path.join(out_dir, f"{tag}-{hex(off)}.dts")
        open(dtb, "wb").write(buf[off : off + total])
        info = {"offset": hex(off), "size": total}
        r = subprocess.run(["dtc", "-q", "-I", "dtb", "-O", "dts", "-o", dts, dtb], capture_output=True, timeout=120)
        if r.returncode == 0 and os.path.isfile(dts):
            txt = open(dts, errors="replace").read()
            info["lines"] = txt.count("\n")
            info["dts"] = os.path.basename(dts)
            info["model"] = dt_strings(txt, "model")
            info["compatible"] = dt_strings(txt, "compatible")
            info["partitions"] = parse_partitions(txt)
            os.remove(dtb)
        else:
            info["dtc_error"] = r.stderr.decode(errors="replace")[:120]
        found.append(info)
        if len(found) >= 3:
            break
    return found


def kernel_info(kern):
    res = {}
    mc = re.search(rb"CMDLINE:[\x20-\x7e]+", kern)
    if mc:
        res["cmdline"] = mc.group().decode(errors="replace").strip().split("\0")[0]
    mv = re.search(rb"Linux version [\x20-\x7e]+", kern)
    if mv:
        res["kernel_version"] = mv.group().decode(errors="replace").split("\0")[0][:200]
    res["dtb_present"] = bool(re.search(re.escape(DTB_MAGIC), kern))
    for key, pat in (
        ("eth_driver", rb"(ralink[-_]?eth|rt[23]8655[-_]?eth|mtk_eth)"),
        ("switch", rb"(mt7530|ralink[-_]?gsw|mtk[-_]switch)"),
        ("serial", rb"(ttyS[0-9])"),
        ("flash_driver", rb"(m25p80|rt3070|spi[-_]?ralink|mtk[ -]?nand)"),
        ("wifi", rb"(mt7603|mt76x2|mt7615|mfg_boot)"),
    ):
        mm = re.search(pat, kern, re.I)
        if mm:
            res[key] = mm.group(1).decode(errors="replace")
    return res


KEEP_PATTERNS = {
    "platform.sh": r"0x[0-9a-fA-F]{4,}|bs=2k (count|skip)=|ibs=64 skip=|mtdblock|HCMT|machine|case \"",
    "util.sh": r"MACHINE_|get_machine|mtdblock|dd if=|0x[0-9a-f]{4,}",
    "switch.sh": r"switch (reg|port)|reg [sw]|0x[0-9a-fA-F]{6,}|phy|mdio|port",
    "system.sh": r"mtd|mac|oeminfo|dd if=|0x[0-9a-f]{4,}",
    "oem.sh": r"oem|mac|factory|mtd|0x[0-9a-f]{4,}",
}


def extract_rootfs_meta(slice_path, out_dir):
    got = {}
    try:
        subprocess.run(
            ["unsquashfs", "-n", "-q", "-d", out_dir, slice_path] + INTERESTING,
            capture_output=True,
            timeout=300,
        )
    except Exception as e:  # noqa: BLE001
        return {"_error": str(e)[:120]}
    for rel in INTERESTING:
        p = os.path.join(out_dir, rel)
        if not os.path.isfile(p):
            continue
        txt = open(p, "rb").read().decode("latin1")
        txt = "".join(c for c in txt if 31 < ord(c) < 127 or c in "\n\t")
        base = os.path.basename(rel)
        pat = next((v for k, v in KEEP_PATTERNS.items() if base.endswith(k) or rel.endswith(k)), None)
        if pat:
            keep = [ln.strip() for ln in txt.splitlines() if re.search(pat, ln)]
            txt = "\n".join(keep[:60])
        got[rel] = txt[:4000]
    return got


def model_dir(entry, meta):
    tag = "_".join(x for x in (meta["model"].upper(), meta["hwid"], meta["version"], meta["variant"]) if x)
    return os.path.join(DATA, "models", entry["channel"], tag or os.path.basename(entry["path"]))


def process(entry):
    path, name = entry["path"], entry["name"]
    meta = {"channel": entry["channel"], "file": name, "repo_size": entry["size"], "ok": False}
    meta.update(parse_name(name))
    src = os.path.join(UPSTREAM, path)
    try:
        if not os.path.isfile(src) or os.path.getsize(src) == 0:
            meta["error"] = "upstream 文件缺失（先 git clone 到 upstream/）"
            return meta
        raw = open(src, "rb").read()
        meta["sha256"] = hashlib.sha256(raw).hexdigest()[:16]
        data, was_gz = maybe_gunzip(raw)
        meta["outer_gzip"] = was_gz
        meta["flash_bytes"] = len(data)

        imgs = find_images(data)
        sq_any = find_squashfs(data)
        ubi = re.search(rb"UBI#", data)
        meta["images"] = imgs
        kernel = next((i for i in imgs if i["kind"] == "kernel"), None)
        bl_imgs = [i for i in imgs if i["kind"] in ("bootloader", "nand-bl")]
        board_hint = " ".join(i["name"] for i in imgs)
        nand = bool(ubi) or any(i["kind"] == "nand-bl" for i in imgs) or bool(re.search(r"-N\d{3}", board_hint))
        spi = bool(re.search(r"-S\d{3}", board_hint))
        if nand and not spi:
            media = "nand"
        elif spi:
            media = "spi-nor"
        elif ubi or "nand" in meta.get("squashfs", "").lower():
            media = "nand"
        elif sq_any:
            media = "spi-nor"
        else:
            media = "?"
        meta["flash_media"] = media

        tag = "-".join(x for x in (meta["model"].upper(), meta["hwid"], meta["version"]) if x)
        mdir = model_dir(entry, meta)
        meta["out_dir"] = os.path.relpath(mdir, DATA)
        os.makedirs(mdir, exist_ok=True)
        dtbs = []

        # 引导区 = 第一个容器之前的裸 flash 内容；容器直接从偏移 0 开始就没有引导区
        first = min([i["offset"] for i in imgs] + ([sq_any] if sq_any else []) + ([ubi.start()] if ubi else []) or [0])
        raw_head = data[:first] if first >= 0x10000 else b""
        uboot = raw_head if re.search(rb"U-Boot|uIP/|HCMT|U_BOOT |bootcmd=|mt7621", raw_head[:0x200000]) else b""
        meta["has_bootloader"] = bool(uboot) or any(i["kind"] in ("bootloader", "nand-bl") for i in imgs)
        meta["uboot_bytes"] = len(uboot)
        meta["uboot_sha256"] = hashlib.sha256(uboot).hexdigest()[:16] if uboot else ""
        if uboot:
            meta.update(uboot_strings(uboot))
            open(os.path.join(mdir, "uboot.bin"), "wb").write(uboot)
        meta["layout"] = "+".join(
            x
            for x in (
                "head" if uboot else "",
                "blimg" if bl_imgs else "",
                "uImage" if kernel else "",
                "squashfs" if sq_any else "",
                "ubi" if ubi else "",
            )
            if x
        )

        for i in bl_imgs:
            payload = data[i["offset"] + i["hdr_size"] : i["offset"] + i["hdr_size"] + i["image_size"]]
            comp, dec = try_decompress(payload)
            i["compress"] = comp
            blob = dec or payload
            open(os.path.join(mdir, f"bootloader-{i['kind']}-{hex(i['offset'])}.bin"), "wb").write(blob)
            st = uboot_strings(blob)
            i["banner"], i["board_names"], i["features"] = st["banner"], st["board_names"], st["features"]
            if not meta.get("banner") and st["banner"]:
                meta.update({k: v for k, v in st.items() if not meta.get(k)})
            if not dtbs:
                dtbs = extract_dtbs(blob, os.path.join(mdir, "files", "dtb"), tag + "-bl")

        if kernel:
            meta["kernel"] = kernel
            payload = data[kernel["offset"] + kernel["hdr_size"] : kernel["offset"] + kernel["hdr_size"] + kernel["image_size"]]
            comp, kern = try_decompress(payload)
            meta["kernel"]["compress"] = comp
            if kern:
                meta["kernel"].update(kernel_info(kern))
                if meta["kernel"].get("dtb_present") and not dtbs:
                    dtbs = extract_dtbs(kern, os.path.join(mdir, "files", "dtb"), tag)
            if not dtbs:
                tail_off = kernel["offset"] + kernel["hdr_size"] + kernel["image_size"]
                dtbs = extract_dtbs(data[tail_off : tail_off + 0x80000], os.path.join(mdir, "files", "dtb"), tag + "-tail")

        if dtbs:
            meta["dtbs"] = dtbs
            src = next((x for x in dtbs if x.get("partitions")), dtbs[0])
            meta["partitions"] = src.get("partitions", [])
            meta["dtb_model"] = src.get("model", "")
            meta["dtb_compatible"] = src.get("compatible", "")

        sq = find_squashfs(data, (kernel["offset"] + kernel["image_size"]) if kernel else 0) or sq_any
        if sq:
            slice_path = os.path.join(mdir, "rootfs.slice")
            open(slice_path, "wb").write(data[sq:])
            meta["squash_off"] = hex(sq)
            meta["squashfs"] = file_kind(slice_path)
            meta["rootfs_meta"] = extract_rootfs_meta(slice_path, os.path.join(mdir, "files"))
            os.remove(slice_path)

        # 分区写入规则（platform.sh 里的 dd bs=2k count/skip）反映真实 flash 布局
        plat = (meta.get("rootfs_meta") or {}).get("lib/upgrade/platform.sh", "")
        for mm in re.finditer(r"bs=2k (count|skip)=(\d+)", plat):
            meta.setdefault("mtd_copy_rules", []).append(f"{mm.group(1)}={mm.group(2)} -> {hex(int(mm.group(2)) * 2048)}")
        stamp = re.search(r"ibs=64 skip=(\d+)", (meta.get("rootfs_meta") or {}).get("lib/platform.sh", ""))
        if stamp:
            meta["boot_stamp_addr"] = hex(int(stamp.group(1)) * 64)

        open(os.path.join(mdir, "meta.json"), "w").write(json.dumps(meta, ensure_ascii=False, indent=1))
        meta["ok"] = True
    except Exception as e:  # noqa: BLE001
        meta["error"] = f"{type(e).__name__}: {e}"[:200]
    return meta


def load_index():
    p = os.path.join(DATA, "index.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def save_index(idx):
    os.makedirs(DATA, exist_ok=True)
    json.dump(idx, open(os.path.join(DATA, "index.json"), "w"), ensure_ascii=False, indent=1)
    cols = [
        "model", "hwid", "version", "variant", "channel", "file", "layout", "flash_media",
        "has_bootloader", "flash_bytes", "uboot_bytes", "uboot_sha256", "banner", "board_names",
        "boot_stamp", "boot_stamp_addr", "kernel", "squash_off", "squashfs", "mtd_copy_rules",
        "cmdline", "kernel_version", "dtb_present", "dtb_model", "dtb_compatible", "partitions",
        "env", "features", "ok", "error",
    ]
    with open(os.path.join(DATA, "index.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for m in idx.values():
            row = dict(m)
            k = m.get("kernel") or {}
            row["cmdline"] = k.get("cmdline", "")
            row["kernel_version"] = k.get("kernel_version", "")
            row["dtb_present"] = k.get("dtb_present", "")
            row["board_names"] = "|".join(m.get("board_names", []))
            row["features"] = "|".join(m.get("features", []))
            row["env"] = "; ".join(f"{a}={b}" for a, b in (m.get("env") or {}).items())
            row["kernel"] = json.dumps({x: k.get(x) for x in ("offset", "image_size", "load", "entry", "name", "compress")}, ensure_ascii=False)
            row["mtd_copy_rules"] = "|".join(m.get("mtd_copy_rules", []))
            row["partitions"] = " ".join(f"{p['label']}@{p['offset']}+{p['size']}" for p in m.get("partitions", []))
            row["squashfs"] = m.get("squashfs", "")[:80]
            w.writerow(row)


def cmd_list(_args):
    if not os.path.isdir(UPSTREAM):
        log(f"!! 缺少 {UPSTREAM}，请先 git clone --depth 1 {OWNER}/{REPO} 到 upstream/")
        return
    items = fetch_listing()
    os.makedirs(DATA, exist_ok=True)
    json.dump(items, open(os.path.join(DATA, "listing.json"), "w"), ensure_ascii=False, indent=1)
    log(f"{len(items)} files -> data/listing.json  (源: {UPSTREAM})")


def cmd_unpack(args):
    listing = json.load(open(os.path.join(DATA, "listing.json")))
    if args.model:
        want = {m.lower() for m in args.model}
        listing = [e for e in listing if parse_name(e["name"])["model"].lower() in want]
    if args.limit:
        listing = listing[: args.limit]
    idx = load_index()
    todo = [e for e in listing if f"{e['channel']}/{e['name']}" not in idx or args.force]
    log(f"待处理 {len(todo)}/{len(listing)}，并发 {args.jobs}")
    done = 0
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futs = [pool.submit(process, e) for e in todo]
        for fut in as_completed(futs):
            meta = fut.result()
            done += 1
            idx[f"{meta['channel']}/{meta['file']}"] = meta
            flag = "OK " if meta.get("ok") else "ERR"
            log(f"[{done}/{len(todo)}] {flag} {meta['channel']}/{meta['file']} "
                f"uboot={meta.get('uboot_bytes')} board={meta.get('board_names')} err={meta.get('error','')}")
            if done % 10 == 0:
                save_index(idx)
    save_index(idx)
    log("index 写入 data/index.json / index.csv")


def best(recs):
    def score(m):
        return (
            bool(m.get("partitions")),
            bool(m.get("dtbs")),
            bool(m.get("banner")),
            bool(m.get("kernel")),
            m.get("version") or "",
        )

    return max(recs, key=score)


def group_models(good):
    g = {}
    for m in good:
        g.setdefault((m["model"], m["hwid"]), []).append(m)
    return g


def cmd_summary(_args):
    idx = load_index()
    good = [m for m in idx.values() if m.get("ok")]
    groups = group_models(good)
    bl = {}
    for m in good:
        if m.get("uboot_sha256"):
            bl.setdefault(m["uboot_sha256"], []).append(m)
    builds = {}
    for m in good:
        if m.get("banner"):
            key = (m["banner"], m.get("boot_stamp", ""))
            builds.setdefault(key, []).append(m)

    L = ["# 蒲公英固件解包报告（oraybox-firmwares）\n"]
    L.append(
        f"- 固件 {len(good)} 个，型号/硬件组合 {len(groups)} 个；"
        f"提取到 DTS {sum(1 for m in good if m.get('dtbs'))} 份，"
        f"含引导区 {sum(1 for m in good if m.get('has_bootloader'))} 份，"
        f"按内容去重的引导区 {len(bl)} 个，按 banner+版本戳去重的原厂 u-boot 构建 {len(builds)} 种。\n"
    )

    L.append("## 型号对照表\n")
    L.append("| 型号 | 硬件 | 介质 | SoC/板名 | DTB model | u-boot banner | 版本戳 | uImage@ | squashfs@ | DTS |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for (mdl, hw), recs in sorted(groups.items()):
        m = best(recs)
        k = m.get("kernel") or {}
        boards = "|".join(m.get("board_names") or []) or (m.get("dtb_compatible") or "").split(",")[0]
        L.append(
            f"| {mdl} | {hw} | {m.get('flash_media','')} | {boards} | {m.get('dtb_model','')} | {m.get('banner','')} | "
            f"{m.get('boot_stamp','')} | {hex(k['offset']) if k else '-'} | {m.get('squash_off','-')} | "
            f"{'Y' if m.get('dtbs') else '-'} |"
        )

    L.append("\n## 分区表（来自固件内 DTB 反编译）\n")
    L.append("| 型号 | 硬件 | 分区 |")
    L.append("|---|---|---|")
    for (mdl, hw), recs in sorted(groups.items()):
        m = best(recs)
        if m.get("partitions"):
            cells = " ".join(f"`{p['label']}` {p['offset']}+{p['size']}" for p in m["partitions"])
            L.append(f"| {mdl} | {hw} | {cells} |")

    L.append("\n## 原厂 u-boot 构建（按 banner + 版本戳去重）\n")
    L.append("| banner | 版本戳 | 引导区大小 | 覆盖型号 |")
    L.append("|---|---|---|---|")
    for (bnr, st), ms in sorted(builds.items(), key=lambda kv: -len(kv[1])):
        size = best(ms).get("uboot_bytes")
        L.append(f"| {bnr} | {st} | {size} | {', '.join(sorted({x['model'] + '/' + x['hwid'] for x in ms}))} |")

    L.append("\n## 引导区按内容去重（同一型不同固件版本是否有变化）\n")
    L.append("| sha16 | 大小 | banner | 版本戳 | 特性 | 型号 |")
    L.append("|---|---|---|---|---|---|")
    for sha, ms in sorted(bl.items(), key=lambda kv: -len(kv[1])):
        m = best(ms)
        L.append(
            f"| `{sha}` | {m.get('uboot_bytes')} | {m.get('banner','')} | {m.get('boot_stamp','')} | "
            f"{','.join(m.get('features', []))} | {', '.join(sorted({x['model'] + '/' + x['hwid'] for x in ms}))} |"
        )

    L.append("\n## 内嵌引导镜像（NAND BL / u-boot 2018 FIT）\n")
    for m in good:
        for i in m.get("images", []):
            if i["kind"] in ("bootloader", "nand-bl"):
                L.append(
                    f"- {m['model']}/{m['hwid']} {m['version']}: `{i['name'][:60]}` @ {hex(i['offset'])} "
                    f"size={i['image_size']} load={i['load']} kind={i['kind']} fit={i['fit']} banner={i.get('banner','')}"
                )

    no_bl = sorted({f"{m['model']}/{m['hwid']}" for m in good if not m.get("has_bootloader")})
    L.append("\n## 不含引导区的固件（纯 sysupgrade，需从设备 SPI/NAND 读原厂 u-boot）\n")
    L.append(", ".join(no_bl) or "-")

    out = os.path.join(DATA, "SUMMARY.md")
    open(out, "w").write("\n".join(L) + "\n")
    log(f"-> {out}  ({len(L)} 行)")


def cmd_dts(_args):
    """把每个型号解出来的 DTS 收集到 data/dts/。"""
    idx = load_index()
    outdir = os.path.join(DATA, "dts")
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for (mdl, hw), recs in sorted(group_models([m for m in idx.values() if m.get("ok")]).items()):
        m = best(recs)
        if not m.get("dtbs") or not m.get("out_dir"):
            continue
        tag = "_".join(x for x in (mdl, hw, m["version"]) if x)
        for d in m["dtbs"]:
            src = os.path.join(DATA, m["out_dir"], "files", "dtb", d["dts"])
            if os.path.isfile(src):
                open(os.path.join(outdir, f"{tag}.dts"), "w").write(open(src, errors="replace").read())
                n += 1
    log(f"{n} 份 DTS -> {outdir}")


SOC_BY_TOKEN = [("7621", "MT7621"), ("6271", "MT7628"), ("7628", "MT7628"), ("6320", "MT7620"), ("7620", "MT7620")]


def detect_soc(m):
    blob = " ".join(
        (m.get("board_names") or [])
        + [(m.get("kernel") or {}).get("name", ""), m.get("dtb_compatible", ""), m.get("dtb_model", "")]
    )
    rel = (m.get("rootfs_meta") or {}).get("etc/openwrt_release", "")
    tgt = re.search(r"DISTRIB_TARGET=['\"]?([\w/-]+)", rel)
    if tgt:
        t = tgt.group(1)
        if t.startswith("x86"):
            return "x86_64"
        mm2 = re.search(r"mt(\d{4})", t)
        if mm2:
            return "MT" + mm2.group(1)        # ramips/mt7628 之类
    mm = re.search(r"DISTRIB_TARGET=['\"]?ramips/(mt\d+)", rel)
    if mm:
        return mm.group(1).upper()
    for tok, name in SOC_BY_TOKEN:
        if tok in blob:
            return name
    return "?"


def size_str(n):
    return f"{n // 1024}k" if n % (1024 * 1024) else f"{n // (1024 * 1024)}M"


def phandle_map(txt):
    """phandle 数字 -> 节点名，用于把 gpios = <ph pin flg> 解析成 GPIO 组/脚。"""
    out = {}
    for mm in re.finditer(r"phandle\s*=\s*<\s*0x([0-9a-fA-F]+)\s*>", txt):
        head = txt[: mm.start()]
        nodes = re.findall(r"([A-Za-z0-9@_,.$-]+)\s*\{", head)
        if nodes:
            out[mm.group(1).lower()] = nodes[-1]
    return out


def gpio_of(txt, ph, pin):
    node = phandle_map(txt).get(ph.lower(), "")
    mb = re.search(r"bank@(\d+)$", node)
    bank = int(mb.group(1)) if mb else 0      # 指向 gpio 控制器根节点时按 bank a 处理
    n = int(pin, 16)
    return {
        "node": node,
        "bank": bank,
        "pin": n,
        "label_gpio": chr(ord("a") + bank) + str(n) if bank < 3 else "",
        "guess": bank * 16 + n,               # 待核对：mt7621 分组 a=0-15 b=16-31 c=32-47
    }


GPIO_KIND = {"gpio-keys": "reset", "gpio-keys-polled": "reset", "gpio-leds": "sysled"}


def dt_buttons_leds(dts_path):
    """按 compatible 归集按键/LED 的 GPIO（dtc 输出里节点名不固定）。"""
    if not os.path.isfile(dts_path):
        return {}
    txt = open(dts_path, errors="replace").read()
    res = {}
    for mm in re.finditer(r'label\s*=\s*"([^"]+)"\s*;\s*gpios\s*=\s*<\s*0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)', txt):
        before = txt[max(0, mm.start() - 700) : mm.start()]
        cm = re.findall(r'compatible\s*=\s*"gpio-(keys-polled|keys|leds)"', before)
        if not cm:
            continue
        kind = GPIO_KIND.get("gpio-" + cm[-1])
        if not kind:
            continue
        g = gpio_of(txt, mm.group(2), mm.group(3))
        g["label"] = mm.group(1)
        res.setdefault(kind, []).append(g)
    return res


def offset_from_mtdparts(mp):
    """按 mtdparts 字符串累加到 firmware 之前的字节偏移。"""
    total = 0
    for cell in mp.split(","):
        mm = re.match(r"\s*(\d+)([kKmM])\(", cell)
        if not mm:
            break
        total += int(mm.group(1)) * (1024 if mm.group(2).lower() == "k" else 1024 * 1024)
        if "firmware" in cell:
            break
    return total or None


def uboot_embedded_mtdparts(m):
    """原厂 u-boot 二进制里编译进去的 CONFIG_MTDPARTS_DEFAULT。"""
    if not m.get("out_dir"):
        return ""
    d = os.path.join(DATA, m["out_dir"])
    if not os.path.isdir(d):
        return ""
    for fn in sorted(os.listdir(d)):
        if not (fn == "uboot.bin" or fn.startswith("bootloader-")):
            continue
        blob = open(os.path.join(d, fn), "rb").read()
        mm = re.search(rb"mtdparts=[A-Za-z0-9_.:+-]+:([0-9a-zA-Z]+\(u-boot\)[0-9a-zA-Z_(),+.-]*)", blob)
        if mm:
            return mm.group(1).decode(errors="replace")
    return ""


def synth_mtdparts(media, koffset):
    """没有分区表时按 ramips 标准布局推断。"""
    if media == "nand":
        return "512k(u-boot),512k(u-boot-env),256k(factory),-(firmware)"
    if koffset == 0x50000:
        return "192k(u-boot),64k(u-boot-env),64k(factory),-(firmware)"
    if koffset:
        head = size_str(koffset - 0x20000) + "(u-boot),64k(u-boot-env),64k(factory),-(firmware)"
        return head
    return ""


def parts_to_mtdparts(parts):
    cells = []
    for p in parts:
        size = int(p["size"], 16)
        if p["label"] in ("bdinfo", "reserve", "overlay", "opt", "debug", "firmware_backup", "fullflash"):
            continue
        cells.append(f"{size_str(size)}({p['label']})")
    if cells and cells[-1].endswith("(firmware)"):
        cells[-1] = "-(firmware)"
    return ",".join(cells)


DDR_BY_MB = {64: "DDR2-64MiB", 128: "DDR3-128MiB", 256: "DDR3-256MiB", 512: "DDR3-512MiB"}


def dt_ram_mb(dts_path):
    if not dts_path or not os.path.isfile(dts_path):
        return None
    txt = open(dts_path, errors="replace").read()
    mm = re.search(r"memory[@\w-]*\s*\{[^}]*?reg\s*=\s*<\s*0x[0-9a-fA-F]+\s+0x([0-9a-fA-F]+)", txt, re.S)
    return int(mm.group(1), 16) // (1024 * 1024) if mm else None


def load_ddr_probe():
    p = os.path.join(DATA, "ddr-probe.json")
    if not os.path.isfile(p):
        return {}
    raw = json.load(open(p))
    out = {}
    for path, rec in raw.items():
        rel = os.path.relpath(path, DATA)
        model_dir = str(os.path.dirname(rel))
        if os.path.basename(path) == "uboot.bin" or rec.get("ddr"):
            out.setdefault(model_dir, []).append((rel, rec))
    return out


SERIAL_PROBE = {}


def cmd_boards(_args):
    """导出板级参数表 + 给 uboot-mt7621 的 configs-mt7621/*.defconfig。"""
    idx = load_index()
    good = [m for m in idx.values() if m.get("ok")]
    DDR_PROBE = load_ddr_probe()
    sp = os.path.join(DATA, "serial-probe.json")
    if os.path.isfile(sp):
        SERIAL_PROBE.update(json.load(sp))
    outdir = os.path.join(DATA, "boards")
    os.makedirs(outdir, exist_ok=True)

    # 供体库：同 SoC 家族 + 同介质 + 同 firmware 偏移的真实分区表
    donors = {}
    for m in good:
        for p in m.get("partitions") or []:
            if p["label"] == "firmware":
                donors.setdefault(
                    (detect_soc(m), m.get("flash_media"), int(p["offset"], 16)),
                    (parts_to_mtdparts(m["partitions"]), f"{m['model']}/{m['hwid']}"),
                )
                break

    rows = []
    for (mdl, hw), recs in sorted(group_models(good).items()):
        m = best(recs)
        dts = None
        if m.get("dtbs") and m.get("out_dir"):
            d = next((x for x in m["dtbs"] if x.get("dts")), None)
            dts = os.path.join(DATA, m["out_dir"], "files", "dtb", d["dts"]) if d else None
        parts = m.get("partitions") or []
        soc = detect_soc(m)
        io = dt_buttons_leds(dts) if dts else {}
        kname = (m.get("kernel") or {}).get("name", "")
        kern = m.get("kernel") or {}
        kfw = next((int(p["offset"], 16) for p in parts if p["label"] == "firmware"), kern.get("offset"))
        mp, src = "", ""
        if parts:
            mp, src = parts_to_mtdparts(parts), "DTB"
        elif uboot_embedded_mtdparts(m):
            mp, src = uboot_embedded_mtdparts(m), "u-boot 内嵌默认值"
        elif (soc, m.get("flash_media"), kfw) in donors:
            mp, src = donors[(soc, m.get("flash_media"), kfw)][0], f"继承 {donors[(soc, m.get('flash_media'), kfw)][1]}"
        else:
            s = synth_mtdparts(m.get("flash_media"), kfw)
            mp, src = (s, "推断") if s else ("", "缺失")
        gap = ["cpufreq", "ramfreq", "ddrparam", "oldparam"]   # 固件里拿不到，需要串口或反汇编
        ram_mb = dt_ram_mb(dts)
        cpufreq = next((r.get("cpufreq") for r in [SERIAL_PROBE.get(f"{mdl}_{hw}") or {}] if r), "")
        probe = DDR_PROBE.get(m.get("out_dir", ""), [])
        ddr_base = "|".join(x[1]["ddr"][0]["config"].replace("MT7621_DRAM_", "").replace("_LEGACY", "") for x in probe if x[1].get("ddr"))
        ram_implied = max((f["mhz"] for _, r in probe for f in r.get("freq", [])), default=None)
        oldp = next((str(r["oldparam"]) for _, r in probe if r.get("oldparam") is not None), "")
        ddr_guess = DDR_BY_MB.get(ram_mb, "")
        if ram_mb:
            gap.remove("ddrparam")
        if ram_implied:
            gap.remove("ramfreq")
        if mp == "":
            gap.append("mtdparts")
        if not io:
            gap.append("reset/sysled")
        rows.append(
            {
                "model": mdl, "hwid": hw, "soc": soc, "media": m.get("flash_media", ""),
                "firmware": m["file"], "kernel_offset": hex(kern.get("offset", 0)) if kern else "",
                "fw_offset": hex(kfw) if kfw else "",
                "mtdparts": mp, "mtdparts_src": src, "boot_banner": m.get("banner", ""),
                "boot_stamp": m.get("boot_stamp", ""), "head_bytes": m.get("uboot_bytes", 0),
                "dtb": "Y" if m.get("dtbs") else "-",
                "reset": json.dumps(io.get("reset", []), ensure_ascii=False),
                "sysled": json.dumps(io.get("sysled", []), ensure_ascii=False),
                "kernel_name": kname, "ram_mb": ram_mb or "", "dramc_in_uboot": ddr_base,
                "ramfreq_hint": ram_implied or "", "oldparam_hint": oldp, "todo": "|".join(gap),
            }
        )
        # 只对 MT7621 出 defconfig
        if soc == "MT7621" and mp:
            board = f"oray_{(mdl + '_' + hw).strip('_').lower()}"
            ko = offset_from_mtdparts(mp) or kfw
            lines = [
                f"--flash {'NAND' if m.get('flash_media') == 'nand' else 'NOR'}",
                f'--mtdparts "{mp}"',
                f'--model "OrayBox_{mdl + ("-" + hw if hw else "")}"',
                f"--kernel-offset {hex(ko)}",
            ]
            for key, flags in (("reset", ("--reset-pin", "--wps-pin")),
                               ("sysled", ("--sysled-pin", "--sysled2-pin"))):
                for i, g in enumerate(io.get(key) or []):
                    if g.get("guess") is None:
                        continue
                    flag = flags[i] if i < len(flags) else None
                    lines.append(f"# {g['label']} -> {g['node']} {g['label_gpio'] or 'pin' + str(g['pin'])}")
                    if flag:
                        lines.append(f"{flag} {g['guess']}")
                    else:
                        lines.pop()
            lines.append("# cpufreq 固件里拿不到：跑 tools/serial_probe.py 抓开机横幅后填")
            lines.append(f"--cpufreq {cpufreq or 'TODO'}")
            lines.append(f"# ramfreq 依据：原厂 u-boot 里的频率立即数 {ram_implied} MT/s" if ram_implied else "# ramfreq 待串口确认")
            lines.append(f"--ramfreq {ram_implied or 'TODO'}")
            lines.append(f"# ddrparam 依据：DTB memory = {ram_mb}MB" if ddr_guess else "# ddrparam 待确认（固件里只有 SDK 基线表）")
            lines.append(f"--ddrparam {ddr_guess or 'TODO'}")
            lines.append(f"--oldparam {(oldp or 'false').lower()}")
            lines += ["--baudrate 115200", "--yes"]
            notes = [f"# mtdparts 来源: {src}"]
            if ddr_base:
                notes.append(f"# 原厂 u-boot 内嵌 dramc 基线表: {ddr_base}（MTK SDK 会按实测容量改写，别直接照搬）")
            lines.append("\n".join(notes))
            open(os.path.join(outdir, board + "_defconfig"), "w").write("\n".join(lines) + "\n")

    with open(os.path.join(DATA, "board-params.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    n7621 = sum(1 for r in rows if r["soc"] == "MT7621")
    log(f"{len(rows)} 个型号/硬件 -> data/board-params.csv；MT7621 {n7621} 个，defconfig 写入 {outdir}")
    for soc in sorted({r["soc"] for r in rows}):
        log(f"  {soc}: {', '.join(sorted(r['model'] + '/' + r['hwid'] for r in rows if r['soc'] == soc))}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(func=cmd_list)
    u = sub.add_parser("unpack")
    u.add_argument("--model", action="append", default=[])
    u.add_argument("--limit", type=int, default=0)
    u.add_argument("--jobs", type=int, default=3)
    u.add_argument("--force", action="store_true")
    u.set_defaults(func=cmd_unpack)
    sub.add_parser("summary").set_defaults(func=cmd_summary)
    sub.add_parser("dts").set_defaults(func=cmd_dts)
    sub.add_parser("boards").set_defaults(func=cmd_boards)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
