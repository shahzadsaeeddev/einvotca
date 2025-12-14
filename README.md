# 🧾 POS & Business Management System

> **Enterprise-grade POS & Accounting System** built for real-world businesses.

A full-featured **POS & Business Management System** designed to handle **sales, inventory, accounting, and financial reporting** for small to medium-sized businesses.

---

## ✨ Features at a Glance

- 🏢 Multi-business support
- 🔐 Secure authentication via **Keycloak** (Google & Email login)
- 📊 Real-time sales, revenue & inventory insights
- 💰 Complete accounting & financial reporting
- 📦 Inventory & stock management
- 💬 WhatsApp integration for business communication

---

## 🔐 Authentication & Onboarding Flow

1️⃣ **User Login / Registration**  
- Login via **Google OAuth** or **Email/Password**
- Authentication handled by **Keycloak**

2️⃣ **Business Type Selection**  
- Retail, Wholesale, Services, etc.

3️⃣ **Business Profile Setup**  
- Business name  
- Address  
- Currency  
- Invoice preferences  

4️⃣ **Dashboard Redirect**  
- User is redirected to the main dashboard after setup

---

## 📊 Dashboard Overview

The dashboard provides real-time business insights:

- 📈 Today’s Sales
- 💵 Total Revenue
- 🔄 Total Receivable & Payable
- 📉 Sales Overview (Charts)
- 🏆 Top Selling Products
- 📦 Live Stock Levels
- 🧾 Recent Transactions
- 💳 Payment Method Distribution

---

## 🖼️ Gallery
- Upload and manage business images
- Store product & branding media

---

## 📦 Inventory Management
- Add & manage products
- Product attributes (size, color, category, etc.)
- Live stock tracking
- Low / out-of-stock indicators

---

## 🛒 Buy & Sell Module

### ⚡ Quick Actions
- Create Sale Invoice  
- Create Purchase  
- Create Payment  
- Create Receipt  

### 📤 Sales
- Sale Invoice  
- Sales Return / Credit Note  
- Day Closing  

### 📥 Purchases
- Purchase  
- Purchase Orders  
- Purchase Return / Debit Note  

### 🔁 Transactions
- Payment Vouchers  
- Receipt Vouchers  
- Journal Entries  

---

## 💰 Accounts Module

### 📋 Master Data
- Customers  
- Suppliers  
- Investors  

### 🏦 Accounts
- Bank Accounts  
- Chart of Accounts  
- Employees  

### 📊 Financial Overview
- Income & Expense  
- Assets & Liabilities  

---

## 📑 Reports

### 📦 Inventory Reports
- Inventory Report  
- Out of Stock Report  

### 💼 Financial Reports
- General Journal  
- Ledger (Statement)  
- Trial Balance  
- Income Statement  
- Balance Sheet  

### 🔄 Transaction Reports
- Sales Reports  
- Purchase Reports  

---

## ⚙️ Setup & Configuration

### 🏢 Business Setup
- Business Profile  
- Invoice Configuration  

### 👥 User Management
- Users & Roles  
- Permissions  

### 🔗 Integrations
- WhatsApp Integration  

### 🛠️ System Configuration
- Records  
- Account Settings  

---

## 🧠 System Architecture

- Modular **Django Apps**
- REST APIs using **Django REST Framework**
- Asynchronous background tasks with **Celery & Redis**
- Secure enterprise authentication using **Keycloak**
- Containerized using **Docker**
- Scalable & production-ready design

---

## 🛠️ Tech Stack

| Layer        | Technology |
|-------------|------------|
| Backend     | Python, Django, Django REST Framework |
| Auth        | Keycloak (Google OAuth & Email Login) |
| Database    | PostgreSQL |
| Async Tasks | Celery, Redis |
| Frontend   | React.js |
| UI Library | Ant Design |
| DevOps     | Docker |

---

## ⚡ Installation & Setup

```bash
git clone https://github.com/your-username/pos-system.git
cd pos-system
docker-compose up --build
