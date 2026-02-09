from django.core.management.base import BaseCommand
from core.models import Course, Lesson, Quiz, User


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample courses...')
        
        # Create sample courses
        courses_data = [
            {
                'title': 'Machine Learning Fundamentals',
                'description': 'Learn the basics of ML, including supervised and unsupervised learning, neural networks, and practical applications.',
                'category': 'machine_learning',
                'level': 'intermediate',
                'duration_hours': 40,
                'lessons_count': 15,
                'enrolled_count': 1250,
                'rating': 4.8,
                'topics': ['Supervised Learning', 'Unsupervised Learning', 'Neural Networks', 'Model Evaluation'],
                'content_types': ['video', 'text', 'quiz']
            },
            {
                'title': 'Modern Web Development',
                'description': 'Master HTML5, CSS3, JavaScript, and React to build responsive, interactive web applications.',
                'category': 'web_development',
                'level': 'beginner',
                'duration_hours': 35,
                'lessons_count': 20,
                'enrolled_count': 2100,
                'rating': 4.9,
                'topics': ['HTML5 & CSS3', 'JavaScript ES6+', 'React Fundamentals', 'State Management'],
                'content_types': ['video', 'interactive', 'quiz']
            },
            {
                'title': 'Data Science with Python',
                'description': 'Comprehensive guide to data analysis, visualization, and machine learning using Python.',
                'category': 'data_science',
                'level': 'intermediate',
                'duration_hours': 50,
                'lessons_count': 25,
                'enrolled_count': 980,
                'rating': 4.7,
                'topics': ['Pandas', 'NumPy', 'Matplotlib', 'Scikit-learn'],
                'content_types': ['video', 'text', 'quiz']
            },
            {
                'title': 'Cloud Computing Essentials',
                'description': 'Understand cloud architecture, AWS services, and deployment strategies for modern applications.',
                'category': 'cloud_computing',
                'level': 'beginner',
                'duration_hours': 30,
                'lessons_count': 18,
                'enrolled_count': 760,
                'rating': 4.6,
                'topics': ['AWS Basics', 'Cloud Architecture', 'Serverless', 'DevOps'],
                'content_types': ['video', 'text']
            },
            {
                'title': 'AI for Business Applications',
                'description': 'Learn how to implement AI solutions in real-world business scenarios and drive innovation.',
                'category': 'artificial_intelligence',
                'level': 'advanced',
                'duration_hours': 45,
                'lessons_count': 22,
                'enrolled_count': 540,
                'rating': 4.8,
                'topics': ['AI Strategy', 'NLP', 'Computer Vision', 'Ethics'],
                'content_types': ['video', 'text', 'quiz']
            },
            {
                'title': 'React Native Development',
                'description': 'Build cross-platform mobile applications using React Native and best practices.',
                'category': 'mobile_development',
                'level': 'intermediate',
                'duration_hours': 38,
                'lessons_count': 19,
                'enrolled_count': 890,
                'rating': 4.7,
                'topics': ['React Native Basics', 'Navigation', 'API Integration', 'Publishing'],
                'content_types': ['video', 'interactive', 'quiz']
            }
        ]
        
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                defaults=course_data
            )
            if created:
                self.stdout.write(f'  Created course: {course.title}')
                
                # Create sample lessons for each course
                for i in range(1, min(course_data['lessons_count'], 5) + 1):
                    lesson = Lesson.objects.create(
                        course=course,
                        title=f'Lesson {i}: Introduction to {course_data["topics"][0] if course_data["topics"] else "Concepts"}',
                        description=f'Learn about {course_data["topics"][0] if course_data["topics"] else "key concepts"} in this lesson.',
                        content_type=course_data['content_types'][i % len(course_data['content_types'])],
                        content_text='This is a sample lesson content. In a real application, this would contain rich educational material with examples, explanations, and exercises.',
                        video_url='',
                        order=i
                    )
                    
                    # Create sample quiz for each lesson
                    Quiz.objects.create(
                        lesson=lesson,
                        question='What is the main concept covered in this lesson?',
                        options=['Option A', 'Option B', 'Option C', 'Option D'],
                        correct_answer=0,
                        explanation='This is the correct answer because...'
                    )
                    
                    self.stdout.write(f'    Created lesson {i}')
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))