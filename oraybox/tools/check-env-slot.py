#!/usr/bin/env python3
"""断言：每块板的 CONFIG_ENV_OFFSET + CONFIG_ENV_SIZE 必须整块落在自己的 env 槽里，
且绝不越过 factory（MAC/无线校准），否则 env save 会刷坏校准区。"""
import glob
import os
import re
import sys

bad = 0
root = sys.argv[1] if len(sys.argv) > 1 else "oraybox"
dirs = sorted(glob.glob(f"{root}/mt76*/boards/*/") + glob.glob(f"{root}/mt76*/oraybox-*/"))
for d in dirs:
    cfgs = glob.glob(os.path.join(d, "*_defconfig"))
    dtss = glob.glob(os.path.join(d, "*.dts"))
    if len(dtss) == 0:
        print(f"-- {d.rstrip('/')} 是模板目录（只有 defconfig，供生成器当基线），跳过")
        continue
    if len(cfgs) != 1 or len(dtss) != 1:
        print(f"!! {d}: 板目录需要恰好 1 份 defconfig + 1 份 dts（实际 {len(cfgs)}/{len(dtss)}）")
        bad += 1
        continue
    cfg, dts = cfgs[0], dtss[0]
    c, t = open(cfg).read(), open(dts).read()
    mo, ms = re.search(r"CONFIG_ENV_OFFSET=(0x[0-9a-f]+)", c), re.search(r"CONFIG_ENV_SIZE=(0x[0-9a-f]+)", c)
    if not (mo and ms):
        print(f"!! {d}: defconfig 缺 CONFIG_ENV_OFFSET/SIZE")
        bad += 1
        continue
    off, size = int(mo.group(1), 16), int(ms.group(1), 16)
    parts = {
        lab: (int(o, 16), int(s, 16))
        for lab, o, s in re.findall(r'label = "([^"]+)";\s*\n\s*reg = <0x([0-9a-f]+) 0x([0-9a-f]+)>', t)
    }
    ub = parts.get("u-boot", (0, 0x30000))
    fac = parts.get("factory")
    env = parts.get("u-boot-env") or parts.get("kpanic")
    errs = []
    if off < ub[0] + ub[1]:
        errs.append(f"ENV_OFFSET {hex(off)} 落在 u-boot 分区内（u-boot 结束于 {hex(ub[0]+ub[1])}）")
    if env and not (env[0] <= off and off + size <= env[0] + env[1]):
        errs.append(f"env {hex(off)}+{hex(size)} 超出 {hex(env[0])}+{hex(env[1])} 这个槽")
    if fac and off + size > fac[0]:
        errs.append(f"env 尾部 {hex(off+size)} 越过 factory {hex(fac[0])}，env save 会刷坏校准区")
    if errs:
        bad += 1
        print(f"!! {os.path.basename(d.rstrip('/'))}: " + "；".join(errs))
    else:
        print(f"OK {os.path.basename(d.rstrip('/')):<16} env {hex(off)}+{hex(size)} 槽 {env[0] and hex(env[0])} factory {fac and hex(fac[0])}")
print(f"\n{len(dirs)} 块板检查完，问题 {bad} 块")
sys.exit(1 if bad else 0)
