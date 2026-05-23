# university_gui.py
# 一个很简单的 GUI，把你原来的 CLI 功能包一层出来用
# 需要同目录下有 unified_university_app.py

import tkinter as tk
from tkinter import ttk, messagebox
import random

# 导入你原来文件里的东西
from unified_university_app import (
    DataStore,
    AuthService,
    get_student_by_id,
    save_student,
    view_all_students,
    remove_student_admin,
    clear_all,
    grade_from_mark,
    gen_subject_id,
    recompute_average,
)

# ------------------------
# 主应用
# ------------------------
class UniversityGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("University System (GUI)")
        self.root.geometry("420x300")

        # 准备好认证服务，复用你原来的逻辑
        self.ds = DataStore()
        self.auth = AuthService(self.ds)

        # 主界面
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="University System (GUI)", font=("Arial", 14, "bold")).pack(pady=10)

        ttk.Button(main_frame, text="Student", command=self.open_student_window).pack(pady=5, fill="x")
        ttk.Button(main_frame, text="Admin", command=self.open_admin_window).pack(pady=5, fill="x")
        ttk.Button(main_frame, text="Quit", command=root.destroy).pack(pady=5, fill="x")

    # ------------------------
    # 学生窗口
    # ------------------------
    def open_student_window(self):
        win = tk.Toplevel(self.root)
        win.title("Student")
        win.geometry("400x260")

        tabs = ttk.Notebook(win)
        tabs.pack(fill="both", expand=True, padx=5, pady=5)

        # 注册 tab
        reg_frame = ttk.Frame(tabs, padding=10)
        tabs.add(reg_frame, text="Register")

        ttk.Label(reg_frame, text="Name:").grid(row=0, column=0, sticky="w")
        name_entry = ttk.Entry(reg_frame, width=30)
        name_entry.grid(row=0, column=1, pady=3)

        ttk.Label(reg_frame, text="Email:").grid(row=1, column=0, sticky="w")
        email_entry = ttk.Entry(reg_frame, width=30)
        email_entry.grid(row=1, column=1, pady=3)
        # 提示要用 @university.com
        ttk.Label(reg_frame, text="(must end with @university.com)", foreground="gray").grid(row=2, column=1, sticky="w")

        ttk.Label(reg_frame, text="Password:").grid(row=3, column=0, sticky="w")
        pwd_entry = ttk.Entry(reg_frame, show="*", width=30)
        pwd_entry.grid(row=3, column=1, pady=3)
        ttk.Label(reg_frame, text="(A-Z开头 + ≥4字母 + ≥3数字)", foreground="gray").grid(row=4, column=1, sticky="w")

        def do_register():
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            pwd = pwd_entry.get().strip()
            # 直接复用你原来的注册逻辑
            stu = self.auth.register(name, email, pwd)
            if stu is not None:
                messagebox.showinfo("Success", f"Registration successful.\nYour ID is {stu['student_id']}")
            else:
                messagebox.showerror("Failed", "Register failed. Please check email/password format.")

        ttk.Button(reg_frame, text="Register", command=do_register).grid(row=5, column=1, pady=8, sticky="e")

        # 登录 tab
        login_frame = ttk.Frame(tabs, padding=10)
        tabs.add(login_frame, text="Login")

        ttk.Label(login_frame, text="Email:").grid(row=0, column=0, sticky="w")
        login_email = ttk.Entry(login_frame, width=30)
        login_email.grid(row=0, column=1, pady=3)

        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky="w")
        login_pwd = ttk.Entry(login_frame, show="*", width=30)
        login_pwd.grid(row=1, column=1, pady=3)

        def do_login():
            email = login_email.get().strip()
            pwd = login_pwd.get().strip()
            user = self.auth.login(email, pwd)
            if user is not None:
                messagebox.showinfo("Login", "Login successful.")
                # 打开学生面板，传入学生ID
                StudentPanel(self.root, user["student_id"])
            else:
                messagebox.showerror("Login", "Incorrect email or password, or format not correct.")

        ttk.Button(login_frame, text="Login", command=do_login).grid(row=2, column=1, pady=8, sticky="e")

    # ------------------------
    # 管理员窗口
    # ------------------------
    def open_admin_window(self):
        win = tk.Toplevel(self.root)
        win.title("Admin")
        win.geometry("520x400")

        top_frame = ttk.Frame(win, padding=5)
        top_frame.pack(fill="x")

        ttk.Button(top_frame, text="Show all students", command=lambda: self.show_all_students(text_area)).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Clear ALL", command=lambda: self.clear_all_students(text_area)).pack(side="left", padx=5)

        # 删除学生
        del_frame = ttk.Frame(win, padding=5)
        del_frame.pack(fill="x")
        ttk.Label(del_frame, text="Remove student ID (6 digits):").pack(side="left")
        del_entry = ttk.Entry(del_frame, width=10)
        del_entry.pack(side="left", padx=3)
        ttk.Button(del_frame, text="Remove", command=lambda: self.remove_student(del_entry.get().strip(), text_area)).pack(side="left", padx=3)

        text_area = tk.Text(win, wrap="word")
        text_area.pack(fill="both", expand=True, padx=5, pady=5)

    def show_all_students(self, text_widget):
        text_widget.delete("1.0", tk.END)
        students = view_all_students()
        if not students:
            text_widget.insert(tk.END, "(empty) No students.\n")
            return
        for s in students:
            sid = s.get("student_id") or s.get("id")
            name = s.get("name", "(no name)")
            subs = s.get("subjects") or []
            avg = s.get("avg_mark", "N/A")
            text_widget.insert(tk.END, f"{sid}  {name}  subjects={len(subs)}  avg={avg}\n")

    def remove_student(self, sid, text_widget):
        if len(sid) != 6 or not sid.isdigit():
            messagebox.showerror("Error", "ID must be exactly 6 digits.")
            return
        ok = remove_student_admin(sid)
        if ok:
            messagebox.showinfo("Admin", "Removed.")
            self.show_all_students(text_widget)
        else:
            messagebox.showerror("Admin", "Not found.")

    def clear_all_students(self, text_widget):
        # GUI里就直接给它 clear_all("CLEAR")
        if messagebox.askyesno("Confirm", "This will DELETE ALL students. Continue?"):
            if clear_all("CLEAR"):
                messagebox.showinfo("Admin", "All students cleared.")
                self.show_all_students(text_widget)
            else:
                messagebox.showerror("Admin", "Failed to clear.")


