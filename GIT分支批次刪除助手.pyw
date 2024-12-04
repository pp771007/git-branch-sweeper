import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar, END
import json
import git

class GitBranchDeleter:
    def __init__(self, root):
        self.root = root
        self.root.title("GIT 分支批次刪除助手")
        self.root.geometry("600x500")
        
        # 資料夾列表
        self.folder_list = []
        
        # 設定 UI
        self.setup_ui()
        
        # 加載上次存檔的資料
        self.load_saved_data()

    def setup_ui(self):
        # 選擇資料夾按鈕
        select_folder_btn = tk.Button(self.root, text="選擇資料夾", command=self.choose_folder)
        select_folder_btn.pack(pady=10)

        # 資料夾列表 Listbox
        self.folder_listbox = Listbox(self.root, selectmode=tk.SINGLE, exportselection=False, height=5)
        self.folder_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar = Scrollbar(self.folder_listbox, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.folder_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.folder_listbox.yview)
        self.folder_listbox.bind('<ButtonRelease-1>', self.set_target_folder)
            
        # 新增右鍵選單
        self.folder_menu = tk.Menu(self.root, tearoff=0)
        self.folder_menu.add_command(label="刪除", command=self.delete_folder)
        self.folder_listbox.bind('<Button-3>', self.show_folder_menu)

        # 目標資料夾的分支列表 Listbox
        self.branch_listbox = Listbox(self.root, selectmode=tk.EXTENDED, exportselection=False, height=15)
        self.branch_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar2 = Scrollbar(self.branch_listbox, orient=tk.VERTICAL)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        self.branch_listbox.config(yscrollcommand=scrollbar2.set)
        scrollbar2.config(command=self.branch_listbox.yview)

        # 刪除分支按鈕
        delete_branch_btn = tk.Button(self.root, text="刪除所選分支", command=self.delete_selected_branches)
        delete_branch_btn.pack(pady=10)

        # 新增推送分支按鈕
        push_branch_btn = tk.Button(self.root, text="推送所選分支", command=self.push_selected_branches)
        push_branch_btn.pack(pady=10)
            
        # 新增顯示推送結果標籤
        self.push_result_label = tk.Label(self.root, text="", fg="green")
        self.push_result_label.pack(pady=5)

        # 視窗關閉事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 綁定視窗大小變化事件
        self.root.bind("<Configure>", self.on_resize)

    def show_folder_menu(self, event):
        # 確保點擊位置的項目被選中
        self.folder_listbox.selection_clear(0, tk.END)
        clicked_index = self.folder_listbox.nearest(event.y)
        self.folder_listbox.selection_set(clicked_index)
        
        # 顯示選單
        try:
            self.folder_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.folder_menu.grab_release()

    def delete_folder(self):
        selection = self.folder_listbox.curselection()
        if selection:
            index = selection[0]
            folder_path = self.folder_list[index]
            if messagebox.askyesno("確認刪除", f"確定要從列表中移除此資料夾嗎？\n{folder_path}"):
                self.folder_list.pop(index)
                self.update_folder_listbox()
                # 清空分支列表
                self.branch_listbox.delete(0, tk.END)
                
    def choose_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            try:
                # 檢查資料夾是否為有效的 Git 儲存庫
                git.Repo(folder_selected)
                # 檢查資料夾是否已存在於列表中
                if folder_selected not in self.folder_list:
                    self.folder_list.append(folder_selected)
                    self.folder_list.sort()  # 排序資料夾列表
                    self.update_folder_listbox()
                else:
                    messagebox.showinfo("提示", "此資料夾已在列表中。")
            except git.exc.InvalidGitRepositoryError:
                messagebox.showerror("錯誤", "此資料夾不是有效的 Git 儲存庫。")

    def update_folder_listbox(self):
        self.folder_listbox.delete(0, END)
        for folder in self.folder_list:
            self.folder_listbox.insert(tk.END, folder)

    def set_target_folder(self, event):
        selection = self.folder_listbox.curselection()
        if selection:
            index = selection[0]
            folder_path = self.folder_list[index]
            self.load_branches(folder_path)

    def load_branches(self, folder_path):
        try:
            repo = git.Repo(folder_path)
            branches = [branch.name for branch in repo.branches]
            self.branch_listbox.delete(0, tk.END)
            current_branch = repo.active_branch.name  # 取得目前的分支名稱
            for branch in branches:
                if branch == current_branch:
                    self.branch_listbox.insert(tk.END, f"* {branch} (當前分支)")  # 目前選擇的分支名稱強調顯示
                else:
                    self.branch_listbox.insert(tk.END, branch)
        except git.exc.InvalidGitRepositoryError:
            messagebox.showerror("錯誤", "此資料夾不是有效的 Git 儲存庫。")
            self.folder_list.remove(folder_path)
            self.update_folder_listbox()

    def delete_selected_branches(self):
        selected_indices = self.branch_listbox.curselection()
        if not selected_indices:
            return
        
        folder_index = self.folder_listbox.curselection()[0]
        folder_path = self.folder_list[folder_index]

        repo = git.Repo(folder_path)
        for index in selected_indices:
            branch_name = self.branch_listbox.get(index)
            if branch_name.startswith("*"):
                continue  # 如果分支名稱以 * 開頭，代表是目前的分支，跳過刪除操作
            repo.git.branch("-D", branch_name)
        
        self.load_branches(folder_path)

    def push_selected_branches(self):
        selected_indices = self.branch_listbox.curselection()
        if not selected_indices:
            return

        folder_index = self.folder_listbox.curselection()[0]
        folder_path = self.folder_list[folder_index]

        repo = git.Repo(folder_path)
        success_branches = []
        failed_branches = []

        for index in selected_indices:
            branch_name = self.branch_listbox.get(index).replace("* ", "").replace(" (當前分支)", "")
            try:
                repo.git.push("-u", "origin", branch_name)
                success_branches.append(branch_name)
            except git.exc.GitCommandError as e:
                failed_branches.append(branch_name)

        # 更新結果標籤
        if success_branches and not failed_branches:
            self.push_result_label.config(text=f"成功推送分支: {', '.join(success_branches)}", fg="green")
        elif failed_branches and not success_branches:
            self.push_result_label.config(text=f"推送失敗分支: {', '.join(failed_branches)}", fg="red")
        elif success_branches and failed_branches:
            self.push_result_label.config(
                text=f"成功推送分支: {', '.join(success_branches)}\n失敗分支: {', '.join(failed_branches)}",
                fg="orange"
            )
        else:
            self.push_result_label.config(text="", fg="green")

    def on_closing(self):
        # 關閉視窗時存檔
        window_geometry = {
            "x": self.root.winfo_x(),
            "y": self.root.winfo_y(),
            "width": self.root.winfo_width(),
            "height": self.root.winfo_height(),
            "folders": self.folder_list
        }
        
        with open("GIT分支批次刪除助手.txt", "w", encoding="utf-8") as f:
            json.dump(window_geometry, f, ensure_ascii=False, indent=4)

        self.root.destroy()

    def load_saved_data(self):
        try:
            with open("GIT分支批次刪除助手.txt", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.root.geometry(f"{data['width']}x{data['height']}+{data['x']}+{data['y']}")
                self.folder_list = data['folders']
                self.update_folder_listbox()
        except FileNotFoundError:
            pass

    def on_resize(self, event):
        # 視窗大小變化時，調整 Listbox 和按鈕的大小
        self.folder_listbox.config(width=self.root.winfo_width() // 2)
        self.branch_listbox.config(width=self.root.winfo_width() // 2)

if __name__ == "__main__":
    root = tk.Tk()
    app = GitBranchDeleter(root)
    root.mainloop()
