#!/usr/bin/env python3
"""从解包出的内核 DTB 派生 mainline mt7628 的 board dts + defconfig。

    python3 gen-7628-dts.py [--index data/index.json] [--out repo/oraybox/mt7628/boards]

只写有证据的东西：分区表、复位键/LED、MAC 来源、console、内存大小。
没有 DTB 的板子用同 SoC 供体（文件头会写明"继承 X，未实测"）。
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orayfw as O  # noqa: E402

TEMPLATE = """// SPDX-License-Identifier: GPL-2.0
/*
 * OrayBox {MODEL}-{HW} — 自动派生，未上机验证
 *
 * 证据来源: {SRC_NOTE}
 *   SoC      : MT7628AN (MIPS 24Kc)  RAM {RAM}
 *   console  : {CONSOLE}
 *   MAC      : {MACNOTE}
 *   按键/LED : {GPIONOTE}
 *
 * 用法见 oraybox/mt7628/README.md；改动分区表前先跑 check-dts.sh 校验。
 */

/dts-v1/;

#include "mt7628a.dtsi"

/ {{
	compatible = "oraybox,{LOW}", "ralink,mt7628a-soc";
	model = "OrayBox {MODEL}-{HW}";

	aliases {{
		serial0 = &uart0;
		spi0 = &spi0;
	}};

	chosen {{
		stdout-path = &uart0;
	}};
}};

&pinctrl {{
	state_default: pin_state {{
		pleds {{
			groups = "p0led", "p1led", "p2led", "p3led", "p4led";
			function = "led";
		}};
	}};
}};

&uart0 {{
	status = "okay";
}};

&spi0 {{
	status = "okay";
	num-cs = <1>;

	spi-flash@0 {{
		compatible = "jedec,spi-nor";
		spi-max-frequency = <25000000>;
		reg = <0>;

		partitions {{
			compatible = "fixed-partitions";
			#address-cells = <1>;
			#size-cells = <1>;

{PARTS}
		}};
	}};
}};

&eth {{
	mediatek,wan-port = <0>;

	pinctrl-names = "default";
	pinctrl-0 = <&ephy_router_mode>;
}};
"""

PART = """			partition@{OFF} {{
				label = "{LABEL}";
				reg = <0x{OFF} 0x{SIZE}>;{RO}
			}};