# ------------------------
# 学生登录后的小面板
# ------------------------
class StudentPanel:
    def __init__(self, root, student_id):
        self.student_id = student_id
        self.win = tk.Toplevel(root)
        self.win.title(f"Student Panel - {student_id}")
        self.win.geometry("430x320")

        # 顶部信息
        info_frame = ttk.Frame(self.win, padding=5)
        info_frame.pack(fill="x")
        self.info_label = ttk.Label(info_frame, text=f"Student ID: {student_id}")
        self.info_label.pack(side="left")

        # 列表
        self.listbox = tk.Listbox(self.win, height=8)
        self.listbox.pack(fill="x", padx=5, pady=5)

        # 按钮区
        btn_frame = ttk.Frame(self.win, padding=5)
        btn_frame.pack(fill="x")

        ttk.Button(btn_frame, text="Refresh Subjects", command=self.refresh_subjects).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Enrol Subject", command=self.enrol_subject).pack(side="left", padx=4)

        # 删除科目
        del_frame = ttk.Frame(self.win, padding=5)
        del_frame.pack(fill="x")
        ttk.Label(del_frame, text="Remove subject ID (3 digits):").pack(side="left")
        self.del_entry = ttk.Entry(del_frame, width=6)
        self.del_entry.pack(side="left", padx=3)
        ttk.Button(del_frame, text="Remove", command=self.remove_subject).pack(side="left", padx=3)

        # 改密码
        pw_frame = ttk.Frame(self.win, padding=5)
        pw_frame.pack(fill="x")
        ttk.Label(pw_frame, text="New password:").pack(side="left")
        self.new_pw_entry = ttk.Entry(pw_frame, width=15, show="*")
        self.new_pw_entry.pack(side="left", padx=3)
        ttk.Button(pw_frame, text="Change", command=self.change_password).pack(side="left")

        # 初次刷新
        self.refresh_subjects()

    def get_student(self):
        return get_student_by_id(self.student_id)

    def refresh_subjects(self):
        self.listbox.delete(0, tk.END)
        stu = self.get_student()
        if not stu:
            self.listbox.insert(tk.END, "Student not found.")
            return
        subs = stu.get("subjects") or []
        if not subs:
            self.listbox.insert(tk.END, "No subjects.")
        else:
            for s in subs:
                sid = str(s.get("id")).zfill(3)
                mark = s.get("mark")
                grade = s.get("grade")
                self.listbox.insert(tk.END, f"{sid}  mark={mark}  grade={grade}")
        avg = stu.get("avg_mark") or 0
        self.listbox.insert(tk.END, f"--- Average: {avg}")

    def enrol_subject(self):
        stu = self.get_student()
        if not stu:
            messagebox.showerror("Error", "Student not found.")
            return
        subs = stu.get("subjects") or []
        if len(subs) >= 4:
            messagebox.showerror("Error", "Students are allowed to enrol in 4 subjects only.")
            return
        existing = [str(s.get("id")).zfill(3) for s in subs]
        sid = gen_subject_id(existing)
        mark = random.randint(25, 100)
        grade = grade_from_mark(mark)
        subs.append({"id": sid, "mark": mark, "grade": grade})
        stu["subjects"] = subs
        recompute_average(stu)
        save_student(stu)
        self.refresh_subjects()
        messagebox.showinfo("Enrol", f"Subject {sid} enrolled.")

    def remove_subject(self):
        target = self.del_entry.get().strip().zfill(3)
        if not target.isdigit() or len(target) != 3:
            messagebox.showerror("Error", "Subject ID must be 3 digits.")
            return
        stu = self.get_student()
        if not stu:
            messagebox.showerror("Error", "Student not found.")
            return
        subs = stu.get("subjects") or []
        before = len(subs)
        subs = [s for s in subs if str(s.get("id")).zfill(3) != target]
        if len(subs) == before:
            messagebox.showerror("Error", "Subject not found.")
            return
        stu["subjects"] = subs
        recompute_average(stu)
        save_student(stu)
        self.refresh_subjects()
        messagebox.showinfo("Removed", f"Subject {target} removed.")

    def change_password(self):
        new_pw = self.new_pw_entry.get().strip()
        if not new_pw:
            messagebox.showerror("Error", "Password cannot be empty.")
            return
        # 这里直接改字典并保存，保持和你原文件里字段一致
        stu = self.get_student()
        if not stu:
            messagebox.showerror("Error", "Student not found.")
            return
        stu["student_password"] = new_pw
        stu["password"] = new_pw
        save_student(stu)
        messagebox.showinfo("Password", "Password changed.")
        self.new_pw_entry.delete(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = UniversityGUI(root)
    root.mainloop()
