// LearnAI - Intelligent E-Learning Platform
// Main JavaScript Application

// ==========================================
// USER MANAGEMENT SYSTEM
// ==========================================

class UserManagement {
    constructor() {
        this.users = this.loadUsers();
        this.currentUser = this.loadCurrentUser();
    }

    loadUsers() {
        const stored = localStorage.getItem('learnai_users');
        return stored ? JSON.parse(stored) : [];
    }

    saveUsers() {
        localStorage.setItem('learnai_users', JSON.stringify(this.users));
    }

    loadCurrentUser() {
        const stored = localStorage.getItem('learnai_current_user');
        return stored ? JSON.parse(stored) : null;
    }

    saveCurrentUser(user) {
        localStorage.setItem('learnai_current_user', JSON.stringify(user));
    }

    register(userData) {
        const existingUser = this.users.find(u => u.email === userData.email);
        if (existingUser) {
            throw new Error('User with this email already exists');
        }

        const newUser = {
            id: this.generateId(),
            ...userData,
            createdAt: new Date().toISOString(),
            learningProfile: {
                learningStyle: 'visual',
                skillLevel: 'beginner',
                interests: userData.interests || [],
                learningPace: 'moderate',
                preferredContentType: 'video'
            },
            progress: {
                coursesEnrolled: 0,
                lessonsCompleted: 0,
                quizzesTaken: 0,
                quizAverage: 0,
                totalLearningHours: 0
            },
            behavior: {
                lastActiveDate: new Date().toISOString(),
                loginCount: 0,
                averageSessionDuration: 0,
                preferredStudyTime: 'morning'
            }
        };

        this.users.push(newUser);
        this.saveUsers();
        return newUser;
    }

    login(email, password) {
        const user = this.users.find(u => u.email === email && u.password === password);
        if (!user) {
            throw new Error('Invalid email or password');
        }

        // Update user behavior
        user.behavior.lastActiveDate = new Date().toISOString();
        user.behavior.loginCount++;
        
        this.saveCurrentUser(user);
        this.saveUsers();
        return user;
    }

    logout() {
        localStorage.removeItem('learnai_current_user');
        this.currentUser = null;
    }

    updateProfile(updates) {
        if (!this.currentUser) return;
        
        Object.assign(this.currentUser, updates);
        const userIndex = this.users.findIndex(u => u.id === this.currentUser.id);
        if (userIndex !== -1) {
            this.users[userIndex] = this.currentUser;
            this.saveUsers();
            this.saveCurrentUser(this.currentUser);
        }
    }

    generateId() {
        return 'user_' + Math.random().toString(36).substr(2, 9);
    }

    isLoggedIn() {
        return this.currentUser !== null;
    }

    getCurrentUser() {
        return this.currentUser;
    }
}

// ==========================================
// COURSE MANAGEMENT SYSTEM
// ==========================================

class CourseManagement {
    constructor() {
        this.courses = this.loadCourses();
        this.initializeDefaultCourses();
    }

    loadCourses() {
        const stored = localStorage.getItem('learnai_courses');
        return stored ? JSON.parse(stored) : [];
    }

    saveCourses() {
        localStorage.setItem('learnai_courses', JSON.stringify(this.courses));
    }

