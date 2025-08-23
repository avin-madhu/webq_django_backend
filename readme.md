API ENDPOINTS SUMMARY:
- GET /api/students/ - List all students
- POST /api/students/ - Create new student
- GET /api/students/{student_id}/ - Get student details
- GET /api/student/{student_id}/performance/ - Get student performance
- GET /api/resources/ - List all learning resources
- POST /api/resources/ - Create new resource
- POST /api/recommendations/ - Generate AI recommendations
- GET /api/recommendations/{student_id}/ - Get student recommendations
- PATCH /api/recommendations/update/{recommendation_id}/ - Update recommendation status
- GET /api/analytics/dashboard/ - Get system analytics

TESTING:
```
python manage.py test
```