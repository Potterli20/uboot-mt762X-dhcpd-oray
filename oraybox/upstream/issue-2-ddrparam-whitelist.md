标题：build.sh: validate() should reject unknown --ddrparam values

正文：

`customize.sh` 用 `case "$8" in ... esac` 把 `--ddrparam` 映射到 `CONFIG_MT7621_DRAM_*_LEGACY`，
但**没有 default 分支**。所以传错值（`DDR3-256M`、`DDR3-256MB` 这类手误）时不会有任何提示，
只是一条 `CONFIG_MT7621_DRAM_*_LEGACY` 都不写，最终落回 Kconfig 默认（DDR2 128MiB）。

后果是编出来的固件在 DDR3 板子上可能根本点不亮，而构建全程"成功"。
`build.sh` 的 `validate()` 已经检查了 flash 类型、ramfreq 白名单、GPIO 范围、baudrate，
唯独漏了 ddrparam。

建议在 `validate()` 里补一段白名单检查（取值抄 `customize.sh` 的 case 标签）：

```sh
case "${DDRPARM}" in
  DDR2-64MiB|DDR2-128MiB|DDR2-W9751G6KB-64MiB-1066MHz|\
  DDR2-W971GG6KB25-128MiB-800MHz|DDR2-W971GG6KB18-128MiB-1066MHz|\
  DDR3-128MiB|DDR3-256MiB|DDR3-512MiB|DDR3-128MiB-KGD) :;;
  *) echo "Error: unknown ddrparam '${DDRPARM}' (see customize.sh case list)"; exit 1;;
esac
```

更彻底的做法是给 `customize.sh` 的 case 加 default 并 `exit 1`，这样两处都不会静默。
补丁见附件 `02-ddrparam-whitelist.patch`。
