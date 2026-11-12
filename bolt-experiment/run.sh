#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for x in clang llvm-bolt perf2bolt perf python3 taskset; do command -v "$x" >/dev/null || { echo "Missing dependency: $x" >&2; exit 1; }; done
: "${SQLITE_SOURCE:?Set SQLITE_SOURCE to the directory containing sqlite3.c and shell.c}"
mkdir -p build results
clang -O2 -g -fno-omit-frame-pointer -Wl,--emit-relocs "$SQLITE_SOURCE/shell.c" "$SQLITE_SOURCE/sqlite3.c" -lpthread -ldl -lm -o build/sqlite-baseline
python3 workload.py generate results/workload.sql
build/sqlite-baseline results/input.db < results/workload.sql > results/reference.txt
perf record -e cycles:u -j any,u -o results/perf.data -- build/sqlite-baseline results/input.db < results/workload.sql > /dev/null
perf2bolt build/sqlite-baseline -p results/perf.data -o results/profile.fdata
llvm-bolt build/sqlite-baseline -o build/sqlite-bolt -data=results/profile.fdata -reorder-blocks=ext-tsp -reorder-functions=hfsort+ -split-functions -split-all-cold -dyno-stats
python3 workload.py run