    initializeDefaultCourses() {
        if (this.courses.length === 0) {
            this.courses = [
                {
                    id: 'course_ml',
                    title: 'Machine Learning Fundamentals',
                    description: 'Learn the basics of ML, including supervised and unsupervised learning, neural networks, and practical applications.',
                    category: 'Data Science',
                    level: 'Intermediate',
                    duration: '40 hours',
                    lessons: 15,
                    enrolled: 1250,
                    rating: 4.8,
                    progress: 65,
                    topics: ['Supervised Learning', 'Unsupervised Learning', 'Neural Networks', 'Model Evaluation']
                },
                {
                    id: 'course_web',
                    title: 'Modern Web Development',
                    description: 'Master HTML5, CSS3, JavaScript, and React to build responsive, interactive web applications.',
                    category: 'Web Development',
                    level: 'Beginner',
                    duration: '35 hours',
                    lessons: 20,
                    enrolled: 2100,
                    rating: 4.9,
                    progress: 30,
                    topics: ['HTML5 & CSS3', 'JavaScript ES6+', 'React Fundamentals', 'State Management']
                },
                {
                    id: 'course_data',
                    title: 'Data Science with Python',
                    description: 'Comprehensive guide to data analysis, visualization, and machine learning using Python.',
                    category: 'Data Science',
                    level: 'Intermediate',
                    duration: '50 hours',
                    lessons: 25,
                    enrolled: 980,
                    rating: 4.7,
                    progress: 0,
                    topics: ['Pandas', 'NumPy', 'Matplotlib', 'Scikit-learn']
                },
                {
                    id: 'course_cloud',
                    title: 'Cloud Computing Essentials',
                    description: 'Understand cloud architecture, AWS services, and deployment strategies for modern applications.',
                    category: 'Cloud Computing',
                    level: 'Beginner',
                    duration: '30 hours',
                    lessons: 18,
                    enrolled: 760,
                    rating: 4.6,
                    progress: 0,
                    topics: ['AWS Basics', 'Cloud Architecture', 'Serverless', 'DevOps']
                },
                {
                    id: 'course_ai',
                    title: 'AI for Business Applications',
                    description: 'Learn how to implement AI solutions in real-world business scenarios and drive innovation.',
                    category: 'Artificial Intelligence',
                    level: 'Advanced',
                    duration: '45 hours',
                    lessons: 22,
                    enrolled: 540,
                    rating: 4.8,
                    progress: 0,
                    topics: ['AI Strategy', 'NLP', 'Computer Vision', 'Ethics']
                },
                {
                    id: 'course_mobile',
                    title: 'React Native Development',
                    description: 'Build cross-platform mobile applications using React Native and best practices.',
                    category: 'Mobile Development',
                    level: 'Intermediate',
                    duration: '38 hours',
                    lessons: 19,
                    enrolled: 890,
                    rating: 4.7,
                    progress: 0,
                    topics: ['React Native Basics', 'Navigation', 'API Integration', 'Publishing']
                }
            ];
            this.saveCourses();
        }
    }

    getAllCourses() {
        return this.courses;
    }

    getCourseById(id) {
        return this.courses.find(c => c.id === id);
    }

    getCoursesByCategory(category) {
        return this.courses.filter(c => c.category === category);
    }

    searchCourses(query) {
        const lowerQuery = query.toLowerCase();
        return this.courses.filter(c => 
            c.title.toLowerCase().includes(lowerQuery) ||
            c.description.toLowerCase().includes(lowerQuery) ||
            c.topics.some(t => t.toLowerCase().includes(lowerQuery))
        );
    }
}

// ==========================================
// AI RECOMMENDATION ENGINE
// ==========================================

class AIRecommendationEngine {
    constructor(userManagement, courseManagement) {
        this.userManagement = userManagement;
        this.courseManagement = courseManagement;
    }

    generateRecommendations() {
        const user = this.userManagement.getCurrentUser();
        if (!user) return [];

        const courses = this.courseManagement.getAllCourses();
        const profile = user.learningProfile;
        const progress = user.progress;
        const behavior = user.behavior;

        // Calculate recommendation scores for each course
        const scoredCourses = courses.map(course => {
            let score = 0;
            const factors = [];

            // Factor 1: Interest match (weight: 30%)
            const interestMatch = this.calculateInterestMatch(course, profile.interests);
            score += interestMatch * 30;
            factors.push({ name: 'Interest Match', score: interestMatch, weight: 30 });

            // Factor 2: Skill level alignment (weight: 25%)
            const levelMatch = this.calculateLevelMatch(course, profile.skillLevel);
            score += levelMatch * 25;
            factors.push({ name: 'Skill Level', score: levelMatch, weight: 25 });

            // Factor 3: Content type preference (weight: 20%)
            const contentMatch = this.calculateContentMatch(course, profile.preferredContentType);
            score += contentMatch * 20;
            factors.push({ name: 'Content Type', score: contentMatch, weight: 20 });

            // Factor 4: Progress and completion (weight: 15%)
            const progressFactor = this.calculateProgressFactor(course, progress);
            score += progressFactor * 15;
            factors.push({ name: 'Progress Factor', score: progressFactor, weight: 15 });

            // Factor 5: Popularity and rating (weight: 10%)
            const popularityFactor = this.calculatePopularityFactor(course);
            score += popularityFactor * 10;
            factors.push({ name: 'Popularity', score: popularityFactor, weight: 10 });

            return {
                course,
                score,
                factors,
                reasons: this.generateReasons(course, factors)
            };
        });

        // Sort by score and return top recommendations
        scoredCourses.sort((a, b) => b.score - a.score);
        return scoredCourses.slice(0, 6);
    }

