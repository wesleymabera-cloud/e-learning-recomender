"""
AI Recommendation Engine for LearnAI Platform
Implements multi-factor recommendation algorithm with behavior analysis
"""

from django.db.models import Avg, Count, Q
from .models import User, Course, Activity, Enrollment, Recommendation, Feedback
from django.utils import timezone
from datetime import timedelta


class AIRecommendationEngine:
    """
    Advanced AI recommendation system that analyzes learner behavior,
    performance, and preferences to generate personalized recommendations.
    """
    
    def __init__(self):
        self.factor_weights = {
            'interest_match': 0.30,
            'skill_level': 0.25,
            'content_match': 0.20,
            'progress_factor': 0.15,
            'popularity': 0.10
        }
    
    def generate_recommendations(self, user, limit=6):
        """
        Generate personalized recommendations for a user

        Args:
            user: User object
            limit: Maximum number of recommendations to return

        Returns:
            List of Recommendation objects
        """
        # Get all courses not yet enrolled by user
        enrolled_courses = Enrollment.objects.filter(user=user).values_list('course_id', flat=True)
        available_courses = Course.objects.exclude(id__in=enrolled_courses)

        recommendations = []

        for course in available_courses:
            # Calculate scores for each factor
            scores = self._calculate_all_scores(user, course)

            # Calculate total weighted score
            total_score = sum(
                scores[factor] * self.factor_weights[factor]
                for factor in self.factor_weights.keys()
            )

            # Generate reasons for this recommendation
            reasons = self._generate_reasons(course, scores, user)

            # Get internet research results
            internet_resources = self._get_internet_resources(course.title, course.category)

            # Create recommendation record
            recommendation = Recommendation.objects.create(
                user=user,
                course=course,
                total_score=round(total_score * 100, 2),
                factor_scores={k: round(v * 100, 2) for k, v in scores.items()},
                reasons=reasons
            )

            # Add internet resources to reasons
            if internet_resources:
                recommendation.reasons.extend([f"Online resource: {res['title']} - {res['url']}" for res in internet_resources[:3]])
                recommendation.save()

            recommendations.append(recommendation)

        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x.total_score, reverse=True)
        return recommendations[:limit]

    def _get_internet_resources(self, course_title, category, limit=10):
        """
        Perform internet research to find related courses and resources

        Args:
            course_title: Title of the course
            category: Category of the course
            limit: Maximum number of resources to return

        Returns:
            List of dictionaries with 'title' and 'url' keys
        """
        resources = []

        try:
            # Search query for related courses
            query = f"{course_title} {category} online course tutorial"
            search_url = f"https://www.google.com/search?q={query}&num={limit}"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract search results
            for result in soup.find_all('div', class_='g')[:limit]:
                title_elem = result.find('h3')
                link_elem = result.find('a')

                if title_elem and link_elem:
                    title = title_elem.get_text()
                    url = link_elem.get('href')

                    # Filter out unwanted results
                    if url and 'google.com' not in url and 'youtube.com' in url or 'coursera.org' in url or 'udemy.com' in url or 'edX.org' in url:
                        resources.append({
                            'title': title,
                            'url': url
                        })

            # If not enough results, try additional searches
            if len(resources) < 5:
                # Search on Coursera
                coursera_query = f"{course_title} {category}".replace(' ', '+')
                coursera_url = f"https://www.coursera.org/search?query={coursera_query}"

                coursera_response = requests.get(coursera_url, headers=headers, timeout=10)
                if coursera_response.status_code == 200:
                    coursera_soup = BeautifulSoup(coursera_response.text, 'html.parser')
                    course_cards = coursera_soup.find_all('div', {'data-testid': 'course-card'})[:5]

                    for card in course_cards:
                        title_elem = card.find('h3')
                        link_elem = card.find('a')
                        if title_elem and link_elem:
                            title = title_elem.get_text().strip()
                            url = "https://www.coursera.org" + link_elem.get('href')
                            resources.append({
                                'title': f"Coursera: {title}",
                                'url': url
                            })

        except Exception as e:
            # If internet search fails, return empty list
            print(f"Internet research failed: {e}")
            pass

        return resources[:limit]

    def _calculate_all_scores(self, user, course):
        """Calculate scores for all recommendation factors"""
        return {
            'interest_match': self._calculate_interest_match(user, course),
            'skill_level': self._calculate_skill_level_match(user, course),
            'content_match': self._calculate_content_match(user, course),
            'progress_factor': self._calculate_progress_factor(user, course),
            'popularity': self._calculate_popularity_factor(course)
        }
    
    def _calculate_interest_match(self, user, course):
        """
        Calculate how well course matches user's interests
        
        Returns score between 0.0 and 1.0
        """
        if not user.interests:
            return 0.5
        
        # Build course keywords from topics, category, and title
        course_keywords = []
        course_keywords.extend(course.topics)
        course_keywords.append(course.category.lower())
        course_keywords.extend(course.title.lower().split())
        
        matches = 0
        for interest in user.interests:
            interest_lower = interest.lower()
            if any(keyword.lower() in interest_lower or 
                   interest_lower in keyword.lower() 
                   for keyword in course_keywords):
                matches += 1
        
        # Normalize score
        return min(matches / max(len(user.interests), 1), 1.0)
    
    def _calculate_skill_level_match(self, user, course):
        """
        Calculate alignment between user skill level and course difficulty
        
        Returns score between 0.0 and 1.0
        """
        level_map = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
        
        user_level = level_map.get(user.skill_level, 1)
        course_level = level_map.get(course.level, 2)
        
        diff = abs(user_level - course_level)
        
        # Perfect match = 1.0, adjacent level = 0.7, two levels apart = 0.4
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.7
        else:
            return 0.4
    
    def _calculate_content_match(self, user, course):
        """
        Calculate match between user's preferred content type and course content
        
        Returns score between 0.0 and 1.0
        """
        # This would analyze actual course content in a real system
        # For now, use a simplified approach based on course content_types
        
        if not course.content_types:
            return 0.7
        
        if user.preferred_content_type in course.content_types:
            return 0.9
        
        # Partial match if course has multiple content types
        content_scores = {
            'video': 0.9,
            'text': 0.7,
            'interactive': 0.85,
            'quiz': 0.8
        }
        
        return content_scores.get(user.preferred_content_type, 0.7)
    
    def _calculate_progress_factor(self, user, course):
        """
        Calculate factor based on user's progress with similar courses
        
        Returns score between 0.0 and 1.0
        """
        # Check if user has enrolled courses in same category
        enrollments = Enrollment.objects.filter(
            user=user,
            course__category=course.category
        )
        
        # Encourage continuing in same category with in-progress courses
        in_progress = enrollments.filter(
            is_completed=False,
            progress_percentage__gt=0
        ).count()
        
        if in_progress > 0:
            return 0.9
        elif enrollments.count() > 0:
            return 0.8
        
        # Slightly prefer new categories to explore
        return 0.7
    
    def _calculate_popularity_factor(self, user, course):
        """
        Calculate popularity factor based on rating and enrollment
        
        Returns score between 0.0 and 1.0
        """
        # Normalize rating (0-5 to 0-1)
        rating_score = course.rating / 5.0 if course.rating > 0 else 0.5
        
        # Normalize enrollment (capped at 2000 for scale)
        enrollment_score = min(course.enrolled_count / 2000.0, 1.0)
        
        # Weight rating more than enrollment
        return (rating_score * 0.6) + (enrollment_score * 0.4)
    
    def _generate_reasons(self, course, scores, user):
        """Generate personalized reasons for recommendation"""
        reasons = []
        
        # High-interest match
        if scores['interest_match'] > 0.7:
            reasons.append(f"Matches your interest in {course.category}")
        
        # Perfect skill level
        if scores['skill_level'] == 1.0:
            reasons.append(f"Perfect for your {course.level.lower()} skill level")
        elif scores['skill_level'] > 0.7:
            reasons.append(f"Suitable for your current skill level")
        
        # Content type preference
        if scores['content_match'] > 0.8:
            reasons.append("Delivered in your preferred format")
        
        # Progress continuation
        if scores['progress_factor'] > 0.85:
            reasons.append("Continue your progress in this area")
        
        # Popularity
        if scores['popularity'] > 0.8:
            reasons.append(f"Highly rated by {course.enrolled_count}+ learners")
        
        # Default reason
        if not reasons:
            reasons.append("Recommended based on your learning profile")
        
        return reasons


