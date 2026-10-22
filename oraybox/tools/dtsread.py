#!/usr/bin/env python3
"""dtc -O dts 输出的最小解析：按制表符缩进维护节点栈，取 label/phandle/reg。

只用来解决一件事——把内核 dts 里的 mtd-mac-address = <&phandle off> 还原成
"MAC 到底在哪块分区、哪个偏移"。跨节点的贪婪正则会串到别的分区上，所以必须按嵌套走。
"""
import re

_PROP = re.compile(r"\s*([\w,\-.]+)\s*=\s*(.+?);\s*$")
_NODE = re.compile(r"\s*([\w,@.\-]+|/)\s*\{\s*$")
_CLOSE = re.compile(r"\s*\}\s*;\s*$")


def walk_nodes(text):
    """返回 [(path, props)]，props 里 label 是字符串，phandle 是无 0x 的小写十六进制，reg 是列表"""
    stack = []
    out = []
    for ln in text.splitlines():
        if not ln.strip():
            continue
        ind = len(ln) - len(ln.lstrip("\t"))
        while stack and stack[-1][0] >= ind:
            stack.pop()
        m = _NODE.match(ln)
        if m:
            stack.append((ind, m.group(1)))
            out.append(("/".join(n for _, n in stack), {}))
            continue
        if _CLOSE.match(ln):
            if stack:
                stack.pop()
            continue
        p = _PROP.match(ln)
        if not p or not out:
            continue
        key, val = p.group(1), p.group(2)
        props = out[-1][1]
        if key == "label" and "label" not in props:
            props["label"] = val.strip('" ')
        elif key in ("phandle", "linux,phandle"):
            hx = re.findall(r"0x([0-9a-fA-F]+)", val)
            if hx:
                props["phandle"] = hx[-1].lower()
        elif key == "reg":
            props["reg"] = [int(x, 16) for x in re.findall(r"0x([0-9a-fA-F]+)", val)]
    return out


def by_phandle(nodes):
    return {p["phandle"]: p for _, p in nodes if "phandle" in p}


def mac_cells(text):
    """[(分区props, 分区内偏移)]，按文件里出现顺序；解析不出 phandle 的会被跳过并记入 missing"""
    nodes = walk_nodes(text)
    ph = by_phandle(nodes)
    hits, missing = [], []
    for m in re.finditer(r"mtd-mac-address(?:-increment)?\s*=\s*<\s*0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)\s*>", text):
        props = ph.get(m.group(1).lower())
        if props is None:
            missing.append(m.group(1).lower())
        else:
            hits.append((props, int(m.group(2), 16)))
    return hits, missing


def describe(props, off):
    reg = props.get("reg") or []
    base = reg[0] if reg else None
    lab = props.get("label", "?")
    return f"{lab}" + (f"@{hex(base)}" if base is not None else "") + f" +0x{off:x}"