    calculateInterestMatch(course, interests) {
        if (!interests || interests.length === 0) return 0.5;
        
        let matches = 0;
        const courseKeywords = [
            ...course.topics,
            course.category,
            course.title.toLowerCase().split(' ')
        ];

        interests.forEach(interest => {
            const lowerInterest = interest.toLowerCase();
            if (courseKeywords.some(keyword => 
                keyword.toLowerCase().includes(lowerInterest) || 
                lowerInterest.includes(keyword.toLowerCase())
            )) {
                matches++;
            }
        });

        return Math.min(matches / interests.length, 1);
    }

    calculateLevelMatch(course, userLevel) {
        const levels = { 'beginner': 1, 'intermediate': 2, 'advanced': 3 };
        const courseLevelNum = levels[course.level.toLowerCase()] || 2;
        const userLevelNum = levels[userLevel.toLowerCase()] || 1;

        const diff = Math.abs(courseLevelNum - userLevelNum);
        
        // Perfect match = 1, adjacent level = 0.7, two levels apart = 0.4
        if (diff === 0) return 1;
        if (diff === 1) return 0.7;
        return 0.4;
    }

    calculateContentMatch(course, preferredContentType) {
        // Simulate content type matching based on course characteristics
        const contentScores = {
            'video': 0.9,
            'text': 0.7,
            'interactive': 0.85,
            'project': 0.8
        };
        
        // In a real system, this would analyze actual course content
        return contentScores[preferredContentType] || 0.7;
    }

    calculateProgressFactor(course, userProgress) {
        // Encourage continuing in-progress courses
        if (course.progress > 0 && course.progress < 100) {
            return 0.9;
        }
        
        // Slightly prefer courses not yet started
        if (course.progress === 0) {
            return 0.8;
        }
        
        // Completed courses get lower priority
        return 0.3;
    }

    calculatePopularityFactor(course) {
        // Normalize rating and enrollment
        const ratingScore = course.rating / 5;
        const enrollmentScore = Math.min(course.enrolled / 2000, 1);
        
        return (ratingScore * 0.6) + (enrollmentScore * 0.4);
    }

    generateReasons(course, factors) {
        const reasons = [];
        
        factors.forEach(factor => {
            if (factor.score > 0.7) {
                switch(factor.name) {
                    case 'Interest Match':
                        reasons.push(`Matches your interest in ${course.category}`);
                        break;
                    case 'Skill Level':
                        reasons.push(`Perfect for your ${course.level.toLowerCase()} skill level`);
                        break;
                    case 'Content Type':
                        reasons.push(`Delivered in your preferred format`);
                        break;
                    case 'Progress Factor':
                        reasons.push(`Continue your progress in this course`);
                        break;
                    case 'Popularity':
                        reasons.push(`Highly rated by ${course.enrolled}+ learners`);
                        break;
                }
            }
        });

        return reasons.length > 0 ? reasons : ['Recommended based on your learning profile'];
    }

    updateLearningProfile(activityData) {
        const user = this.userManagement.getCurrentUser();
        if (!user) return;

        // Analyze user behavior and update learning profile
        const profile = user.learningProfile;
        
        // Update based on recent activity
        if (activityData.contentTypeUsage) {
            const mostUsed = Object.entries(activityData.contentTypeUsage)
                .sort((a, b) => b[1] - a[1])[0];
            if (mostUsed) {
                profile.preferredContentType = mostUsed[0];
            }
        }

        // Update skill level based on completed courses and quiz performance
        if (activityData.quizPerformance && activityData.completedCourses) {
            const avgQuizScore = activityData.quizPerformance.reduce((a, b) => a + b, 0) / activityData.quizPerformance.length;
            
            if (avgQuizScore > 85 && activityData.completedCourses.length > 2) {
                profile.skillLevel = 'advanced';
            } else if (avgQuizScore > 70 && activityData.completedCourses.length > 0) {
                profile.skillLevel = 'intermediate';
            }
        }

        this.userManagement.updateProfile({ learningProfile: profile });
    }
}