class BehaviorAnalyzer:
    """
    Analyzes user behavior to update learning profiles and provide insights
    """
    
    def analyze_user_behavior(self, user):
        """
        Analyze user's recent behavior and update learning profile
        
        Returns:
            Dictionary with behavior insights
        """
        # Get recent activities (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_activities = Activity.objects.filter(
            user=user,
            timestamp__gte=thirty_days_ago
        )
        
        # Analyze content type preferences
        content_type_usage = self._analyze_content_preferences(recent_activities)
        
        # Analyze learning pace
        learning_pace = self._analyze_learning_pace(recent_activities)
        
        # Analyze quiz performance
        quiz_performance = self._analyze_quiz_performance(user, thirty_days_ago)
        
        # Analyze skill level progression
        skill_level = self._analyze_skill_level(user)
        
        # Update user's learning profile
        self._update_learning_profile(user, {
            'preferred_content_type': content_type_usage.get('most_used', 'video'),
            'learning_pace': learning_pace,
            'skill_level': skill_level
        })
        
        return {
            'content_preferences': content_type_usage,
            'learning_pace': learning_pace,
            'quiz_performance': quiz_performance,
            'skill_level': skill_level
        }
    
    def _analyze_content_preferences(self, activities):
        """Analyze which content types user prefers"""
        content_usage = {}
        
        for activity in activities:
            content_type = activity.details.get('content_type')
            if content_type:
                content_usage[content_type] = content_usage.get(content_type, 0) + 1
        
        if not content_usage:
            return {'most_used': 'video', 'distribution': {}}
        
        most_used = max(content_usage.items(), key=lambda x: x[1])[0]
        
        # Calculate percentage distribution
        total = sum(content_usage.values())
        distribution = {
            k: round(v / total * 100, 1) 
            for k, v in content_usage.items()
        }
        
        return {
            'most_used': most_used,
            'distribution': distribution
        }
    
    def _analyze_learning_pace(self, activities):
        """Determine user's learning pace based on hours spent"""
        learning_time_activities = activities.filter(activity_type='learning_time')
        total_hours = sum(
            activity.details.get('hours', 0) 
            for activity in learning_time_activities
        )
        
        # Average hours per week (assuming 30 days ≈ 4.3 weeks)
        avg_hours_per_week = total_hours / 4.3
        
        if avg_hours_per_week >= 10:
            return 'intensive'
        elif avg_hours_per_week >= 5:
            return 'moderate'
        else:
            return 'slow'
    
    def _analyze_quiz_performance(self, user, since_date):
        """Analyze recent quiz performance"""
        from .models import QuizAttempt
        
        recent_attempts = QuizAttempt.objects.filter(
            user=user,
            attempted_at__gte=since_date
        )
        
        if not recent_attempts.exists():
            return {'average': 0, 'count': 0, 'trend': 'stable'}
        
        scores = [attempt.score for attempt in recent_attempts]
        average = sum(scores) / len(scores)
        
        # Calculate trend (compare first half vs second half)
        mid = len(scores) // 2
        if mid > 0:
            first_half_avg = sum(scores[:mid]) / mid
            second_half_avg = sum(scores[mid:]) / len(scores[mid:])
            
            if second_half_avg > first_half_avg + 10:
                trend = 'improving'
            elif second_half_avg < first_half_avg - 10:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        return {
            'average': round(average, 1),
            'count': recent_attempts.count(),
            'trend': trend
        }
    
    def _analyze_skill_level(self, user):
        """Determine user's skill level based on performance"""
        enrollments = Enrollment.objects.filter(user=user)
        
        # Count completed courses
        completed_courses = enrollments.filter(is_completed=True).count()
        
        # Get average quiz score
        quiz_attempts = user.quiz_attempts.all()
        if quiz_attempts.exists():
            avg_quiz_score = quiz_attempts.aggregate(Avg('score'))['score__avg'] or 0
        else:
            avg_quiz_score = 0
        
        # Determine skill level
        if completed_courses >= 3 and avg_quiz_score >= 85:
            return 'advanced'
        elif completed_courses >= 1 and avg_quiz_score >= 70:
            return 'intermediate'
        else:
            return 'beginner'
    
    def _update_learning_profile(self, user, updates):
        """Update user's learning profile based on behavior analysis"""
        user.preferred_content_type = updates.get('preferred_content_type', user.preferred_content_type)
        user.learning_pace = updates.get('learning_pace', user.learning_pace)
        user.skill_level = updates.get('skill_level', user.skill_level)
        user.save()


