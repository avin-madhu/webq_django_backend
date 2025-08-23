from rest_framework import serializers
from .models import Student, LearningResource, Recommendation

class StudentSerializer(serializers.ModelSerializer):
    completed_courses = serializers.SerializerMethodField()
    pending_courses = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = '__all__'

    def get_completed_courses(self, obj):
        return obj.get_completed_courses()

    def get_pending_courses(self, obj):
        return obj.get_pending_courses()

class StudentPerformanceSerializer(serializers.ModelSerializer):
    completed_courses = serializers.SerializerMethodField()
    pending_courses = serializers.SerializerMethodField()
    total_recommendations = serializers.SerializerMethodField()
    recent_activity = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'student_id', 'name', 'email', 'performance_score',
            'completed_courses', 'pending_courses', 'total_recommendations',
            'recent_activity', 'created_at', 'updated_at'
        ]

    def get_completed_courses(self, obj):
        return obj.get_completed_courses()

    def get_pending_courses(self, obj):
        return obj.get_pending_courses()

    def get_total_recommendations(self, obj):
        return obj.recommendation_set.count()

    def get_recent_activity(self, obj):
        recent_recs = obj.recommendation_set.order_by('-recommendation_date')[:5]
        return [
            {
                'resource_title': rec.resource.title,
                'status': rec.status,
                'date': rec.recommendation_date.isoformat(),
                'confidence': rec.confidence_score
            }
            for rec in recent_recs
        ]

class LearningResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningResource
        fields = '__all__'

class RecommendationSerializer(serializers.ModelSerializer):
    resource = LearningResourceSerializer(read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)
    ai_metadata = serializers.SerializerMethodField()

    class Meta:
        model = Recommendation
        fields = '__all__'

    def get_ai_metadata(self, obj):
        return obj.get_ai_metadata()

class GenerateRecommendationSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    force_regenerate = serializers.BooleanField(default=False)
    max_recommendations = serializers.IntegerField(default=5, min_value=1, max_value=20)
