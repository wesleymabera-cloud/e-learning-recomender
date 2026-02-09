from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db import IntegrityError
from django.db.models import Avg, Q, Sum
from .models import (
    User, Course, Enrollment, Lesson, Quiz, QuizAttempt, Activity, Feedback, Recommendation,
    PDFReadingProgress, ReadingSession, ChatMessage
)
from .services import AIRecommendationEngine, BehaviorAnalyzer, FeedbackGenerator


# ==================== Authentication Views ====================

def index(request):
    """Home page: for guests = welcome + login/signup. For logged-in = welcome back + quick insights and links."""
    if not request.user.is_authenticated:
        return render(request, 'core/index.html', {})
    user = request.user
    enrollments = Enrollment.objects.filter(user=user).select_related('course')
    courses_enrolled = enrollments.count()
    total_pages_read = 0
    for e in enrollments:
        p = PDFReadingProgress.objects.filter(user=user, course=e.course).first()
        total_pages_read += (p.last_page_read if p else 0)
    context = {
        'user': user,
        'courses_enrolled': courses_enrolled,
        'total_pages_read': total_pages_read,
    }
    return render(request, 'core/index.html', context)


def register_view(request):
    """User registration"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        interests = request.POST.getlist('interests')

        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.interests = interests
            user.save()

            # Log activity
            Activity.objects.create(
                user=user,
                activity_type='login',
                details={'method': 'registration'}
            )

            # Login user
            login(request, user)

            return redirect('core:dashboard')
        except IntegrityError:
            return render(request, 'core/register.html', {'error': 'Username already exists. Please choose a different username.'})

    return render(request, 'core/register.html')


def login_view(request):
    """User login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            
            # Update login count
            user.login_count += 1
            user.last_active_date = timezone.now()
            user.save()
            
            # Log activity
            Activity.objects.create(
                user=user,
                activity_type='login',
                details={'method': 'form'}
            )
            
            return redirect('core:dashboard')
        else:
            return render(request, 'core/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'core/login.html')


@login_required
def logout_view(request):
    """User logout"""
    logout(request)
    return redirect('core:index')


# ==================== Dashboard Views ====================

@login_required
def dashboard(request):
    """User dashboard: enrolled courses with PDF progress (page X of Y)."""
    user = request.user
    enrollments = Enrollment.objects.filter(user=user).select_related('course')
    # Attach PDF progress for each enrollment
    enrollment_list = []
    for e in enrollments:
        prog = PDFReadingProgress.objects.filter(user=user, course=e.course).first()
        last_page = prog.last_page_read if prog else 1
        total = e.course.total_pages or 1
        pct = round((last_page / total) * 100, 1) if total else 0
        enrollment_list.append({
            'enrollment': e,
            'course': e.course,
            'last_page': last_page,
            'total_pages': total,
            'progress_pct': pct,
        })
    stats = {
        'courses_enrolled': enrollments.count(),
        'total_pages_read': sum(
            (PDFReadingProgress.objects.filter(user=user, course=e.course).first() or type('X', (), {'last_page_read': 0})()).last_page_read
            for e in enrollments
        ),
    }
    # Fix total_pages_read
    total_read = 0
    for e in enrollments:
        p = PDFReadingProgress.objects.filter(user=user, course=e.course).first()
        total_read += (p.last_page_read if p else 0)
    stats['total_pages_read'] = total_read
    recent_activities = Activity.objects.filter(user=user).order_by('-timestamp')[:10]
    context = {
        'user': user,
        'stats': stats,
        'enrollment_list': enrollment_list,
        'recent_activities': recent_activities,
    }
    return render(request, 'core/dashboard.html', context)


def get_weekly_progress(user):
    """Calculate weekly progress data"""
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    activities = Activity.objects.filter(
        user=user,
        timestamp__gte=seven_days_ago
    )
    
    # Group by day
    daily_progress = {}
    for i in range(7):
        date = (timezone.now() - timedelta(days=i)).date()
        daily_progress[date.strftime('%a')] = 0
    
    for activity in activities:
        if activity.activity_type == 'lesson_completed':
            date = activity.timestamp.strftime('%a')
            daily_progress[date] = daily_progress.get(date, 0) + 1
    
    return daily_progress


# ==================== Course Views ====================

def courses_view(request):
    """Browse only 4 IT PDF courses."""
    # Only 4 PDF IT courses (with summary_for_chat set by populate_pdf_courses)
    courses = Course.objects.exclude(summary_for_chat='').order_by('id')[:4]
    if not courses.exists():
        courses = Course.objects.filter(total_pages__gte=1).order_by('id')[:4]
    context = {
        'courses': courses,
        'category': None,
        'query': None
    }
    return render(request, 'core/courses.html', context)


def course_detail_view(request, course_id):
    """Course detail page (PDF course: enroll and start/continue reading)."""
    course = get_object_or_404(Course, id=course_id)
    is_enrolled = False
    enrollment = None
    progress = None
    if request.user.is_authenticated:
        try:
            enrollment = Enrollment.objects.get(user=request.user, course=course)
            is_enrolled = True
            progress = PDFReadingProgress.objects.filter(user=request.user, course=course).first()
        except Enrollment.DoesNotExist:
            pass
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'progress': progress,
    }
    return render(request, 'core/course_detail.html', context)