class FeedbackGenerator:
    """
    Generates intelligent feedback based on user performance and behavior
    """
    
    def generate_feedback(self, user):
        """
        Generate personalized feedback for a user
        
        Returns:
            List of Feedback objects
        """
        feedback_items = []
        
        # Get user's progress
        enrollments = Enrollment.objects.filter(user=user)
        progress = self._calculate_user_progress(enrollments)
        
        # Get recent quiz performance
        recent_quiz_performance = self._get_recent_quiz_performance(user)
        
        # Get recent activity
        last_activity = Activity.objects.filter(user=user).first()
        
        # Generate positive feedback
        feedback_items.extend(self._generate_positive_feedback(progress, recent_quiz_performance))
        
        # Generate warning feedback
        feedback_items.extend(self._generate_warning_feedback(progress, recent_quiz_performance, last_activity))
        
        # Generate informational feedback
        feedback_items.extend(self._generate_info_feedback(progress, last_activity))
        
        # Save feedback to database
        saved_feedback = []
        for item in feedback_items:
            feedback = Feedback.objects.create(
                user=user,
                feedback_type=item['type'],
                title=item['title'],
                message=item['message']
            )
            saved_feedback.append(feedback)
        
        return saved_feedback
    
    def _calculate_user_progress(self, enrollments):
        """Calculate user's overall progress metrics"""
        return {
            'courses_enrolled': enrollments.count(),
            'courses_completed': enrollments.filter(is_completed=True).count(),
            'lessons_completed': sum(e.lessons_completed for e in enrollments),
            'total_learning_hours': sum(
                Activity.objects.filter(
                    user=e.user,
                    activity_type='learning_time',
                    details__course_id=e.course.id
                ).count() for e in enrollments
            )
        }
    
    def _get_recent_quiz_performance(self, user):
        """Get user's recent quiz performance"""
        from .models import QuizAttempt
        from datetime import timedelta
        
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_attempts = QuizAttempt.objects.filter(
            user=user,
            attempted_at__gte=seven_days_ago
        )
        
        if recent_attempts.exists():
            scores = [attempt.score for attempt in recent_attempts]
            return {
                'average': sum(scores) / len(scores),
                'count': len(scores),
                'recent_scores': scores
            }
        return None
    
    def _generate_positive_feedback(self, progress, quiz_performance):
        """Generate positive/achievement feedback"""
        feedback = []
        
        # Milestone achievements
        if progress['lessons_completed'] > 0 and progress['lessons_completed'] % 10 == 0:
            feedback.append({
                'type': 'achievement',
                'title': '🎉 Milestone Achieved!',
                'message': f"Congratulations! You've completed {progress['lessons_completed']} lessons. Keep up the great momentum!"
            })
        
        # Course completion
        if progress['courses_completed'] > 0:
            feedback.append({
                'type': 'achievement',
                'title': '🏆 Course Completed!',
                'message': f"You've completed {progress['courses_completed']} course(s). Excellent dedication to your learning journey!"
            })
        
        # Exceptional quiz performance
        if quiz_performance and quiz_performance['average'] >= 85:
            feedback.append({
                'type': 'success',
                'title': '⭐ Excellent Performance!',
                'message': f"Your recent quiz average of {quiz_performance['average']:.1f}% shows exceptional understanding of the material."
            })
        
        return feedback
    
    def _generate_warning_feedback(self, progress, quiz_performance, last_activity):
        """Generate warning feedback about performance issues"""
        feedback = []
        
        # Performance decline
        if quiz_performance and quiz_performance['count'] >= 3:
            recent_scores = quiz_performance['recent_scores']
            mid = len(recent_scores) // 2
            if mid > 0:
                first_half_avg = sum(recent_scores[:mid]) / mid
                second_half_avg = sum(recent_scores[mid:]) / len(recent_scores[mid:])
                
                if second_half_avg < first_half_avg - 10:
                    feedback.append({
                        'type': 'warning',
                        'title': '⚠️ Performance Decline',
                        'message': 'Your recent quiz scores have dropped. Consider reviewing previous lessons or taking a short break.'
                    })
        
        # Inactivity warning
        if last_activity:
            days_since_activity = (timezone.now() - last_activity.timestamp).days
            if days_since_activity > 7:
                feedback.append({
                    'type': 'warning',
                    'title': '📅 We Miss You!',
                    'message': f"It's been {days_since_activity} days since your last activity. Consistent learning helps maintain momentum."
                })
        
        return feedback
    
    def _generate_info_feedback(self, progress, last_activity):
        """Generate informational feedback and tips"""
        feedback = []
        
        # Learning efficiency
        if progress['lessons_completed'] > 20 and progress['courses_completed'] < 1:
            feedback.append({
                'type': 'info',
                'title': '📊 Learning Efficiency',
                'message': "You've completed many lessons across different courses. Consider focusing on completing one course to build deeper knowledge."
            })
        
        # Consistency reminder
        if last_activity:
            hours_since_activity = (timezone.now() - last_activity.timestamp).total_seconds() / 3600
            if 3 < hours_since_activity < 72:
                feedback.append({
                    'type': 'info',
                    'title': '💡 Great Progress!',
                    'message': "You're maintaining a good learning rhythm. Keep up the consistent effort!"
                })
        
        return feedback