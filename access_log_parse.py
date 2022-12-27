from collections import Counter
import re
import json
import argparse
from os import listdir
from os.path import isfile, join

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", required=False, default="access.log")
parser.add_argument("-d", "--directory", required=False)
args = parser.parse_args()


LINE_REGEX = r'(\d+\.\d+\.\d+\.\d+)[^\[]+\[(.+)\]\s+\"([A-Z]+)\s+\S+\s+\S+\s(\d{3})\s+\S+\s+"([^"]+)".*\s(\d+)$'


def line_to_dict(line):
    m = re.search(LINE_REGEX, line)
    if m is not None:
        return {'ip': m.group(1), 'datetime': m.group(2), 'method': m.group(3), 'status_code': m.group(4),
                'referrer_url': m.group(5), 'duration': int(m.group(6))}
    else:
        return None


filenames = []
if args.directory:
    for f in listdir(args.directory):
        path = join(args.directory, f)
        if isfile(path) and path.endswith('.log'):
            filenames.append(path)
else:
    filenames = [args.file]

lines = []
for filepath in filenames:
    read_file = open(filepath, 'r')
    file_lines = read_file.read().split('\n')
    for line in file_lines:
        lines.append(line)

parsed_lines = list(filter(lambda v: v is not None, map(line_to_dict, lines)))
quantity_of_requests = len(parsed_lines)
methods_quantity = dict(Counter(list(map(lambda v: v["method"], parsed_lines))))
ips_counter = Counter(list(map(lambda v: v["ip"], parsed_lines)))
top_3_ips = list(map(lambda v: v[0], ips_counter.most_common(3)))
parsed_lines.sort(key=lambda v: v["duration"])
top_3_longest_requests = parsed_lines[-3:]

output = {"quantity_of_requests": quantity_of_requests, "methods_quantity": methods_quantity, "top_3_ips": top_3_ips,
          "top_3_longest_requests": top_3_longest_requests}

output_json = json.dumps(output, indent=2)
with open("output.json", "w") as file:
    file.write(output_json)
print(output_json)
