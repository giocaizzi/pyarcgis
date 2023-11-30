#!/bin/sh

# Redirect output to stderr.
# exec 1>&2

# Check for notebook cell changes.
git diff --cached --name-only --diff-filter=d | while read filename; do
  if [ "${filename##*.}" = "ipynb" ]; then
    nbdiff "${filename}" | grep -q '^+++ '
    if [ $? -eq 1 ]; then
      echo "No changes in code cells detected in ${filename}. Skipping commit."
      exit 1
    fi
  else
    echo "No notebook files detected in commit. Skipping pre-commit hook."
    exit 0
  fi
done