@login_required
def enroll_course(request, course_id):
    """Enroll user in a course. Redirect if form POST, else JSON for AJAX."""
    course = get_object_or_404(Course, id=course_id)
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return redirect('core:course_detail', course_id=course_id)
        return JsonResponse({'success': False, 'message': 'Already enrolled'})
    Enrollment.objects.create(user=request.user, course=course)
    course.enrolled_count += 1
    course.save()
    Activity.objects.create(
        user=request.user,
        activity_type='course_enrolled',
        details={'course_id': course.id, 'course_title': course.title}
    )
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return redirect('core:course_detail', course_id=course_id)
    return JsonResponse({'success': True, 'message': 'Successfully enrolled'})


# ==================== PDF Learning Views ====================

@login_required
def pdf_learn_view(request, course_id):
    """PDF reader: page-by-page with progress persistence."""
    course = get_object_or_404(Course, id=course_id)
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
    except Enrollment.DoesNotExist:
        return redirect('core:course_detail', course_id=course_id)
    progress, _ = PDFReadingProgress.objects.get_or_create(
        user=request.user, course=course,
        defaults={'last_page_read': 1}
    )
    total_pages = course.total_pages or 1
    context = {
        'course': course,
        'enrollment': enrollment,
        'current_page': min(progress.last_page_read, total_pages),
        'total_pages': total_pages,
        'pdf_url': course.pdf_file.url if course.pdf_file else None,
    }
    return render(request, 'core/pdf_reader.html', context)


@login_required
def api_save_progress(request):
    """Save PDF reading progress (page number). Called on page change and beforeunload."""
    if request.method != 'POST':
        return JsonResponse({'success': False})
    import json as json_module
    try:
        data = json_module.loads(request.body) if request.body else {}
        course_id = data.get('course_id')
        page = int(data.get('page', 1))
    except (ValueError, TypeError):
        return JsonResponse({'success': False})
    course = get_object_or_404(Course, id=course_id)
    try:
        Enrollment.objects.get(user=request.user, course=course)
    except Enrollment.DoesNotExist:
        return JsonResponse({'success': False})
    progress, _ = PDFReadingProgress.objects.get_or_create(
        user=request.user, course=course, defaults={'last_page_read': 1}
    )
    prev_page = progress.last_page_read
    progress.last_page_read = min(max(1, page), course.total_pages or 1)
    progress.save()
    # Optional: create or update ReadingSession for speed/habits (simplified: one session per save)
    pages_diff = max(0, progress.last_page_read - prev_page)
    if pages_diff > 0:
        ReadingSession.objects.create(
            user=request.user,
            course=course,
            pages_read=pages_diff,
            duration_minutes=1.0,  # approximate; could be sent from client
        )
    return JsonResponse({'success': True, 'last_page_read': progress.last_page_read})


