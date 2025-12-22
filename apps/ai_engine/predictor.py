try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

import json
import os
from django.conf import settings
from dotenv import load_dotenv

def configure_gemini():
    if not GEMINI_AVAILABLE:
        print("Warning: google.generativeai module not found.")
        return False, "Library 'google-generativeai' not installed."
    
    # 1. Try from Django Settings (Preferred)
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    
    # 2. If not in settings, force load from .env
    if not api_key:
        env_path = settings.BASE_DIR / '.env'
        load_dotenv(env_path)
        api_key = os.environ.get('GEMINI_API_KEY')
    
    if not api_key:
        # 3. Final Check
        print("❌ Warning: GEMINI_API_KEY not found in Settings or .env")
        return False, "API Key not found in .env or settings."

    try:
        genai.configure(api_key=api_key)
        return True, None
    except Exception as e:
        print(f"❌ Error configuring Gemini: {e}")
        return False, f"Config Error: {str(e)}"

class AIPredictor:
   
    def __init__(self):
        self.configured, self.config_error = configure_gemini()
        # Define the priority list of models to try in order
        self.candidates = [
            'models/gemini-3-flash-preview',       # REQUESTED: Bleeding edge
            'models/gemini-2.5-flash',             # New stable(ish)
            'models/gemini-2.0-flash-exp',         # Previous experimental
            'models/gemini-exp-1206',
            'models/gemini-2.0-flash',
            'models/gemini-1.5-flash', 
            'models/gemini-1.5-flash-latest', 
            'models/gemini-pro'
        ]

    def predict_branch_waste_risk(self, branch_context_data):
        if not self.configured:
            return {
                "error": f"AI Error: {self.config_error}",
                "performance_verdict": f"خطأ: {self.config_error}"
            }

        # 1. Context Assembly
        prompt = self._build_prompt(branch_context_data)
        
        last_error = None
        
        # 2. Smart Rotation Loop
        for model_name in self.candidates:
            try:
                print(f"🔄 Attempting AI Analysis with model: {model_name}...")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                
                # Cleaning & Parsing
                response_text = response.text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text.replace("```json", "").replace("```", "")
                
                result = json.loads(response_text)
                
                if "performance_verdict" in result:
                    result["performance_verdict"] += f" ({model_name.replace('models/', '')}) ✨"
                    
                print(f"✅ Success with {model_name}")
                return result

            except Exception as e:
                error_str = str(e).lower()
                print(f"❌ Failed with {model_name}: {e}")
                last_error = e
                
                # Check if it's a Quota/Limit error
                is_quota_error = "429" in error_str or "quota" in error_str or "exhausted" in error_str or "resource" in error_str
                
                if is_quota_error:
                    # Try next model immediately
                    continue
                else:
                    # If it's a "Not Found" error (404), also try next.
                    if "404" in error_str or "not found" in error_str:
                         continue
                    
                    # If it's some other fatal error (like bad prompt), maybe we should stop?
                    # For safety, let's keep rotating to be sure.
                    continue

        # 3. If All Models Fail
        print("All models failed.")
        return {
            "error": str(last_error),
            "performance_verdict": f"تم استنفاد جميع النماذج المجانية اليوم. ({str(last_error)})"
        }

    def _build_prompt(self, data):
        if data.get('analysis_type') == 'purchasing_advice':
           return f"""
           You are an inventory optimization expert.
           Analyze the past 30 days of waste data for "{data.get('branch_name')}" to provide purchasing reduction advice for next week.
           
           Data:
           {json.dumps(data.get('high_waste_items'), indent=2, ensure_ascii=False)}
           
           Task:
           For each item, suggest a specific reduction amount for the next weekly order to minimize waste.
           
           Return STRICTLY a valid JSON object with this key 'suggestions':
           {{
               "suggestions": [
                   {{
                       "product": "Product Name",
                       "unit": "kg/pcs",
                       "total_loss_30d": 0.0,
                       "weekly_waste_avg": 0.0,
                       "recommendation": "Brief recommendation in Arabic (e.g., 'تقليل الطلب بمقدار 2 كجم')",
                       "action_type": "critical/moderate"
                   }}
               ]
           }}
           """
        
        return f"""
        You are an expert Waste Management Consultant.
        Analyze the following inventory data for "{data.get('branch_name')}".
        
        Data:
        {json.dumps(data, indent=2, ensure_ascii=False)}
        
        Objective:
        1. Financial Impact: Estimate 'Total Potential Waste Value' (SAR).
        2. Category Analysis: Breakdown risk by product category.
        3. Strategic Recommendations: Provide at least 3 actionable recommendations in Arabic.
        4. Performance Verdict: Give a VERY SHORT summary (MAX 8 WORDS) in Arabic (e.g., "مخاطر عالية في قسم اللحوم").

        Return STRICTLY a valid JSON object:
        {{
            "financial_impact": {{
                "total_risk_value": 0.0,
                "risk_level": "High/Medium/Low"
            }},
            "category_breakdown": {{ "Category": 0.0 }},
            "risk_items": [],
            "recommendations": ["توصية 1", "توصية 2"],
            "performance_verdict": "عبارة قصيرة جداً هنا"
        }}
        """

# Standalone function as requested in the plan/user snippet
def get_ai_insights(branch_data):
    predictor = AIPredictor()
    return predictor.predict_branch_waste_risk(branch_data)
