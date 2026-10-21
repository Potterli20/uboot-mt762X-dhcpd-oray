#!/usr/bin/env bash
# 把 oraybox/upstream/ 里两个 issue 提交到上游仓库。默认 dry-run，加 --yes 才真发。
#   需要：gh auth login（或 export GITHUB_TOKEN=...）
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOS=("Yuzhii0718/uboot-mt7621-dhcpd")
[ "${1:-}" = "--both" ] && { REPOS=("Yuzhii0718/uboot-mt7621-dhcpd" "DragonBluep/uboot-mt7621"); shift; }
GO=0
[ "${1:-}" = "--yes" ] && GO=1

if ! command -v gh >/dev/null; then echo "!! 没装 gh CLI"; exit 2; fi
if ! gh auth status >/dev/null 2>&1; then
  echo "!! gh 未登录：先跑 gh auth login（或 export GITHUB_TOKEN=...）"; exit 2
fi

for repo in "${REPOS[@]}"; do
  for f in "$HERE"/issue-*.md; do
    title=$(sed -n 's/^标题：//p' "$f" | head -1)
    body=$(sed '1,2d' "$f")
    echo "=== [$repo] $title"
    echo "$body" | head -3
    echo "..."
    if [ "$GO" = 1 ]; then
      gh issue create --repo "$repo" --title "$title" --body "$body"
    else
      echo "    (dry-run，加 --yes 才真发)"
    fi
  done
done
[ "$GO" = 1 ] || echo "\n以上只是预览。确认无误后：bash oraybox/upstream/submit.sh --yes"
