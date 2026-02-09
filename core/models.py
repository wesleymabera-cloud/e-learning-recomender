from django.db import models
from django.contrib.auth.models import AbstractUser
import json

class User(AbstractUser):
    """Extended User model with learning profile"""
    
    # Learning Profile
    LEARNING_STYLES = [
        ('visual', 'Visual'),
        ('auditory', 'Auditory'),
        ('kinesthetic', 'Kinesthetic'),
        ('reading', 'Reading/Writing'),
    ]
    
    SKILL_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    LEARNING_PACES = [
        ('slow', 'Slow (1-3 hours/week)'),
        ('moderate', 'Moderate (5-8 hours/week)'),
        ('intensive', 'Intensive (10+ hours/week)'),
    ]
    
    learning_style = models.CharField(max_length=20, choices=LEARNING_STYLES, default='visual')
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVELS, default='beginner')
    learning_pace = models.CharField(max_length=20, choices=LEARNING_PACES, default='moderate')
    preferred_content_type = models.CharField(max_length=50, default='video')
    interests = models.JSONField(default=list, blank=True)
    
    # Behavior tracking
    login_count = models.IntegerField(default=0)
    last_active_date = models.DateTimeField(auto_now=True)
    average_session_duration = models.FloatField(default=0.0)
    preferred_study_time = models.CharField(max_length=20, default='morning')
    
    def __str__(self):
        return self.username


class Course(models.Model):
    """Course model with comprehensive metadata"""
    
    CATEGORIES = [
        ('web_development', 'Web Development'),
        ('data_science', 'Data Science'),
        ('machine_learning', 'Machine Learning'),
        ('mobile_development', 'Mobile Development'),
        ('cloud_computing', 'Cloud Computing'),
        ('artificial_intelligence', 'Artificial Intelligence'),
    ]
    
    LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORIES)
    level = models.CharField(max_length=20, choices=LEVELS)
    duration_hours = models.IntegerField(default=0)
    lessons_count = models.IntegerField(default=0)
    
    # Popularity metrics
    enrolled_count = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    
    # Content metadata
    topics = models.JSONField(default=list, blank=True)
    content_types = models.JSONField(default=list, blank=True)
    
    # PDF course fields
    pdf_file = models.FileField(upload_to='courses/', null=True, blank=True)
    total_pages = models.PositiveIntegerField(default=1)
    summary_for_chat = models.TextField(blank=True, help_text='Course summary/key points for chatbot answers')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-rating', '-enrolled_count']
    
    def __str__(self):
        return self.title


class Enrollment(models.Model):
    """User enrollment in courses with progress tracking"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    
    # Progress tracking
    lessons_completed = models.IntegerField(default=0)
    progress_percentage = models.FloatField(default=0.0)
    current_lesson = models.IntegerField(default=1)
    
    # Completion tracking
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"


class Lesson(models.Model):
    """Lesson model with different content types"""
    
    CONTENT_TYPES = [
        ('text', 'Text'),
        ('video', 'Video'),
        ('quiz', 'Quiz'),
        ('interactive', 'Interactive'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    
    # Content
    content_text = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    video_duration = models.IntegerField(default=0)  # in seconds
    
    # Ordering
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Quiz(models.Model):
    """Quiz model for lessons"""
    
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    question = models.TextField()
    options = models.JSONField(default=list)  # List of options
    correct_answer = models.IntegerField(default=0)  # Index of correct answer
    explanation = models.TextField(blank=True)
    
    def __str__(self):
        return f"Quiz for {self.lesson.title}"


class QuizAttempt(models.Model):
    """User quiz attempts with scoring"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    selected_answer = models.IntegerField()
    is_correct = models.BooleanField(default=False)
    score = models.FloatField(default=0.0)
    
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-attempted_at']
    
    def __str__(self):
        return f"{self.user.username} - Quiz Attempt ({self.score}%)"


class Activity(models.Model):
    """User activity logging for behavior analysis"""
    
    ACTIVITY_TYPES = [
        ('lesson_completed', 'Lesson Completed'),
        ('quiz_completed', 'Quiz Completed'),
        ('course_enrolled', 'Course Enrolled'),
        ('learning_time', 'Learning Time'),
        ('login', 'Login'),
        ('content_viewed', 'Content Viewed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    
    # Activity details (JSON for flexibility)
    details = models.JSONField(default=dict, blank=True)
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    session_duration = models.FloatField(default=0.0)  # in minutes
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['activity_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"


class Recommendation(models.Model):
    """AI-generated recommendations for users"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='recommendations')
    
    # Scoring
    total_score = models.FloatField(default=0.0)
    
    # Factor scores (JSON for flexibility)
    factor_scores = models.JSONField(default=dict, blank=True)
    
    # Generated reasons
    reasons = models.JSONField(default=list, blank=True)
    
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    is_viewed = models.BooleanField(default=False)
    is_enrolled = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-total_score']
        indexes = [
            models.Index(fields=['user', '-total_score']),
            models.Index(fields=['user', '-generated_at']),
        ]
    
    def __str__(self):
        return f"Recommendation for {self.user.username}: {self.course.title}"


class PDFReadingProgress(models.Model):
    """Tracks PDF reading progress page by page (persists on exit)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pdf_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='pdf_progress')
    last_page_read = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} (page {self.last_page_read})"


class ReadingSession(models.Model):
    """Tracks reading sessions for habits and speed (pages per minute)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_sessions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reading_sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    pages_read = models.PositiveIntegerField(default=0)
    duration_minutes = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.pages_read} pages)"


class ChatMessage(models.Model):
    """Chatbot Q&A; optional course context for answers."""
    ROLE_CHOICES = [('user', 'User'), ('assistant', 'Assistant')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chat_messages', null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Feedback(models.Model):
    """System-generated feedback for users"""
    
    FEEDBACK_TYPES = [
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('info', 'Information'),
        ('achievement', 'Achievement'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.feedback_type.upper()}: {self.title}"