@login_required
def api_chat(request):
    """Chatbot: answer based on course content (course_id and message in POST)."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    import json as json_module
    try:
        data = json_module.loads(request.body) if request.body else {}
        course_id = data.get('course_id')
        message = (data.get('message') or '').strip()
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Invalid payload'})
    if not message:
        return JsonResponse({'success': False, 'error': 'Message is required'})
    course = None
    if course_id:
        try:
            course = Course.objects.get(id=course_id)
            Enrollment.objects.get(user=request.user, course=course)
        except (Course.DoesNotExist, Enrollment.DoesNotExist):
            course = None
    # Store user message
    ChatMessage.objects.create(user=request.user, course=course, role='user', content=message)
    # Build answer from course summary + keywords
    if course and course.summary_for_chat:
        context = course.summary_for_chat + '\n' + (course.description or '')
        answer = _answer_from_course_context(message, context, course.title)
    else:
        answer = "I can only answer questions about a course you're currently learning. Open a course and ask again, or ask about one of your enrolled courses."
    ChatMessage.objects.create(user=request.user, course=course, role='assistant', content=answer)
    return JsonResponse({'success': True, 'answer': answer})


def _answer_from_course_context(question, context, course_title):
    """Generate a short answer based on course context (keyword/template fallback)."""
    q = question.lower()
    if 'what' in q or 'explain' in q or 'define' in q:
        for sent in context.split('.'):
            if any(w in sent.lower() for w in q.replace('?', '').split()[:3]):
                return sent.strip() + '.' if sent.strip() else "This is covered in the course material. Check the relevant section in " + course_title + "."
        return "According to " + course_title + ": " + context[:300] + "..."
    if 'how' in q:
        return "The course '" + course_title + "' covers this step by step. The key points: " + context[:250] + "..."
    return "Based on " + course_title + ": " + (context[:400] + "..." if len(context) > 400 else context)


# ==================== Lesson Views ====================

@login_required
def lesson_view(request, course_id, lesson_id):
    """View lesson content"""
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    
    # Check enrollment
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
    except Enrollment.DoesNotExist:
        return redirect('course_detail', course_id=course_id)
    
    # Get quizzes for this lesson
    quizzes = lesson.quizzes.all()
    
    # Check if user has attempted quizzes
    quiz_attempts = {}
    for quiz in quizzes:
        attempts = QuizAttempt.objects.filter(user=request.user, quiz=quiz)
        if attempts.exists():
            quiz_attempts[quiz.id] = attempts.first()
    
    context = {
        'course': course,
        'lesson': lesson,
        'enrollment': enrollment,
        'quizzes': quizzes,
        'quiz_attempts': quiz_attempts
    }
    
    # Log content view
    Activity.objects.create(
        user=request.user,
        activity_type='content_viewed',
        details={
            'course_id': course.id,
            'lesson_id': lesson.id,
            'content_type': lesson.content_type
        }
    )
    
    return render(request, 'core/lesson.html', context)


@login_required
def complete_lesson(request, course_id, lesson_id):
    """Mark lesson as complete"""
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    
    # Get enrollment
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    # Update progress
    if lesson.order > enrollment.current_lesson:
        enrollment.current_lesson = lesson.order
    
    enrollment.lessons_completed += 1
    
    # Calculate progress percentage
    total_lessons = course.lessons_count
    if total_lessons > 0:
        enrollment.progress_percentage = (enrollment.lessons_completed / total_lessons) * 100
    
    # Check if course is complete
    if enrollment.lessons_completed >= total_lessons:
        enrollment.is_completed = True
        enrollment.completed_at = timezone.now()
    
    enrollment.save()
    
    # Log activity
    Activity.objects.create(
        user=request.user,
        activity_type='lesson_completed',
        details={
            'course_id': course.id,
            'lesson_id': lesson.id,
            'content_type': lesson.content_type
        }
    )
    
    return JsonResponse({'success': True, 'progress': enrollment.progress_percentage})


# ==================== Quiz Views ====================

@login_required
def submit_quiz(request, quiz_id):
    """Submit quiz answer"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    user = request.user
    
    # Get selected answer
    selected_answer = int(request.POST.get('answer'))
    
    # Check correctness
    is_correct = selected_answer == quiz.correct_answer
    score = 100 if is_correct else 0
    
    # Create attempt
    attempt = QuizAttempt.objects.create(
        user=user,
        quiz=quiz,
        selected_answer=selected_answer,
        is_correct=is_correct,
        score=score
    )
    
    # Log activity
    Activity.objects.create(
        user=user,
        activity_type='quiz_completed',
        details={
            'quiz_id': quiz.id,
            'lesson_id': quiz.lesson.id,
            'score': score,
            'correct': is_correct
        }
    )
    
    return JsonResponse({
        'success': True,
        'correct': is_correct,
        'score': score,
        'explanation': quiz.explanation
    })


# ==================== AI Recommendation Views ====================

