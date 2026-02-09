# LearnAI - Django-Powered E-Learning Platform with AI

## 🎯 Overview

This is a **full-featured Django e-learning platform** that integrates artificial intelligence to provide personalized learning experiences. The platform successfully addresses all four specific objectives with a robust backend, AI algorithms, and modern frontend.

## 📦 Project Structure

```
learnai/
├── core/                          # Main application
│   ├── models.py                 # Database models (9 models)
│   ├── views.py                  # All view functions
│   ├── urls.py                   # URL routing
│   ├── admin.py                  # Django admin configuration
│   ├── services.py               # AI recommendation engine
│   ├── migrations/               # Database migrations
│   ├── management/commands/      # Custom management commands
│   └── templates/core/           # HTML templates
├── templates/                    # Base templates
│   ├── base.html                # Master template
│   └── core/                    # App templates
├── learnai/                      # Django project settings
│   ├── settings.py              # Configuration
│   ├── urls.py                  # Project URLs
│   └── wsgi.py                  # WSGI configuration
└── manage.py                     # Django management script
```

## 🗄️ Database Models

### 1. User (Extended AbstractUser)
```python
# Learning Profile
- learning_style: Visual, Auditory, Kinesthetic, Reading/Writing
- skill_level: Beginner, Intermediate, Advanced
- learning_pace: Slow, Moderate, Intensive
- preferred_content_type: video, text, interactive, quiz
- interests: JSON array of interests

# Behavior Tracking
- login_count: Integer
- last_active_date: DateTime
- average_session_duration: Float
- preferred_study_time: String
```

### 2. Course
```python
- title, description, category, level
- duration_hours, lessons_count
- enrolled_count, rating
- topics: JSON array
- content_types: JSON array
```

### 3. Enrollment
```python
- user, course
- lessons_completed, progress_percentage
- current_lesson, is_completed
- completed_at
```

### 4. Lesson
```python
- course, title, description
- content_type: text, video, quiz, interactive
- content_text, video_url
- order
```

### 5. Quiz
```python
- lesson, question
- options: JSON array
- correct_answer: Integer
- explanation
```

### 6. QuizAttempt
```python
- user, quiz
- selected_answer, is_correct
- score, attempted_at
```

### 7. Activity
```python
- user, activity_type
- details: JSON object
- timestamp, session_duration
```

### 8. Recommendation
```python
- user, course
- total_score: Float
- factor_scores: JSON object
- reasons: JSON array
- is_viewed, is_enrolled
```

### 9. Feedback
```python
- user, feedback_type
- title, message
- is_read, is_dismissed
```

## 🤖 AI Recommendation Engine

### Location: `core/services.py`

### AIRecommendationEngine Class

**Multi-Factor Scoring System:**
```python
Factor Weights:
├── Interest Match: 30%
├── Skill Level Alignment: 25%
├── Content Type Preference: 20%
├── Progress Factor: 15%
└── Popularity & Rating: 10%
```

**Key Methods:**
- `generate_recommendations(user, limit)` - Main recommendation logic
- `_calculate_interest_match()` - Matches user interests with course topics
- `_calculate_skill_level_match()` - Aligns difficulty with user skill
- `_calculate_content_match()` - Prefers user's favorite content types
- `_calculate_progress_factor()` - Encourages continuing in-progress courses
- `_calculate_popularity_factor()` - Considers rating and enrollment
- `_generate_reasons()` - Creates personalized explanation for each recommendation

### BehaviorAnalyzer Class

**Methods:**
- `analyze_user_behavior(user)` - Comprehensive behavior analysis
- `_analyze_content_preferences()` - Determines preferred content types
- `_analyze_learning_pace()` - Calculates hours per week
- `_analyze_quiz_performance()` - Tracks score trends
- `_analyze_skill_level()` - Determines current skill level
- `_update_learning_profile()` - Updates user profile automatically

### FeedbackGenerator Class

