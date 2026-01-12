# SaaS Legal IA ⚖️

SaaS Legal IA is a comprehensive platform for legal document management and case analysis, powered by AI.

## 🚀 Main Features

- **Document Management:** Secure storage and categorization of legal files.
- **Roles & Permissions:** Granular access control using Spatie's Laravel-permission.
- **User Management:** Complete system for managing clients and internal users.
- **Subscription Engine:** Management of plans and client billing.
- **Professional Dashboard:** Real-time analytics and economic activity monitoring.

## 🛠️ Tech Stack

### Backend
- **Laravel 11+**
- **MySQL**
- **Spatie Laravel-permission**
- **JWT Authentication**

### Frontend
- **Vue.js 3**
- **Vite**
- **Vuetify**
- **Pinia** (State Management)

### DevOps
- **Docker & Docker Compose**

## ⚙️ Project Setup

### Prerequisites
- Docker & Docker Compose installed on your machine.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/alberthlima/saas_legal.git
   cd saas_legal
   ```

2. **Start the containers:**
   ```bash
   docker compose up -d
   ```

3. **Install Backend dependencies and setup database:**
   ```bash
   docker compose exec laravel composer install
   docker compose exec laravel php artisan migrate:fresh --seed
   ```

4. **Install Frontend dependencies:**
   The frontend installs automatically on startup, but you can manually run:
   ```bash
   docker compose exec frontend npm install
   ```

## 🔑 Default Credentials

After seeding the database, you can log in with:

- **Email:** `mlima@gmail.com`
- **Password:** `12345678`
- **Role:** Super-Admin

## 🌐 Access URLs

- **API:** [http://localhost:8000](http://localhost:8000)
- **Frontend:** [http://localhost:5173](http://localhost:5173)

---
Developed by **Alberth Lima**
