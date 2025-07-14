-- Tạo bảng departments
CREATE TABLE departments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

-- Tạo bảng employees
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    hire_date TEXT,
    department_id INTEGER,
    FOREIGN KEY(department_id) REFERENCES departments(id)
);
