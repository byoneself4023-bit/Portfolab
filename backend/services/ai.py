# -*- coding: utf-8 -*-
import os
import requests
from services import analysis as analysis_service


ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


def get_portfolio_comment(portfolio_no):
    """
    Claude API를 사용하여 포트폴리오 분석 코멘트 생성
    """
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return None, "Claude API 키가 설정되지 않았습니다."
        
        # 포트폴리오 분석 데이터 수집
        summary, err = analysis_service.get_portfolio_summary(portfolio_no)
        if err:
            return None, err
        
        risk, err = analysis_service.get_risk_metrics(portfolio_no)
        if err:
            return None, err
        
        sector, err = analysis_service.get_sector_distribution(portfolio_no)
        if err:
            return None, err
        
        # 프롬프트 구성
        prompt = _build_analysis_prompt(summary, risk, sector)
        
        # Claude API 호출
        response = _call_claude_api(api_key, prompt)
        
        if not response:
            return None, "AI 분석 요청에 실패했습니다."
        
        return {
            "comment": response.get('comment', ''),
            "suggestions": response.get('suggestions', []),
            "analysis_data": {
                "summary": summary,
                "risk": risk,
                "sector": sector
            }
        }, None
    except Exception as e:
        return None, str(e)


def _build_analysis_prompt(summary, risk, sector):
    """분석 프롬프트 구성"""
    stocks_info = ""
    for s in summary.get('stocks', []):
        stocks_info += f"- {s['name']}({s['symbol']}): 비중 {s['weight']}%, 수익률 {s['return_pct']}%\n"
    
    sectors_info = ""
    for s in sector.get('sectors', []):
        sectors_info += f"- {s['sector']}: {s['weight']}%\n"
    
    prompt = f"""
다음은 한 투자자의 포트폴리오 분석 데이터입니다. 이 데이터를 바탕으로 포트폴리오의 장단점을 분석하고, 
개선을 위한 구체적인 제안을 해주세요.

## 포트폴리오 요약
- 총 투자금액: {summary.get('total_invested', 0):,}원
- 총 평가금액: {summary.get('total_value', 0):,}원
- 총 수익률: {summary.get('total_return', 0)}%
- 총 손익: {summary.get('total_profit', 0):,}원

## 보유 종목
{stocks_info}

## 리스크 지표
- 포트폴리오 변동성: {risk.get('portfolio_volatility', 0)}%
- 샤프 비율: {risk.get('sharpe_ratio', 0)}

## 섹터 분포
{sectors_info}

위 정보를 바탕으로 다음 형식으로 답변해주세요:

1. 먼저 이 포트폴리오의 전반적인 상태를 2-3문장으로 평가해주세요.
2. 주요 장점을 2-3가지 알려주세요.
3. 개선이 필요한 부분을 2-3가지 알려주세요.
4. 구체적인 개선 제안을 3가지 해주세요. (예: "A 종목 비중을 10% 줄이고 B 섹터 ETF를 추가하세요")

답변은 한국어로, 투자 초보자도 이해할 수 있게 쉽게 설명해주세요.
"""
    return prompt


def _call_claude_api(api_key, prompt):
    """Claude API 호출"""
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    data = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1500,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result.get('content', [])
        
        if content and len(content) > 0:
            text = content[0].get('text', '')
            return _parse_ai_response(text)
        
        return None
    except requests.exceptions.RequestException as e:
        print(f"Claude API 오류: {e}")
        return None


def _parse_ai_response(text):
    """AI 응답 파싱"""
    # 간단한 파싱 - 전체 텍스트를 comment로, 개선 제안 부분을 suggestions로 추출
    suggestions = []
    
    lines = text.split('\n')
    for line in lines:
        # 번호가 붙은 제안 추출 (예: "1. ...", "- ...")
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith('-')):
            # 제안 관련 키워드가 있으면 suggestions에 추가
            if any(keyword in line for keyword in ['추가', '줄이', '늘리', '고려', '분산', '비중']):
                # 앞의 번호나 대시 제거
                suggestion = line.lstrip('0123456789.-) ').strip()
                if suggestion:
                    suggestions.append(suggestion)
    
    return {
        "comment": text,
        "suggestions": suggestions[:5]  # 최대 5개
    }