**Methods:**
- `generate_feedback(user)` - Creates personalized feedback
- `_generate_positive_feedback()` - Achievements and milestones
- `_generate_warning_feedback()` - Performance declines, inactivity
- `_generate_info_feedback()` - Tips and suggestions

## 🚀 Features Implemented

### ✅ Objective 1: User-Friendly E-Learning Platform

**Authentication System:**
- User registration with interest selection
- Login/logout functionality
- Session management
- Custom user model with learning profile

**Content Delivery:**
- Course catalog with 6 sample courses
- Detailed course pages
- Lessons with multiple content types
- Interactive quizzes with scoring
- Progress tracking per lesson

**User Interface:**
- Modern, responsive design
- Card-based layouts
- Gradient color schemes
- Smooth animations
- Mobile-friendly

### ✅ Objective 2: AI Behavior Analysis Algorithms

**Behavior Tracking:**
- Login frequency and patterns
- Session duration monitoring
- Content type preferences
- Quiz performance trends
- Learning pace calculation
- Study time preferences

**Analysis Features:**
- Content preference distribution
- Learning pace classification
- Quiz performance average and trend
- Skill level progression
- Automatic profile updates

**Data Points Tracked:**
- Activity types: lesson_completed, quiz_completed, course_enrolled, learning_time
- Session duration in minutes
- Content type usage statistics
- Quiz scores over time

### ✅ Objective 3: Personalized Recommendations

**Recommendation Algorithm:**
- 5-factor weighted scoring system
- Interest matching with course topics
- Skill level alignment
- Content type preferences
- Progress continuation incentives
- Popularity and rating consideration

**Dynamic Updates:**
- Recommendations refresh on demand
- Learning profile evolves with activity
- Real-time adaptation to performance
- Context-aware suggestions

**Output:**
- Top 6 recommended courses
- Match score percentage
- Personalized reasons for each recommendation
- Factor breakdown for transparency

### ✅ Objective 4: Performance Tracking & Feedback

**Dashboard Statistics:**
- Courses enrolled count
- Lessons completed count
- Quiz average percentage
- Total learning hours

**Visual Progress:**
- Weekly progress chart
- Activity timeline
- Progress bars per course

**Intelligent Feedback:**
- Achievement notifications (milestones, course completions)
- Performance warnings (declining scores, inactivity)
- Informational tips (learning efficiency, consistency)
- Context-aware messages based on behavior

## 🔧 Setup Instructions

### Prerequisites
```bash
Python 3.11+
pip
```

### Installation

1. **Install Dependencies:**
```bash
pip install django djangorestframework
```

2. **Run Migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

3. **Create Superuser:**
```bash
python manage.py createsuperuser
```

4. **Populate Sample Data:**
```bash
python manage.py populate_sample_data
```

5. **Run Development Server:**
```bash
python manage.py runserver
```

6. **Access the Application:**
```
http://localhost:8000
```

### Admin Interface
Access Django admin at: `http://localhost:8000/admin/`

**Features:**
- Manage users and learning profiles
- Create/edit courses and lessons
- Monitor enrollments and progress
- View activities and recommendations
- Manage feedback

## 📊 API Endpoints

### Authentication
- `POST /register/` - User registration
- `POST /login/` - User login
- `GET /logout/` - User logout

### Dashboard
- `GET /dashboard/` - User dashboard with stats

### Courses
- `GET /courses/` - Course catalog (with search/filter)
- `GET /courses/<id>/` - Course details
- `POST /courses/<id>/enroll/` - Enroll in course

### Lessons
- `GET /courses/<course_id>/lessons/<lesson_id>/` - View lesson
- `POST /courses/<course_id>/lessons/<lesson_id>/complete/` - Mark complete

### Quizzes
- `POST /quizzes/<quiz_id>/submit/` - Submit quiz answer

### Recommendations
- `GET /recommendations/` - AI recommendations
- `POST /recommendations/refresh/` - Refresh recommendations

### Feedback
- `GET /feedback/` - View feedback
- `POST /feedback/<id>/dismiss/` - Dismiss feedback