// ==========================================
// PROGRESS TRACKING SYSTEM
// ==========================================

class ProgressTracking {
    constructor(userManagement) {
        this.userManagement = userManagement;
        this.activities = this.loadActivities();
    }

    loadActivities() {
        const stored = localStorage.getItem('learnai_activities');
        return stored ? JSON.parse(stored) : [];
    }

    saveActivities() {
        localStorage.setItem('learnai_activities', JSON.stringify(this.activities));
    }

    trackActivity(type, details) {
        const user = this.userManagement.getCurrentUser();
        if (!user) return;

        const activity = {
            id: this.generateId(),
            userId: user.id,
            type,
            details,
            timestamp: new Date().toISOString()
        };

        this.activities.push(activity);
        this.saveActivities();
        
        // Update user progress
        this.updateUserProgress(type, details);
    }

    updateUserProgress(type, details) {
        const user = this.userManagement.getCurrentUser();
        if (!user) return;

        const progress = user.progress;

        switch(type) {
            case 'lesson_completed':
                progress.lessonsCompleted++;
                break;
            case 'quiz_completed':
                progress.quizzesTaken++;
                if (details.score) {
                    const newAverage = ((progress.quizAverage * (progress.quizzesTaken - 1)) + details.score) / progress.quizzesTaken;
                    progress.quizAverage = Math.round(newAverage);
                }
                break;
            case 'course_enrolled':
                progress.coursesEnrolled++;
                break;
            case 'learning_time':
                progress.totalLearningHours += details.hours || 0;
                break;
        }

        this.userManagement.updateProfile({ progress });
    }

    getRecentActivities(limit = 10) {
        const user = this.userManagement.getCurrentUser();
        if (!user) return [];

        return this.activities
            .filter(a => a.userId === user.id)
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
            .slice(0, limit);
    }

    getWeeklyProgress() {
        const user = this.userManagement.getCurrentUser();
        if (!user) return [];

        const now = new Date();
        const weekAgo = new Date(now - 7 * 24 * 60 * 60 * 1000);
        
        const weeklyActivities = this.activities.filter(a => 
            a.userId === user.id && 
            new Date(a.timestamp) >= weekAgo
        );

        // Group by day
        const dailyProgress = {};
        weeklyActivities.forEach(activity => {
            const date = new Date(activity.timestamp).toLocaleDateString('en-US', { weekday: 'short' });
            if (!dailyProgress[date]) {
                dailyProgress[date] = { lessons: 0, quizzes: 0, hours: 0 };
            }
            
            if (activity.type === 'lesson_completed') dailyProgress[date].lessons++;
            if (activity.type === 'quiz_completed') dailyProgress[date].quizzes++;
            if (activity.type === 'learning_time') dailyProgress[date].hours += activity.details.hours || 0;
        });

        return dailyProgress;
    }

    generateId() {
        return 'activity_' + Math.random().toString(36).substr(2, 9);
    }
}

// ==========================================
// FEEDBACK GENERATION SYSTEM
// ==========================================

class FeedbackGenerator {
    constructor(userManagement, progressTracking) {
        this.userManagement = userManagement;
        this.progressTracking = progressTracking;
    }

