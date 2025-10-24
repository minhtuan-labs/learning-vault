# P.A.M - Private Asset Management System

This project is a personal journey to build a comprehensive asset management system, embracing the **"build, learn, and share"** philosophy. It serves as a practical learning ground for modern technologies like FastAPI, Streamlit, and Docker.

---

## 🎯 Project Goal

The **P.A.M** system is designed to provide a holistic and detailed overview of personal assets, helping users track fluctuations, manage cash flow, and make better-informed financial decisions.

---

## ✨ Key Features

### Phase 1: Core Features (MVP)
- [ ] **Multi-Asset Management:** Track various asset classes, including:
    - Cash
    - Stocks
    - ETFs/Funds
    - Savings Accounts
- [ ] **Cash Flow Tracking:** Log and categorize all transactions (e.g., deposits, withdrawals, buys/sells, dividend income).
- [ ] **Real-time Data Integration:** Automatically fetch current stock prices from public APIs to calculate unrealized gains/losses.
- [ ] **Visual Dashboard:** Provide intuitive charts (pie charts, line charts) to visualize asset allocation and portfolio growth over time.
- [ ] **Automated Alerts:** Send notifications via **Telegram** when stock prices hit pre-defined Target Price or Stop-Loss levels.

### Phase 2: Enhancements (Future)
- [ ] **AI/ML Integration:** Build and integrate a model to forecast stock price trends.

## 🛠️ Technology Stack

| Component     | Technology                                       |
|---------------|--------------------------------------------------|
| **Backend** | Python, FastAPI                                  |
| **Frontend** | Streamlit                                        |
| **Database** | PostgreSQL                                       |
| **Deployment**| Docker, Docker Compose                           |
| **Alerting** | Telegram Bot API                                 |

---

## 🏛️ System Architecture

The project is built on a basic microservice architecture, completely decoupling the Frontend and Backend:

-   **Frontend (Streamlit):** The user interface, responsible for displaying data and handling user interactions. It communicates with the Backend via API requests.
-   **Backend (FastAPI):** The brain of the system. It handles all business logic, user authentication, and database interactions.
-   **Database (PostgreSQL):** Persistently stores all user and financial data.
-   **Telegram Worker:** A separate, scheduled process that checks asset prices and dispatches alerts.

---

## 📁 Project Structure

```
.
├── pam_backend/        # Backend (FastAPI) source code
├── pam_frontend/       # Frontend (Streamlit) source code
├── telegram_worker/    # Telegram alerting service source code
├── docker-compose.yml  # The orchestrator for all services
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
* Git
* Docker & Docker Compose

### Installation & Launch
1.  **Clone the `learning-vault` repository:**
    ```bash
    git clone [https://github.com/minhtuan-labs/learning-vault.git](https://github.com/minhtuan-labs/learning-vault.git)
    ```

2.  **Navigate to the project directory:**
    This project is located within the `projects` folder.
    ```bash
    cd learning-vault/projects/pam-private-asset-management/
    # (Assuming this is the chosen directory name for the project)
    ```

3.  **Create environment file:**
    Create a single `.env` file in the project root based on the `env.example` file provided.
    ```bash
    cp env.example .env
    # Edit .env with your database credentials and JWT secret key
    ```

4.  **Generate JWT Secret Key:**
    ```bash
    openssl rand -hex 32
    # Copy the generated key to JWT_SECRET_KEY in your .env file
    ```

5.  **Build and run with Docker Compose:**
    From the project's root directory, run:
    ```bash
    docker-compose up --build -d
    ```
    * **Frontend** will be available at: `http://localhost:6868` 💰
    * **Backend API docs** will be available at: `http://localhost:8000/docs`

---

## 📜 License
MIT License — for learning, research, and experimentation.

---

**Author:** *Pham Minh Tuan*  
© 2025 — *TinyChatBot: Build, Learn, Share.*
