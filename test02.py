import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
import sqlite3
from datetime import datetime

# 数据库初始化
class HospitalDatabase:
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        # 直接创建表
        # 1. 创建用户表
        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS User (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    login_name TEXT NOT NULL UNIQUE,
                    pwd_hash TEXT NOT NULL,
                    role_code TEXT NOT NULL CHECK (role_code IN ('Admin', 'Doctor', 'Patient')),
                    entity_id INTEGER NOT NULL
                )
                ''')

        # 2. 创建业务表
        # 2.1 科室表
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Department (
                    dept_id INTEGER PRIMARY KEY,
                    dept_name TEXT NOT NULL,
                    location TEXT,
                    phone TEXT,
                    description TEXT
                )
                """)

        # 2.2 医生表
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Doctor (
                    doctor_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    gender TEXT NOT NULL CHECK (gender IN ('男', '女')),
                    title TEXT NOT NULL CHECK (title IN ('主任医师', '副主任医师', '主治医师', '住院医师')),
                    contact TEXT,
                    dept_id INTEGER NOT NULL,
                    FOREIGN KEY (dept_id) REFERENCES Department(dept_id)
                )
                """)

        # 2.3 病人表
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Patient (
                    patient_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    gender TEXT NOT NULL CHECK (gender IN ('男', '女')),
                    age INTEGER,
                    id_card TEXT UNIQUE NOT NULL,
                    contact TEXT,
                    address TEXT
                )
                """)

        # 2.4 排班表
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Schedule (
                    schedule_id INTEGER PRIMARY KEY,
                    doctor_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    time_slot TEXT NOT NULL,
                    location TEXT NOT NULL CHECK (location IN ('门诊', '住院部')),
                    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id),
                    UNIQUE (doctor_id, date, time_slot)
                )
                """)

        # 2.5 管理员表
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Administrator (
                    AdminID INTEGER PRIMARY KEY,
                    AdminName TEXT NOT NULL,
                    Password TEXT NOT NULL,
                    contact TEXT
                )
                """)

        # 2.6 病房表
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Ward (
                    ward_id INTEGER PRIMARY KEY,
                    dept_id INTEGER,
                    location TEXT,
                    charge_standard REAL,
                    FOREIGN KEY (dept_id) REFERENCES Department(dept_id)
                )
                """)

        # 2.7 病床表
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Bed (
                    ward_id INTEGER,
                    bed_no INTEGER,
                    status TEXT NOT NULL CHECK (status IN ('空闲', '已占用')),
                    PRIMARY KEY (ward_id, bed_no),
                    FOREIGN KEY (ward_id) REFERENCES Ward(ward_id)
                )
                """)

        # 2.8 药品表
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Medicine (
                    medicine_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    specification TEXT,
                    price REAL NOT NULL,
                    stock INTEGER NOT NULL CHECK (stock >= 0),
                    manufacturer TEXT,
                    description TEXT
                )
                """)

        # 2.9 挂号表
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Registration (
                    reg_id INTEGER PRIMARY KEY,
                    patient_id INTEGER NOT NULL,
                    dept_id INTEGER NOT NULL,
                    doctor_id INTEGER NOT NULL,
                    reg_time DATETIME NOT NULL,
                    fee REAL NOT NULL,
                    status TEXT CHECK (status IN ('待就诊', '已就诊')),
                    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
                    FOREIGN KEY (dept_id) REFERENCES Department(dept_id),
                    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id)
                )
                """)

        # 2.10 处方表
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Prescription (
                    prescription_id INTEGER PRIMARY KEY,
                    reg_id INTEGER NOT NULL UNIQUE,
                    diagnosis TEXT NOT NULL,
                    date DATE NOT NULL,
                    FOREIGN KEY (reg_id) REFERENCES Registration(reg_id)
                )
                """)

        # 2.11 药品清单表
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Medicine_List (
                    prescription_id INTEGER NOT NULL,
                    medicine_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL CHECK (quantity > 0),
                    usage TEXT,
                    dosage TEXT,
                    PRIMARY KEY (prescription_id, medicine_id),
                    FOREIGN KEY (prescription_id) REFERENCES Prescription(prescription_id),
                    FOREIGN KEY (medicine_id) REFERENCES Medicine(medicine_id)
                )
                """)

        # 2.12 处方费用表
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Prescription_Fee (
                    prescription_id INTEGER PRIMARY KEY,
                    diagnosis_fee REAL NOT NULL,
                    medicine_fee REAL NOT NULL,
                    total_fee REAL NOT NULL,
                    payment_status TEXT CHECK (payment_status IN ('未支付', '已支付')),
                    FOREIGN KEY (prescription_id) REFERENCES Prescription(prescription_id)
                )
                """)

        # 2.13 住院档案表
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Hospitalization (
                    hospitalization_id INTEGER PRIMARY KEY,
                    patient_id INTEGER NOT NULL,
                    admission_time DATETIME NOT NULL,
                    discharge_time DATETIME,
                    ward_id INTEGER NOT NULL,
                    bed_no INTEGER NOT NULL,
                    doctor_id INTEGER NOT NULL,
                    status TEXT CHECK (status IN ('在院', '已出院')),
                    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
                    FOREIGN KEY (ward_id, bed_no) REFERENCES Bed(ward_id, bed_no),
                    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id)
                )
                """)

        # 2.14 住院记录表
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Hospitalization_Record (
                    record_id INTEGER PRIMARY KEY,
                    hospitalization_id INTEGER NOT NULL,
                    record_time DATETIME NOT NULL,
                    condition_description TEXT NOT NULL,
                    treatment_plan TEXT NOT NULL,
                    FOREIGN KEY (hospitalization_id) REFERENCES Hospitalization(hospitalization_id)
                )
                """)

        # 2.15 住院费用表
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Hospitalization_Fee (
                    fee_id INTEGER PRIMARY KEY,
                    hospitalization_id INTEGER NOT NULL,
                    fee_date DATE NOT NULL,
                    bed_fee REAL NOT NULL,
                    treatment_fee REAL NOT NULL,
                    medicine_fee REAL NOT NULL,
                    other_fee REAL NOT NULL,
                    total_fee REAL NOT NULL,
                    FOREIGN KEY (hospitalization_id) REFERENCES Hospitalization(hospitalization_id)
                )
                """)
        # 3. 插入测试数据
        self.insert_test_data()
        self.conn.commit()
    def hash_password(self, password):
        """密码哈希函数"""
        return hashlib.sha256(password.encode()).hexdigest()

    def insert_test_data(self):
        """插入测试数据"""
        try:
            # 插入科室数据 (admin.Department)
            self.cursor.executemany("""
            INSERT INTO Department (dept_id, dept_name, location, phone, description)
            VALUES (?, ?, ?, ?, ?)
            """, [
                (101, '呼吸科', '门诊楼3层', '010-8888101', '擅长呼吸系统疾病诊疗'),
                (102, '消化科', '门诊楼4层', '010-8888102', '专注胃肠疾病治疗'),
                (103, '心血管科', '住院部B座5层', '010-8888103', '心脏疾病专科'),
                (104, '外科', '住院部A座6层', '010-8888104', '各类外科手术'),
                (105, '儿科', '门诊楼2层', '010-8888105', '儿童疾病诊疗')
            ])

            # 插入管理员数据 (admin.Administrator)
            self.cursor.executemany("""
            INSERT INTO Administrator (AdminID, AdminName, Password, contact)
            VALUES (?, ?, ?, ?)
            """, [
                (1, '张大明', 'Admin@123', '13800138001'),
                (2, '李华', 'Admin@456', '13900139002'),
                (3, '王芳', 'Admin@789', '13600136003'),
                (4, '陈刚', 'Admin@abc', '13700137004'),
                (5, '赵敏', 'Admin@xyz', '13500135005')
            ])

            # 插入病房数据 (admin.Ward)
            self.cursor.executemany("""
            INSERT INTO Ward (ward_id, dept_id, location, charge_standard)
            VALUES (?, ?, ?, ?)
            """, [
                (201, 101, '住院部B座301室', 800.00),
                (202, 101, '住院部B座302室', 800.00),
                (203, 103, '住院部B座501室', 1000.00),
                (204, 103, '住院部B座502室', 1000.00),
                (205, 103, '住院部B座503室', 1000.00)
            ])

            # 插入病床数据 (admin.Bed)
            self.cursor.executemany("""
            INSERT INTO Bed (ward_id, bed_no, status)
            VALUES (?, ?, ?)
            """, [
                (201, 1, '空闲'),
                (201, 2, '已占用'),
                (202, 1, '空闲'),
                (203, 1, '已占用'),
                (205, 1, '空闲')
            ])

            # 插入医生数据 (doc.Doctor)
            self.cursor.executemany("""
            INSERT INTO Doctor (doctor_id, name, gender, title, contact, dept_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """, [
                (100001, '张伟', '男', '主任医师', '13811111111', 101),
                (100002, '李娜', '女', '副主任医师', '13922222222', 102),
                (100003, '王军', '男', '主治医师', '13633333333', 103),
                (100004, '陈雨', '女', '住院医师', '13744444444', 104),
                (100005, '赵敏', '女', '主治医师', '13555555555', 105)
            ])

            # 插入药品数据 (doc.Medicine)
            self.cursor.executemany("""
            INSERT INTO Medicine (medicine_id, name, specification, price, stock, manufacturer, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [
                (101, '阿莫西林胶囊', '0.25g*24粒', 15.50, 100, 'XX制药厂', '抗生素'),
                (102, '奥美拉唑肠溶胶囊', '20mg*14粒', 28.80, 80, 'YY药业', '胃药'),
                (103, '硝酸甘油片', '0.5mg*100片', 12.00, 50, 'ZZ医药', '心血管药物'),
                (104, '布洛芬缓释胶囊', '0.3g*10粒', 18.00, 120, 'AAA公司', '止痛药'),
                (105, '小儿感冒颗粒', '6g*10袋', 22.50, 90, 'BBB制药', '儿童感冒药')
            ])

            # 插入排班数据 (doc.Schedule)
            self.cursor.executemany("""
            INSERT INTO Schedule (schedule_id, doctor_id, date, time_slot, location)
            VALUES (?, ?, ?, ?, ?)
            """, [
                (1, 100001, '2025-05-24', '上午09:00-11:30', '门诊'),
                (2, 100002, '2025-05-24', '下午14:00-16:30', '门诊'),
                (3, 100003, '2025-05-25', '上午08:30-11:00', '住院部'),
                (4, 100004, '2025-05-25', '下午13:30-15:30', '门诊'),
                (5, 100005, '2025-05-26', '上午09:00-11:30', '门诊')
            ])

            # 插入病人数据 (pat.Patient)
            self.cursor.executemany("""
            INSERT INTO Patient (patient_id, name, gender, age, id_card, contact, address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [
                (1000001, '张三', '男', 30, '110101200001011234', '13800138001', '北京市朝阳区'),
                (1000002, '李四', '女', 25, '120102199902023456', '13900139002', '上海市黄浦区'),
                (1000003, '王五', '男', 45, '130103198003035678', '13600136003', '广州市天河区'),
                (1000004, '赵六', '女', 50, '140104197504047890', '13700137004', '深圳市南山区'),
                (1000005, '周七', '男', 18, '150105200505059012', '13500135005', '杭州市西湖区')
            ])

            # 插入挂号数据 (pat.Registration)
            self.cursor.executemany("""
            INSERT INTO Registration (reg_id, patient_id, dept_id, doctor_id, reg_time, fee, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [
                (1, 1000001, 101, 100001, '2025-05-24 08:30:00', 50.00, '已就诊'),
                (2, 1000002, 102, 100002, '2025-05-24 10:00:00', 50.00, '已就诊'),
                (3, 1000003, 103, 100003, '2025-05-24 14:30:00', 80.00, '已就诊'),
                (4, 1000004, 104, 100004, '2025-05-25 09:00:00', 80.00, '已就诊'),
                (5, 1000005, 105, 100005, '2025-05-25 13:30:00', 30.00, '已就诊')
            ])

            # 插入处方数据 (doc.Prescription)
            self.cursor.executemany("""
            INSERT INTO Prescription (prescription_id, reg_id, diagnosis, date)
            VALUES (?, ?, ?, ?)
            """, [
                (1, 1, '上呼吸道感染', '2025-05-24'),
                (2, 2, '胃炎', '2025-05-24'),
                (3, 3, '高血压', '2025-05-24'),
                (4, 4, '外伤感染', '2025-05-25'),
                (5, 5, '儿童发热', '2025-05-25')
            ])

            # 插入药品清单数据 (doc.Medicine_List)
            self.cursor.executemany("""
            INSERT INTO Medicine_List (prescription_id, medicine_id, quantity, usage, dosage)
            VALUES (?, ?, ?, ?, ?)
            """, [
                (1, 101, 2, '口服，每日三次', '0.25g'),
                (2, 102, 1, '口服，每日一次', '20mg'),
                (3, 103, 1, '必要时舌下含服', '0.5mg'),
                (4, 104, 1, '口服，每日两次', '0.3g'),
                (5, 105, 2, '冲服，每日三次', '6g')
            ])

            # 插入处方费用数据 (doc.Prescription_Fee)
            self.cursor.executemany("""
            INSERT INTO Prescription_Fee (prescription_id, diagnosis_fee, medicine_fee, total_fee, payment_status)
            VALUES (?, ?, ?, ?, ?)
            """, [
                (1, 50.00, 31.00, 81.00, '已支付'),
                (2, 50.00, 28.80, 78.80, '已支付'),
                (3, 80.00, 12.00, 92.00, '已支付'),
                (4, 80.00, 18.00, 98.00, '已支付'),
                (5, 30.00, 45.00, 75.00, '已支付')
            ])
            # 插入住院档案数据 (pat.Hospitalization)
            self.cursor.executemany("""
            INSERT INTO Hospitalization (hospitalization_id, patient_id, admission_time, discharge_time, ward_id, bed_no, doctor_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (1, 1000001, '2025-05-20 10:00:00', None, 201, 2, 100001, '在院'),
                (2, 1000002, '2025-05-18 14:00:00', '2025-05-23 09:00:00', 202, 1, 100002, '已出院'),
                (3, 1000003, '2025-05-22 08:30:00', None, 203, 1, 100003, '在院'),
                (4, 1000004, '2025-05-25 15:00:00', None, 205, 1, 100004, '在院'),
                (5, 1000005, '2025-05-26 10:30:00', None, 201, 1, 100005, '在院')
            ])
            # 插入住院记录数据 (pat.Hospitalization_Record)
            self.cursor.executemany("""
            INSERT INTO Hospitalization_Record (record_id, hospitalization_id, record_time, condition_description, treatment_plan)
            VALUES (?, ?, ?, ?, ?)
            """, [
                (1, 1, '2025-05-20 10:30:00', '咳嗽、发热3天', '抗生素治疗，支持疗法'),
                (2, 2, '2025-05-18 15:00:00', '胃痛、反酸1周', '抑酸治疗，饮食调整'),
                (3, 3, '2025-05-22 09:00:00', '高血压病史5年，近期血压控制不佳', '调整降压药物，监测血压'),
                (4, 4, '2025-05-25 16:00:00', '右下肢外伤后感染', '清创换药，抗生素治疗'),
                (5, 5, '2025-05-26 11:00:00', '儿童发热2天', '退热治疗，观察病情变化')
            ])
            # 插入住院费用数据 (pat.Hospitalization_Fee)
            self.cursor.executemany("""
            INSERT INTO Hospitalization_Fee (fee_id, hospitalization_id, fee_date, bed_fee, treatment_fee, medicine_fee, other_fee, total_fee)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (1, 1, '2025-05-24', 800.00, 200.00, 150.00, 50.00, 1200.00),
                (2, 2, '2025-05-23', 800.00, 150.00, 100.00, 50.00, 1100.00),
                (3, 3, '2025-05-24', 1000.00, 300.00, 200.00, 100.00, 1600.00),
                (4, 4, '2025-05-25', 1000.00, 250.00, 180.00, 70.00, 1500.00),
                (5, 5, '2025-05-26', 800.00, 150.00, 120.00, 30.00, 1100.00)
            ])
            # 插入用户数据
            self.cursor.executemany("""
            INSERT INTO User (login_name, pwd_hash, role_code, entity_id)
            VALUES (?, ?, ?, ?)
            """, [
                ('admin1', self.hash_password('Admin@123'), 'Admin', 1),
                ('zhangwei', self.hash_password('zhang123'), 'Doctor', 100001),
                ('lina', self.hash_password('lina123'), 'Doctor', 100002),
                ('wangjun', self.hash_password('wang123'), 'Doctor', 100003),
                ('zhangsan', self.hash_password('zhangsan123'), 'Patient', 1000001),
                ('lisi', self.hash_password('lisi123'), 'Patient', 1000002),
                ('wangwu', self.hash_password('wangwu123'), 'Patient', 1000003)
            ])

            self.conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"插入测试数据时出错: {e}")

    def login(self, username, password):#用户登录验证
        hashed_pwd = self.hash_password(password)
        self.cursor.execute("""
        SELECT role_code, entity_id FROM User 
        WHERE login_name = ? AND pwd_hash = ?
        """, (username, hashed_pwd))
        result = self.cursor.fetchone()
        return result if result else (None, None)

    def get_doctor_schedule(self, doctor_id):#获取医生排班
        today = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute("""
        SELECT s.schedule_id, s.date, s.time_slot, s.location, d.dept_name
        FROM Schedule s
        JOIN Doctor doc ON s.doctor_id = doc.doctor_id
        JOIN Department d ON doc.dept_id = d.dept_id
        WHERE s.doctor_id = ? AND s.date = ?
        """, (doctor_id, today))
        return self.cursor.fetchall()

    def get_doctor_patients(self, doctor_id):#获取医生接诊的病人
        self.cursor.execute("""
        SELECT r.reg_id, r.reg_time, r.status, p.name, d.dept_name, s.time_slot
        FROM Registration r
        JOIN Patient p ON p.patient_id = r.patient_id
        JOIN Schedule s ON r.doctor_id = s.doctor_id AND date(r.reg_time) = s.date
        JOIN Department d ON r.dept_id = d.dept_id
        WHERE r.doctor_id = ?
        """, (doctor_id,))
        return self.cursor.fetchall()

    def get_patient_registrations(self, patient_id):#获取病人的挂号信息
        self.cursor.execute("""
        SELECT r.reg_id, r.dept_id, d.dept_name, r.reg_time, r.status
        FROM Registration r
        JOIN Department d ON r.dept_id = d.dept_id
        WHERE r.patient_id = ?
        """, (patient_id,))
        return self.cursor.fetchall()

    def get_patient_prescriptions(self, patient_id):#获取病人的处方信息
        self.cursor.execute("""
        SELECT pr.prescription_id, pr.date, pr.diagnosis
        FROM Prescription pr
        JOIN Registration r ON pr.reg_id = r.reg_id
        WHERE r.patient_id = ?
        """, (patient_id,))
        return self.cursor.fetchall()

    def get_department_stats(self):#获取科室统计信息
        self.cursor.execute("""
        SELECT d.dept_name, s.date, COUNT(*) as count
        FROM Schedule s
        JOIN Doctor doc ON s.doctor_id = doc.doctor_id
        JOIN Department d ON doc.dept_id = d.dept_id
        GROUP BY d.dept_name, s.date
        """)
        return self.cursor.fetchall()
    def get_doctor_stats(self):#获取医生工作量统计
        self.cursor.execute("""
        SELECT doc.doctor_id, doc.name, COUNT(r.reg_id) as count
        FROM Doctor doc
        LEFT JOIN Registration r ON doc.doctor_id = r.doctor_id
        GROUP BY doc.doctor_id, doc.name
        """)
        return self.cursor.fetchall()
    def get_patient_stats(self):#获取病人治疗情况统计
        self.cursor.execute("""
        SELECT p.name, COUNT(r.reg_id) as reg_count, COUNT(pr.prescription_id) as pres_count
        FROM Patient p
        LEFT JOIN Registration r ON p.patient_id = r.patient_id
        LEFT JOIN Prescription pr ON pr.reg_id = r.reg_id
        GROUP BY p.name
        """)
        return self.cursor.fetchall()
# GUI 界面
class HospitalManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("医院管理系统")
        self.root.geometry("800x600")
        # 创建数据库实例
        self.db = HospitalDatabase()
        # 当前用户信息
        self.current_user = None
        self.current_role = None
        self.current_entity_id = None
        # 创建登录界面
        self.create_login_frame()

    def create_login_frame(self):#创建登录界面
        self.clear_window()
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True)
        ttk.Label(frame, text="医院管理系统", font=('Arial', 16)).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(frame, text="用户名:").grid(row=1, column=0, sticky=tk.E, pady=5)
        self.username_entry = ttk.Entry(frame)
        self.username_entry.grid(row=1, column=1, pady=5)
        ttk.Label(frame, text="密码:").grid(row=2, column=0, sticky=tk.E, pady=5)
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)
        login_btn = ttk.Button(frame, text="登录", command=self.handle_login)
        login_btn.grid(row=3, column=0, columnspan=2, pady=10)
        # 测试账号提示
        ttk.Label(frame, text="测试账号:", font=('Arial', 10)).grid(row=4, column=0, sticky=tk.E, pady=5)
        test_accounts = ttk.Label(frame,
                                  text="管理员: admin1/Admin@123\n医生: zhangwei123/zhang123\n病人: zhangsan/zhangsan123",
                                  font=('Arial', 10), justify=tk.LEFT)
        test_accounts.grid(row=4, column=1, sticky=tk.W, pady=5)

    def handle_login(self):#处理登录
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("错误", "用户名和密码不能为空")
            return

        role, entity_id = self.db.login(username, password)

        if role:
            self.current_user = username
            self.current_role = role
            self.current_entity_id = entity_id

            if role == 'Admin':
                self.create_admin_dashboard()
            elif role == 'Doctor':
                self.create_doctor_dashboard()
            elif role == 'Patient':
                self.create_patient_dashboard()
        else:
            messagebox.showerror("错误", "用户名或密码错误")

    def create_admin_dashboard(self):#创建管理员仪表板
        self.clear_window()
        # 顶部菜单
        menubar = tk.Menu(self.root)
        # 科室管理菜单
        dept_menu = tk.Menu(menubar, tearoff=0)
        dept_menu.add_command(label="查看科室", command=self.show_departments)
        dept_menu.add_command(label="添加科室", command=self.add_department)
        menubar.add_cascade(label="科室管理", menu=dept_menu)
        # 医生管理菜单
        doctor_menu = tk.Menu(menubar, tearoff=0)
        doctor_menu.add_command(label="查看医生", command=self.show_doctors)
        doctor_menu.add_command(label="添加医生", command=self.add_doctor)
        menubar.add_cascade(label="医生管理", menu=doctor_menu)
        # 病人管理菜单
        patient_menu = tk.Menu(menubar, tearoff=0)
        patient_menu.add_command(label="查看病人", command=self.show_patients)
        menubar.add_cascade(label="病人管理", menu=patient_menu)
        # 统计报表菜单
        report_menu = tk.Menu(menubar, tearoff=0)
        report_menu.add_command(label="科室统计", command=self.show_dept_stats)
        report_menu.add_command(label="医生工作量", command=self.show_doctor_stats)
        report_menu.add_command(label="病人治疗情况", command=self.show_patient_stats)
        menubar.add_cascade(label="统计报表", menu=report_menu)
        # 用户菜单
        user_menu = tk.Menu(menubar, tearoff=0)
        user_menu.add_command(label="退出登录", command=self.create_login_frame)
        menubar.add_cascade(label="用户", menu=user_menu)
        self.root.config(menu=menubar)
        # 欢迎信息
        welcome_label = ttk.Label(self.root, text=f"欢迎管理员 {self.current_user}", font=('Arial', 14))
        welcome_label.pack(pady=20)
        # 显示科室统计
        self.show_dept_stats()

    def create_doctor_dashboard(self):#创建医生仪表板
        self.clear_window()
        # 顶部菜单
        menubar = tk.Menu(self.root)
        # 排班菜单
        schedule_menu = tk.Menu(menubar, tearoff=0)
        schedule_menu.add_command(label="今日排班", command=self.show_doctor_schedule)
        menubar.add_cascade(label="排班", menu=schedule_menu)
        # 病人菜单
        patient_menu = tk.Menu(menubar, tearoff=0)
        patient_menu.add_command(label="我的病人", command=self.show_my_patients)
        menubar.add_cascade(label="病人", menu=patient_menu)
        # 用户菜单
        user_menu = tk.Menu(menubar, tearoff=0)
        user_menu.add_command(label="退出登录", command=self.create_login_frame)
        menubar.add_cascade(label="用户", menu=user_menu)
        self.root.config(menu=menubar)
        # 欢迎信息
        welcome_label = ttk.Label(self.root, text=f"欢迎医生 {self.current_user}", font=('Arial', 14))
        welcome_label.pack(pady=20)
        # 显示今日排班
        self.show_doctor_schedule()

    def create_patient_dashboard(self):#创建病人仪表板
        self.clear_window()
        # 顶部菜单
        menubar = tk.Menu(self.root)
        # 挂号菜单
        reg_menu = tk.Menu(menubar, tearoff=0)
        reg_menu.add_command(label="我的挂号", command=self.show_my_registrations)
        menubar.add_cascade(label="挂号", menu=reg_menu)
        # 处方菜单
        pres_menu = tk.Menu(menubar, tearoff=0)
        pres_menu.add_command(label="我的处方", command=self.show_my_prescriptions)
        menubar.add_cascade(label="处方", menu=pres_menu)
        # 用户菜单
        user_menu = tk.Menu(menubar, tearoff=0)
        user_menu.add_command(label="退出登录", command=self.create_login_frame)
        menubar.add_cascade(label="用户", menu=user_menu)
        self.root.config(menu=menubar)
        # 欢迎信息
        welcome_label = ttk.Label(self.root, text=f"欢迎病人 {self.current_user}", font=('Arial', 14))
        welcome_label.pack(pady=20)
        # 显示我的挂号
        self.show_my_registrations()
    def clear_window(self):#清除窗口内容
        for widget in self.root.winfo_children():
            widget.destroy()

        # 清除菜单
        try:
            self.root.config(menu=tk.Menu(self.root))
        except:
            pass
    # 管理员功能
    def show_departments(self):#显示科室列表
        self.clear_content()
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # 查询科室数据
        self.db.cursor.execute("SELECT * FROM Department")
        departments = self.db.cursor.fetchall()
        # 创建表格
        tree = ttk.Treeview(frame, columns=('dept_id', 'dept_name', 'location', 'phone'), show='headings')
        tree.heading('dept_id', text='科室ID')
        tree.heading('dept_name', text='科室名称')
        tree.heading('location', text='位置')
        tree.heading('phone', text='电话')

        for dept in departments:
            tree.insert('', tk.END, values=dept)

        tree.pack(fill=tk.BOTH, expand=True)

    def add_department(self): #添加科室
        self.clear_content()
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="添加新科室", font=('Arial', 14)).grid(row=0, column=0, columnspan=2, pady=10)
        # 科室ID
        ttk.Label(frame, text="科室ID:").grid(row=1, column=0, sticky=tk.E, pady=5)
        dept_id_entry = ttk.Entry(frame)
        dept_id_entry.grid(row=1, column=1, pady=5)
        # 科室名称
        ttk.Label(frame, text="科室名称:").grid(row=2, column=0, sticky=tk.E, pady=5)
        dept_name_entry = ttk.Entry(frame)
        dept_name_entry.grid(row=2, column=1, pady=5)
        # 位置
        ttk.Label(frame, text="位置:").grid(row=3, column=0, sticky=tk.E, pady=5)
        location_entry = ttk.Entry(frame)
        location_entry.grid(row=3, column=1, pady=5)
        # 电话
        ttk.Label(frame, text="电话:").grid(row=4, column=0, sticky=tk.E, pady=5)
        phone_entry = ttk.Entry(frame)
        phone_entry.grid(row=4, column=1, pady=5)
        # 描述
        ttk.Label(frame, text="描述:").grid(row=5, column=0, sticky=tk.E, pady=5)
        desc_entry = ttk.Entry(frame)
        desc_entry.grid(row=5, column=1, pady=5)

        def save_department():#保存科室信息
            try:
                dept_id = int(dept_id_entry.get())
                dept_name = dept_name_entry.get()
                location = location_entry.get()
                phone = phone_entry.get()
                desc = desc_entry.get()
                if not dept_name:
                    messagebox.showerror("错误", "科室名称不能为空")
                    return

                self.db.cursor.execute("""
                INSERT INTO Department (dept_id, dept_name, location, phone, description)
                VALUES (?, ?, ?, ?, ?)
                """, (dept_id, dept_name, location, phone, desc))
                self.db.conn.commit()
                messagebox.showinfo("成功", "科室添加成功")
                self.show_departments()
            except sqlite3.IntegrityError:
                messagebox.showerror("错误", "科室ID已存在")
            except ValueError:
                messagebox.showerror("错误", "科室ID必须是数字")
            except Exception as e:
                messagebox.showerror("错误", f"添加科室失败: {e}")

        save_btn = ttk.Button(frame, text="保存", command=save_department)
        save_btn.grid(row=6, column=0, columnspan=2, pady=10)

    def show_doctors(self):#显示医生列表
        self.clear_content()
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # 查询医生数据
        self.db.cursor.execute("""
        SELECT d.doctor_id, d.name, d.gender, d.title, d.contact, dept.dept_name
        FROM Doctor d
        JOIN Department dept ON d.dept_id = dept.dept_id
        """)
        doctors = self.db.cursor.fetchall()
        # 创建表格
        tree = ttk.Treeview(frame, columns=('doctor_id', 'name', 'gender', 'title', 'contact', 'dept_name'),
                            show='headings')
        tree.heading('doctor_id', text='医生ID')
        tree.heading('name', text='姓名')
        tree.heading('gender', text='性别')
        tree.heading('title', text='职称')
        tree.heading('contact', text='联系方式')
        tree.heading('dept_name', text='所属科室')
        for doc in doctors:
            tree.insert('', tk.END, values=doc)

        tree.pack(fill=tk.BOTH, expand=True)

    def add_doctor(self):#添加医生
        self.clear_content()
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="添加新医生", font=('Arial', 14)).grid(row=0, column=0, columnspan=2, pady=10)
        # 医生ID
        ttk.Label(frame, text="医生ID:").grid(row=1, column=0, sticky=tk.E, pady=5)
        doctor_id_entry = ttk.Entry(frame)
        doctor_id_entry.grid(row=1, column=1, pady=5)
        # 姓名
        ttk.Label(frame, text="姓名:").grid(row=2, column=0, sticky=tk.E, pady=5)
        name_entry = ttk.Entry(frame)
        name_entry.grid(row=2, column=1, pady=5)
        # 性别
        ttk.Label(frame, text="性别:").grid(row=3, column=0, sticky=tk.E, pady=5)
        gender_var = tk.StringVar()
        ttk.Radiobutton(frame, text="男", variable=gender_var, value="男").grid(row=3, column=1, sticky=tk.W)
        ttk.Radiobutton(frame, text="女", variable=gender_var, value="女").grid(row=3, column=1)
        # 职称
        ttk.Label(frame, text="职称:").grid(row=4, column=0, sticky=tk.E, pady=5)
        title_var = tk.StringVar()
        title_combobox = ttk.Combobox(frame, textvariable=title_var,
                                      values=["主任医师", "副主任医师", "主治医师", "住院医师"])
        title_combobox.grid(row=4, column=1, pady=5)
        # 联系方式
        ttk.Label(frame, text="联系方式:").grid(row=5, column=0, sticky=tk.E, pady=5)
        contact_entry = ttk.Entry(frame)
        contact_entry.grid(row=5, column=1, pady=5)
        # 所属科室
        ttk.Label(frame, text="所属科室:").grid(row=6, column=0, sticky=tk.E, pady=5)
        self.db.cursor.execute("SELECT dept_id, dept_name FROM Department")
        departments = self.db.cursor.fetchall()
        dept_var = tk.StringVar()
        dept_combobox = ttk.Combobox(frame, textvariable=dept_var,
                                     values=[f"{dept[0]} - {dept[1]}" for dept in departments])
        dept_combobox.grid(row=6, column=1, pady=5)
        def save_doctor():#保存医生信息
            try:
                doctor_id = int(doctor_id_entry.get())
                name = name_entry.get()
                gender = gender_var.get()
                title = title_var.get()
                contact = contact_entry.get()
                dept_str = dept_var.get()
                if not name or not gender or not title or not dept_str:
                    messagebox.showerror("错误", "请填写所有必填字段")
                    return
                dept_id = int(dept_str.split(' - ')[0])
                self.db.cursor.execute("""
                INSERT INTO Doctor (doctor_id, name, gender, title, contact, dept_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (doctor_id, name, gender, title, contact, dept_id))
                self.db.conn.commit()
                messagebox.showinfo("成功", "医生添加成功")
                self.show_doctors()
            except sqlite3.IntegrityError:
                messagebox.showerror("错误", "医生ID已存在")
            except ValueError:
                messagebox.showerror("错误", "医生ID和科室ID必须是数字")
            except Exception as e:
                messagebox.showerror("错误", f"添加医生失败: {e}")
        save_btn = ttk.Button(frame, text="保存", command=save_doctor)
        save_btn.grid(row=7, column=0, columnspan=2, pady=10)
    def show_patients(self):#显示病人列表
        self.clear_content()
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # 查询病人数据
        self.db.cursor.execute("SELECT * FROM Patient")
        patients = self.db.cursor.fetchall()
        # 创建表格
        tree = ttk.Treeview(frame, columns=('patient_id', 'name', 'gender', 'age', 'id_card', 'contact', 'address'),
                            show='headings')
        tree.heading('patient_id', text='病人ID')
        tree.heading('name', text='姓名')
        tree.heading('gender', text='性别')
        tree.heading('age', text='年龄')
        tree.heading('id_card', text='身份证号')
        tree.heading('contact', text='联系方式')
        tree.heading('address', text='地址')
        for patient in patients:
            tree.insert('', tk.END, values=patient)
        tree.pack(fill=tk.BOTH, expand=True)

    def show_dept_stats(self):#显示科室统计
        self.clear_content()
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # 查询统计数据
        stats = self.db.get_department_stats()
        # 创建表格
        tree = ttk.Treeview(frame, columns=('dept_name', 'date', 'count'), show='headings')
        tree.heading('dept_name', text='科室名称')
        tree.heading('date', text='日期')
        tree.heading('count', text='排班数量')
        for stat in stats:
            tree.insert('', tk.END, values=stat)
        tree.pack(fill=tk.BOTH, expand=True)

    def show_doctor_stats(self):#显示医生工作量统计
        self.clear_content()
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # 查询统计数据
        stats = self.db.get_doctor_stats()
        # 创建表格
        tree = ttk.Treeview(frame, columns=('doctor_id', 'name', 'count'), show='headings')
        tree.heading('doctor_id', text='医生ID')
        tree.heading('name', text='医生姓名')
        tree.heading('count', text='接诊总数')
        for stat in stats:
            tree.insert('', tk.END, values=stat)
        tree.pack(fill=tk.BOTH, expand=True)

    def show_patient_stats(self):#显示病人治疗情况统计
        self.clear_content()
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # 查询统计数据
        stats = self.db.get_patient_stats()
        # 创建表格
        tree = ttk.Treeview(frame, columns=('name', 'reg_count', 'pres_count'), show='headings')
        tree.heading('name', text='病人姓名')
        tree.heading('reg_count', text='挂号次数')
        tree.heading('pres_count', text='处方次数')
        for stat in stats:
            tree.insert('', tk.END, values=stat)

        tree.pack(fill=tk.BOTH, expand=True)
    # 医生功能
    def show_doctor_schedule(self):#显示医生排班
        self.clear_content()
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # 查询排班数据
        schedule = self.db.get_doctor_schedule(self.current_entity_id)
        if not schedule:
            ttk.Label(frame, text="今日无排班").pack(pady=20)
            return
        # 创建表格
        tree = ttk.Treeview(frame, columns=('schedule_id', 'date', 'time_slot', 'location', 'dept_name'),
                            show='headings')
        tree.heading('schedule_id', text='排班ID')
        tree.heading('date', text='日期')
        tree.heading('time_slot', text='时间段')
        tree.heading('location', text='地点')
        tree.heading('dept_name', text='科室')
        for s in schedule:
            tree.insert('', tk.END, values=s)
        tree.pack(fill=tk.BOTH, expand=True)

    def show_my_patients(self):#显示医生的病人
        self.clear_content()
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # 查询病人数据
        patients = self.db.get_doctor_patients(self.current_entity_id)
        if not patients:
            ttk.Label(frame, text="暂无接诊病人").pack(pady=20)
            return
        # 创建表格
        tree = ttk.Treeview(frame, columns=('reg_id', 'reg_time', 'status', 'name', 'dept_name', 'time_slot'),
                            show='headings')
        tree.heading('reg_id', text='挂号ID')
        tree.heading('reg_time', text='挂号时间')
        tree.heading('status', text='状态')
        tree.heading('name', text='病人姓名')
        tree.heading('dept_name', text='科室')
        tree.heading('time_slot', text='时间段')
        for p in patients:
            tree.insert('', tk.END, values=p)
        tree.pack(fill=tk.BOTH, expand=True)
    # 病人功能
    def show_my_registrations(self):#显示病人的挂号
        self.clear_content()
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # 查询挂号数据
        registrations = self.db.get_patient_registrations(self.current_entity_id)
        if not registrations:
            ttk.Label(frame, text="暂无挂号记录").pack(pady=20)
            return
        # 创建表格
        tree = ttk.Treeview(frame, columns=('reg_id', 'dept_id', 'dept_name', 'reg_time', 'status'), show='headings')
        tree.heading('reg_id', text='挂号ID')
        tree.heading('dept_id', text='科室ID')
        tree.heading('dept_name', text='科室名称')
        tree.heading('reg_time', text='挂号时间')
        tree.heading('status', text='状态')
        for reg in registrations:
            tree.insert('', tk.END, values=reg)
        tree.pack(fill=tk.BOTH, expand=True)

    def show_my_prescriptions(self):#显示病人的处方
        self.clear_content()
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # 查询处方数据
        prescriptions = self.db.get_patient_prescriptions(self.current_entity_id)
        if not prescriptions:
            ttk.Label(frame, text="暂无处方记录").pack(pady=20)
            return
        # 创建表格
        tree = ttk.Treeview(frame, columns=('prescription_id', 'date', 'diagnosis'), show='headings')
        tree.heading('prescription_id', text='处方ID')
        tree.heading('date', text='日期')
        tree.heading('diagnosis', text='诊断结果')
        for pres in prescriptions:
            tree.insert('', tk.END, values=pres)
        tree.pack(fill=tk.BOTH, expand=True)
    def clear_content(self):#清除内容区域，保留菜单和标题
        for widget in self.root.winfo_children()[2:]:
            widget.destroy()
# 主程序
if __name__ == "__main__":
    root = tk.Tk()
    app = HospitalManagementApp(root)
    root.mainloop()