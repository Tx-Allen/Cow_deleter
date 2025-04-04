def sort_lines_by_prefix(filepath, output_path):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    parsed_lines = []
    for line in lines:
        key = line.split(' ')[0]
        rest = ' '.join(line.split(' ')[1:])
        if '-' in key:
            part1, part2 = key.split('-')
            try:
                parsed_lines.append(((int(part1), int(part2)), line.strip()))
            except ValueError:
                continue  # 跳过无法解析的行

    sorted_lines = sorted(parsed_lines, key=lambda x: (x[0][0], x[0][1]))
    sorted_content = [line for _, line in sorted_lines]

    with open(output_path, 'w') as f:
        for line in sorted_content:
            f.write(line + '\n')

    print(f"已保存排序结果到：{output_path}")

# 示例用法
input_file = "val380 (copy).txt"
output_file = "val380_sorted.txt"
sort_lines_by_prefix(input_file, output_file)
