import os
import tkinter as tk
from tkinter import Scrollbar, Listbox
from PIL import Image, ImageTk

# 配置路径
image_folder = "images"
txt_file_path = "train380_sorted_copy.txt"
image_ext = ".png"

# 读取文本内容
with open(txt_file_path, 'r') as f:
    all_lines = [line.strip() for line in f if line.strip()]

lines = all_lines.copy()
keys = [line.split(' ')[0] for line in lines]
current_index = 0
undo_stack = []


def update_listbox():
    image_listbox.delete(0, tk.END)
    for k in keys:
        image_listbox.insert(tk.END, k)


def log_message(msg):
    output_text.config(state=tk.NORMAL)
    output_text.insert(tk.END, msg + '\n')
    output_text.see(tk.END)
    output_text.config(state=tk.DISABLED)


def show_image(index):
    global current_index
    if index < 0:
        index = 0
    elif index >= len(keys):
        log_message("已浏览完所有图片")
        return

    current_index = index
    key = keys[current_index]
    image_path = os.path.join(image_folder, f"{key}{image_ext}")

    key_label.config(text=f"当前图片：{key}{image_ext}")

    if os.path.exists(image_path):
        img = Image.open(image_path).resize((600, 400))
        photo = ImageTk.PhotoImage(img)
        img_label.config(image=photo)
        img_label.image = photo
    else:
        img_label.config(image='', text=f"{key}{image_ext} 不存在")
        img_label.image = None
        log_message(f"警告：图片 {key}{image_ext} 不存在")

    update_listbox()
    image_listbox.select_clear(0, tk.END)
    image_listbox.select_set(current_index)
    image_listbox.see(current_index)


def show_next_image():
    if current_index + 1 < len(keys):
        show_image(current_index + 1)


def show_previous_image():
    if current_index - 1 >= 0:
        show_image(current_index - 1)


def delete_from_current_to_end():
    global lines, keys, current_index, undo_stack

    if current_index >= len(keys):
        return

    current_key = keys[current_index]
    chapter, number = current_key.split('-')
    number = int(number)

    deleted_keys = [line.split(' ')[0] for line in lines if line.startswith(f"{chapter}-") and int(line.split(' ')[0].split('-')[1]) >= number]
    undo_stack.append((lines.copy(), deleted_keys))

    lines = [line for line in lines if not (
        line.split(' ')[0].startswith(f"{chapter}-") and int(line.split(' ')[0].split('-')[1]) >= number
    )]
    keys[:] = [line.split(' ')[0] for line in lines]

    with open(txt_file_path, 'w') as f:
        for line in lines:
            f.write(line + '\n')

    log_message(f"已删除从 {chapter}-{number} 开始的所有行")

    if current_index >= len(keys):
        show_image(len(keys) - 1)
    else:
        show_image(current_index)


def delete_current_line():
    global lines, keys, current_index, undo_stack

    if current_index >= len(keys):
        return

    deleted_key = keys[current_index]
    undo_stack.append((lines.copy(), [deleted_key]))

    lines = [line for line in lines if not line.startswith(deleted_key)]
    keys[:] = [line.split(' ')[0] for line in lines]

    with open(txt_file_path, 'w') as f:
        for line in lines:
            f.write(line + '\n')

    log_message(f"已删除 {deleted_key} 的行")

    if current_index >= len(keys):
        show_image(len(keys) - 1)
    else:
        show_image(current_index)


def undo_last_delete():
    global lines, keys, current_index
    if not undo_stack:
        log_message("没有可撤销的操作")
        return

    lines_backup, deleted_keys = undo_stack.pop()
    lines = lines_backup
    keys[:] = [line.split(' ')[0] for line in lines]

    with open(txt_file_path, 'w') as f:
        for line in lines:
            f.write(line + '\n')

    if deleted_keys:
        try:
            current_index = keys.index(deleted_keys[0])
        except ValueError:
            current_index = 0
    log_message("已撤销上次删除操作")
    show_image(current_index)


def on_select_from_list(event):
    selection = image_listbox.curselection()
    if selection:
        idx = selection[0]
        show_image(idx)


# 构建 GUI 窗口
root = tk.Tk()
root.title("图像删除工具 with 菜单栏")

# 布局区域
left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, fill=tk.Y)

main_frame = tk.Frame(root)
main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# 列表菜单栏
scrollbar = Scrollbar(left_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

image_listbox = Listbox(left_frame, width=15, yscrollcommand=scrollbar.set)
image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
image_listbox.bind('<<ListboxSelect>>', on_select_from_list)
scrollbar.config(command=image_listbox.yview)

# 图片显示区域
img_label = tk.Label(main_frame)
img_label.pack()

# 当前图片 key
key_label = tk.Label(main_frame, text="", font=("Arial", 14))
key_label.pack(pady=10)

# 按钮区域
btn_frame = tk.Frame(main_frame)
btn_frame.pack(pady=10)

btn_prev = tk.Button(btn_frame, text="上一张", command=show_previous_image)
btn_prev.pack(side=tk.LEFT, padx=5)

btn_next = tk.Button(btn_frame, text="下一张", command=show_next_image)
btn_next.pack(side=tk.LEFT, padx=5)

btn_delete = tk.Button(btn_frame, text="删除章节后续", command=delete_from_current_to_end)
btn_delete.pack(side=tk.LEFT, padx=5)

btn_delete_one = tk.Button(btn_frame, text="删除当前一张", command=delete_current_line)
btn_delete_one.pack(side=tk.LEFT, padx=5)

btn_undo = tk.Button(btn_frame, text="撤销删除", command=undo_last_delete)
btn_undo.pack(side=tk.LEFT, padx=5)

# 输出栏
output_text = tk.Text(main_frame, height=8, state=tk.DISABLED, wrap=tk.WORD)
output_text.pack(fill=tk.X, padx=10, pady=10)

# 初始化
update_listbox()
show_image(0)
root.mainloop()
