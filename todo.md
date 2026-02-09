# TODO List for LearnAI Platform Enhancements

## Completed Tasks ✅
- [x] Updated logout_view to redirect to 'core:index'
- [x] Added real-time data updates to dashboard with JavaScript polling every 30 seconds
- [x] Enhanced AIRecommendationEngine with internet research functionality
- [x] Added search_internet API endpoint for chatbot-style search
- [x] Updated recommendations page with search bar and internet research results display
- [x] Restructured recommendations page as AI Learning Assistant with chatbot interface

## Pending Tasks ⏳
- [ ] Test the real-time dashboard updates
- [ ] Test the internet search functionality
- [ ] Verify all URLs and API endpoints work correctly
- [ ] Test the overall user flow from signup to dashboard to recommendations

## Notes
- Real-time dashboard updates fetch stats from /core/api/stats/ every 30 seconds
- Internet research searches Google and Coursera for learning resources
- Recommendations page now includes a search bar for direct internet research
- Dashboard shows last updated timestamp and visual feedback on updates
