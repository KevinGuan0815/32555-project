[README.txt](https://github.com/user-attachments/files/28176247/README.txt)
UNIVERSITY CLI APPLICATION – README (TXT VERSION)

1) PROJECT OVERVIEW
This command-line application implements the University Management System required in Assessment 1 – Part 2.
It integrates three subsystems in one program:
  • Student System (Dev A): registration and login
  • Subject Enrolment System (Dev B): enrol/remove/show subjects, change password
  • Admin System (Dev C): list/group/partition students, remove by ID, clear database (with backup)
All data operations read/write a single JSON file via a shared datastore API.

2) FILES IN THIS PROJECT
  • unified_university_app.py     ← main CLI program (integrated Dev A/B/C + datastore)
  • students.data.json            ← JSON datastore (see Section 6 for schema)

NOTE: The original brief refers to a file named "students.data". If your marker requires that name, set
DATA_FILE = "students.data" in the datastore section inside unified_university_app.py. Functionality remains identical.

3) ALIGNMENT WITH TEACHER REQUIREMENTS (PART 2 SPEC)
  • Four menus: University / Student / Subject Enrolment / Admin (wording and indentation match sample I/O)
  • Student System: register + login with regex validation
       - Email must end with "@university.com" (case-insensitive)
       - Password must match regex: ^[A-Z][A-Za-z]{4,}\d{3,}$
  • Subject Enrolment System (Dev B):
       - (s) show subjects → print ID  Mark  Grade; then Average: XX.XX
       - (e) enrol subject → auto 3-digit ID (001–999), random mark 25–100, graded to Z/P/C/D/HD
       - Enrol cap = 4 subjects; 5th attempt prints: "Students are allowed to enrol in 4 subjects only."
       - (r) remove subject → validate 3-digit ID; not found → "Subject not found."; format error → "Invalid subject ID format."
       - (c) change password → validates using same regex as Dev A; on success updates both password fields
       - (x) exit → return to Student System
       - Average mark recomputed and persisted after every enrol/remove
  • Admin System:
       - Show all students
       - Group students by grade (A/B/C/D/F, based on overall average)
       - PASS/FAIL categorization (threshold: average ≥ 50)
       - Remove student by 6-digit ID
       - Clear database (with backup to .bak)
  • Error handling: invalid/empty input prints friendly messages; the program does not crash.

4) MENUS & OPTIONS (WORDING)
UNIVERSITY SYSTEM
  (A) Admin
  (S) Student
  (X) Exit

STUDENT SYSTEM
  (l) login
  (r) register
  (x) exit

SUBJECT ENROLMENT SYSTEM (Dev B)
  (c) change password
  (e) enrol subject
  (r) remove subject
  (s) show subjects
  (x) exit

ADMIN SYSTEM (Dev C)
  1) Show all students
  2) Group by grade
  3) PASS/FAIL categorization
  4) Remove student by ID
  5) Clear database
  0) Back

5) VALIDATION RULES
Email: must end with @university.com (case-insensitive).
Password: must match ^[A-Z][A-Za-z]{4,}\d{3,}$ (starts with uppercase, ≥5 letters, ≥3 digits).
Subject ID: 3-digit zero-padded string (001..999); we zero-pad user input (e.g., "7" → "007").
Student ID: 6-digit zero-padded string (000001..999999).

6) DATA STORAGE (JSON)
File: students.data.json (configurable to students.data)
Schema (minimal fields):
[
  {
    "student_id": "000123",
    "id": "000123",                   # maintained for compatibility
    "name": "John Smith",
    "email": "john.smith@university.com",
    "password": "HelloWorld123",
    "student_password": "HelloWorld123",  # kept in sync with password
    "subjects": [
      { "id": "084", "mark": 76, "grade": "D" },
      { "id": "245", "mark": 63, "grade": "P" }
    ],
    "avg_mark": 69.50
  }
]
All CRUD operations (register/login/enrol/remove/change/show/admin) interact with this file through the datastore
functions: read_all_students / write_all_students / get_student_by_id / save_student / backup_before_clear.

7) GRADE MAPPING
Per Part 1 policy for individual subjects:
  Z  < 50
  P  50–64
  C  65–74
  D  75–84
  HD ≥ 85
Admin grouping view uses A/B/C/D/F labels based on average mark; PASS if average ≥ 50, otherwise FAIL.

8) HOW TO RUN
Prerequisites: Python 3.x
Steps:
  1) Place unified_university_app.py and students.data.json in the same folder.
  2) Open a terminal in that folder.
  3) Run:  python unified_university_app.py
  4) Navigate: University → Student → (r) register or (l) login → Subject Enrolment System.

9) DEMO SCRIPT (FOR PRESENTATION)
Student System → (l) login → Subject Enrolment System
  a) (s) show → "No subjects enrolled." if none
  b) (e) enrol → prints "Subject 0xx enrolled."; then (s) show → list + Average
  c) Repeat (e) to reach 4 subjects; the 5th (e) prints "Students are allowed to enrol in 4 subjects only."
  d) (r) remove → test existing ID (success) and non-existing ID (prints "Subject not found.")
  e) (c) change → test invalid password (prints "Invalid password format.") then valid (prints "Password changed successfully.")
  f) (x) exit → back to Student System; switch to Admin System to show updated lists and PASS/FAIL.

10) TEST CHECKLIST
  [ ] Show with empty subjects prints: "No subjects enrolled."
  [ ] Enrol 1..4 subjects; average mark recomputes; the 5th enrol is blocked with required message.
  [ ] Remove existing subject by 3-digit ID; non-existing prints: "Subject not found."
  [ ] Change password invalid → prints: "Invalid password format."; valid → persists and prints success.
  [ ] Persistence: restart program; data remains updated; Admin views reflect changes.

11) DESIGN PRINCIPLES
  • Single Source of Truth: one datastore used by Dev A/B/C
  • Consistency: Subject ID formatting, password regex reuse, sample I/O wording
  • Robustness: invalid/empty inputs handled; non-crashing behaviour
  • Immediate Persistence: save to JSON after each change; reload in menu to keep RAM/disk in sync
  • Compatibility: maintain both student_id/id and password/student_password fields

12) INDIVIDUAL CONTRIBUTIONS (EXAMPLE; ADAPT TO YOUR GROUP)
  • Dev A – Eduardo Hernandez Dominguez: Student System (register/login), regex validation, ID generation, handoff to Dev B
  • Dev B – Huanyu Yang: Subject Enrolment System (c/e/r/s), 4-subject cap, 3-digit ID, random marks, Z/P/C/D/HD mapping,
                         average recomputation, datastore persistence, dual-password field update for compatibility
  • Dev C – Dan Zhang: Admin System (show, group by grade, PASS/FAIL, remove by ID, clear with backup)
  • Wenqing Guan: Requirements, UML/use-cases/class design, I/O wording alignment, integration support

13) SUBMISSION NOTES (PART 2 & PART 3)
  • Submit a single .zip for the group under Canvas (Part 2). Include source code and this README.
  • Zip naming format per Canvas: group<group-number>-Cmp1<lab-number>.zip
  • Part 3: In-person showcase. Each member must present their section and code walkthrough.
  • Do NOT submit AI-generated code. Ensure your final code and comments are your own work.

14) CONFIGURATION NOTES
  • To use the original filename in the brief, set DATA_FILE = "students.data" in unified_university_app.py.
  • All messages should match the sample I/O wording; avoid extra prints in error paths.

15) CONTACT / HELP
If the datastore appears empty, verify that students.data.json is valid JSON (an array of student objects).
Ensure emails end with @university.com and passwords match the regex before login.
