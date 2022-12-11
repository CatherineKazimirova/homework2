import subprocess
from collections import Counter
import re
from datetime import datetime

LINE_REGEX = r'^([\w\.]+)\s+\S+\s+(\d+[,\.]\d+)\s+(\d+[,\.]\d+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s(.+)$'


def line_to_dict(line):
    m = re.search(LINE_REGEX, line)
    if m is not None:
        return {'user': m.group(1), 'cpu': m.group(2), 'mem': m.group(3), 'cmd': m.group(4)}
    else:
        return None


ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
lines = ps.split('\n')
parsed_lines = list(filter(lambda v: v is not None, map(line_to_dict, lines)))


def get_user(parsed_line):
    return '\'{}\''.format(parsed_line['user'])


def count_memory(all_processes):
    total = 0.0
    for process in all_processes:
        total += float(process['mem'])

    return total


def count_cpu(all_processes):
    total = 0.0
    for process in all_processes:
        total += float(process['cpu'])

    return total


users_all = list(map(get_user, parsed_lines))
system_users = ", ".join(set(users_all))
user_counter = Counter(users_all)
total_memory = count_memory(parsed_lines)
total_cpu = count_cpu(parsed_lines)
parsed_lines.sort(key=lambda v: v['mem'])
most_expensive_by_memory = parsed_lines[-1]['cmd'][:20]
parsed_lines.sort(key=lambda v: v['cpu'])
most_expensive_by_cpu = parsed_lines[-1]['cmd'][:20]
current_date = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

with open(current_date + '-scan' + '.txt', 'w') as file:
    print('Отчёт о состоянии системы:', file=file)
    print('Пользователи системы: {}'.format(system_users), file=file)
    print('Процессов запущено: {}'.format(len(list(parsed_lines))), file=file)
    print('Пользовательских процессов:', file=file)
    for user_name in user_counter.keys():
        print('{}: {}'.format(user_name, user_counter[user_name]), file=file)
    print('Всего памяти используется: {}%'.format(round(total_memory, 1)), file=file)
    print('Всего CPU используется: {}%'.format(round(total_cpu, 1)), file=file)
    print('Больше всего памяти использует: {}'.format(most_expensive_by_memory), file=file)
    print('Больше всего CPU использует: {}'.format(most_expensive_by_cpu), file=file)