"""


def parse_kernel_dts(path):
    txt = open(path, errors="replace").read()
    pm = O.phandle_map(txt)
    parts = []
    for mm in re.finditer(r"partition@([0-9a-f]+)\s*\{(.*?)\n\t\t\t\t\};", txt, re.S):
        body = mm.group(2)
        lab = re.search(r'label\s*=\s*"([^"]+)"', body)
        reg = re.search(r"reg\s*=\s*<\s*0x([0-9a-f]+)\s+0x([0-9a-f]+)", body)
        if lab and reg:
            parts.append({"label": lab.group(1), "offset": reg.group(1), "size": reg.group(2)})
    keys = []
    for mm in re.finditer(r'label\s*=\s*"([^"]+)"\s*;\s*gpios\s*=\s*<\s*0x([0-9a-f]+)\s+0x([0-9a-f]+)', txt):
        node = pm.get(mm.group(2), "")
        bank = re.search(r"bank@(\d+)", node)
        keys.append({"label": mm.group(1), "bank": int(bank.group(1)) if bank else 0, "pin": int(mm.group(3), 16)})
    mac = re.search(r"mtd-mac-address\s*=\s*<\s*0x([0-9a-f]+)\s+0x([0-9a-f]+)", txt)
    macnote = "未找到"
    if mac:
        lab = next((p["label"] for p in parts if pm.get(mac.group(1)) and p["label"] in pm[mac.group(1)]), "")
        macnote = f"{lab or pm.get(mac.group(1), '?')} 分区偏移 0x{int(mac.group(2), 16):x}"
    mem = re.search(r"memory[@\w-]*\s*\{[^}]*?reg\s*=\s*<\s*0x[0-9a-f]+\s+0x([0-9a-f]+)", txt, re.S)
    console = re.search(r'bootargs\s*=\s*"([^"]*)"', txt)
    return {
        "parts": parts,
        "keys": keys,
        "mac": macnote,
        "ram": f"{int(mem.group(1), 16) // (1024 * 1024)}MB" if mem else "未写明（u-boot 运行时探测）",
        "console": (console.group(1) if console else "115200"),
    }


def render(model, hw, info, src_note):
    cells, seen = [], set()
    for p in info["parts"]:
        off, size = p["offset"].lstrip("0") or "0", int(p["size"], 16)
        if size == 0 or off in seen:      # 零大小/重偏移（如厂商的 fullflash）会让 dtc 报 duplicate_node_names
            continue
        seen.add(off)
        p = dict(p, offset=off)
        ro = "  /* 只读 */" if p["label"] in ("u-boot", "factory") else ""
        cells.append(PART.format(OFF=off, LABEL=p["label"], SIZE=p["size"], RO=ro).rstrip("\n"))
    gpio = ", ".join(f"{k['label']}=gpio{k['bank']}/{k['pin']}" for k in info["keys"]) or "无 DTB 依据"
    return TEMPLATE.format(
        MODEL=model, HW=hw, LOW=f"{model}-{hw}".lower(), SRC_NOTE=src_note, RAM=info["ram"],
        CONSOLE=info["console"], MACNOTE=info["mac"], GPIONOTE=gpio, PARTS="\n\n".join(cells),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default="data/index.json")
    ap.add_argument("--out", default="repo/oraybox/mt7628/boards")
    ap.add_argument("--defconfig-src", default="repo/oraybox/mt7628/oraybox-x4c/mt7628_oraybox_x4c_defconfig")
    args = ap.parse_args()

    idx = json.load(open(args.index))
    good = [m for m in idx.values() if m.get("ok")]
    by = O.group_models(good)
    base_dc = open(args.defconfig_src).read()

    todo = []
    for (mdl, hw), recs in sorted(by.items()):
        soc = O.detect_soc(max(recs, key=lambda x: bool(x.get("dtbs"))))
        if soc != "MT7628":
            continue
        m = max(recs, key=lambda x: (bool(x.get("partitions")), bool(x.get("dtbs"))))
        dts = O.dts_path_of(m)
        info = parse_kernel_dts(dts) if dts else None
        todo.append((mdl, hw, m, info, dts))

    donors = [(mdl, hw, it, f"内核 DTB 直读（{m['file']}）") for mdl, hw, m, it, _ in todo if it and it["parts"]]
    if not donors:
        print("没有任何 MT7628 的 DTB，无法派生"); return
    made = []
    for mdl, hw, m, info, dts in todo:
        if info and info["parts"]:
            note = f"内核 DTB 直读（{m['file']}）"
        else:
            # 先找同型号前缀的供体，再退回任意有分区表的 MT7628
            fam = re.match(r"[A-Za-z]+\d*", mdl)
            dn = next((d for d in donors if fam and d[0].startswith(fam.group())), donors[0])
            info, note = dict(dn[2]), f"分区/GPIO 继承 {dn[0]}/{dn[1]}（本板固件无 DTB，老内核不带 DT），未实测"
        outdir = os.path.join(args.out, f"{mdl}_{hw}")
        os.makedirs(outdir, exist_ok=True)
        name = f"mt7628a-oraybox-{mdl}-{hw}".lower()
        open(os.path.join(outdir, name + ".dts"), "w").write(render(mdl, hw, info, note))
        dc = re.sub(r'CONFIG_DEFAULT_DEVICE_TREE="[^"]*"', f'CONFIG_DEFAULT_DEVICE_TREE="{name}"', base_dc)
        open(os.path.join(outdir, name.replace("mt7628a-oraybox-", "mt7628_oraybox_").replace("-", "_") + "_defconfig"), "w").write(dc)
        made.append((mdl, hw, note, len(info["parts"])))
        print(f"生成 {mdl}/{hw}: 分区 {len(info['parts'])} 个  ← {note}")

    print(f"\n共 {len(made)} 块板，输出 {args.out}")


if __name__ == "__main__":
    main()
