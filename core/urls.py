from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Authentication
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Courses
    path('courses/', views.courses_view, name='courses'),
    path('courses/<int:course_id>/', views.course_detail_view, name='course_detail'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('courses/<int:course_id>/learn/', views.pdf_learn_view, name='pdf_learn'),
    
    # API: progress & chatbot
    path('api/save-progress/', views.api_save_progress, name='api_save_progress'),
    path('api/chat/', views.api_chat, name='api_chat'),
    
    # Lessons
    path('courses/<int:course_id>/lessons/<int:lesson_id>/', views.lesson_view, name='lesson'),
    path('courses/<int:course_id>/lessons/<int:lesson_id>/complete/', views.complete_lesson, name='complete_lesson'),
    
    # Quizzes
    path('quizzes/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    
    # Recommendations
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('recommendations/refresh/', views.refresh_recommendations, name='refresh_recommendations'),
    
    # Feedback
    path('feedback/', views.feedback_view, name='feedback'),
    path('feedback/<int:feedback_id>/dismiss/', views.dismiss_feedback, name='dismiss_feedback'),
    
    # API endpoints
    path('api/stats/', views.api_stats, name='api_stats'),
    path('api/progress/', views.api_progress, name='api_progress'),
    path('api/search/', views.search_internet, name='search_internet'),
]