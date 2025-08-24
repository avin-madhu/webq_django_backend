import logging
import json
import re
from typing import List, Dict, Any
from django.conf import settings
from groq import Groq
from .models import Student, LearningResource, Recommendation

logger = logging.getLogger(__name__)


class AIRecommendationEngine:
    def __init__(self):
        if getattr(settings, "GROQ_API_KEY", None):
            try:
                self.client = Groq(api_key=settings.GROQ_API_KEY)
                self.model = "llama-3.1-8b-instant" # model used
                logger.info("Groq AI model initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self.client, self.model = None, None
        else:
            logger.warning("Groq API key not configured. Using fallback logic.")
            self.client, self.model = None, None
    
    def clean_ai_response(self,ai_text):
        # Remove code fences
        ai_text = re.sub(r"```(?:json)?|```", "", ai_text)
        # Remove JS-style comments
        ai_text = re.sub(r"//.*", "", ai_text)
        return ai_text.strip()

    def _chat(self, prompt: str) -> str:
        """Send prompt to Groq and return response text"""
        if not self.client or not self.model:
            return ""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=800,
                top_p=1,
            )
            # print(response.choices[0].message.content.strip())
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            return ""

    def analyze_student_performance(self, student: Student) -> Dict[str, Any]:
        """Analyze student performance and generate insights"""
        performance_data = {
            "student_id": student.student_id,
            "performance_score": student.performance_score,
            "completed_courses": student.get_completed_courses(),
            "pending_courses": student.get_pending_courses(),
            "total_completed": len(student.get_completed_courses()),
            "total_pending": len(student.get_pending_courses()),
        }

        logger.info(f"Analyzing student {student.student_id} with score {student.performance_score}")

        # Determine performance category
        if student.performance_score >= 85:
            category = "excellent"
        elif student.performance_score >= 70:
            category = "good"
        elif student.performance_score >= 50:
            category = "average"
        else:
            category = "needs_improvement"

        analysis = {
            "performance_category": category,
            "strengths": [],
            "weaknesses": [],
            "learning_style": "visual",  # Default learning style
            "recommended_focus_areas": [],
        }

        # AI-powered analysis if Groq is available
        if self.client:
            try:
                prompt = self._create_analysis_prompt(performance_data)
                logger.info("Sending analysis prompt to Groq")
                ai_response = self._chat(prompt)

                logger.info(f"Groq analysis response: {ai_response[:200]}...")
                ai_analysis = self._parse_ai_analysis(ai_response)
                analysis.update(ai_analysis)
                logger.info(f"Updated analysis: {analysis}")

            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
                analysis = self._fallback_analysis(performance_data, analysis)
        # if groq is not available 
        else:
            analysis = self._fallback_analysis(performance_data, analysis)

        return analysis

    def generate_recommendations(self, student: Student, max_recommendations: int = 5) -> List[Dict]:
        """Generate personalized learning recommendations"""
        logger.info(f"Generating recommendations for student {student.student_id}")

        analysis = self.analyze_student_performance(student)
        available_resources = LearningResource.objects.all()

        logger.info(f"Total available resources: {available_resources.count()}")

        recommendations = []
        if self.client:
            try:
                logger.info("Using AI for recommendation generation")
                recommendations = self._ai_generate_recommendations(
                    student, analysis, available_resources, max_recommendations
                )
                logger.info(f"AI generated {len(recommendations)} recommendations")
            except Exception as e:
                logger.error(f"AI recommendation generation failed: {e}")
                recommendations = self._fallback_recommendations(
                    student, analysis, available_resources, max_recommendations
                )
        else:
            recommendations = self._fallback_recommendations(
                student, analysis, available_resources, max_recommendations
            )

        return recommendations

    def _create_analysis_prompt(self, performance_data: Dict) -> str:
        return f"""
        Analyze this student's learning performance and provide insights:

        Student Performance Data:
        - Performance Score: {performance_data['performance_score']}/100
        - Completed Courses: {performance_data['completed_courses']}
        - Pending Courses: {performance_data['pending_courses']}
        - Total Completed: {performance_data['total_completed']}
        - Total Pending: {performance_data['total_pending']}

        Please provide analysis in the following JSON format:
        {{
            "strengths": ["strength1", "strength2"],
            "weaknesses": ["weakness1", "weakness2"],
            "learning_style": "visual|auditory|kinesthetic|reading",
            "recommended_focus_areas": ["area1", "area2"]
        }}

        Return only a valid JSON object without explanations, Markdown, or comments.
        """

    def _parse_ai_analysis(self, ai_response: str) -> Dict:
        try:
            ai_response = self.clean_ai_response(ai_response)
            start = ai_response.find("{")
            end = ai_response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = ai_response[start:end]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to parse AI analysis: {e}")
            logger.error(f"AI response was: {ai_response}")
        return {}

    def _ai_generate_recommendations(self, student: Student, analysis: Dict, resources, max_recommendations: int) -> List[Dict]:
        resources_data = [
            {
                "id": r.resource_id,
                "title": r.title,
                "type": r.type,
                "difficulty": r.difficulty_level,
                "priority": r.recommendation_priority,
                "course_id": r.course_id,
            }
            for r in resources
        ]

        prompt = f"""
        Generate personalized learning recommendations for this student:

        Student Analysis:
        {json.dumps(analysis, indent=2)}

        Available Resources:
        {json.dumps(resources_data[:20], indent=2)}

        Generate {max_recommendations} recommendations in JSON format:
        {{
            "recommendations": [
                {{
                    "resource_id": "resource_id",
                    "confidence_score": 0.8,
                    "reason": "Why this resource is recommended"
                }}
            ]
        }}
        """

        ai_response = self._chat(prompt)
        logger.info(f"Groq recommendation response: {ai_response[:200]}...")
        ai_recs = self._parse_ai_recommendations(ai_response)
        return self._validate_recommendations(ai_recs, resources)

    def _parse_ai_recommendations(self, ai_response: str) -> List[Dict]:
        try:
            ai_response = self.clean_ai_response(ai_response)
            start = ai_response.find("{")
            end = ai_response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = ai_response[start:end]
                data = json.loads(json_str)
                return data.get("recommendations", [])
        except Exception as e:
            logger.error(f"Failed to parse AI recommendations: {e}")
            logger.error(f"AI response was: {ai_response}")
        return []

    def _validate_recommendations(self, ai_recs: List[Dict], resources) -> List[Dict]:
        validated = []
        resource_ids = {r.resource_id: r for r in resources}

        for rec in ai_recs:
            resource_id = rec.get("resource_id")
            if resource_id in resource_ids:
                validated.append(
                    {
                        "resource": resource_ids[resource_id],
                        "confidence_score": min(max(rec.get("confidence_score", 0.5), 0.0), 1.0),
                        "reason": rec.get("reason", "AI recommended based on performance analysis"),
                    }
                )
        return validated
    
    def _fallback_analysis(self, performance_data: Dict, base_analysis: Dict) -> Dict:
        """Rule-based fallback analysis"""
        score = performance_data['performance_score']
        completed = performance_data['total_completed']
        
        logger.info(f"Using fallback analysis for score {score}, completed {completed}")
        
        if score >= 85:
            base_analysis['strengths'] = ['High performance', 'Good understanding', 'Consistent progress']
            base_analysis['recommended_focus_areas'] = ['Advanced topics', 'Specialized skills']
        elif score >= 70:
            base_analysis['strengths'] = ['Solid foundation', 'Regular participation']
            base_analysis['weaknesses'] = ['Some concept gaps']
            base_analysis['recommended_focus_areas'] = ['Reinforcement', 'Practice problems']
        else:
            base_analysis['strengths'] = ['Willingness to learn']
            base_analysis['weaknesses'] = ['Fundamental concepts', 'Study habits']
            base_analysis['recommended_focus_areas'] = ['Basic concepts', 'Study techniques']

        if completed < 2:
            base_analysis['recommended_focus_areas'].append('Course completion')

        return base_analysis

    def _fallback_recommendations(self, student: Student, analysis: Dict, 
                                resources, max_recommendations: int) -> List[Dict]:
        """Rule-based fallback recommendations"""
        logger.info(f"Starting fallback recommendations for student {student.student_id}")
        
        recommendations = []
        performance_score = student.performance_score
        
        # Filter resources based on performance
        if performance_score < 50:
            target_difficulty = 'beginner'
            target_types = ['tutorial', 'article']
        elif performance_score < 75:
            target_difficulty = 'intermediate'
            target_types = ['tutorial', 'video', 'quiz']
        else:
            target_difficulty = 'advanced'
            target_types = ['video', 'quiz', 'assignment']

        logger.info(f"Target difficulty: {target_difficulty}, Target types: {target_types}")

        # Get existing recommendations to avoid duplicates
        # FIX: Use resource__id instead of resource_id
        existing_resource_ids = set(
            student.recommendation_set.values_list('resource__id', flat=True)
        )
        
        logger.info(f"Existing resource IDs to exclude: {existing_resource_ids}")
        logger.info(f"Total resources before filtering: {len(resources)}")

        # Filter and score resources
        scored_resources = []
        for resource in resources:
            if resource.id in existing_resource_ids:
                logger.info(f"Skipping resource {resource.resource_id} - already recommended")
                continue
                
            score = 0
            reason_parts = []

            # Difficulty match
            if resource.difficulty_level == target_difficulty:
                score += 3
                reason_parts.append(f"Matches {target_difficulty} level")
            
            # Type preference
            if resource.type in target_types:
                score += 2
                reason_parts.append(f"Recommended {resource.type} format")
            
            # Priority weight
            score += resource.recommendation_priority / 10
            
            # Performance-based adjustments
            if performance_score < 50 and resource.type == 'tutorial':
                score += 2
                reason_parts.append("Tutorial for concept reinforcement")
            elif performance_score >= 75 and resource.type == 'assignment':
                score += 2
                reason_parts.append("Challenge assignment for skill development")

            confidence = min(score / 10, 1.0)
            reason = "; ".join(reason_parts) or "Selected based on performance analysis"
            
            scored_resources.append({
                'resource': resource,
                'score': score,
                'confidence_score': confidence,
                'reason': reason
            })
            
            logger.info(f"Scored resource {resource.resource_id}: score={score}, confidence={confidence}")

        logger.info(f"Total scored resources: {len(scored_resources)}")

        # Sort and take top recommendations
        scored_resources.sort(key=lambda x: x['score'], reverse=True)
        final_recommendations = scored_resources[:max_recommendations]
        
        logger.info(f"Returning {len(final_recommendations)} recommendations")
        
        return final_recommendations