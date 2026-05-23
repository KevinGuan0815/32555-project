"""
Unified University CLI Application
- Auth + Student registration/login      (from dev_a_EDUARDO.py)
- Subject enrolment / password change    (from enrolment_devb_huanyu.py)
- Admin reporting / remove / clear       (from admin_devC_dan.py)
- Single datastore (JSON) with function-style API so other parts can call.

Run:
    python unified_university_app.py
"""

import json
import os
import random
import re
from typing import Dict, List, Optional

# ==========================
# 1. Datastore (shared) Wenqing Guan
# ==========================

DATA_FILE = "students.data.json"     


def _ds_load() -> List[dict]:
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def _ds_save(students: List[dict]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(students, f, ensure_ascii=False, indent=2)



def read_all_students() -> List[dict]:
    return _ds_load()


def write_all_students(students: List[dict]) -> None:
    _ds_save(students)


def get_student_by_id(student_id: str) -> Optional[dict]:
    for s in _ds_load():
        if s.get("id") == student_id:
            return s
    return None


def save_student(student: dict) -> bool:
    students = _ds_load()

    sid = student.get("student_id") or student.get("id")
    if not sid:
        return False
    student["student_id"] = sid
    student["id"] = sid

    if "student_password" in student and "password" not in student:
        student["password"] = student["student_password"]
    if "password" in student and "student_password" not in student:
        student["student_password"] = student["password"]

    for i, s in enumerate(students):
        if s.get("student_id") == sid or s.get("id") == sid:
            students[i] = student
            _ds_save(students)
            return True

    students.append(student)
    _ds_save(students)
    return True


# ==========================
# 2. Dev A: Auth / CLI base Eduardo.HernandezDominguez
# ==========================

EMAIL_RE = re.compile(r"@university\.com$", re.IGNORECASE)
PASS_RE = re.compile(r"^[A-Z][A-Za-z]{4,}\d{3,}$")


class DataStore:
    """Class-style datastore kept for AuthService – it uses the same DATA_FILE."""

    def __init__(self, file_path: str = DATA_FILE):
        self.file_path = file_path

    def load_students(self) -> list:
        return _ds_load()

    def save_students(self, students: list) -> None:
        _ds_save(students)

    def update_student(self, student: dict) -> None:
        save_student(student)


class AuthService:
    def __init__(self, datastore: DataStore):
        self.datastore = datastore

    def validate_email(self, email: str) -> bool:
        email = (email or "").strip().lower()
        return bool(EMAIL_RE.search(email))

    def validate_password(self, password: str) -> bool:
        return PASS_RE.match(password or "") is not None

    def generate_student_id(self) -> str:
        students = self.datastore.load_students()
        used = {s.get("student_id") for s in students}
        while True:
            n = random.randint(1, 999_999)
            sid = f"{n:06d}"
            if sid not in used:
                return sid

    def register(self, name: str, email: str, password: str):
        name = (name or "").strip()
        email = (email or "").strip().lower()
        password = (password or "").strip()

        if not self.validate_email(email):
            print("Invalid email format. (must end with @university.com)")
            return None
        if not self.validate_password(password):
            print("Invalid password format. (A-Z + letters>=4 + digits>=3)")
            return None

        students = self.datastore.load_students()
        if any(s.get("email") == email for s in students):
            print("Email already registered.")
            return None

        new_student = {
            "name": name,
            "email": email,
            "student_password": password,
            "password": password,          # keep both fields
            "student_id": self.generate_student_id(),
            "id": None,                    # will be set below
            "subjects": []
        }
        new_student["id"] = new_student["student_id"]
        save_student(new_student)
        print(f"Registration successful. Your ID is {new_student['student_id']}")
        return new_student

    def match_credentials(self, email: str, password: str):
        students = self.datastore.load_students()
        for s in students:
            if s.get("email") == email and (
                s.get("student_password") == password or s.get("password") == password
            ):
                return s
        return None

    def authenticate(self, email: str, password: str):
        email = (email or "").strip().lower()
        password = (password or "").strip()
        if not self.validate_email(email):
            print("Invalid email format.")
            return None
        if not self.validate_password(password):
            print("Invalid password format.")
            return None
        user = self.match_credentials(email, password)
        if user is None:
            print("Incorrect email or password.")
            return None
        print("Login successful.")
        return user

    def login(self, email: str, password: str):
        return self.authenticate(email, password)


# ==========================
# 3. Dev B: enrolment system Hunayu Yang
# ==========================

ENROL_LIMIT = 4  # UML says 0..4


def _prompt(msg: str) -> str:
    try:
        return input(msg)
    except EOFError:
        return ""


def grade_from_mark(mark: int) -> str:
    if mark < 50: return "Z"
    elif 50 <= mark <= 64: return "P"
    elif 65 <= mark <= 74: return "C"
    elif 75 <= mark <= 84: return "D"
    else: return "HD"


def recompute_average(student: Dict) -> float:
    subjects = student.get("subjects") or []
    if not subjects:
        student["avg_mark"] = 0.0
        return 0.0
    marks = [s.get("mark") for s in subjects if isinstance(s.get("mark"), (int, float))]
    avg = sum(marks) / len(marks) if marks else 0.0
    student["avg_mark"] = round(avg, 2)
    return student["avg_mark"]


def gen_subject_id(existing_ids: List[str]) -> str:
    tried = set()
    while True:
        n = random.randint(1, 999)
        sid = f"{n:03d}"
        if sid not in existing_ids and sid not in tried:
            return sid
        tried.add(sid)


def enrol_handle_show(student: Dict):
    subjects = student.get("subjects") or []
    if not subjects:
        print("No subjects enrolled.")
        return
    print("Subjects:")
    for s in subjects:
        sid = str(s.get("id")).zfill(3)
        mark = s.get("mark")
        grade = s.get("grade")
        print(f"{sid}  {mark}  {grade}")
    avg = recompute_average(student)
    print(f"Average: {avg:.2f}")


def enrol_handle_enrol(student: Dict):
    subjects = student.get("subjects") or []
    if len(subjects) >= ENROL_LIMIT:
        print("Students are allowed to enrol in 4 subjects only.")
        return
    existing = [str(s.get("id")).zfill(3) for s in subjects]
    sid = gen_subject_id(existing)
    mark = random.randint(25, 100)
    grade = grade_from_mark(mark)
    new_subj = {"id": sid, "mark": mark, "grade": grade}
    subjects.append(new_subj)
    student["subjects"] = subjects
    recompute_average(student)
    if save_student(student):
        print(f"Subject {sid} enrolled.")
    else:
        print("(error) Failed to save subject.")


def enrol_handle_remove(student: Dict):
    raw = _prompt("Enter subject ID: ")
    target = (raw or "").strip().zfill(3)
    if not target.isdigit() or len(target) != 3:
        print("Invalid subject ID format.")
        return
    subjects = student.get("subjects") or []
    before = len(subjects)
    subjects = [s for s in subjects if str(s.get("id")).zfill(3) != target]
    if len(subjects) == before:
        print("Subject not found.")
        return
    student["subjects"] = subjects
    recompute_average(student)
    if save_student(student):
        print(f"Subject {target} removed.")
    else:
        print("(error) Failed to save changes.")


def enrol_handle_change(student: Dict):
    new_pw = _prompt("Enter new password: ")
    if not PASS_RE.match(new_pw or ""):
        print("Invalid password format.")
        return
    student["student_password"] = new_pw
    student["password"] = new_pw  # keep two fields
    if save_student(student):
        print("Password changed successfully.")
    else:
        print("(error) Failed to save password.")


def run_enrolment_menu(session: Dict):
    sid = session.get("studentId")
    student = get_student_by_id(sid)
    if not student:
        print(f"(error) Student {sid} not found.")
        return
    while True:
        print("=== Subject Enrolment System ===")
        print("(c) change password")
        print("(e) enrol subject")
        print("(r) remove subject")
        print("(s) show subjects")
        print("(x) exit")
        opt = (_prompt("Select an option: ") or "").strip().lower()
        if opt == "x":
            print("Returning to Student System.")
            break
        elif opt == "s":
            enrol_handle_show(student)
        elif opt == "e":
            enrol_handle_enrol(student)
            student = get_student_by_id(sid) or student
        elif opt == "r":
            enrol_handle_remove(student)
            student = get_student_by_id(sid) or student
        elif opt == "c":
            enrol_handle_change(student)
            student = get_student_by_id(sid) or student
        else:
            print("Invalid option.")


# ==========================
# 4. Dev C: Admin system Dan Zhang
# ==========================

PASS_THRESHOLD = 50


def _admin_prompt(msg: str) -> str:
    try:
        return input(msg)
    except EOFError:
        return ""


def _avg_mark(student: dict):
    subs = student.get("subjects") or []
    if not subs:
        return None
    marks = [s.get("mark") for s in subs if isinstance(s.get("mark"), (int, float)) and 0 <= s.get("mark") <= 100]
    if not marks:
        return None
    return sum(marks) / len(marks)


def _grade_from_avg(avg):
    if avg is None:
        return "N/A"
    elif 85 <= avg <= 100:
        return "A"
    elif 70 <= avg < 85:
        return "B"
    elif 60 <= avg < 70:
        return "C"
    elif 50 <= avg < 60:
        return "D"
    else:
        return "F"


def view_all_students():
    return read_all_students()


def view_students_by_grade():
    all_students = read_all_students()
    students_by_grade = {}

    # use student_id as key first, fallback to id
    student_avgs = { (student.get("student_id") or student.get("id")): _avg_mark(student) for student in all_students }

    for student in all_students:
        key = student.get("student_id") or student.get("id")
        avg = student_avgs.get(key)
        grade = _grade_from_avg(avg)
        students_by_grade.setdefault(grade, []).append(student)

    for grade, students_in_grade in students_by_grade.items():
        students_in_grade.sort(
            key=lambda student: (student_avgs.get(student.get("student_id") or student.get("id")) if student_avgs.get(student.get("student_id") or student.get("id")) is not None else -1),
            reverse=True
        )
    return students_by_grade


def pass_fail_categorization():
    all_students = read_all_students()
    categorized_students = {"PASS": [], "FAIL": []}
    student_avgs = { (student.get("student_id") or student.get("id")): _avg_mark(student) for student in all_students }

    for student in all_students:
        key = student.get("student_id") or student.get("id")
        avg = student_avgs.get(key)
        category = "PASS" if (avg is not None and avg >= PASS_THRESHOLD) else "FAIL"
        categorized_students[category].append(student)

    for category, students_in_category in categorized_students.items():
        students_in_category.sort(
            key=lambda student: (student_avgs.get(student.get("student_id") or student.get("id")) if student_avgs.get(student.get("student_id") or student.get("id")) is not None else -1),
            reverse=True
        )

    return categorized_students


def remove_student_admin(student_id: str) -> bool:
    all_students = read_all_students()
    remaining_students = [
        student for student in all_students
        if (student.get("student_id") or student.get("id")) != student_id
    ]

    if len(remaining_students) == len(all_students):
        return False

    write_all_students(remaining_students)
    return True


def clear_all(user_confirmation: str) -> bool:
    if user_confirmation != "CLEAR":
        return False
    try:
        write_all_students([])
        return True
    except Exception:
        return False


def _format_avg(stu: dict) -> str:
    avg = _avg_mark(stu)
    return f"{avg:.1f}" if avg is not None else "N/A"


def _print_student_line(student: dict) -> None:
    student_id = student.get("student_id") or student.get("id") or "??????"
    student_name = student.get("name", "(no name)")
    subjects_cnt = len(student.get("subjects") or [])
    avg_str = _format_avg(student)
    print(f"{student_id}  {student_name:20}  avg={avg_str}  subjects={subjects_cnt}")


def _print_section_title(title: str) -> None:
    print("\n" + title)
    print("-" * len(title))


def _prompt_six_digit_id() -> Optional[str]:
    student_id = _admin_prompt("Enter 6-digit student ID to remove: ").strip()
    if not (len(student_id) == 6 and student_id.isdigit()):
        print("Invalid ID format. It should be exactly 6 digits (e.g., 000123).")
        return None
    return student_id


def _confirm_clear() -> bool:
    confirm_text = _admin_prompt("Type 'CLEAR' to wipe all students: ").strip()
    if confirm_text != "CLEAR":
        print("Cancelled.")
        return False
    return True


def admin_menu() -> None:
    while True:
        print("\n=== Admin System ===")
        print("1) Show all students")
        print("2) Group by grade")
        print("3) PASS/FAIL categorization")
        print("4) Remove student by ID")
        print("5) Clear database")
        print("0) Back")
        choice = _admin_prompt("Select an option: ").strip()

        if choice == "0":
            print("Returning to University System...")
            break

        elif choice == "1":
            all_students = view_all_students()
            if not all_students:
                print("(empty) No students found.")
            else:
                _print_section_title("All Students")
                for student in all_students:
                    _print_student_line(student)

        elif choice == "2":
            students_by_grade = view_students_by_grade()
            if not students_by_grade:
                print("(empty) No students found.")
            else:
                _print_section_title("Students Grouped by Grade")
                for grade in sorted(students_by_grade.keys()):
                    group = students_by_grade[grade]
                    print(f"\n[Grade {grade}]  count={len(group)}")
                    for student in group:
                        _print_student_line(student)

        elif choice == "3":
            pass_fail = pass_fail_categorization()
            _print_section_title("PASS / FAIL Categorization")
            print(f"\n[PASS] ({len(pass_fail['PASS'])})")
            for student in pass_fail["PASS"]:
                _print_student_line(student)
            print(f"\n[FAIL] ({len(pass_fail['FAIL'])})")
            for student in pass_fail["FAIL"]:
                _print_student_line(student)

        elif choice == "4":
            student_id = _prompt_six_digit_id()
            if student_id is None:
                continue
            removed = remove_student_admin(student_id)
            print("Removed." if removed else "Not found.")

        elif choice == "5":
            if _confirm_clear() and clear_all("CLEAR"):
                print("Database cleared.")

        else:
            print("Invalid option. Please choose 0–5.")


# ==========================
# 5. Top-level CLI app Eduardo.HernandezDominguez
# ==========================

class CLIUApp:
    def __init__(self):
        self.ds = DataStore()
        self.auth = AuthService(self.ds)

    def start(self) -> None:
        while True:
            print("=== University System ===")
            print("(A) Admin")
            print("(S) Student")
            print("(X) Exit")
            choice = input("Select an option: ").strip().upper()
            if choice == "X":
                break
            elif choice == "S":
                self.show_student_menu()
            elif choice == "A":
                self.show_admin_menu()
            else:
                print("Invalid option.")

    def show_student_menu(self) -> None:
        while True:
            print("=== Student System ===")
            print("(l) login")
            print("(r) register")
            print("(x) exit")
            opt = input("Select an option: ").strip().lower()
            if opt == "x":
                print("Returning to University System.")
                break
            elif opt == "r":
                name = input("Enter name: ")
                email = input("Enter university email: ")
                password = input("Enter password: ")
                self.auth.register(name, email, password)
            elif opt == "l":
                email = input("Enter email: ")
                password = input("Enter password: ")
                user = self.auth.login(email, password)
                if user is not None:
                    self._handoff_to_enrolment(user["student_id"])
            else:
                print("Invalid option.")

    def show_admin_menu(self) -> None:
        admin_menu()

    def _handoff_to_enrolment(self, student_id: str):
        # real handoff
        run_enrolment_menu({"studentId": student_id})


if __name__ == "__main__":
    CLIUApp().start()
