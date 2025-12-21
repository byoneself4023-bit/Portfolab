# -*- coding: utf-8 -*-
import google.generativeai as genai
import os
import json

# Gemini API 설정
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')


def analyze_portfolio(portfolio_data):
    """포트폴리오 종합 분석 및 AI 조언"""
    try:
        prompt = f"""
당신은 전문 투자 어드바이저입니다. 다음 포트폴리오를 분석하고 한국어로 조언해주세요.

## 포트폴리오 정보
- 총 투자금액: {portfolio_data['total_invested']:,}원
- 총 평가금액: {portfolio_data['total_value']:,}원
- 총 수익률: {portfolio_data['total_return']}%
- 변동성: {portfolio_data['volatility']}%
- 샤프비율: {portfolio_data['sharpe_ratio']}

## 보유 종목
{json.dumps(portfolio_data['stocks'], ensure_ascii=False, indent=2)}

## 요청사항
다음 3가지를 JSON 형식으로 답변해주세요:

1. "risk_analysis": 변동성과 샤프비율에 대한 해석 (2-3문장)
2. "recommendation": 구체적인 매수/매도 제안 (2-3문장)  
3. "overall_comment": 포트폴리오 종합 평가 및 조언 (3-4문장)

JSON 형식으로만 답변하세요:
{{"risk_analysis": "...", "recommendation": "...", "overall_comment": "..."}}
"""
        
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # JSON 파싱 시도
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        result = json.loads(result_text)
        return result, None
        
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 텍스트 그대로 반환
        return {
            "risk_analysis": "분석 중 오류가 발생했습니다.",
            "recommendation": "다시 시도해주세요.",
            "overall_comment": response.text if response else "AI 응답을 받지 못했습니다."
        }, None
    except Exception as e:
        return None, str(e)


def get_rebalancing_suggestion(portfolio_data, target_volatility=30):
    """목표 변동성에 맞는 리밸런싱 제안"""
    try:
        prompt = f"""
당신은 포트폴리오 리밸런싱 전문가입니다.

## 현재 포트폴리오
- 현재 변동성: {portfolio_data['volatility']}%
- 목표 변동성: {target_volatility}%
- 보유 종목:
{json.dumps(portfolio_data['stocks'], ensure_ascii=False, indent=2)}

## 요청사항
목표 변동성({target_volatility}%)을 달성하기 위한 구체적인 리밸런싱 제안을 해주세요.

다음 JSON 형식으로 답변하세요:
{{
    "current_status": "현재 상태 요약 (1문장)",
    "suggestions": [
        {{"stock": "종목명", "action": "매수/매도", "quantity": "수량", "reason": "이유"}}
    ],
    "expected_result": "리밸런싱 후 예상 결과 (1-2문장)"
}}

JSON 형식으로만 답변하세요.
"""
        
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        result = json.loads(result_text)
        return result, None
        
    except Exception as e:
        return None, str(e)


def explain_metrics(volatility, sharpe_ratio):
    """변동성과 샤프비율에 대한 AI 설명"""
    try:
        prompt = f"""
당신은 친절한 투자 교육자입니다. 초보 투자자도 이해할 수 있게 설명해주세요.

## 현재 지표
- 변동성: {volatility}%
- 샤프비율: {sharpe_ratio}

## 요청사항
각 지표에 대해 다음을 설명해주세요:
1. 현재 수치가 의미하는 것
2. 좋은지 나쁜지 평가
3. 개선 방법 (필요한 경우)

다음 JSON 형식으로 답변하세요:
{{
    "volatility_explanation": "변동성 설명 (2-3문장)",
    "sharpe_explanation": "샤프비율 설명 (2-3문장)",
    "improvement_tip": "개선 팁 (1-2문장)"
}}

JSON 형식으로만 답변하세요.
"""
        
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        result = json.loads(result_text)
        return result, None
        
    except Exception as e:
        return None, str(e)