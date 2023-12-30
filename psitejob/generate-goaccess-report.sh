#!/bin/bash
declare -r output_dir="/usr/local/stuhrs_dk/web/goaccess/"
declare -r log_dir="/var/log/stuhrs_dk/web/"

echo "Generating GoAccess report..."
zcat -f "${log_dir}/access.log.*.gz" | goaccess -o "${output_dir}/index.html"  "${log_dir}/access.log" --log-format=COMBINED -
echo "Report generated!"