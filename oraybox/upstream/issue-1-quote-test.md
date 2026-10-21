标题：customize.sh: unquoted command substitution silently disables the DDR3-512MiB frequency cap

正文：

`customize.sh` 的 DDR3-512MiB 分支想把 1200 MT/s 降到该容量的上限 1066，但判断条件里的命令替换没有加引号：

```sh
if [ -n $(cat ${DEFCONFIG} | grep MT7621_DRAM_FREQ_1200_LEGACY) ]; then
	echo "The max DRAM speed for 512 MiB RAM is 1066 MT/s"
	sed -i 's/MT7621_DRAM_FREQ_1200_LEGACY/MT7621_DRAM_FREQ_1066_LEGACY/' ${DEFCONFIG}
fi
```

`grep` 返回两行以上时 `[` 直接报错、条件恒假，降级不会发生：

```
$ if [ -n $(printf 'A=y\nB=y\n') ]; then echo true; else echo false; fi
bash: [: A=y: 需要二元运算符
false
```

复现：用 `--ddrparam DDR3-512MiB --ramfreq 1200` 构建，然后看生成的 defconfig 里
`CONFIG_MT7621_DRAM_FREQ_1200_LEGACY` 是否还在（还在就说明降级没跑）。
只要 `${DEFCONFIG}` 里有两行匹配（例如同时存在别的 `MT7621_DRAM_FREQ_1200_LEGACY` 引用）就会触发。

建议改成：

```sh
if [ -n "$(cat ${DEFCONFIG} | grep MT7621_DRAM_FREQ_1200_LEGACY)" ]; then
```

补丁见附件 `01-quote-test.patch`（我们在自己的分支 `Potterli20/uboot-mt762X-dhcpd-oray` 上已应用）。
