#!/bin/bash
declare -r output_dir="/usr/local/psitejob/goaccess"
declare -r log_dir="/var/log/stuhrs_dk/web"

echo "$(date) - Generating GoAccess report..."
goaccess -o "${output_dir}/index.html" -f "${log_dir}/access.log" "${log_dir}/access.log.1" --log-format=COMBINED
echo "$(date) - Report generated!"