"""Ensure we have exactly 4 IT PDF courses with total_pages and summary_for_chat."""
from django.core.management.base import BaseCommand
from core.models import Course


PDF_COURSES = [
    {
        'title': 'Machine Learning Fundamentals',
        'description': 'Learn the basics of ML, including supervised and unsupervised learning, neural networks, and practical applications.',
        'category': 'machine_learning',
        'level': 'intermediate',
        'total_pages': 12,
        'summary_for_chat': (
            'Machine Learning Fundamentals covers: supervised learning (labeled data, classification, regression), '
            'unsupervised learning (clustering, dimensionality reduction), neural networks basics, model evaluation '
            '(accuracy, precision, recall, F1), overfitting and regularization, and practical Python with scikit-learn.'
        ),
    },
    {
        'title': 'Modern Web Development',
        'description': 'Master HTML5, CSS3, JavaScript, and React to build responsive, interactive web applications.',
        'category': 'web_development',
        'level': 'beginner',
        'total_pages': 15,
        'summary_for_chat': (
            'Modern Web Development covers: HTML5 structure and semantics, CSS3 layout (Flexbox, Grid), responsive design, '
            'JavaScript ES6+ (variables, functions, async/await), React components and hooks, state management, '
            'and building and deploying web apps.'
        ),
    },
    {
        'title': 'Data Science with Python',
        'description': 'Comprehensive guide to data analysis, visualization, and machine learning using Python.',
        'category': 'data_science',
        'level': 'intermediate',
        'total_pages': 18,
        'summary_for_chat': (
            'Data Science with Python covers: Pandas for data manipulation, NumPy for numerical computing, '
            'Matplotlib and Seaborn for visualization, data cleaning and preprocessing, statistical analysis, '
            'introduction to scikit-learn for ML, and Jupyter notebooks.'
        ),
    },
    {
        'title': 'Cloud Computing Essentials',
        'description': 'Understand cloud architecture, AWS services, and deployment strategies for modern applications.',
        'category': 'cloud_computing',
        'level': 'beginner',
        'total_pages': 14,
        'summary_for_chat': (
            'Cloud Computing Essentials covers: cloud service models (IaaS, PaaS, SaaS), AWS core services (EC2, S3, Lambda), '
            'cloud architecture patterns, serverless computing, DevOps basics, and deployment and scaling strategies.'
        ),
    },
]


class Command(BaseCommand):
    help = 'Create or update 4 IT PDF courses with total_pages and summary_for_chat'

    def handle(self, *args, **kwargs):
        for i, data in enumerate(PDF_COURSES):
            course, created = Course.objects.update_or_create(
                title=data['title'],
                defaults={
                    'description': data['description'],
                    'category': data['category'],
                    'level': data['level'],
                    'total_pages': data['total_pages'],
                    'summary_for_chat': data['summary_for_chat'],
                    'duration_hours': 20 + (i * 5),
                    'lessons_count': 0,
                }
            )
            self.stdout.write(f'  {"Created" if created else "Updated"}: {course.title} ({course.total_pages} pages)')
        self.stdout.write(self.style.SUCCESS('PDF courses ready.'))
