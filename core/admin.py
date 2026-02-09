from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Course, Enrollment, Lesson, Quiz, QuizAttempt, Activity, Recommendation, Feedback, PDFReadingProgress, ReadingSession, ChatMessage


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'skill_level', 'learning_style', 'login_count', 'last_active_date']
    list_filter = ['skill_level', 'learning_style', 'learning_pace', 'date_joined']
    search_fields = ['username', 'email']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Learning Profile', {
            'fields': ('learning_style', 'skill_level', 'learning_pace', 'preferred_content_type', 'interests')
        }),
        ('Behavior Tracking', {
            'fields': ('login_count', 'last_active_date', 'average_session_duration', 'preferred_study_time')
        }),
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'level', 'enrolled_count', 'rating', 'duration_hours']
    list_filter = ['category', 'level', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'progress_percentage', 'lessons_completed', 'is_completed', 'enrolled_at']
    list_filter = ['is_completed', 'enrolled_at']
    search_fields = ['user__username', 'course__title']
    readonly_fields = ['enrolled_at']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'content_type', 'order', 'created_at']
    list_filter = ['content_type', 'course__category']
    search_fields = ['title', 'course__title']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['id', 'lesson', 'question']
    search_fields = ['question', 'lesson__title']


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'is_correct', 'score', 'attempted_at']
    list_filter = ['is_correct', 'attempted_at']
    readonly_fields = ['attempted_at']


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'timestamp', 'session_duration']
    list_filter = ['activity_type', 'timestamp']
    search_fields = ['user__username']
    readonly_fields = ['timestamp']


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'total_score', 'is_viewed', 'is_enrolled', 'generated_at']
    list_filter = ['is_viewed', 'is_enrolled', 'generated_at']
    search_fields = ['user__username', 'course__title']
    readonly_fields = ['generated_at']


@admin.register(PDFReadingProgress)
class PDFReadingProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'last_page_read', 'updated_at']
    list_filter = ['course', 'updated_at']
    search_fields = ['user__username', 'course__title']


@admin.register(ReadingSession)
class ReadingSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'started_at', 'ended_at', 'pages_read', 'duration_minutes']
    list_filter = ['course', 'started_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'role', 'created_at']
    list_filter = ['role', 'course', 'created_at']
    search_fields = ['user__username', 'content']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'feedback_type', 'title', 'is_read', 'is_dismissed', 'created_at']
    list_filter = ['feedback_type', 'is_read', 'is_dismissed', 'created_at']
    search_fields = ['user__username', 'title']
    readonly_fields = ['created_at']