@login_required
def recommendations_view(request):
    """Recommendations: reading habits, speed, related course links."""
    user = request.user
    sessions = ReadingSession.objects.filter(user=user).select_related('course')
    total_pages = sessions.aggregate(Sum('pages_read'))['pages_read__sum'] or 0
    total_mins = sum(s.duration_minutes or 0 for s in sessions)
    reading_speed = round(total_pages / total_mins, 1) if total_mins else 0  # pages per minute
    avg_pages_per_session = round(total_pages / sessions.count(), 1) if sessions.exists() else 0
    hour_counts = {}
    for s in sessions:
        h = s.started_at.hour
        hour_counts[h] = hour_counts.get(h, 0) + 1
    preferred_hour = max(hour_counts, key=hour_counts.get) if hour_counts else None
    preferred_time = f"{preferred_hour}:00" if preferred_hour is not None else "Not enough data"
    enrolled_qs = Enrollment.objects.filter(user=user)
    enrolled_categories = list(enrolled_qs.values_list('course__category', flat=True).distinct())
    enrolled_course_ids = list(enrolled_qs.values_list('course_id', flat=True))
    related_courses = Course.objects.filter(
        total_pages__gte=1
    ).exclude(
        id__in=enrolled_course_ids
    ).filter(category__in=enrolled_categories)[:6]
    ai_engine = AIRecommendationEngine()
    day_ago = timezone.now() - timedelta(days=1)
    recent_recommendations = list(
        Recommendation.objects.filter(
            user=user, generated_at__gte=day_ago
        ).select_related('course')[:6]
    )
    if not recent_recommendations:
        try:
            recent_recommendations = ai_engine.generate_recommendations(user, limit=6)
        except Exception:
            recent_recommendations = []
    # Fallback list of courses to recommend (simple \"you might like\"), used if no AI recommendations
    fallback_courses = []
    if not recent_recommendations:
        fallback_courses = list(
            Course.objects.exclude(id__in=enrolled_course_ids)[:6]
        )
    try:
        analyzer = BehaviorAnalyzer()
        behavior_insights = analyzer.analyze_user_behavior(user)
    except Exception:
        behavior_insights = None
    context = {
        'user': user,
        'recommendations': recent_recommendations,
        'fallback_courses': fallback_courses,
        'behavior_insights': behavior_insights,
        'reading_speed': reading_speed,
        'avg_pages_per_session': avg_pages_per_session,
        'preferred_time': preferred_time,
        'related_courses': related_courses,
        'total_pages_read': total_pages,
    }
    return render(request, 'core/recommendations.html', context)


@login_required
def refresh_recommendations(request):
    """Refresh AI recommendations"""
    user = request.user
    
    # Delete old recommendations
    Recommendation.objects.filter(user=user).delete()
    
    # Generate new ones
    ai_engine = AIRecommendationEngine()
    recommendations = ai_engine.generate_recommendations(user)
    
    return JsonResponse({
        'success': True,
        'count': len(recommendations)
    })


# ==================== Feedback Views ====================

@login_required
def feedback_view(request):
    """View user feedback"""
    user = request.user
    
    # Generate new feedback
    feedback_generator = FeedbackGenerator()
    feedback_items = feedback_generator.generate_feedback(user)
    
    # Mark feedback as read
    Feedback.objects.filter(user=user, is_read=False).update(is_read=True)
    
    # Get all feedback
    all_feedback = Feedback.objects.filter(user=user).order_by('-created_at')[:20]
    
    context = {
        'feedback': all_feedback,
        'user': user
    }
    
    return render(request, 'core/feedback.html', context)


@login_required
def dismiss_feedback(request, feedback_id):
    """Dismiss feedback notification"""
    feedback = get_object_or_404(Feedback, id=feedback_id, user=request.user)
    feedback.is_dismissed = True
    feedback.save()
    
    return JsonResponse({'success': True})


# ==================== API Endpoints ====================

@login_required
def api_stats(request):
    """API endpoint for user statistics"""
    user = request.user

    enrollments = Enrollment.objects.filter(user=user)

    stats = {
        'courses_enrolled': enrollments.count(),
        'lessons_completed': sum(e.lessons_completed for e in enrollments),
        'quizzes_taken': user.quiz_attempts.count(),
        'quiz_average': 0,
        'total_learning_hours': Activity.objects.filter(
            user=user,
            activity_type='learning_time'
        ).count(),
        'last_updated': timezone.now().isoformat()
    }

    if stats['quizzes_taken'] > 0:
        stats['quiz_average'] = round(
            user.quiz_attempts.aggregate(Avg('score'))['score__avg'] or 0,
            1
        )

    return JsonResponse(stats)


@login_required
def api_progress(request):
    """API endpoint for progress data"""
    user = request.user

    weekly_progress = get_weekly_progress(user)

    return JsonResponse({
        'weekly_progress': weekly_progress,
        'last_updated': timezone.now().isoformat()
    })


@login_required
def search_internet(request):
    """API endpoint for internet search"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})

    query = request.POST.get('query', '').strip()
    if not query:
        return JsonResponse({'success': False, 'error': 'Query is required'})

    try:
        from .services import AIRecommendationEngine
        engine = AIRecommendationEngine()
        resources = engine._get_internet_resources(query, 'general', limit=10)

        return JsonResponse({
            'success': True,
            'resources': resources
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
