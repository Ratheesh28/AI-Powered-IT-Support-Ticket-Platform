# AI-Powered IT Support Ticket Intelligence Platform

An AI-powered IT support platform that automatically classifies support tickets, assigns priority levels, and recommends relevant troubleshooting knowledge base articles through an interactive dashboard.

## Overview

The AI-Powered IT Support Ticket Intelligence Platform is designed to simplify IT support ticket management by combining machine learning with rule-based automation.

When a user submits a support ticket, the platform predicts its category, assigns a priority level, stores the ticket, and recommends relevant troubleshooting resources.

The application provides a centralized dashboard for monitoring ticket activity and analyzing ticket classification results.

## Key Features

- **AI-Based Ticket Classification:** Automatically classifies tickets into Network, Hardware, Software, and Account Access categories.
- **Automatic Priority Assignment:** Assigns Critical, High, Medium, or Low priority using a rule-based engine.
- **Knowledge Base Recommendations:** Recommends relevant troubleshooting articles based on the predicted ticket category and keyword relevance.
- **Ticket Management:** Creates, stores, retrieves, and displays support tickets.
- **Interactive Dashboard:** Displays total tickets, average prediction confidence, supported categories, and ticket statistics.
- **Analytics Dashboard:** Visualizes ticket distribution and machine learning evaluation metrics.
- **REST API:** Provides backend endpoints through FastAPI with interactive Swagger documentation.

## Technology Stack

| Component         | Technologies                              |
| ----------------- | ----------------------------------------- |
| Frontend          | React, Vite, JavaScript, CSS              |
| Backend           | Python, FastAPI                           |
| Machine Learning  | scikit-learn, TF-IDF, Logistic Regression |
| Database          | SQLite, SQLAlchemy                        |
| Data Processing   | pandas, NumPy                             |
| API Communication | Axios                                     |
| Charts            | Recharts                                  |
| Icons             | Lucide React                              |
| API Documentation | Swagger UI                                |

## System Architecture

```
              User
               |
               v
       React Frontend
          (Vite)
               |
               v
        FastAPI Backend
               |
       +-------+--------+
       |       |        |
       v       v        v
   Ticket   Priority  Knowledge
Classifier  Engine     Base
       |       |        |
       +-------+--------+
               |
               v
         SQLite Database
               |
               v
       Dashboard & Analytics
```

## Machine Learning Approach

The platform uses a text classification pipeline based on:

1. **TF-IDF Vectorization:** Converts ticket title and description text into numerical feature representations.
2. **Logistic Regression:** Predicts the most likely IT support ticket category.
3. **Probability Scores:** Provides class probabilities and the maximum predicted probability as the model confidence score.

Supported categories:

- Network
- Hardware
- Software
- Account Access

The trained model is loaded by the FastAPI application during startup.

## Priority Assignment

A separate rule-based engine assigns ticket priority based on predefined keywords and severity indicators.

| Priority | Description                                   |
| -------- | --------------------------------------------- |
| Critical | Major outages and serious security incidents  |
| High     | Important services or multiple users affected |
| Medium   | General support issues                        |
| Low      | Minor issues and general assistance requests  |

Priority assignment is independent of the machine learning category prediction.

## Knowledge Base Recommendation

The recommendation engine retrieves relevant troubleshooting articles based on the predicted ticket category and keyword relevance.

Each recommendation contains:

- Article title
- Description
- Category
- Relevance score
- Step-by-step troubleshooting instructions

## Project Structure

```
AI-IT-Support-Ticket-Platform/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── predictor.py
│   │   ├── preprocessing.py
│   │   ├── priority.py
│   │   ├── knowledge_base.py
│   │   ├── recommendation_engine.py
│   │   ├── routes.py
│   │   └── schemas.py
│   │
│   ├── data/
│   ├── ml/
│   ├── models/
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── App.css
│   └── package.json
│
└── README.md
```

## Application Pages

1. **Dashboard:** Displays ticket statistics and category overview.
2. **Create Ticket:** Accepts ticket details and displays classification, priority, and knowledge base recommendations.
3. **Ticket History:** Displays submitted tickets with pagination.
4. **Analytics:** Presents ticket distribution charts and model evaluation metrics.

## Installation and Setup

### Prerequisites

- Python 3.10 or later
- Node.js and npm
- Git

### 1. Clone the repository

```
git clone https://github.com/Ratheesh28/AI-Powered-IT-Support-Ticket-Platform.git
cd AI-Powered-IT-Support-Ticket-Platform
```

### 2. Set up the backend

```
cd backend

python -m venv .venv

.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Ensure the trained model artifact is available in `backend/models/` before starting the application. The generated model files are excluded from Git.

Start the FastAPI server:

```
python -m uvicorn app.main:app --reload
```

Backend API:

`http://127.0.0.1:8000`

Swagger documentation:

`http://127.0.0.1:8000/docs`

### 3. Set up the frontend

Open another terminal:

```
cd frontend

npm install

npm run dev
```

Frontend application:

`http://localhost:5173`

## API Endpoints

| Method | Endpoint     | Purpose                  |
| ------ | ------------ | ------------------------ |
| GET    | `/health`    | Check application health |
| POST   | `/predict`   | Predict ticket category  |
| POST   | `/tickets`   | Create a support ticket  |
| GET    | `/tickets`   | Retrieve ticket history  |
| GET    | `/analytics` | Retrieve analytics data  |

Additional knowledge base recommendation functionality is available through the backend.

## Testing

The project includes backend tests for API functionality, preprocessing, and the machine learning pipeline.

The application has also been manually tested for:

- Backend health and model loading
- Ticket classification
- Ticket creation and database persistence
- Automatic priority assignment
- Knowledge base recommendations
- Ticket history and pagination
- Dashboard statistics
- Analytics charts

## Dataset and Model Limitations

**Important:** The current model was trained and evaluated using synthetic demo ticket data.

The reported evaluation metrics, including the displayed 100% accuracy, reflect performance on that synthetic evaluation dataset. They should not be interpreted as evidence of real-world enterprise performance.

The priority engine uses predefined keyword rules and is not a machine learning priority predictor.

The prediction confidence represents the model's maximum class probability and does not guarantee prediction correctness.

## Future Enhancements

- Integration with real-world IT support ticket datasets.
- Improved classification using larger and more diverse datasets.
- Semantic knowledge base search.
- User authentication and role-based access control.
- Deployment using cloud infrastructure.
- Advanced ticket assignment and SLA monitoring.

## Author

**Ratheesh Kumar**

B.E. Computer Science and Engineering (IoT)

GitHub: [Ratheesh28](https://github.com/Ratheesh28)

---

*Developed as an AI-powered IT support ticket intelligence project.*