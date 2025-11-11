-- ============================================
-- 🏦 SecureBank - Bank Management SQL Schema
-- Author: Chinta Soma Sekhar
-- Date: 2025
-- Description: Database schema for Flask-based
--              Bank Management System.
-- ============================================

-- Drop database if exists (for development reset)
DROP DATABASE IF EXISTS Bank;
CREATE DATABASE Bank;
USE Bank;

-- ============================================
-- 🧱 1. Bank Employees Table
-- ============================================

CREATE TABLE bankemployees (
    empid INT PRIMARY KEY,
    empname VARCHAR(100) NOT NULL,
    designation VARCHAR(100),
    branch VARCHAR(100)
);

-- Default employees who can become Admins
INSERT INTO bankemployees (empid, empname, designation, branch) VALUES
(101, 'Amit Verma', 'Branch Manager', 'Hyderabad'),
(102, 'Priya Iyer', 'Operations Officer', 'Bangalore'),
(103, 'Rohit Sharma', 'Cashier', 'Chennai'),
(104, 'Sneha Reddy', 'Customer Relations', 'Mumbai'),
(105, 'Vikas Patel', 'Loan Officer', 'Delhi');

-- ============================================
-- 👨‍💼 2. Admin Accounts Table
-- ============================================

CREATE TABLE admin_accounts (
    adminname VARCHAR(100) NOT NULL,
    phnno VARCHAR(15) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    employeeid INT NOT NULL,
    PRIMARY KEY (employeeid),
    FOREIGN KEY (employeeid) REFERENCES bankemployees(empid)
);

-- ============================================
-- 👤 3. User Accounts Table
-- ============================================

CREATE TABLE user_accounts (
    username VARCHAR(100) NOT NULL,
    phnno VARCHAR(15) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    accounttype ENUM('savings', 'current') NOT NULL,
    accountno BIGINT PRIMARY KEY,
    balance DECIMAL(12,2) DEFAULT 0.00
);

-- ============================================
-- 🔐 4. Logins Table
-- ============================================

CREATE TABLE logins (
    id BIGINT PRIMARY KEY,
    pin VARCHAR(255) NOT NULL,
    usertype ENUM('Admin', 'Account Holder') NOT NULL,
    account_creation_date DATE DEFAULT (CURRENT_DATE()),
    account_creation_time TIME DEFAULT (CURRENT_TIME())
);

-- ============================================
-- 💰 5. Transactions Table
-- ============================================

CREATE TABLE transactions (
    transid INT AUTO_INCREMENT PRIMARY KEY,
    accountno BIGINT NOT NULL,
    transactiontype ENUM('credit', 'debit') NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    Event_date DATE DEFAULT (CURRENT_DATE()),
    Event_time TIME DEFAULT (CURRENT_TIME()),
    FOREIGN KEY (accountno) REFERENCES user_accounts(accountno)
);

-- ============================================
-- ✅ SAMPLE DATA (Optional for testing)
-- ============================================

-- Example user account
INSERT INTO user_accounts (username, phnno, email, accounttype, accountno, balance)
VALUES ('Test User', '9876543210', 'testuser@example.com', 'savings', 100320519999, 10000.00);

-- Example admin account
INSERT INTO admin_accounts (adminname, phnno, email, employeeid)
VALUES ('Admin Master', '9998887776', 'admin@securebank.com', 101);

-- Example login entries (Plain for testing; app will hash automatically)
INSERT INTO logins (id, pin, usertype)
VALUES 
(100320519999, '1234', 'Account Holder'),
(101, '1234', 'Admin');

-- ============================================
-- 🧾 Testing Commands (optional)
-- ============================================
-- SELECT * FROM user_accounts;
-- SELECT * FROM admin_accounts;
-- SELECT * FROM logins;
-- SELECT * FROM transactions;

-- ============================================
-- 🎯 End of Schema
-- ============================================
