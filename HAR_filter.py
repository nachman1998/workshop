import json
import ipaddress
import csv
import argparse

def har_to_csv(har_path, csv_path):
    """
    Extract server IPs from HAR and write them to CSV
    without a header.
    Format:
    src_ip,src_port,dst_ip,dst_port,proto
    """

    with open(har_path, "r", encoding="utf-8") as f:
        har_data = json.load(f)

    entries = har_data.get("log", {}).get("entries", [])
    seen_ips = set()

    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        for entry in entries:
            server_ip = entry.get("serverIPAddress")

            if not server_ip:
                continue

            try:
                clean_ip = server_ip.strip("[]")

                if clean_ip in seen_ips:
                    continue

                seen_ips.add(clean_ip)
                writer.writerow([
                    clean_ip,    # src_ip
                    str("None"), # src_port
                    str("None"), # dst_ip
                    str("None"), # dst_port
                    str("None")  # proto
                ])

            except ValueError:
                pass



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='filter.'
    )
    parser.add_argument('--input',    required=True,                  help='Path to HAR file')
    parser.add_argument('--out_name', required=False, default="filter_HAR", help='output CSV file name')
    args = parser.parse_args()

    har_to_csv(args.input, args.out_name)