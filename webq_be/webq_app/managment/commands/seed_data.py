from django.core.management.base import BaseCommand
from webq_app.models import Student, LearningResource
import random

class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database with sample data...')
        
        # Create sample students
        students_data = [
            {
                'student_id': 'STU001',
                'name': 'Alice Johnson',
                'email': 'alice.johnson@example.com',
                'performance_score': 85.5,
                'completed_courses': '["Python Basics", "Data Structures"]',
                'pending_courses': '["Machine Learning", "Web Development"]'
            },
            {
                'student_id': 'STU002',
                'name': 'Bob Smith',
                'email': 'bob.smith@example.com',
                'performance_score': 62.3,
                'completed_courses': '["HTML/CSS", "JavaScript Basics"]',
                'pending_courses': '["React", "Node.js", "Database Design"]'
            },
            {
                'student_id': 'STU003',
                'name': 'Carol Davis',
                'email': 'carol.davis@example.com',
                'performance_score': 45.7,
                'completed_courses': '["Programming Fundamentals"]',
                'pending_courses': '["Python Basics", "Problem Solving", "Algorithms"]'
            },
            {
                'student_id': 'STU004',
                'name': 'David Wilson',
                'email': 'david.wilson@example.com',
                'performance_score': 92.1,
                'completed_courses': '["Python Advanced", "Machine Learning", "Data Science"]',
                'pending_courses': '["Deep Learning", "AI Ethics"]'
            },
            {
                'student_id': 'STU005',
                'name': 'Eva Martinez',
                'email': 'eva.martinez@example.com',
                'performance_score': 78.9,
                'completed_courses': '["Web Development", "React", "Node.js"]',
                'pending_courses': '["DevOps", "Cloud Computing"]'
            }
        ]

        for student_data in students_data:
            student, created = Student.objects.get_or_create(
                student_id=student_data['student_id'],
                defaults=student_data
            )
            if created:
                self.stdout.write(f'Created student: {student.name}')

        # Create sample learning resources
        resources_data = [
            {
                'resource_id': 'RES001',
                'title': 'Python Fundamentals Tutorial',
                'type': 'tutorial',
                'difficulty_level': 'beginner',
                'course_id': 'PY101',
                'recommendation_priority': 8,
                'description': 'Complete beginner tutorial covering Python basics',
                'url': 'https://example.com/python-fundamentals',
                'estimated_duration': 45
            },
            {
                'resource_id': 'RES002',
                'title': 'Data Structures Explained',
                'type': 'video',
                'difficulty_level': 'intermediate',
                'course_id': 'CS201',
                'recommendation_priority': 7,
                'description': 'Video series on common data structures',
                'url': 'https://example.com/data-structures',
                'estimated_duration': 60
            },
            {
                'resource_id': 'RES003',
                'title': 'JavaScript DOM Manipulation',
                'type': 'article',
                'difficulty_level': 'intermediate',
                'course_id': 'WEB201',
                'recommendation_priority': 6,
                'description': 'Article on DOM manipulation techniques',
                'url': 'https://example.com/dom-manipulation',
                'estimated_duration': 30
            },
            {
                'resource_id': 'RES004',
                'title': 'Machine Learning Quiz',
                'type': 'quiz',
                'difficulty_level': 'advanced',
                'course_id': 'ML301',
                'recommendation_priority': 9,
                'description': 'Comprehensive quiz on ML concepts',
                'url': 'https://example.com/ml-quiz',
                'estimated_duration': 25
            },
            {
                'resource_id': 'RES005',
                'title': 'React Components Deep Dive',
                'type': 'tutorial',
                'difficulty_level': 'intermediate',
                'course_id': 'REACT201',
                'recommendation_priority': 8,
                'description': 'Advanced React components tutorial',
                'url': 'https://example.com/react-components',
                'estimated_duration': 90
            },
            {
                'resource_id': 'RES006',
                'title': 'Algorithm Design Patterns',
                'type': 'video',
                'difficulty_level': 'advanced',
                'course_id': 'ALG301',
                'recommendation_priority': 7,
                'description': 'Video on common algorithm design patterns',
                'url': 'https://example.com/algorithm-patterns',
                'estimated_duration': 75
            },
            {
                'resource_id': 'RES007',
                'title': 'HTML5 Semantic Elements',
                'type': 'article',
                'difficulty_level': 'beginner',
                'course_id': 'WEB101',
                'recommendation_priority': 5,
                'description': 'Guide to HTML5 semantic elements',
                'url': 'https://example.com/html5-semantics',
                'estimated_duration': 20
            },
            {
                'resource_id': 'RES008',
                'title': 'Database Design Assignment',
                'type': 'assignment',
                'difficulty_level': 'intermediate',
                'course_id': 'DB201',
                'recommendation_priority': 8,
                'description': 'Hands-on database design exercise',
                'url': 'https://example.com/db-assignment',
                'estimated_duration': 120
            },
            {
                'resource_id': 'RES009',
                'title': 'Python Error Handling',
                'type': 'tutorial',
                'difficulty_level': 'beginner',
                'course_id': 'PY101',
                'recommendation_priority': 6,
                'description': 'Tutorial on exception handling in Python',
                'url': 'https://example.com/python-errors',
                'estimated_duration': 35
            },
            {
                'resource_id': 'RES010',
                'title': 'Advanced CSS Animations',
                'type': 'video',
                'difficulty_level': 'advanced',
                'course_id': 'WEB301',
                'recommendation_priority': 7,
                'description': 'Advanced CSS animation techniques',
                'url': 'https://example.com/css-animations',
                'estimated_duration': 55
            }
        ]

        for resource_data in resources_data:
            resource, created = LearningResource.objects.get_or_create(
                resource_id=resource_data['resource_id'],
                defaults=resource_data
            )
            if created:
                self.stdout.write(f'Created resource: {resource.title}')

        self.stdout.write(
            self.style.SUCCESS('Successfully seeded database with sample data!')
        )