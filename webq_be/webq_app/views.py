from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from .models import Student, LearningResource, Recommendation
from .serializers import (
    StudentSerializer, StudentPerformanceSerializer,
    LearningResourceSerializer, RecommendationSerializer,
    GenerateRecommendationSerializer
)
from .ai_engine import AIRecommendationEngine
import logging

logger = logging.getLogger(__name__)

class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'student_id'

class StudentPerformanceView(generics.RetrieveAPIView):
    """Get detailed student performance data"""
    queryset = Student.objects.all()
    serializer_class = StudentPerformanceSerializer
    lookup_field = 'student_id'

class LearningResourceListCreateView(generics.ListCreateAPIView):
    queryset = LearningResource.objects.all()
    serializer_class = LearningResourceSerializer

class LearningResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LearningResource.objects.all()
    serializer_class = LearningResourceSerializer
    lookup_field = 'resource_id'

@api_view(['POST'])
def generate_recommendations(request):
    """Generate AI-powered recommendations for a student"""
    serializer = GenerateRecommendationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    student_id = serializer.validated_data['student_id']
    force_regenerate = serializer.validated_data['force_regenerate']
    max_recommendations = serializer.validated_data['max_recommendations']

    try:
        student = get_object_or_404(Student, student_id=student_id)
        
        # Check if we should generate new recommendations
        if not force_regenerate:
            existing_count = student.recommendation_set.filter(
                status='recommended'
            ).count()
            
            if existing_count >= max_recommendations:
                return Response({
                    'message': f'Student already has {existing_count} active recommendations',
                    'student_id': student_id,
                    'existing_recommendations': existing_count
                })

        # Initialize AI engine
        ai_engine = AIRecommendationEngine()
        
        # Generate recommendations
        recommendations_data = ai_engine.generate_recommendations(
            student, max_recommendations
        )

        # Create recommendation records
        created_recommendations = []
        for rec_data in recommendations_data:
            recommendation, created = Recommendation.objects.get_or_create(
                student=student,
                resource=rec_data['resource'],
                defaults={
                    'confidence_score': rec_data['confidence_score'],
                    'reason': rec_data['reason'],
                    'status': 'recommended'
                }
            )
            
            if created or force_regenerate:
                if force_regenerate and not created:
                    # Update existing recommendation
                    recommendation.confidence_score = rec_data['confidence_score']
                    recommendation.reason = rec_data['reason']
                    recommendation.recommendation_date = timezone.now()
                    recommendation.status = 'recommended'
                    recommendation.save()
                
                created_recommendations.append(recommendation)

        # Serialize response
        serializer = RecommendationSerializer(created_recommendations, many=True)
        
        return Response({
            'message': f'Generated {len(created_recommendations)} recommendations',
            'student_id': student_id,
            'recommendations': serializer.data
        })

    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return Response({
            'error': 'Failed to generate recommendations',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_student_recommendations(request, student_id):
    """Retrieve all recommendations for a student"""
    try:
        student = get_object_or_404(Student, student_id=student_id)
        
        # Filter by status if provided
        status_filter = request.GET.get('status', None)
        recommendations = student.recommendation_set.all()
        
        if status_filter:
            recommendations = recommendations.filter(status=status_filter)
        
        # Order by recommendation date (newest first)
        recommendations = recommendations.order_by('-recommendation_date')
        
        serializer = RecommendationSerializer(recommendations, many=True)
        
        return Response({
            'student_id': student_id,
            'student_name': student.name,
            'total_recommendations': recommendations.count(),
            'recommendations': serializer.data
        })

    except Exception as e:
        logger.error(f"Error retrieving recommendations: {e}")
        return Response({
            'error': 'Failed to retrieve recommendations',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# for debugging purposes!
@api_view(['GET'])
def debug_recommendations(request, student_id):
    """Debug endpoint to check recommendation generation"""
    try:
        student = get_object_or_404(Student, student_id=student_id)
        
        # Basic checks
        total_resources = LearningResource.objects.count()
        existing_recommendations = student.recommendation_set.count()
        existing_resource_ids = list(student.recommendation_set.values_list('resource__id', flat=True))
        
        # Check AI engine
        ai_engine = AIRecommendationEngine()
        
        debug_info = {
            'student_info': {
                'id': student.student_id,
                'name': student.name,
                'performance_score': student.performance_score,
                'completed_courses': student.get_completed_courses(),
                'pending_courses': student.get_pending_courses()
            },
            'resources_info': {
                'total_resources': total_resources,
                'existing_recommendations': existing_recommendations,
                'existing_resource_ids': existing_resource_ids
            },
            'ai_info': {
                'has_api_key': bool(settings.GEMINI_API_KEY),
                'has_model': ai_engine.model is not None
            }
        }
        
        # Try to get some sample resources
        sample_resources = []
        for resource in LearningResource.objects.all()[:5]:
            sample_resources.append({
                'id': resource.id,
                'resource_id': resource.resource_id,
                'title': resource.title,
                'type': resource.type,
                'difficulty': resource.difficulty_level,
                'priority': resource.recommendation_priority
            })
        
        debug_info['sample_resources'] = sample_resources
        
        # Try generating recommendations with debug
        try:
            recommendations = ai_engine.generate_recommendations(student, max_recommendations=3)
            debug_info['recommendation_result'] = {
                'success': True,
                'count': len(recommendations),
                'recommendations': [
                    {
                        'resource_id': rec['resource'].resource_id,
                        'title': rec['resource'].title,
                        'confidence': rec['confidence_score'],
                        'reason': rec['reason']
                    }
                    for rec in recommendations
                ]
            }
        except Exception as e:
            debug_info['recommendation_result'] = {
                'success': False,
                'error': str(e)
            }
        
        return Response(debug_info)
        
    except Exception as e:
        logger.error(f"Debug error: {e}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_recommendation_status(request, recommendation_id):
    """Update the status of a specific recommendation"""
    try:
        recommendation = get_object_or_404(Recommendation, id=recommendation_id)
        new_status = request.data.get('status')
        
        valid_statuses = ['recommended', 'viewed', 'completed', 'dismissed']
        if new_status not in valid_statuses:
            return Response({
                'error': f'Invalid status. Must be one of: {valid_statuses}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        recommendation.status = new_status
        recommendation.save()
        
        serializer = RecommendationSerializer(recommendation)
        return Response(serializer.data)

    except Exception as e:
        logger.error(f"Error updating recommendation status: {e}")
        return Response({
            'error': 'Failed to update recommendation status',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_analytics_dashboard(request):
    """Get system-wide analytics and insights"""
    try:
        total_students = Student.objects.count()
        total_resources = LearningResource.objects.count()
        total_recommendations = Recommendation.objects.count()
        
        # Performance distribution
        excellent_students = Student.objects.filter(performance_score__gte=85).count()
        good_students = Student.objects.filter(
            performance_score__gte=70, performance_score__lt=85
        ).count()
        average_students = Student.objects.filter(
            performance_score__gte=50, performance_score__lt=70
        ).count()
        needs_improvement = Student.objects.filter(performance_score__lt=50).count()
        
        # Recommendation status distribution
        rec_stats = {}
        for status, _ in Recommendation.STATUS_CHOICES:
            rec_stats[status] = Recommendation.objects.filter(status=status).count()
        
        # Resource type distribution
        resource_stats = {}
        for res_type, _ in LearningResource.RESOURCE_TYPES:
            resource_stats[res_type] = LearningResource.objects.filter(type=res_type).count()

        return Response({
            'overview': {
                'total_students': total_students,
                'total_resources': total_resources,
                'total_recommendations': total_recommendations
            },
            'performance_distribution': {
                'excellent': excellent_students,
                'good': good_students,
                'average': average_students,
                'needs_improvement': needs_improvement
            },
            'recommendation_status_distribution': rec_stats,
            'resource_type_distribution': resource_stats
        })

    except Exception as e:
        logger.error(f"Error generating analytics: {e}")
        return Response({
            'error': 'Failed to generate analytics',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)