### API Data
- `GET /api/stats/` - User statistics (JSON)
- `GET /api/progress/` - Progress data (JSON)

## 🎨 Templates Structure

### Base Template: `templates/base.html`
- Navigation bar
- Footer
- CSS styles
- Content blocks

### Page Templates:
- `index.html` - Home page with features
- `dashboard.html` - User dashboard with analytics
- `courses.html` - Course catalog
- `recommendations.html` - AI recommendations with insights
- `login.html` - Login form
- `register.html` - Registration form

## 📈 Sample Data Included

The platform comes pre-populated with:

**6 Courses:**
1. Machine Learning Fundamentals (Intermediate)
2. Modern Web Development (Beginner)
3. Data Science with Python (Intermediate)
4. Cloud Computing Essentials (Beginner)
5. AI for Business Applications (Advanced)
6. React Native Development (Intermediate)

**Each Course Includes:**
- 5 lessons with varied content types
- Quizzes for each lesson
- Progress tracking
- Rating and enrollment stats

## 🔐 Security Features

- CSRF protection enabled
- User authentication required for protected views
- Login_required decorators
- Secure password hashing
- Session management

## 🚀 Deployment Ready

The application is ready for deployment with:

- Production-grade Django structure
- Database migrations
- Static file handling
- Admin interface
- API endpoints
- Error handling

## 🎯 Project Compliance

### All Four Objectives Completed:

1. ✅ **User-Friendly E-Learning Platform**
   - Modern Django templates
   - Complete authentication system
   - Multi-format content delivery
   - Responsive design

2. ✅ **AI Behavior Analysis Algorithms**
   - Sophisticated Python classes
   - Multi-factor analysis
   - Real-time behavior tracking
   - Automatic profile updates

3. ✅ **Personalized Recommendations**
   - Weighted scoring algorithm
   - 5-factor recommendation system
   - Dynamic reason generation
   - Refresh on demand

4. ✅ **Performance Tracking & Feedback**
   - Comprehensive dashboard
   - Visual progress charts
   - Intelligent feedback system
   - Real-time statistics

## 📝 Live Demo

**Access the platform at:**
https://learnai-000uu.app.super.myninja.ai

**Features to Try:**
1. Register a new account with interests
2. Browse courses and enroll
3. View dashboard with analytics
4. Check AI recommendations
5. Take quizzes and track progress
6. View intelligent feedback

## 🔮 Future Enhancements

Potential additions for production:

1. **Advanced ML Integration**
   - TensorFlow.js for client-side ML
   - Scikit-learn for server-side predictions
   - Real-time personalization

2. **Enhanced Features**
   - Video hosting integration
   - Discussion forums
   - Peer learning features
   - Gamification system

3. **Technical Improvements**
   - Redis caching
   - Celery for async tasks
   - PostgreSQL database
   - CDN for static files

4. **Analytics**
   - Advanced reporting dashboard
   - Instructor analytics
   - Learning path recommendations
   - A/B testing

## 📄 License

This is a demonstration project created for educational purposes.

## 👨‍💻 Technical Stack

**Backend:**
- Django 5.2
- Python 3.11
- Django REST Framework
- SQLite (development)

**Frontend:**
- Django Templates
- CSS3 with Variables
- Vanilla JavaScript
- Responsive Design

**AI/ML:**
- Custom Python algorithms
- Multi-factor scoring
- Behavior analysis
- Dynamic personalization

---

## 🎉 Conclusion

This Django-powered LearnAI platform successfully demonstrates a complete, production-ready e-learning system with integrated AI capabilities. All four specific objectives have been fully implemented with:

- **Robust Backend:** Django models, views, and services
- **AI Algorithms:** Sophisticated recommendation engine
- **Modern Frontend:** Responsive templates with modern design
- **Complete Features:** Authentication, content delivery, tracking, and feedback

The platform is fully functional, deployed, and ready for use as a prototype or foundation for further development.