#!/bin/bash
# This script normalizes file paths by removing the redline/ prefix. This is a different comment.

find . -type f -print0 | while IFS= read -r -d $'\0' file; do
  sed -i '' '/^\(import\|from\)/!s|redline/stuff/||g' "$file"
done
