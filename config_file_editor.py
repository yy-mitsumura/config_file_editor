DEF_DATA={
    "jww_root": r"C:\JWW",
    "is_sort": False
         } 
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog, filedialog
import json
import os
import sys
import re
import time
from collections import defaultdict
import datetime
import shutil

def smart_open(file_path):
    mode='r'
    encodings = ["cp932", "utf-8", "utf-8-sig"]

    for enc in encodings:    
        try:
            with open(file_path, mode, encoding=enc) as f:
                content = f.readlines()
            return content 
        except UnicodeDecodeError:
            print(f"失敗: {enc}")
            continue 

    with open(file_path, mode, encoding='cp932', errors='replace') as f:
        print(f"成功: cp932(rep)")
        content = f.readlines() 
    return content

def treeview_sort_column(tree, col, reverse):
    data_list = [(tree.set(item, col), item) for item in tree.get_children('')]
    data_list.sort(key=lambda t: t[0], reverse=reverse)

    for index, (_, item) in enumerate(data_list):
        tree.move(item, '', index)

    tree.heading(col, command=lambda: treeview_sort_column(tree, col, not reverse))


def treeview_sort_column_underscore(tree, col, reverse):
    def custom_sort_key(value):
        return (0 if value.startswith("_") else 1, value.lower())

    data_list = [(tree.set(item, col), item) for item in tree.get_children('')]
    data_list.sort(key=lambda t: custom_sort_key(t[0]), reverse=reverse)

    for index, (_, item) in enumerate(data_list):
        tree.move(item, '', index)

    tree.heading(col, command=lambda: treeview_sort_column_underscore(tree, col, not reverse))

class ToolTip:
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None

    def show_tip(self, text, x, y):
        if self.tip_window or not text:
            return
        time.sleep(0.3)
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.attributes("-topmost", True)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x+20}+{y+20}")

        label = tk.Label(tw, text=text, background="#ffffe0", relief=tk.SOLID, borderwidth=1, justify="left")
        label.pack()

    def hide_tip(self):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class TreeviewTooltipManager:
    def __init__(self):
        self.tooltips = {}
        self.previous_item_ids = {}

    def on_motion(self, event, treeview):
        treeview_id = id(treeview)
        if treeview_id not in self.tooltips:
            self.tooltips[treeview_id] = ToolTip(treeview)
            self.previous_item_ids[treeview_id] = None

        tooltip = self.tooltips[treeview_id]

        previous_item_id = self.previous_item_ids[treeview_id]

        item_id = treeview.identify_row(event.y)

        if item_id != previous_item_id:
            self.previous_item_ids[treeview_id] = item_id
            tooltip.hide_tip()

            if item_id:
                values = treeview.item(item_id, "values")
                
                values_str = ""
                for i, value in enumerate(values):
                    command_str="1"+values[0][5:7]+str(i-1)
                    if i==0:
                        values_str += value +"\n------\n"
                    if 0<i and i<len(values)-1:
                        values_str += f"【{command_str}】    {value}\n"
                    if i==len(values)-1:
                        values_str += f"【  dir】    {value}"
                tooltip_text = f"{values_str}"
                tooltip.show_tip(tooltip_text, event.x_root, event.y_root)
        elif not item_id:
            tooltip.hide_tip()

    def on_leave(self, event, treeview):
        treeview_id = id(treeview)
        if treeview_id in self.tooltips:
            self.tooltips[treeview_id].hide_tip()

