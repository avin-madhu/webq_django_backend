from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Student, LearningResource, Recommendation
from .ai_engine import AIRecommendationEngine


class ModelTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            student_id='TEST001',
            name='Test Student',
            email='test@example.com',
            performance_score=75.5,
            completed_courses='["Course1", "Course2"]',
            pending_courses='["Course3"]'
        )
        
        self.resource = LearningResource.objects.create(
            resource_id='TESTRES001',
            title='Test Resource',
            type='tutorial',
            difficulty_level='intermediate',
            course_id='TEST101',
            recommendation_priority=7
        )

    def test_student_model(self):
        self.assertEqual(self.student.student_id, 'TEST001')
        self.assertEqual(self.student.get_completed_courses(), ["Course1", "Course2"])
        self.assertEqual(self.student.get_pending_courses(), ["Course3"])

    def test_learning_resource_model(self):
        self.assertEqual(self.resource.resource_id, 'TESTRES001')
        self.assertEqual(self.resource.type, 'tutorial')

    def test_recommendation_model(self):
        recommendation = Recommendation.objects.create(
            student=self.student,
            resource=self.resource,
            confidence_score=0.85,
            reason='Test recommendation'
        )
        self.assertEqual(recommendation.status, 'recommended')
        self.assertEqual(recommendation.confidence_score, 0.85)


class APITests(APITestCase):
    def setUp(self):
        self.student = Student.objects.create(
            student_id='API001',
            name='API Test Student',
            email='apitest@example.com',
            performance_score=65.0
        )
        
        self.resource = LearningResource.objects.create(
            resource_id='APIRES001',
            title='API Test Resource',
            type='video',
            difficulty_level='beginner',
            course_id='API101',
            recommendation_priority=6
        )

    def test_get_student_performance(self):
        url = reverse('student-performance', kwargs={'student_id': 'API001'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['student_id'], 'API001')

    def test_generate_recommendations(self):
        url = reverse('generate-recommendations')
        data = {
            'student_id': 'API001',
            'force_regenerate': True,
            'max_recommendations': 3
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # validate structure of response
        self.assertIn('recommendations', response.data)
        self.assertIsInstance(response.data['recommendations'], list)

        if response.data['recommendations']:
            first = response.data['recommendations'][0]
            self.assertIn('reason', first)
            self.assertIn('confidence_score', first)

    def test_get_student_recommendations(self):
        # First create a recommendation
        Recommendation.objects.create(
            student=self.student,
            resource=self.resource,
            confidence_score=0.7
        )
        
        url = reverse('student-recommendations', kwargs={'student_id': 'API001'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['recommendations']), 1)


class AIEngineTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            student_id='AI001',
            name='AI Test Student',
            email='aitest@example.com',
            performance_score=45.0
        )
        
        self.resource = LearningResource.objects.create(
            resource_id='AIRES001',
            title='AI Test Resource',
            type='tutorial',
            difficulty_level='beginner',
            course_id='AI101',
            recommendation_priority=8
        )
        
        self.ai_engine = AIRecommendationEngine()

    def test_analyze_student_performance(self):
        analysis = self.ai_engine.analyze_student_performance(self.student)
        self.assertIn('performance_category', analysis)
        self.assertEqual(analysis['performance_category'], 'needs_improvement')

    def test_generate_recommendations(self):
        recommendations = self.ai_engine.generate_recommendations(
            self.student, max_recommendations=2
        )
        self.assertIsInstance(recommendations, list)
        if recommendations:
            self.assertIn('resource', recommendations[0])
            self.assertIn('confidence_score', recommendations[0])
