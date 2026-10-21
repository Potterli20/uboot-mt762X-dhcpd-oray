# 值得回推上游的两个问题

来源：做 OrayBox 板级支持时实测踩到。**目前只是本地整理，没有代你提交**——
在 Yuzhii0718/uboot-mt7621-dhcpd 与 DragonBluep/uboot-mt7621 公开发声需要本人确认。

## 1. `customize.sh` 里 `[ -n $(...) ]` 未加引号（真 bug）

DDR3-512MiB 分支本该把 1200 MT/s 降到上限 1066，但条件是未加引号的命令替换：

```sh
if [ -n $(cat ${DEFCONFIG} | grep MT7621_DRAM_FREQ_1200_LEGACY) ]; then
```

`grep` 返回多行时 `[` 直接报错、条件恒假，降级静默不生效：

```
$ if [ -n $(printf 'A=y\nB=y\n') ]; then echo true; else echo false; fi
bash: [: A=y: 需要二元运算符
false
```

复现：`--ddrparam DDR3-512MiB --ramfreq 1200` 构建，检查生成的 defconfig 里
`MT7621_DRAM_FREQ_1200_LEGACY` 是否还在（在 = 降级没发生）。
修法见 `01-quote-test.patch`（本仓库已应用）。

## 2. `build.sh validate()` 不校验 `--ddrparam` 取值（加固建议）

`customize.sh` 用 `case "$8"` 匹配白名单，**没有 default 分支**：写错值（例如 `DDR3-256M`、
`DDR3-256MB`）时不会报错，只是不写任何 `CONFIG_MT7621_DRAM_*_LEGACY`，于是落回 Kconfig 默认
（DDR2 128MB）—— 编出来的固件在新板子上可能直接点不亮，而且没有任何提示。

建议 validate() 里加白名单检查，见 `02-ddrparam-whitelist.patch`。
本仓库的 CI（`build-oraybox-all.yml`）另外加了产物体积守卫，防止镜像超出 u-boot 分区。


## 要提交的话（需要你来点）

发 issue/PR 走 GitHub API，需要授权；本环境里 `gh` 未登录、也没有 `GITHUB_TOKEN`，
SSH key 只能推 `Potterli20/*` 的 git，不能替你在别人仓库发帖。两个 issue 正文已写成
`issue-1-quote-test.md` / `issue-2-ddrparam-whitelist.md`，配套 patch 在同目录：

```bash
gh auth login                      # 或 export GITHUB_TOKEN=...
bash oraybox/upstream/submit.sh           # dry-run 预览
bash oraybox/upstream/submit.sh --yes     # 真发到 Yuzhii0718/uboot-mt7621-dhcpd
bash oraybox/upstream/submit.sh --both --yes   # 连 DragonBluep/uboot-mt7621 一起（第三方仓库，自行判断）
```
