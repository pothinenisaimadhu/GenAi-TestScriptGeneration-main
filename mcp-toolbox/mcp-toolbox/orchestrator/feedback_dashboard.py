#!/usr/bin/env python3
"""
Feedback dashboard for viewing and analyzing collected feedback.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import pandas as pd

class FeedbackDashboard:
    """Dashboard for analyzing feedback data."""
    
    def __init__(self):
        self.feedback_dir = "user_feedback"
        os.makedirs(self.feedback_dir, exist_ok=True)
    
    def display_dashboard(self) -> None:
        """Display comprehensive feedback dashboard."""
        print("📊 FEEDBACK DASHBOARD")
        print("=" * 50)
        
        # Load all feedback data
        feedback_data = self._load_all_feedback()
        
        if not feedback_data:
            print("No feedback data available.")
            return
        
        # Display summary statistics
        self._display_summary_stats(feedback_data)
        
        # Display trends
        self._display_trends(feedback_data)
        
        # Display recommendations
        self._display_recommendations(feedback_data)
        
        # Generate charts if possible
        try:
            self._generate_charts(feedback_data)
        except ImportError:
            print("\\n📈 Charts require matplotlib and pandas. Install with: pip install matplotlib pandas")
    
    def _load_all_feedback(self) -> List[Dict[str, Any]]:
        """Load all feedback files."""
        feedback_data = []
        
        try:
            for filename in os.listdir(self.feedback_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.feedback_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            feedback_data.append(data)
                    except Exception as e:
                        print(f"Warning: Could not load {filename}: {e}")
        except FileNotFoundError:
            print("Feedback directory not found.")
        
        return feedback_data
    
    def _display_summary_stats(self, feedback_data: List[Dict]) -> None:
        """Display summary statistics."""
        print(f"\\n📈 SUMMARY STATISTICS")
        print("-" * 30)
        
        total_sessions = len(feedback_data)
        print(f"Total feedback sessions: {total_sessions}")
        
        # Completion feedback stats
        completion_feedback = [f for f in feedback_data if 'completion_feedback' in f]
        if completion_feedback:
            scores = [f['completion_feedback'].get('overall_score', 0) for f in completion_feedback]
            avg_score = sum(scores) / len(scores) if scores else 0
            print(f"Average overall score: {avg_score:.1f}/5")
            
            satisfaction_scores = [f['completion_feedback'].get('overall_satisfaction', 0) for f in completion_feedback]
            avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
            print(f"Average satisfaction: {avg_satisfaction:.1f}/5")
            
            recommendations = sum(1 for f in completion_feedback 
                                if f['completion_feedback'].get('would_recommend', False))
            rec_rate = recommendations / len(completion_feedback) * 100 if completion_feedback else 0
            print(f"Recommendation rate: {rec_rate:.1f}%")
        
        # Individual test case feedback
        test_feedback = [f for f in feedback_data if 'user_responses' in f and 'quality_rating' in f.get('user_responses', {})]
        if test_feedback:
            quality_ratings = [f['user_responses']['quality_rating'] for f in test_feedback]
            avg_quality = sum(quality_ratings) / len(quality_ratings) if quality_ratings else 0
            print(f"Average test case quality: {avg_quality:.1f}/5")
            
            complete_count = sum(1 for f in test_feedback 
                               if f['user_responses'].get('is_complete', False))
            completion_rate = complete_count / len(test_feedback) * 100 if test_feedback else 0
            print(f"Test case completion rate: {completion_rate:.1f}%")
    
    def _display_trends(self, feedback_data: List[Dict]) -> None:
        """Display feedback trends over time."""
        print(f"\\n📅 TRENDS")
        print("-" * 20)
        
        # Group by date
        daily_feedback = {}
        for feedback in feedback_data:
            timestamp = feedback.get('timestamp', '')
            if timestamp:
                try:
                    date = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).date()
                    if date not in daily_feedback:
                        daily_feedback[date] = []
                    daily_feedback[date].append(feedback)
                except:
                    continue
        
        if daily_feedback:
            print(f"Feedback collected over {len(daily_feedback)} days")
            
            # Recent trend (last 7 days)
            recent_dates = sorted(daily_feedback.keys())[-7:]
            if recent_dates:
                recent_scores = []
                for date in recent_dates:
                    day_feedback = daily_feedback[date]
                    completion_feedback = [f for f in day_feedback if 'completion_feedback' in f]
                    if completion_feedback:
                        scores = [f['completion_feedback'].get('overall_score', 0) for f in completion_feedback]
                        avg_score = sum(scores) / len(scores) if scores else 0
                        recent_scores.append(avg_score)
                        print(f"  {date}: {len(day_feedback)} sessions, avg score: {avg_score:.1f}")
                
                if len(recent_scores) > 1:
                    trend = "improving" if recent_scores[-1] > recent_scores[0] else "declining"
                    print(f"Recent trend: {trend}")
    
    def _display_recommendations(self, feedback_data: List[Dict]) -> None:
        """Display improvement recommendations based on feedback."""
        print(f"\\n💡 IMPROVEMENT RECOMMENDATIONS")
        print("-" * 35)
        
        # Analyze common issues
        low_scores = []
        improvement_suggestions = []
        
        for feedback in feedback_data:
            if 'completion_feedback' in feedback:
                cf = feedback['completion_feedback']
                overall_score = cf.get('overall_score', 5)
                
                if overall_score < 3:
                    low_scores.append(feedback)
                
                suggestion = cf.get('improvement_suggestions', '')
                if suggestion:
                    improvement_suggestions.append(suggestion)
        
        # Generate recommendations
        recommendations = []
        
        if len(low_scores) > len(feedback_data) * 0.3:  # More than 30% low scores
            recommendations.append("Focus on improving overall test case quality")
            recommendations.append("Review and enhance LLM question generation")
        
        # Analyze specific feedback areas
        completion_feedback = [f for f in feedback_data if 'completion_feedback' in f]
        if completion_feedback:
            quality_scores = [f['completion_feedback'].get('test_case_quality', 5) for f in completion_feedback]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 5
            
            if avg_quality < 3:
                recommendations.append("Enhance test case generation algorithms")
                recommendations.append("Add more domain-specific templates")
            
            time_scores = [f['completion_feedback'].get('time_efficiency', 5) for f in completion_feedback]
            avg_time = sum(time_scores) / len(time_scores) if time_scores else 5
            
            if avg_time < 3:
                recommendations.append("Optimize workflow processing time")
                recommendations.append("Reduce number of interactive questions")
            
            llm_helpful = [f['completion_feedback'].get('llm_questions_helpful', True) for f in completion_feedback]
            helpful_rate = sum(llm_helpful) / len(llm_helpful) if llm_helpful else 1
            
            if helpful_rate < 0.7:
                recommendations.append("Improve LLM question relevance and quality")
                recommendations.append("Add more context-aware question generation")
        
        # Display recommendations
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print("  ✅ System performing well based on current feedback")
        
        # Display common improvement suggestions
        if improvement_suggestions:
            print(f"\\n📝 Common user suggestions:")
            # Simple word frequency analysis
            all_words = ' '.join(improvement_suggestions).lower().split()
            word_freq = {}
            for word in all_words:
                if len(word) > 3:  # Skip short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            for word, count in common_words:
                if count > 1:
                    print(f"  • '{word}' mentioned {count} times")
    
    def _generate_charts(self, feedback_data: List[Dict]) -> None:
        """Generate feedback charts."""
        print(f"\\n📊 GENERATING CHARTS...")
        
        # Prepare data for charts
        completion_feedback = [f for f in feedback_data if 'completion_feedback' in f]
        
        if not completion_feedback:
            print("No completion feedback data for charts.")
            return
        
        # Overall scores over time
        timestamps = []
        overall_scores = []
        
        for feedback in completion_feedback:
            timestamp = feedback.get('timestamp', '')
            score = feedback['completion_feedback'].get('overall_score', 0)
            
            if timestamp and score:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamps.append(dt)
                    overall_scores.append(score)
                except:
                    continue
        
        if timestamps and overall_scores:
            # Create charts
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
            
            # Overall scores over time
            ax1.plot(timestamps, overall_scores, marker='o')
            ax1.set_title('Overall Scores Over Time')
            ax1.set_ylabel('Score (1-5)')
            ax1.grid(True)
            
            # Score distribution
            ax2.hist(overall_scores, bins=5, range=(1, 5), alpha=0.7)
            ax2.set_title('Score Distribution')
            ax2.set_xlabel('Score')
            ax2.set_ylabel('Frequency')
            
            # Category scores
            categories = ['overall_satisfaction', 'test_case_quality', 'test_coverage', 'time_efficiency']
            category_scores = []
            
            for category in categories:
                scores = [f['completion_feedback'].get(category, 0) for f in completion_feedback]
                avg_score = sum(scores) / len(scores) if scores else 0
                category_scores.append(avg_score)
            
            ax3.bar(categories, category_scores)
            ax3.set_title('Average Scores by Category')
            ax3.set_ylabel('Score (1-5)')
            ax3.tick_params(axis='x', rotation=45)
            
            # Recommendation rate
            recommend_count = sum(1 for f in completion_feedback 
                                if f['completion_feedback'].get('would_recommend', False))
            not_recommend_count = len(completion_feedback) - recommend_count
            
            ax4.pie([recommend_count, not_recommend_count], 
                   labels=['Would Recommend', 'Would Not Recommend'],
                   autopct='%1.1f%%')
            ax4.set_title('Recommendation Rate')
            
            plt.tight_layout()
            
            # Save chart
            chart_path = os.path.join(self.feedback_dir, 'feedback_dashboard.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            print(f"Charts saved to: {chart_path}")
            
            # Show chart if in interactive environment
            try:
                plt.show()
            except:
                print("Charts generated but display not available in this environment")

def main():
    """Main function to run the dashboard."""
    dashboard = FeedbackDashboard()
    dashboard.display_dashboard()

if __name__ == "__main__":
    main()