from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import json

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    performance_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        default=0.0
    )
    completed_courses = models.TextField(default='[]')  # JSON string
    pending_courses = models.TextField(default='[]')   # JSON string
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.student_id})"

    def get_completed_courses(self):
        return json.loads(self.completed_courses)

    def set_completed_courses(self, courses_list):
        self.completed_courses = json.dumps(courses_list)

    def get_pending_courses(self):
        return json.loads(self.pending_courses)

    def set_pending_courses(self, courses_list):
        self.pending_courses = json.dumps(courses_list)

class LearningResource(models.Model):
    RESOURCE_TYPES = [
        ('tutorial', 'Tutorial'),
        ('article', 'Article'),
        ('video', 'Video'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    ]

    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    resource_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    course_id = models.CharField(max_length=20)
    recommendation_priority = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5
    )
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    estimated_duration = models.IntegerField(default=30)  # minutes
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.type})"

    class Meta:
        ordering = ['-recommendation_priority', 'title']

class Recommendation(models.Model):
    STATUS_CHOICES = [
        ('recommended', 'Recommended'),
        ('viewed', 'Viewed'),
        ('completed', 'Completed'),
        ('dismissed', 'Dismissed'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE)
    recommendation_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recommended')
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.5
    )
    reason = models.TextField(blank=True)
    ai_metadata = models.TextField(default='{}')  # JSON string for AI analysis data

    def __str__(self):
        return f"Recommendation for {self.student.name}: {self.resource.title}"

    class Meta:
        unique_together = ['student', 'resource']
        ordering = ['-recommendation_date']

    def get_ai_metadata(self):
        return json.loads(self.ai_metadata)

    def set_ai_metadata(self, metadata_dict):
        self.ai_metadata = json.dumps(metadata_dict)