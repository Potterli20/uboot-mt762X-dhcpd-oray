#!/usr/bin/env python3
"""从解包出的内核 DTB 派生 mainline (mach-mtmips) 的 board dts + defconfig。

    python3 gen-mtmips-dts.py --soc MT7628
    python3 gen-mtmips-dts.py --soc MT7620
    python3 gen-mtmips-dts.py            # 两个都做

只写有证据的东西：分区表、复位键/LED、MAC 来源、console、内存大小。
没有 DTB 的板子按"同型号前缀 → 同 SoC"找供体，文件头写明来源与"未实测"。
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dtsread  # noqa: E402
import orayfw as O  # noqa: E402

SOC = {
    "MT7628": {
        "include": "mt7628a.dtsi",
        "soc_compat": "ralink,mt7628a-soc",
        "uart": "uart0",
        "dts_prefix": "mt7628a-oraybox-",
        "dcfg_prefix": "mt7628_oraybox_",
        "base_defconfig": "repo/oraybox/mt7628/oraybox-x4c/mt7628_oraybox_x4c_defconfig",
        "out": "repo/oraybox/mt7628/boards",
        "eth": """&eth {
	mediatek,wan-port = <0>;

	pinctrl-names = "default";
	pinctrl-0 = <&ephy_router_mode>;
};""",
        "spi_extra": "",
        "pinctrl": """&pinctrl {
\tstate_default: pin_state {
\t\tpleds {
\t\t\tgroups = "p0led", "p1led", "p2led", "p3led", "p4led";
\t\t\tfunction = "led";
\t\t};
\t};
};""",
    },
    "MT7620": {
        "include": "mt7620.dtsi",
        "soc_compat": "mediatek,mt7620-soc",
        "uart": "uartlite",
        "dts_prefix": "mt7620-oraybox-",
        "dcfg_prefix": "mt7620_oraybox_",
        "base_defconfig": "repo/oraybox/mt7620/oraybox-r300a/mt7620_oraybox_r300a_1121g_defconfig",
        "out": "repo/oraybox/mt7620/boards",
        # 依据：R300A-1121G 等内核 DTB 里只有 gsw、没有 mt7530 节点，故用 rfb 的 gsw 形态
        "eth": """&eth {
	status = "okay";

	pinctrl-names = "default";
	pinctrl-0 = <&gsw_pins>;
};""",
        "spi_extra": "\t\tnum-cs = <2>;\n",
        "pinctrl": """&pinctrl {
\tstate_default: pin_state {
\t\tpleds {
\t\t\tgroups = "ephy led", "wled";
\t\t\tfunction = "led";
\t\t};

\t\tgpios {
\t\t\tgroups = "uartf";
\t\t\tfunction = "gpio";
\t\t};
\t};

\t/* gsw_pins 在 mainline 里是板级 dts 自己定义的 label（mt7620.dtsi 没有），照 rfb 抄 */
\tgsw_pins: gsw_pins {
\t\tmdio {
\t\t\tgroups = "mdio";
\t\t\tfunction = "mdio";
\t\t};

\t\trgmii1 {
\t\t\tgroups = "rgmii1";
\t\t\tfunction = "rgmii1";
\t\t};

\t\trgmii2 {
\t\t\tgroups = "rgmii2";
\t\t\tfunction = "rgmii2";
\t\t};
\t};
};""",
    },
}

TMPL = """// SPDX-License-Identifier: GPL-2.0
/*
 * OrayBox {MODEL}-{HW} ({SOC}) — 由 oraybox/tools/gen-mtmips-dts.py 自动派生，未上机验证
 *
 * 证据来源: {SRC_NOTE}
 *   RAM      : {RAM}
 *   console  : {CONSOLE}
 *   MAC      : {MACNOTE}
 *   按键/LED : {GPIONOTE}
 *
 * 分区表照抄固件 DTB；u-boot 镜像必须小于 u-boot 分区，CI 里有体积守卫。
 */

/dts-v1/;

#include "{INCLUDE}"

/ {{
	compatible = "oraybox,{LOW}", "{SOC_COMPAT}";
	model = "OrayBox {MODEL}-{HW}";

	aliases {{
		serial0 = &{UART};
		spi0 = &spi0;
	}};

	chosen {{
		stdout-path = &{UART};
	}};
}};

&{UART} {{
	status = "okay";
}};

{PINCTRL}