    generateFeedback() {
        const user = this.userManagement.getCurrentUser();
        if (!user) return [];

        const feedback = [];
        const progress = user.progress;
        const recentActivities = this.progressTracking.getRecentActivities(20);

        // Positive feedback for achievements
        if (progress.lessonsCompleted > 0 && progress.lessonsCompleted % 10 === 0) {
            feedback.push({
                type: 'success',
                title: '🎉 Milestone Achieved!',
                message: `Congratulations! You've completed ${progress.lessonsCompleted} lessons. Keep up the great momentum!`
            });
        }

        if (progress.quizAverage >= 85) {
            feedback.push({
                type: 'success',
                title: '⭐ Excellent Performance!',
                message: `Your quiz average of ${progress.quizAverage}% shows exceptional understanding of the material.`
            });
        }

        // Warning for declining performance
        const recentQuizzes = recentActivities.filter(a => a.type === 'quiz_completed').slice(-5);
        if (recentQuizzes.length >= 3) {
            const recentScores = recentQuizzes.map(q => q.details.score);
            const recentAverage = recentScores.reduce((a, b) => a + b, 0) / recentScores.length;
            
            if (recentAverage < progress.quizAverage - 10) {
                feedback.push({
                    type: 'warning',
                    title: '⚠️ Performance Decline',
                    message: 'Your recent quiz scores have dropped. Consider reviewing previous lessons or taking a short break.'
                });
            }
        }

        // Activity recommendations
        const lastActivity = recentActivities[0];
        if (lastActivity) {
            const daysSinceLastActivity = Math.floor((new Date() - new Date(lastActivity.timestamp)) / (1000 * 60 * 60 * 24));
            
            if (daysSinceLastActivity > 3) {
                feedback.push({
                    type: 'info',
                    title: '💡 Stay Consistent',
                    message: `It's been ${daysSinceLastActivity} days since your last activity. Regular learning helps maintain momentum and improves retention.`
                });
            }
        }

        // Learning pace recommendations
        if (progress.totalLearningHours > 20 && progress.lessonsCompleted < 10) {
            feedback.push({
                type: 'info',
                title: '📊 Learning Efficiency',
                message: 'You\'re spending significant time on lessons. Consider exploring different learning formats or asking for help if concepts are challenging.'
            });
        }

        return feedback;
    }
}

// ==========================================
// UI CONTROLLER
// ==========================================

class UIController {
    constructor() {
        this.userManagement = new UserManagement();
        this.courseManagement = new CourseManagement();
        this.aiEngine = new AIRecommendationEngine(this.userManagement, this.courseManagement);
        this.progressTracking = new ProgressTracking(this.userManagement);
        this.feedbackGenerator = new FeedbackGenerator(this.userManagement, this.progressTracking);
        
        this.initializeUI();
    }

    initializeUI() {
        this.renderCourses();
        this.renderRecommendations();
        this.renderDashboardStats();
        this.renderRecentActivity();
        this.renderFeedback();
        this.drawProgressChart();
        this.updateAuthUI();
    }

