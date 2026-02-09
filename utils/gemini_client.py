# utils/gemini_client.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Gemini API 설정
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")

genai.configure(api_key=GEMINI_API_KEY)

def ask_gemini(prompt, model_name="gemini-2.5-flash-lite"):
    """
    Gemini API에 프롬프트를 보내고 응답을 받는 함수
    
    Args:
        prompt (str): LLM에게 보낼 프롬프트
        model_name (str): 사용할 모델 (기본값: gemini-1.5-flash)
            - gemini-1.5-flash: 빠르고 효율적 (권장)
            - gemini-1.5-pro: 더 강력하지만 느림
    
    Returns:
        str: LLM 응답 텍스트
    """
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        
        # 응답 텍스트 추출
        if response.text:
            return response.text
        else:
            return "Error: 응답이 비어있습니다."
    
    except Exception as e:
        return f"Error: {str(e)}"

def ask_gemini_with_config(prompt, model_name="gemini-1.5-flash", temperature=0.7, max_tokens=2048):
    """
    고급 설정이 가능한 Gemini API 호출
    
    Args:
        prompt (str): 프롬프트
        model_name (str): 모델명
        temperature (float): 창의성 수준 (0.0~1.0)
        max_tokens (int): 최대 토큰 수
    
    Returns:
        str: LLM 응답
    """
    try:
        model = genai.GenerativeModel(model_name)
        
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
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