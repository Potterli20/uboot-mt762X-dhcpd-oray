#!/usr/bin/env python3
"""抓串口开机横幅，补 defconfig 里固件给不出的 cpufreq / ramfreq / ddrparam。

用法：接好 TTL 串口，开机后立刻跑
    python3 serial_probe.py /dev/ttyUSB0 --seconds 25
纯 stdlib（termios），不需要 pyserial。结果写 data/serial-probe.json。
"""
import argparse
import json
import os
import re
import sys
import termios
import time

TTY_ATTRS = [(termios.IGNBRK | termios.BRKINT | termios.PARMRK | termios.ISTRIP
              | termios.INLCR | termios.IGNCR | termios.ICRNL | termios.IXON, 0),
             (0, 0),
             (0, termios.CS8 | termios.CREAD | termios.CLOCAL),
             (0, 0)]

CPU_RE = re.compile(r"(CPU|Processor)[:\s]+[^0-9]*(\d{3})\s*MHz", re.I)
DRAM_RE = re.compile(r"DRAM[:\s]+(?:.*?(\d{3,4})\s*MHz)?(?:.*?(\d+)\s*MB)?", re.I)
MB_RE = re.compile(r"(\d+)\s*MB", re.I)
MHZ_RE = re.compile(r"(\d{3,4})\s*MHz", re.I)
DDR_RE = re.compile(r"(DDR[23])", re.I)

# 参考仓库 --ddrparam 的取值，按容量映射（ddrtype 由串口横幅决定）
DDRPARAM = {("DDR2", 64): "DDR2-64MiB", ("DDR2", 128): "DDR2-128MiB",
            ("DDR3", 128): "DDR3-128MiB", ("DDR3", 256): "DDR3-256MiB", ("DDR3", 512): "DDR3-512MiB"}


def open_tty(path, baud):
    fd = os.open(path, os.O_RDONLY | os.O_NOCTTY)
    a = termios.tcgetattr(fd)
    for i, (cur, new) in enumerate(TTY_ATTRS):
        a[i] = (a[i] & ~cur) | new if isinstance(cur, int) else a[i]
    speed = {9600: termios.B9600, 19200: termios.B19200, 38400: termios.B38400,
             57600: termios.B57600, 115200: termios.B115200, 921600: termios.B921600}[baud]
    a[4] = a[5] = speed
    a[6][termios.VMIN] = 0
    a[6][termios.VTIME] = 1
    termios.tcsetattr(fd, termios.TCSANOW, a)
    termios.tcflush(fd, termios.TCIFLUSH)
    return fd


def parse(text):
    out = {"raw_lines": [l.strip() for l in text.splitlines() if l.strip()][:200]}
    m = CPU_RE.search(text)
    if m:
        out["cpufreq"] = int(m.group(2))
    md = DRAM_RE.search(text)
    if md:
        seg = text[md.start(): md.start() + 120]
        fr = MHZ_RE.search(seg)
        mb = MB_RE.search(seg)
        if fr:
            out["ramfreq"] = int(fr.group(1))
        if mb:
            out["ram_mb"] = int(mb.group(1))
    dd = DDR_RE.search(text)
    if dd:
        out["ddr_type"] = dd.group(1).upper()
    elif out.get("ram_mb"):
        # 横幅不印 DDR 类型：MT7621 上 ≥128MB 基本是 DDR3，≤64MB 才可能是 DDR2
        out["ddr_type"] = "DDR2" if out["ram_mb"] <= 64 else "DDR3"
        out["ddr_type_guessed"] = True
    if out.get("ddr_type") and out.get("ram_mb"):
        out["ddrparam"] = DDRPARAM.get((out["ddr_type"], out["ram_mb"]), "")
        if out.get("ddr_type_guessed"):
            out["ddrparam_note"] = f"按 {out['ddr_type']}+{out['ram_mb']}MB 猜的，颗粒不明时用 --ddr-type 覆盖"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tty", nargs="?", default="/dev/ttyUSB0")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--seconds", type=float, default=20)
    ap.add_argument("--out", default="data/serial-probe.json")
    ap.add_argument("--ddr-type", choices=["DDR2", "DDR3", "ddr2", "ddr3"], help="覆盖横幅猜出来的颗粒类型")
    ap.add_argument("--file", help="不接串口，直接解析已保存的日志文件")
    args = ap.parse_args()

    if args.file:
        text = open(args.file, errors="replace").read()
    else:
        if not os.path.exists(args.tty):
            sys.exit(f"找不到 {args.tty}；或者用 --file 解析已存的串口日志")
        fd = open_tty(args.tty, args.baud)
        print(f"读 {args.tty} @{args.baud} {args.seconds}s，请在另一端重启设备…", flush=True)
        buf, t0 = [], time.time()
        while time.time() - t0 < args.seconds:
            try:
                chunk = os.read(fd, 512)
            except BlockingIOError:
                chunk = b""
            if chunk:
                s = chunk.decode("latin1")
                buf.append(s)
                print(s, end="", flush=True)
            else:
                time.sleep(0.05)
        os.close(fd)
        text = "".join(buf)

    res = parse(text)
    if args.ddr_type:
        res["ddr_type"] = args.ddr_type.upper()
        res["ddrparam"] = DDRPARAM.get((res["ddr_type"], res.get("ram_mb", 0)), "")
    print("\n--- 解析结果 ---")
    for k in ("cpufreq", "ramfreq", "ram_mb", "ddr_type", "ddrparam"):
        print(f"  {k:<9}= {res.get(k, '未识别')}")
    if res.get("cpufreq") and res.get("ddrparam"):
        print(f"\n可直接填进 defconfig：\n  --cpufreq {res['cpufreq']}\n  --ramfreq {res.get('ramfreq', 1200)}"
              f"\n  --ddrparam {res['ddrparam']}")
    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        json.dump(res, open(args.out, "w"), ensure_ascii=False, indent=1)
        print(f"-> {args.out}")


if __name__ == "__main__":
    main()