    renderCourses() {
        const coursesGrid = document.getElementById('courses-grid');
        if (!coursesGrid) return;

        const courses = this.courseManagement.getAllCourses();
        coursesGrid.innerHTML = courses.map(course => `
            <div class="course-card fade-in">
                <div class="course-image">
                    ${course.title.charAt(0)}
                </div>
                <div class="course-content">
                    <h3 class="course-title">${course.title}</h3>
                    <p class="course-description">${course.description}</p>
                    <div style="margin-bottom: 1rem;">
                        <span style="background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)); color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">${course.category}</span>
                        <span style="color: var(--text-secondary); font-size: 0.875rem; margin-left: 0.5rem;">${course.level}</span>
                    </div>
                    <div class="course-meta">
                        <div style="flex: 1;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.875rem; margin-bottom: 0.25rem;">
                                <span>Progress</span>
                                <span>${course.progress}%</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${course.progress}%"></div>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: 600; color: var(--primary-color);">⭐ ${course.rating}</div>
                            <div style="font-size: 0.75rem; color: var(--text-secondary);">${course.enrolled} enrolled</div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderRecommendations() {
        const recommendationsList = document.getElementById('recommendations-list');
        if (!recommendationsList) return;

        const recommendations = this.aiEngine.generateRecommendations();
        
        if (recommendations.length === 0) {
            recommendationsList.innerHTML = '<p style="color: var(--text-secondary);">Please log in to get personalized recommendations.</p>';
            return;
        }

        recommendationsList.innerHTML = recommendations.map((item, index) => `
            <div class="recommendation-card">
                <div class="recommendation-badge">${index === 0 ? '🥇 Top Pick' : index === 1 ? '🥈 Highly Recommended' : '⭐ Recommended'}</div>
                <h4 style="margin-bottom: 0.5rem; font-weight: 700;">${item.course.title}</h4>
                <p style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">${item.course.description.substring(0, 100)}...</p>
                ${item.reasons.map(reason => `
                    <div class="recommendation-reason">✓ ${reason}</div>
                `).join('')}
                <button class="btn btn-primary" style="margin-top: 1rem; font-size: 0.875rem; padding: 0.5rem 1rem;" onclick="enrollCourse('${item.course.id}')">Enroll Now</button>
            </div>
        `).join('');
    }

    renderDashboardStats() {
        const user = this.userManagement.getCurrentUser();
        if (!user) return;

        const progress = user.progress;
        
        document.getElementById('stat-courses').textContent = progress.coursesEnrolled;
        document.getElementById('stat-lessons').textContent = progress.lessonsCompleted;
        document.getElementById('stat-quizzes').textContent = `${progress.quizAverage || 0}%`;
        document.getElementById('stat-hours').textContent = `${Math.round(progress.totalLearningHours)}h`;
    }

    renderRecentActivity() {
        const recentActivity = document.getElementById('recent-activity');
        if (!recentActivity) return;

        const activities = this.progressTracking.getRecentActivities(5);
        
        if (activities.length === 0) {
            recentActivity.innerHTML = '<p style="color: var(--text-secondary);">No recent activity yet. Start learning to see your progress!</p>';
            return;
        }

        recentActivity.innerHTML = activities.map(activity => {
            const date = new Date(activity.timestamp).toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            
            const icons = {
                'lesson_completed': '📚',
                'quiz_completed': '✅',
                'course_enrolled': '🎯',
                'learning_time': '⏱️'
            };

            return `
                <div style="padding: 1rem; border-bottom: 1px solid var(--border-color); display: flex; align-items: center; gap: 1rem;">
                    <span style="font-size: 1.5rem;">${icons[activity.type] || '📌'}</span>
                    <div style="flex: 1;">
                        <div style="font-weight: 600;">${this.formatActivityType(activity.type)}</div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary);">${date}</div>
                    </div>
                </div>
            `;
        }).join('');
    }

    formatActivityType(type) {
        const labels = {
            'lesson_completed': 'Lesson Completed',
            'quiz_completed': 'Quiz Completed',
            'course_enrolled': 'Course Enrolled',
            'learning_time': 'Learning Session'
        };
        return labels[type] || type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    renderFeedback() {
        // Feedback is already rendered in HTML, but could be dynamically updated
        const feedback = this.feedbackGenerator.generateFeedback();
        console.log('Generated feedback:', feedback);
    }

    drawProgressChart() {
        const canvas = document.getElementById('progressChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const weeklyProgress = this.progressTracking.getWeeklyProgress();
        
        const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const data = days.map(day => weeklyProgress[day]?.lessons || 0);
        const maxValue = Math.max(...data, 5);

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const padding = 60;
        const chartWidth = canvas.width - padding * 2;
        const chartHeight = canvas.height - padding * 2;
        const barWidth = chartWidth / days.length - 20;

        // Draw bars
        days.forEach((day, index) => {
            const x = padding + index * (barWidth + 20);
            const barHeight = (data[index] / maxValue) * chartHeight;
            const y = canvas.height - padding - barHeight;

            // Draw bar
            const gradient = ctx.createLinearGradient(x, y, x, canvas.height - padding);
            gradient.addColorStop(0, '#4F46E5');
            gradient.addColorStop(1, '#7C3AED');
            
            ctx.fillStyle = gradient;
            ctx.fillRect(x, y, barWidth, barHeight);

            // Draw value
            ctx.fillStyle = '#111827';
            ctx.font = 'bold 14px sans-serif';
            ctx.textAlign = 'center';
            if (data[index] > 0) {
                ctx.fillText(data[index], x + barWidth / 2, y - 10);
            }

            // Draw label
            ctx.fillStyle = '#6B7280';
            ctx.font = '14px sans-serif';
            ctx.fillText(day, x + barWidth / 2, canvas.height - padding + 20);
        });

        // Draw y-axis labels
        ctx.fillStyle = '#6B7280';
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'right';
        for (let i = 0; i <= maxValue; i++) {
            const y = canvas.height - padding - (i / maxValue) * chartHeight;
            ctx.fillText(i.toString(), padding - 10, y + 5);
            
            // Draw grid line
            ctx.strokeStyle = '#E5E7EB';
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(canvas.width - padding, y);
            ctx.stroke();
        }

        // Draw title
        ctx.fillStyle = '#111827';
        ctx.font = 'bold 16px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Lessons Completed Per Day', canvas.width / 2, 30);
    }

    updateAuthUI() {
        const user = this.userManagement.getCurrentUser();
        if (user) {
            // Update UI for logged-in user
            const navButtons = document.querySelector('.nav-buttons');
            if (navButtons) {
                navButtons.innerHTML = `
                    <span style="margin-right: 1rem; font-weight: 600;">Welcome, ${user.name || 'User'}</span>
                    <button class="btn btn-secondary" onclick="handleLogout()">Logout</button>
                `;
            }
        }
    }
}

// ==========================================
// GLOBAL FUNCTIONS
// ==========================================

let uiController;

document.addEventListener('DOMContentLoaded', () => {
    uiController = new UIController();
});

// Modal functions
function showModal(type) {
    const modal = document.getElementById(`${type}-modal`);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(type) {
    const modal = document.getElementById(`${type}-modal`);
    if (modal) {
        modal.classList.remove('active');
    }
}

// Login handler
function handleLogin(event) {
    event.preventDefault();
    const form = event.target;
    const email = form.querySelector('input[type="email"]').value;
    const password = form.querySelector('input[type="password"]').value;

    try {
        uiController.userManagement.login(email, password);
        closeModal('login');
        uiController.updateAuthUI();
        uiController.renderRecommendations();
        uiController.renderDashboardStats();
        alert('Login successful!');
    } catch (error) {
        alert(error.message);
    }
}

// Register handler
function handleRegister(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    const userData = {
        name: form.querySelector('input[type="text"]').value,
        email: form.querySelector('input[type="email"]').value,
        password: form.querySelector('input[type="password"]').value,
        interests: Array.from(form.querySelector('select').selectedOptions).map(opt => opt.value)
    };

    try {
        uiController.userManagement.register(userData);
        closeModal('register');
        alert('Registration successful! Please login.');
        showModal('login');
    } catch (error) {
        alert(error.message);
    }
}

// Logout handler
function handleLogout() {
    uiController.userManagement.logout();
    uiController.updateAuthUI();
    uiController.renderRecommendations();
    alert('Logged out successfully!');
}

// Course enrollment
function enrollCourse(courseId) {
    const user = uiController.userManagement.getCurrentUser();
    if (!user) {
        alert('Please login to enroll in courses.');
        showModal('login');
        return;
    }

    uiController.progressTracking.trackActivity('course_enrolled', { courseId });
    uiController.renderDashboardStats();
    uiController.renderRecentActivity();
    alert('Successfully enrolled in the course!');
}

// Content tab switching
function showContentTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.content-tab').forEach(tab => {
        tab.style.display = 'none';
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`tab-${tabName}`).style.display = 'block';
    
    // Add active class to clicked tab button
    event.target.classList.add('active');
}

// Quiz selection
function selectQuizOption(element) {
    document.querySelectorAll('.quiz-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    element.classList.add('selected');
}

// Quiz submission
function submitQuiz() {
    const selectedOption = document.querySelector('.quiz-option.selected');
    if (!selectedOption) {
        alert('Please select an answer before submitting.');
        return;
    }

    const isCorrect = selectedOption.textContent.includes('B. Supervised Learning');
    const score = isCorrect ? 100 : 0;

    uiController.progressTracking.trackActivity('quiz_completed', { 
        score,
        correct: isCorrect 
    });

    if (isCorrect) {
        alert('Correct! Well done!');
    } else {
        alert('Incorrect. The correct answer is B. Supervised Learning.');
    }

    uiController.renderDashboardStats();
    uiController.renderRecentActivity();
}

// Dashboard section switching
function showDashboardSection(section) {
    // Update active state in sidebar
    document.querySelectorAll('.sidebar-menu a').forEach(link => {
        link.classList.remove('active');
    });
    event.target.classList.add('active');

    // In a full implementation, this would show/hide different dashboard sections
    console.log('Showing dashboard section:', section);
}

// Close modals when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
}