# utils/gemini_client.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(override=True)

# Gemini API 설정
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
print(f"GEMINI_API_KEY: {GEMINI_API_KEY}")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")

genai.configure(api_key=GEMINI_API_KEY)

# 사용 가능한 모델 목록
AVAILABLE_MODELS = {
    'gemini-2.5-flash': '빠르고 효율적 (권장)',
    'gemini-2.5-flash-lite': '최신 고성능 모델',
    'gemini-2.0-flash-lite': '초고속 응답'
}

def ask_gemini(prompt, model_name="gemini-2.5-flash", temperature=0.7):
    """
    Gemini API에 프롬프트를 보내고 응답을 받는 함수
    
    Args:
        prompt (str): LLM에게 보낼 프롬프트
        model_name (str): 사용할 모델
        temperature (float): 창의성 수준 (0.0~1.0)
    
    Returns:
        str: LLM 응답 텍스트
    """
    try:
        model = genai.GenerativeModel(model_name)
        
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=2048,
        )
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        if response.text:
            return response.text
        else:
            return "Error: 응답이 비어있습니다."
    
    except Exception as e:
        return f"Error: {str(e)}"

def get_available_models():
    """사용 가능한 모델 목록 반환"""
    return AVAILABLE_MODELS