&spi0 {{
	status = "okay";
{SPI_EXTRA}
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

{ETH}
"""

PART = """\t\t\tpartition@{OFF} {{
\t\t\t\tlabel = "{LABEL}";
\t\t\t\treg = <0x{OFF} 0x{SIZE}>;{RO}
\t\t\t}};"""


def parse_kernel_dts(path):
    txt = open(path, errors="replace").read()
    pm = O.phandle_map(txt)
    # 用缩进栈走节点，不按 "partition@" + 固定制表符数匹配：NAND 的 dts 多一层嵌套，
    # 老写法整块读不到分区（A500/P5/X5-6256/7256 全中），X3A 里原厂还把节点名拼成了 "artition@fe0000"。
    parts = []
    for _, p in dtsread.walk_nodes(txt):
        reg = p.get("reg")
        if "label" in p and reg and len(reg) == 2:
            parts.append({"label": p["label"], "offset": f"{reg[0]:x}", "size": f"{reg[1]:x}"})
    keys = []
    for mm in re.finditer(r'label\s*=\s*"([^"]+)"\s*;\s*gpios\s*=\s*<\s*0x([0-9a-f]+)\s+0x([0-9a-f]+)', txt):
        node = pm.get(mm.group(2), "")
        bank = re.search(r"(?:bank|gpio)(\d+)", node)
        keys.append({"label": mm.group(1), "ctrl": (bank.group(1) if bank else "0"), "pin": int(mm.group(3), 16)})
    mac = dtsread.mac_cells(txt)[0]
    macnote = "未找到"
    if mac:
        props, off = mac[0]
        reg = props.get("reg") or []
        macnote = props.get("label", "?") + (f"@{hex(reg[0])}" if reg else "") + f" +0x{off:x}"
    mem = re.search(r"memory[@\w-]*\s*\{[^}]*?reg\s*=\s*<\s*0x[0-9a-f]+\s+0x([0-9a-f]+)", txt, re.S)
    boots = re.search(r'bootargs\s*=\s*"([^"]*)"', txt)
    return {
        "parts": parts, "keys": keys, "mac": macnote,
        "ram": f"{int(mem.group(1), 16) // (1024 * 1024)}MB" if mem else "未写明（u-boot 运行时探测）",
        "console": (boots.group(1) if boots else "115200"),
    }


def render(soc, model, hw, info, src_note):
    cells, seen = [], set()
    for p in info["parts"]:
        off, size = p["offset"].lstrip("0") or "0", int(p["size"], 16)
        if size == 0 or off in seen:      # 零大小/重偏移（厂商的 fullflash）会让 dtc 报 duplicate_node_names
            continue
        seen.add(off)
        ro = "  /* 只读 */" if p["label"] in ("u-boot", "factory") else ""
        cells.append(PART.format(OFF=off, LABEL=p["label"], SIZE=hex(size)[2:], RO=ro))
    gpio = ", ".join(f"{k['label']}=&gpio{k['ctrl']} {k['pin']}" for k in info["keys"]) or "无 DTB 依据"
    c = SOC[soc]
    return TMPL.format(
        MODEL=model, HW=hw, LOW=f"{model}-{hw}".lower(), SOC=soc, SRC_NOTE=src_note,
        RAM=info["ram"], CONSOLE=info["console"], MACNOTE=info["mac"], GPIONOTE=gpio,
        INCLUDE=c["include"], SOC_COMPAT=c["soc_compat"], UART=c["uart"], SPI_EXTRA=c["spi_extra"],
        PINCTRL=c["pinctrl"],
        ETH=c["eth"], PARTS="\n\n".join(cells),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default="data/index.json")
    ap.add_argument("--soc", action="append", default=[])
    args = ap.parse_args()

    idx = json.load(open(args.index))
    by = O.group_models([m for m in idx.values() if m.get("ok")])
    for soc in (args.soc or list(SOC)):
        c = SOC[soc]
        base_dc = open(c["base_defconfig"]).read()
        todo, donors = [], []
        for (mdl, hw), recs in sorted(by.items()):
            if O.detect_soc(max(recs, key=lambda x: bool(x.get("dtbs")))) != soc:
                continue
            m = max(recs, key=lambda x: (bool(x.get("partitions")), bool(x.get("dtbs"))))
            dts = O.dts_path_of(m)
            info = parse_kernel_dts(dts) if dts else None
            todo.append((mdl, hw, m, info))
            if info and info["parts"]:
                donors.append((mdl, hw, info, f"内核 DTB 直读（{m['file']}）"))
        if not donors:
            print(f"{soc}: 没有任何 DTB，跳过")
            continue
        n = 0
        for mdl, hw, m, info in todo:
            if info and info["parts"]:
                note = f"内核 DTB 直读（{m['file']}）"
            else:
                fam = re.match(r"[A-Za-z]+\d*", mdl)
                dn = next((d for d in donors if fam and d[0].startswith(fam.group())), donors[0])
                info, note = dict(dn[2]), f"分区/GPIO 继承 {dn[0]}/{dn[1]}（本板固件无 DTB），未实测"
            outdir = os.path.join(c["out"], f"{mdl}_{hw}")
            os.makedirs(outdir, exist_ok=True)
            name = f"{c['dts_prefix']}{mdl}-{hw}".lower()
            open(os.path.join(outdir, name + ".dts"), "w").write(render(soc, mdl, hw, info, note))
            dc = re.sub(r'CONFIG_DEFAULT_DEVICE_TREE="[^"]*"', f'CONFIG_DEFAULT_DEVICE_TREE="{name}"', base_dc)
            open(os.path.join(outdir, f"{c['dcfg_prefix']}{mdl}_{hw}".lower() + "_defconfig"), "w").write(dc)
            n += 1
        print(f"{soc}: 生成 {n} 块板 -> {c['out']}")


if __name__ == "__main__":
    main()
