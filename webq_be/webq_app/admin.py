from django.contrib import admin
from .models import Student, LearningResource, Recommendation

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'email', 'performance_score', 'created_at')
    list_filter = ('performance_score', 'created_at')
    search_fields = ('student_id', 'name', 'email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('student_id', 'name', 'email')
        }),
        ('Performance Data', {
            'fields': ('performance_score', 'completed_courses', 'pending_courses')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ('resource_id', 'title', 'type', 'difficulty_level', 'recommendation_priority', 'created_at')
    list_filter = ('type', 'difficulty_level', 'recommendation_priority')
    search_fields = ('resource_id', 'title', 'course_id')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('resource_id', 'title', 'description', 'url')
        }),
        ('Classification', {
            'fields': ('type', 'difficulty_level', 'course_id', 'recommendation_priority')
        }),
        ('Additional Info', {
            'fields': ('estimated_duration', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('created_at',)

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('student', 'resource', 'status', 'confidence_score', 'recommendation_date')
    list_filter = ('status', 'confidence_score', 'recommendation_date')
    search_fields = ('student__name', 'student__student_id', 'resource__title')
    
    fieldsets = (
        ('Recommendation Details', {
            'fields': ('student', 'resource', 'status', 'confidence_score')
        }),
        ('Analysis', {
            'fields': ('reason', 'ai_metadata')
        }),
        ('Timestamps', {
            'fields': ('recommendation_date',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('recommendation_date',)