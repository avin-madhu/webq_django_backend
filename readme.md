# Student Learning Recommendation System ( BACKEND )  

An AI-powered backend system built with **Django & DRF**, designed to track student performance, manage resources, and generate personalized learning recommendations.  

---

## API Endpoints  

### Students  
- `GET /api/students/` – List all students  
- `POST /api/students/` – Create new student  
- `GET /api/students/{student_id}/` – Get student details  

### Performance  
- `GET /api/student/{student_id}/performance/` – Get student performance  

### Resources  
- `GET /api/resources/` – List all resources  
- `POST /api/resources/` – Create new resource  

### Recommendations  
- `POST /api/recommendations/` – Generate AI recommendations  
- `GET /api/recommendations/{student_id}/` – Get student recommendations  
- `PATCH /api/recommendations/update/{recommendation_id}/` – Update recommendation status  

### Analytics  
- `GET /api/analytics/dashboard/` – Get system analytics  

---

## Tech Stack  
- **Backend**: Django, Django REST Framework  
- **AI Integration**: Groq (LLM API)  
- **Database**: SQLite (default) / PostgreSQL (production)  
- **Testing**: Django Test Framework  
---

## 🚀 Setup & Installation  

1. Clone the repository:  

```
git clone https://github.com/avin-madhu/webq_django_backend.git
   
cd webq_be
```
2. Create and activate a Virtual Environment

```
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```
3. Install dependencies

```
pip install -r requirements.txt
```
4. run migrations:

```
python manage.py migrate
```
5. Load seed data
```
python seed_data.py
```
## Sample GET and response

REQUEST:
```
GET /api/student/STU001/performance/
```
RESPONSE:
```
HTTP 200 OK
Allow: GET, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "student_id": "STU001",
    "name": "Alice Johnson",
    "email": "alice.johnson@example.com",
    "performance_score": 85.5,
    "completed_courses": [
        "Python Basics",
        "Data Structures"
    ],
    "pending_courses": [
        "Machine Learning",
        "Web Development"
    ],
    "total_recommendations": 8,
    "recent_activity": [
        {
            "resource_title": "Data Structures Explained",
            "status": "recommended",
            "date": "2025-08-23T11:05:03.873818+00:00",
            "confidence": 0.8
        },
        {
            "resource_title": "Machine Learning Quiz",
            "status": "recommended",
            "date": "2025-08-23T11:05:03.867923+00:00",
            "confidence": 0.9
        },
        {
            "resource_title": "Algorithm Design Patterns",
            "status": "recommended",
            "date": "2025-08-23T11:05:03.859902+00:00",
            "confidence": 0.95
        },
        {
            "resource_title": "HTML5 Semantic Elements",
            "status": "recommended",
            "date": "2025-08-23T11:04:56.285618+00:00",
            "confidence": 0.05
        },
        {
            "resource_title": "JavaScript DOM Manipulation",
            "status": "recommended",
            "date": "2025-08-23T11:04:56.264405+00:00",
            "confidence": 0.06
        }
    ],
    "created_at": "2025-08-23T09:38:31.026189Z",
    "updated_at": "2025-08-23T09:38:31.026189Z"
}
```