def main():
    def load_or_initialize_config(file_path):
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(DEF_DATA, f, indent=4)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                jww_root_sv.set(data["jww_root"])
                is_sort_bv.set(data["is_sort"])
        except:
            pass

    def save_config(config_path, event=None):
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "jww_root": jww_root_sv.get(),
                    "is_sort": is_sort_bv.get()
                },
                 f, indent=4)
        if not check_jwwin_installed_dir(jww_root_sv.get()):
            for item in tree.get_children():
                tree.delete(item)
            for item in tree2.get_children():
                tree2.delete(item)
            
        if check_jwjwf_file(jww_root_sv.get()):
            lines=load_jwjwf(jww_root_sv.get())
            if lines or lines==[]:
                apply_jwjwf(lines)

    def select_jwwin_installed_dir(config_path):
        jw_dir=filedialog.askdirectory(title="Jw_winがあるフォルダを選択")
        if not jw_dir:
            return
        jww_root_sv.set(jw_dir)
        save_config(config_path)

    def check_jwwin_installed_dir(path):
        if os.path.isdir(path) and\
           os.path.isfile(os.path.normpath(os.path.join(path, "Jw_win.exe"))):
            has_jw_root_lb_b["text"]="ok"
            has_jw_root_lb_b["background"]="#00ee00"
            return True
        else:
            has_jw_root_lb_b["text"]="_"
            has_jw_root_lb_b["background"]="#ee0000"            
            return False
    def check_jwjwf_file(path):
        if check_jwwin_installed_dir(path) and\
           os.path.isfile(os.path.normpath(os.path.join(path, "Jw_win.jwf"))):
            has_jwjwf_lb_b["text"]="ok"
            has_jwjwf_lb_b["background"]="#00ee00"
            return True
        else:
            has_jwjwf_lb_b["text"]="_"
            has_jwjwf_lb_b["background"]="#ee0000"            
            return False
    def create_jwjwf(path):
        jwjwf=os.path.normpath(os.path.join(path, "Jw_win.jwf"))
        if os.path.isdir(path) and\
           os.path.isfile(os.path.normpath(os.path.join(path, "Jw_win.exe"))) and\
           not os.path.isfile(jwjwf):
                with open(jwjwf, mode="x") as file:
                    pass
                reload(path)

    def reload(path):
            for item in tree.get_children():
                tree.delete(item)
            for item in tree2.get_children():
                tree2.delete(item)
            is_exist_jwjwf_dir=check_jwwin_installed_dir(path)
            is_exist_jwjwf=check_jwjwf_file(path)
            if is_exist_jwjwf_dir and is_exist_jwjwf:
                lines=load_jwjwf(jww_root_sv.get())
                if lines or lines==[]:
                    apply_jwjwf(lines)        
    def load_jwjwf(path):
        jwjwf=os.path.normpath(os.path.join(path, "Jw_win.jwf"))
        if os.path.isdir(path) and\
            os.path.isfile(os.path.normpath(os.path.join(path, "Jw_win.exe"))) and\
            os.path.isfile(jwjwf):
                lines=[var.rstrip("\n") for var in smart_open(jwjwf)]
                return lines
    def apply_jwjwf(lines):
        for item in tree.get_children():
            tree.delete(item)
        for item in tree2.get_children():
            tree2.delete(item)
        jogai["text"]=""

        gcom_list=[]
        key_list=[]
        for line in lines:
            if line.startswith("GCOM_1"):
                gcom_list.append(line)
            elif  re.match(r'^KEY(_|F|S)[2-9A-Z]?', line):
                key_list.append(line)
        ele_str=f'以下の行は使用できない文字   *?"<>|,   が含まれているため表示されません。ファイルを直接編集して取り除くと表示されます↓\n'
        all_frag=False
        ng_dict={}
        for item in gcom_list:
            gcom_num=item.split("=")[0]
            bats_and_dir_str=item.split("=")[1]
            bats_and_dir=bats_and_dir_str.split(",")

            bats_and_dir.extend([""]*(11-len(bats_and_dir))) #12-len ?
            ng_frag=False
            ng_dict[gcom_num]=[]
            if 11<len(bats_and_dir):
                ng_frag=True
                all_frag=True             
                ng_dict[gcom_num].append(",")
            for ele in bats_and_dir:
                if not varid_gaihen(ele):
                    ng_frag=True
                    all_frag=True
                    ng_dict[gcom_num].append(ele)

            if not ng_frag:
                tree.insert("", "end", values=(gcom_num,
                                                bats_and_dir[0],
                                                bats_and_dir[1],
                                                bats_and_dir[2],
                                                bats_and_dir[3],
                                                bats_and_dir[4],
                                                bats_and_dir[5],
                                                bats_and_dir[6],
                                                bats_and_dir[7],
                                                bats_and_dir[8],
                                                bats_and_dir[9],
                                                bats_and_dir[10]))

        for key, value in ng_dict.items():
            if not len(value) == 0:           
                ele_str += key + " ".join(value)+"\n"

        jogai["text"]=ele_str
        if not all_frag:
            jogai["text"]=""
        
        for item in key_list:
            key_name=item.split("=")[0]
            command_list=(item.split("=")[1].strip()).split()
            command, shift_command = (command_list + ["", ""])[:2]
            item_num=tree2.insert("", "end", values=(key_name, command, shift_command))
            if (not varid_com_num_str(command) and not (command == "")) or (not varid_com_num_str(shift_command) and not (shift_command == "")):
                tags=list(tree2.item(item_num, "tags"))
                tags.insert(0, "red")
                tree2.item(item_num, tags=tags)

    def update_key_map(key_str, command_str, event=None, is_shift=None, ):
        for item in tree2.get_children():
            if (tree2.item(item)["values"][0]).strip() == key_str.strip():
                values=tree2.item(item)["values"]
                if is_shift:
                    values[2]=command_str
                else:
                    values[1]=command_str
                tree2.item(item, values=tuple(values))
        jwjwf_update(jww_root_sv.get())

    def update_gaihen(value, ind, s_items, event=None):
        values=tree.item(s_items)["values"]
        new_value=simpledialog.askstring("新しい値", "新しい値を入力", initialvalue=value)
        if not new_value:
            return
        if not varid_gaihen(new_value):
            invalid_chars = '*?"<>|,' # `\`と`:`はフルパスで使うので除外しない
            if messagebox.askyesno("", f"使用できない文字のどれか({invalid_chars})が含まれています。　_に置き換えてもいいですか？"):
                new_value=sanitize_filename(new_value)
            else:
                return
        values[ind]=new_value
        tree.item(s_items, values=tuple(values))
        jwjwf_update(jww_root_sv.get())

    def varid_gaihen(text:str):
        invalid_chars = r'[*?"<>|,]' # `\`と`:`はフルパスで使うので除外しない
        if re.search(invalid_chars, text):
            return False
        else:
            return True

    def sanitize_filename(path):
        invalid_chars = r'[*?"<>|,]'
        sanitized_filename = re.sub(invalid_chars, '_', path)
        return sanitized_filename
    
    popup_font=("", 11)
    def popUp(event):
        popupMenu=tk.Menu(root, tearoff=False)
        selected_items = tree.selection()
        keys=[]        
        for item in tree2.get_children():
            keys.append(tree2.item(item)["values"])
        values=tree.item(selected_items)["values"]

        for i,value in enumerate(values):
            command_str="1"+str(values[0][5:7])+str(i-1)
            if i==len(values)-1:
                command_str="  dir"
            if not i == 0:
                sub_menu=tk.Menu(root, tearoff=False)
                bind_menu=tk.Menu(root, tearoff=False)
                sub_menu.add_command(label="編集", command=lambda ind=i, v=value:update_gaihen(value=v, ind=ind, s_items=selected_items), font=popup_font)
                if not i==len(values)-1:
                    sub_menu.add_cascade(label="割り当て", menu=bind_menu, font=popup_font)
                    
                    for key in keys:
                        bind_menu_sub=tk.Menu(root, tearoff=False)
                        bind_menu.add_cascade(label=key[0], menu=bind_menu_sub, font=popup_font)

                        bind_menu_sub.add_command(label="「通常」", command=lambda k=key[0], c=command_str: update_key_map(key_str=k, command_str=c), font=popup_font)
                        if not key[0].strip()=="KEYSP":
                            bind_menu_sub.add_command(label="shift時", command=lambda k=key[0], c=command_str: update_key_map(key_str=k, command_str=c, is_shift=True), font=popup_font)

                popupMenu.add_cascade(label=f"【{command_str}】 {value}", menu=sub_menu, font=popup_font)
        popupMenu.post(event.x_root, event.y_root)
    def varid_com_num_str(text:str):
        invalid_chars = r'^\d\d?\d?\d?$'
        if re.match(invalid_chars, text):
            return True
        else:
            return False
    def edit_key_map(value, s_items, is_shift=None):
        values=tree2.item(s_items)["values"]
        new_value=simpledialog.askinteger("新しい値", "新しい値を入力", initialvalue=value)
        new_value=str(new_value)
        if not new_value:
            return
        if not varid_com_num_str(new_value):
            messagebox.showerror("", "最大四桁の数字です")
            return
        if is_shift:
            values[2]=new_value
        else:
            values[1]=new_value
        tree2.item(s_items, values=tuple(values))
        jwjwf_update(jww_root_sv.get())

    def popUp2(event):
        popupMenu=tk.Menu(root, tearoff=False)
        selected_items = tree2.selection()
        values=tree2.item(selected_items)["values"]
        popupMenu.add_command(label=" 「通常」を編集", command=lambda v=values[1]:edit_key_map(v, selected_items, False), font=popup_font)
        if not tree2.item(selected_items)["values"][0].strip()=="KEYSP":   
            popupMenu.add_command(label="shift時 を編集", command=lambda v=values[2]:edit_key_map(v, selected_items, True), font=popup_font)        
        popupMenu.post(event.x_root, event.y_root)
    def jwjwf_update(path):
        jwjwf=os.path.normpath(os.path.join(path, "Jw_win.jwf"))
        if not check_jwjwf_file(path):
            return

        lines=[var.rstrip("\n") for var in smart_open(jwjwf)]
        new_lines=[]
        for item in tree2.get_children():        
            key=tree2.item(item)["values"]
            key1=str(key[1])
            if str(key[1]) == "":
                key1=0
            new_str=f"{key[0].strip()} = {key1} {str(key[2])}"

            if lines:
                updated=False
                for i, line in enumerate(lines):

                    if line.startswith(key[0].strip()):
                        lines[i]=new_str
                        updated=True
                        break
                if not updated:
                    new_lines.append(new_str)
            else:
                new_lines.append(new_str)

        for item in tree.get_children():
            values=tree.item(item)["values"]
            new_str=f"{values[0].strip()} ={str(values[1])},{str(values[2])},{str(values[3])},{str(values[4])},{str(values[5])},{str(values[6])},{str(values[7])},{str(values[8])},{str(values[9])},{str(values[10])},{str(values[11])}"
            if lines:
                updated=False
                for i, line in enumerate(lines):
                    if line.startswith(values[0].strip()):
                        lines[i]=new_str
                        updated=True
                        break
                if not updated:
                    new_lines.append(new_str)
            else:
                new_lines.append(new_str)

        lines=lines+new_lines
        lines="\n".join(lines)
        backup(is_auto=True)
        with open(jwjwf, "w", encoding="cp932") as file:
            file.writelines(lines)
        if is_sort_bv.get():
            sort_lines()            
        lines=load_jwjwf(jww_root_sv.get())
        if lines or lines==[]:
            apply_jwjwf(lines)

    def sort_lines():
        if not check_jwjwf_file(jww_root_sv.get()):
            return
        jwjwf=os.path.normpath(os.path.join(jww_root_sv.get(), "Jw_win.jwf"))

        lines=[var.rstrip("\n") for var in smart_open(jwjwf)]
        sp_ind=0
        nanaroku_ind=None
        gcoms=[]
        functions=[]
        alphabets=[]
        exclude_inds=[]
        ends=[]
        for i, line in enumerate(lines):
            if re.match("^GCOM_1\\d0", line):
                gcoms.append(line)
            elif re.match("^KEY76", line):
                nanaroku_ind=i
                nanaroku=lines[nanaroku_ind]

            elif re.match("^KEYSP", line):
                sp_ind=i
                sp=lines[sp_ind]

            elif re.match("^KEYF", line):
                functions.append(line)

            elif re.match("^KEY_", line):
                alphabets.append(line)
            elif re.match("^END", line):
                ends.append(line)
            else:

                exclude_inds.append(i)


        lines=[x for i, x in enumerate(lines) if i in exclude_inds]
        gcoms.sort()
        alphabets.sort()
        functions.sort()
        new_lines = lines + gcoms + alphabets + functions
        if sp_ind:           
            new_lines.append(sp)
            
        if nanaroku_ind:
            new_lines.append(nanaroku)
        new_lines = new_lines + ends
        new_lines = "\n".join(new_lines)
        backup(is_auto=True)
        with open(jwjwf, "w", encoding="cp932") as file:
            file.writelines(new_lines)

    def key_insert():
        def sub_func(key_str):
            ex_keys=[tree2.item(item)["values"][0][3:5] for item in tree2.get_children()]
            ex_expected_underbar_keys=[]
            for key in ex_keys:
                if "_" in key:
                    ex_expected_underbar_keys.append(key[1:])
                else:
                    ex_expected_underbar_keys.append(key)            
            if not key_str in ex_expected_underbar_keys:
                if re.match("^[A-Z]$", key_str):
                    key_str2="KEY_"+key_str
                else:
                    key_str2="KEY"+key_str

                tree2.insert("","end",values=(key_str2,"",""))
            tl.destroy()
            jwjwf_update(jww_root_sv.get())
        if not check_jwwin_installed_dir(jww_root_sv.get()):
            return
        if not check_jwjwf_file(jww_root_sv.get()):
            return
        key_set=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
                    "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9",
                    "SP"]
        keys=[tree2.item(item)["values"][0][3:5] for item in tree2.get_children()]
        expected_underbar_keys=[]
        for key in keys:
            if "_" in key:
                expected_underbar_keys.append(key[1:])
            else:
                expected_underbar_keys.append(key)
        diffs=[item for item in key_set if item not in expected_underbar_keys]
        tl=tk.Toplevel()
        tl.geometry("+0+0")
        lb=tk.Label(tl, text="追加するキーを選んでください")
        lb.pack()
        fr1=tk.Frame(tl)
        fr2=tk.Frame(tl)
        fr3=tk.Frame(tl)
        fr1.pack()
        fr2.pack()
        fr3.pack()
        for i, key in enumerate(diffs):
            
            if i<10:
                bt=tk.Button(fr1, text=key, height=3, font=("", 11), command=lambda k=key:sub_func(key_str=k))
                bt.pack(padx=10, pady=10, side="left")
            if 10<=i and i<20:
                bt=tk.Button(fr2, text=key, height=3, font=("", 11), command=lambda k=key:sub_func(key_str=k))
                bt.pack(padx=10, pady=10, side="left")
            if 20<=i:
                bt=tk.Button(fr3, text=key, height=3, font=("", 11), command=lambda k=key:sub_func(key_str=k))
                bt.pack(padx=10, pady=10, side="left")    



    def gcom_insert():
        def sub_func(gcom_str):
            if not gcom_str in [tree.item(item)["values"][0].strip() for item in tree.get_children()]:
                tree.insert("","end",values=(gcom_str, "", "", "", "", "", "", "", "", "", "", ""))
            tl.destroy()
            jwjwf_update(jww_root_sv.get())
        if not check_jwwin_installed_dir(jww_root_sv.get()):
            return
        if not check_jwjwf_file(jww_root_sv.get()):
            return
        gcom_set=["GCOM_100",
                  "GCOM_120",
                  "GCOM_130",
                  "GCOM_140",
                  "GCOM_150",
                  "GCOM_160",
                  "GCOM_170",
                  "GCOM_180",
                  "GCOM_190",
                  ]
        gcoms=[tree.item(item)["values"][0].strip() for item in tree.get_children()]


        diffs=[item for item in gcom_set if item not in gcoms]
        # diffs.sort()
        tl=tk.Toplevel()
        tl.geometry("+0+0")
        lb=tk.Label(tl, text="追加するGCOMを選んでください")
        lb.pack()
        for gcom in diffs:
            tk.Button(tl, text=gcom, height=3, font=("", 11), command=lambda g=gcom:sub_func(gcom_str=g)).pack(padx=10, side="left")

    

    def check_duplicates(path):
        def sub_func(lines, line_list):               
            def escape_line(leave_ind, line_list, lines):
                line_list.remove(leave_ind)
                for ind in line_list:
                    lines[ind]="# "+ lines[ind]
                lines="\n".join(lines)
                backup(is_auto=True)
                with open(jwjwf_path, "w", encoding="cp932") as file:
                    file.writelines(lines)
                tl.destroy()
            def on_close():   
                tl.destroy()
                root.quit()
                sys.exit()
            
            tl=tk.Toplevel(background="#FFC8C8")
            tl.geometry("+0+0")
            tl.grab_set()
            tl.attributes("-topmost", True)
            tl.protocol("WM_DELETE_WINDOW", on_close) 
            tk.Label(tl, text="重複しています。【残す方】を選んでください。\n\n残さない方はコメントアウトされます。\n\nウィンドウの「×」を押すとプログラムを終了します。", background="#FFC8C8").pack()
            for line in line_list:
                tk.Button(tl, text=lines[line], command=lambda l=line, lis=line_list, lines=lines: escape_line(l, lis, lines)).pack()
            tl.wait_window()

            
        if os.path.isdir(path) and\
            os.path.isfile(os.path.normpath(os.path.join(path, "Jw_win.exe"))) and\
            os.path.isfile(os.path.normpath(os.path.join(path, "Jw_win.jwf"))):
            jwjwf_path=os.path.normpath(os.path.join(path, "Jw_win.jwf"))

            occurrences = defaultdict(list) 
            pattern = re.compile('^(GCOM_1\\d\\d|KEY(_[A-Z]|F\\d|SP|76))')
            
            lines=smart_open(jwjwf_path)   
            for line_num, line in enumerate(lines, start=1):
                matches = pattern.findall(line)
                for match in matches:
                    occurrences[match].append(line_num-1)
            lines=[var.rstrip("\n") for var in lines]        
            for match, line_list in occurrences.items():
                if len(line_list) > 1:
                    sub_func(lines, line_list)

    def open_jwwin_installed_dir(path):
        if check_jwwin_installed_dir(path): 
            os.startfile(path)
    def backup(is_auto=False):
        if not check_jwjwf_file(jww_root_sv.get()):
            return
        jwjwfpath=os.path.join(jww_root_sv.get(), "Jw_win.jwf")    
        os.makedirs("backup", exist_ok=True)
        os.makedirs(os.path.join("backup", "auto"), exist_ok=True)
        os.makedirs(os.path.join("backup", "manual"), exist_ok=True)
        time=datetime.datetime.now().strftime("%y%m%d%H%M%S")
        if is_auto: 
            save_path=os.path.join("backup", "auto", f"{time}.jwf")
            shutil.copyfile(jwjwfpath, save_path)
        else:
            save_path=os.path.join("backup", "manual", f"{time}.jwf")
            shutil.copyfile(jwjwfpath, save_path)
                        

    root = tk.Tk()
    root.geometry("+0+0")
    jww_root_fr=tk.Frame(root)
    jww_root_fr.pack(anchor="w")
    jww_root_lb=tk.Label(jww_root_fr, text="Jw_win.exeのインストール先フォルダ: ")
    jww_root_lb.pack(anchor="w", side="left")
    jww_root_sv=tk.StringVar()
    jww_root_lb_content=tk.Label(jww_root_fr, textvariable=jww_root_sv, background="#eeee99")
    jww_root_lb_content.pack(side="left")
    jww_root_select_bt=tk.Button(jww_root_fr, text="指定フォルダを変更する", relief="solid", height=2, command=lambda:select_jwwin_installed_dir("config.json"))
    jww_root_select_bt.pack(side="left")
    jww_root_open_bt=tk.Button(jww_root_fr, text="インストール先を開く", relief="solid", height=2, command=lambda: open_jwwin_installed_dir(jww_root_sv.get()))
    jww_root_open_bt.pack(side="left")



    jw_jwf_fr=tk.Frame(root, background="#aaaaaa")
    jw_jwf_fr.pack(anchor="w")
    has_jw_root_lb=tk.Label(jw_jwf_fr, text="Jw_winインストール先フォルダの有無及びJw_win.exeの有無: ")
    has_jw_root_lb_b=tk.Label(jw_jwf_fr, text="_", background="#ee0000")
    has_jw_root_lb.grid(row=0, column=0, padx=5, pady=2, sticky="e")
    has_jw_root_lb_b.grid(row=0, column=1, padx=5, pady=2, sticky="w")
    has_jwjwf_lb=tk.Label(jw_jwf_fr, text="↑且つ Jw_win.jwfの有無: ")
    has_jwjwf_lb_b=tk.Label(jw_jwf_fr, text="_", background="#ee0000")
    has_jwjwf_lb.grid(row=1, column=0, padx=5, pady=2, sticky="e")
    has_jwjwf_lb_b.grid(row=1, column=1, padx=5, pady=2, sticky="w")
    create_jwjwf_bt=tk.Button(jw_jwf_fr, text="空のJw_win.jwfを作成する", relief="solid", height=2, command=lambda: create_jwjwf(jww_root_sv.get()))
    create_jwjwf_bt.grid(row=1, column=2, padx=20)
    reload_jwjwf_bt=tk.Button(jw_jwf_fr, text="Jw_win.jwf再読み込み", relief="solid", height=2, command=lambda: reload(jww_root_sv.get()))
    reload_jwjwf_bt.grid(row=1, column=3, padx=20)
    backup_jwjwf_bt=tk.Button(jw_jwf_fr, text="現時点のJw_win.jwfをバックアップする", relief="solid", height=2, command=lambda: backup(is_auto=False))
    backup_jwjwf_bt.grid(row=1, column=4, padx=20)
    is_sort_bv=tk.BooleanVar(root, value=False)
    tk.Checkbutton(root, text="Jw_win.jwfの更新時にソートを行う(切り替えるとJw_win.jwfの再読み込みもします)", relief="solid", height=2, variable=is_sort_bv, command=lambda: save_config("config.json")).pack(anchor="w")
    tk.Button(root, text="直ちにソートを行う", relief="solid", height=2, command=sort_lines).pack(anchor="w")
    tk.Button(root, text="GCOM行を追加", relief="solid", height=2, command=gcom_insert).pack()
    


    tree_fr=tk.Frame(root)
    tree_fr.pack()

    tree_column_names=("GCOM", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "dir")
    tree = ttk.Treeview(tree_fr,
                        columns=tree_column_names,
                        show="headings",
                        height=4
                        )
    tree.bind("<Button-3>", popUp)
    tt_manager=TreeviewTooltipManager()
    tree.bind("<Motion>", lambda e, tv=tree: tt_manager.on_motion(e, tv))
    tree.bind("<Leave>", lambda e, tv=tree: tt_manager.on_leave(e, tv))    
    for name in tree_column_names:
       tree.column(name, width=80)
    tree.heading("GCOM", text="GCOM", command=lambda: treeview_sort_column(tree, "GCOM", True))
    tree.heading("0", text="0", command=lambda: treeview_sort_column(tree, "0", True))
    tree.heading("1", text="1", command=lambda: treeview_sort_column(tree, "1", True))
    tree.heading("2", text="2", command=lambda: treeview_sort_column(tree, "2", True))
    tree.heading("3", text="3", command=lambda: treeview_sort_column(tree, "3", True))
    tree.heading("4", text="4", command=lambda: treeview_sort_column(tree, "4", True))
    tree.heading("5", text="5", command=lambda: treeview_sort_column(tree, "5", True))
    tree.heading("6", text="6", command=lambda: treeview_sort_column(tree, "6", True))
    tree.heading("7", text="7", command=lambda: treeview_sort_column(tree, "7", True))
    tree.heading("8", text="8", command=lambda: treeview_sort_column(tree, "8", True))
    tree.heading("9", text="9", command=lambda: treeview_sort_column(tree, "9", True))
    tree.heading("dir", text="dir", command=lambda: treeview_sort_column(tree, "dir", True))
    scrbr=tk.Scrollbar(tree_fr, orient=tk.VERTICAL, command=tree.yview, width=30)
    scrbr.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)
    tree.configure(yscrollcommand=scrbr.set)
    jogai=tk.Label(root, text="_", justify="left")
    jogai.pack()

    tree_fr2=tk.Frame(root)
    tree_fr2.pack()
    tree2 = ttk.Treeview(tree_fr2,
                        columns=("キー", "通常", "shift時"),
                        show="headings",
                        height=15
                        )
    tree2.bind("<Button-3>", popUp2)  
    tree2.heading("キー", text="キー", command=lambda: treeview_sort_column_underscore(tree2, "キー", False))
    tree2.heading("通常", text="通常", command=lambda: treeview_sort_column(tree2, "通常", True))
    tree2.heading("shift時", text="shift時", command=lambda: treeview_sort_column(tree2, "shift時", True))

    scrbr2=tk.Scrollbar(tree_fr2, orient=tk.VERTICAL, command=tree2.yview, width=30)
    scrbr2.pack(side="right", fill="y")
    tree2.pack(side="left", fill="both", expand=True)
    key_inserter=tk.Button(root, text="KEY行を追加", relief="solid", height=2, command=key_insert)
    key_inserter.pack()
    tree2.configure(yscrollcommand=scrbr2.set)
    tree2.tag_configure("red", background="#FFC8C8")

    load_or_initialize_config("config.json")  
    check_jwwin_installed_dir(jww_root_sv.get())
    check_jwjwf_file(jww_root_sv.get())
    check_duplicates(jww_root_sv.get())    
    lines=load_jwjwf(jww_root_sv.get())
    if lines or lines==[]:
        apply_jwjwf(lines)

    root.mainloop()
if __name__ == "__main__":
    os.chdir(os.path.dirname(sys.argv[0]))
    main()