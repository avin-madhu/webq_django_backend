from django.urls import path
from . import views

urlpatterns = [
    # Student endpoints
    path('students/', views.StudentListCreateView.as_view(), name='student-list-create'),
    path('students/<str:student_id>/', views.StudentDetailView.as_view(), name='student-detail'),
    path('student/<str:student_id>/performance/', views.StudentPerformanceView.as_view(), name='student-performance'),
    
    # Learning resource endpoints
    path('resources/', views.LearningResourceListCreateView.as_view(), name='resource-list-create'),
    path('resources/<str:resource_id>/', views.LearningResourceDetailView.as_view(), name='resource-detail'),
    
    # Recommendation endpoints
    path('recommendations/', views.generate_recommendations, name='generate-recommendations'),
    path('recommendations/<str:student_id>/', views.get_student_recommendations, name='student-recommendations'),
    path('recommendations/update/<int:recommendation_id>/', views.update_recommendation_status, name='update-recommendation-status'),
    
    # Debug endpoint
    path('debug/recommendations/<str:student_id>/', views.debug_recommendations, name='debug-recommendations'),
    
    # Analytics endpoint
    path('analytics/dashboard/', views.get_analytics_dashboard, name='analytics-dashboard'),
]