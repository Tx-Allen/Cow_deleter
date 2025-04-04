def extract_line_map_with_index(filepath):
    """返回一个字典：key是x-y，value是(行号, 内容)"""
    line_map = {}
    with open(filepath, 'r') as f:
        for idx, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            key = line.split(' ')[0]
            line_map[key] = (idx + 1, line)  # 行号从1开始
    return line_map

def compare_files_with_summary(file1, file2, result_file):
    map1 = extract_line_map_with_index(file1)
    map2 = extract_line_map_with_index(file2)

    keys1 = set(map1.keys())
    keys2 = set(map2.keys())

    all_keys = sorted(keys1 | keys2, key=lambda k: tuple(map(int, k.split('-'))))

    match_count = 0
    mismatch_details = []

    with open(result_file, 'w') as f:
        f.write(f"{'KEY':<10} {'File1_Line':<12} {'File2_Line':<12} Status\n")
        f.write("-" * 50 + "\n")

        for key in all_keys:
            info1 = map1.get(key)
            info2 = map2.get(key)

            if info1 and info2:
                line1_num, line1 = info1
                line2_num, line2 = info2
                if line1 == line2:
                    match_count += 1
                    f.write(f"{key:<10} {line1_num:<12} {line2_num:<12} ✅ Match\n")
                else:
                    mismatch_details.append((key, line1_num, line2_num, line1, line2))
                    f.write(f"{key:<10} {line1_num:<12} {line2_num:<12} ❌ Mismatch\n")
            elif info1:
                mismatch_details.append((key, info1[0], '-', info1[1], ''))
                f.write(f"{key:<10} {info1[0]:<12} {'-':<12} ⚠️ Only in file1\n")
            elif info2:
                mismatch_details.append((key, '-', info2[0], '', info2[1]))
                f.write(f"{key:<10} {'-':<12} {info2[0]:<12} ⚠️ Only in file2\n")

        # 输出统计信息
        f.write("\n")
        f.write(f"✅ 总共匹配成功数量: {match_count}\n")
        if mismatch_details:
            f.write(f"❌ 匹配失败数量: {len(mismatch_details)}\n")
            f.write("\n失败详情:\n")
            for key, line1_num, line2_num, line1, line2 in mismatch_details:
                f.write(f"\n[Key: {key}] File1_Line {line1_num} vs File2_Line {line2_num}\n")
                f.write(f"  File1: {line1}\n")
                f.write(f"  File2: {line2}\n")

if __name__ == "__main__":
    original_file = "train380_sorted.txt"
    sorted_file = "val380_sorted.txt"
    result_output = "result.txt"

    compare_files_with_summary(original_file, sorted_file, result_output)
    print(f"比较完成，结果已保存至 {result_output}")
