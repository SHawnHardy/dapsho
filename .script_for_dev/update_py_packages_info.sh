#!/usr/bin/env bash
PRJPATH="$(realpath "$(dirname "$(dirname "$0")")")"
cd "${PRJPATH}/dapsho" || exit
printf "# Python packages\n\nGenerate using \"pip-licenses\".\n\n-----\n" >"${PRJPATH}/THIRDPARTY_LICENSE/PY_PACKAGES.md"
echo "" >>"${PRJPATH}/THIRDPARTY_LICENSE/PY_PACKAGES.md"

reqs=$(pipreqs --mode no-pin --print | sort -u | tr '\n' ' ')
echo "$reqs"
echo "$reqs" | xargs pip-licenses -a -d -u -f markdown -p >>"${PRJPATH}/THIRDPARTY_LICENSE/PY_PACKAGES.md"
