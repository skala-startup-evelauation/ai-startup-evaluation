#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from datetime import datetime

# 모듈 임포트
from llm_report_generator import TextInvestmentReportGenerator

def main():
    print("🚀 텍스트 기반 투자 보고서 생성기 테스트 시작...")

    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)

    # 한글 폰트 경로 - 간소화
    font_path = "C:/Windows/Fonts/malgun.ttf"  # Windows 맑은 고딕
    if not os.path.exists(font_path):
        print("경고: 기본 한글 폰트를 찾지 못했습니다. 기본 영문 폰트가 사용됩니다.")
        font_path = None
        
    # 보고서 생성기 초기화
    report_generator = TextInvestmentReportGenerator(
        output_dir=output_dir,
        font_path=font_path
    )

    # 샘플 데이터: 기업 정보
    company_data = {
        "name": "AI헬스케어",
        "description": "AI 기반 건강 모니터링 및 예측 플랫폼. 사용자의 웨어러블 기기 데이터를 분석하여 건강 상태를 모니터링하고 잠재적 질병 위험을 예측",
        "founded_year": 2022,
        "products_services": [
            "AI 건강 모니터링 SaaS (병원용)",
            "개인 건강 예측 구독 서비스 (앱)"
        ],
        "total_investments": 1350000,
        "employee_count": 25,
        "patent_count": 3
    }
    
    # 에이전트 1의 출력: 시장 분석 결과
    market_analysis = {
        "summary": "AI 기반 헬스케어 시장은 연평균 25% 성장 중이며, 디지털 헬스케어의 전반적인 성장 추세를 고려할 때 향후 시장 성장이 유망합니다.",
        "market_size": "500조원",
        "growth_rate": 25,
        "score": 75,
        "key_insights": [
            "디지털 의료 서비스에 대한 수요 급증",
            "개인화된 건강 관리에 대한 선호도 증가",
            "원격 의료 시장 확대"
        ]
    }
    
    # 에이전트 2의 출력: 기술 분석 결과
    tech_analysis = {
        "summary": "AI헬스케어는 AI 기술을 활용한 건강 모니터링 플랫폼을 개발하고 있으며, 특허 보유를 통해 기술적 경쟁력을 확보하고 있습니다.",
        "score": 65,
        "strengths": [
            "특허 3건 보유",
            "AI 알고리즘 기반 질병 예측 기술",
            "웨어러블 기기 데이터 분석 역량"
        ],
        "weaknesses": [
            "임상적 검증 단계 진행 중",
            "데이터 처리 확장성 검증 필요"
        ],
        "tech_readiness_level": 6
    }
    
    # 에이전트 3의 출력: 경쟁사 분석 결과
    competitor_analysis = {
        "summary": "글로벌 헬스테크 기업들과의 경쟁이 치열하며, 시장에서의 점유율이 낮은 상황입니다.",
        "main_competitors": [
            "글로벌 헬스테크 기업 H사",
            "국내 의료 AI 스타트업 M사",
            "대형 의료기기 회사 P사"
        ],
        "market_share": {
            "AI헬스케어": 5,
            "글로벌 헬스테크 기업 H사": 40,
            "국내 의료 AI 스타트업 M사": 30,
            "대형 의료기기 회사 P사": 25
        },
        "competitive_position": "기술적 강점을 가지고 있으나 시장 입지가 약함"
    }
    
    # 에이전트 4의 출력: 창업자 분석 결과
    founder_analysis = {
        "summary": "김혁신과 박지능은 각각 의공학과 AI 분야에서의 전문성을 가지고 있으며, 관련 산업 경험을 보유하고 있습니다.",
        "score": 80,
        "strengths": [
            "의공학 박사 학력",
            "AI 석사 학력",
            "의료기기 회사 및 AI 기업 경력"
        ],
        "team_composition": "기술 전문가 중심으로 구성됨",
        "experience_level": "해당 산업 5년 이상 경험 보유"
    }

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_path = f"{output_dir}/AI헬스케어_투자보고서_{timestamp}.pdf"

    print(f"📊 'AI헬스케어' 스타트업에 대한 투자 보고서 생성 중...")
    print("-" * 30)

    # 보고서 생성
    start_time = time.time()
    
    # 여러 에이전트의 분석 결과 통합하여 보고서 생성
    result = report_generator.create_investment_report(
        company_data=company_data,
        market_analysis=market_analysis,
        tech_analysis=tech_analysis,
        competitor_analysis=competitor_analysis,
        founder_analysis=founder_analysis,
        output_path=output_path
    )

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"✅ 보고서 생성 완료!")
    print(f"⏱️ 소요 시간: {elapsed_time:.2f}초")
    print(f"📄 보고서 저장 경로: {result['pdf_path']}")

    # 결과 출력
    report_data = result.get('report_data', {})

    print("\n📝 보고서 핵심 내용:")
    print(f"💰 투자 결정: {report_data.get('investment_decision', 'N/A')}")
    print(f"🎯 확신도: {report_data.get('confidence', 'N/A')}%")
    summary = report_data.get('executive_summary', 'N/A')
    print(f"📌 핵심 요약: {summary[:200]}..." if len(summary) > 200 else f"📌 핵심 요약: {summary}")

    print("\n📊 평가 점수:")
    market_score = report_data.get('market_analysis', {}).get('score', 'N/A')
    tech_score = report_data.get('technology_analysis', {}).get('score', 'N/A')
    founder_score = report_data.get('founder_analysis', {}).get('score', 'N/A')
    print(f"🌐 시장성: {market_score}/100")
    print(f"🔬 기술력: {tech_score}/100")
    print(f"👨‍💼 창업자: {founder_score}/100")

    print(f"\n생성된 PDF 보고서를 확인하세요: {result['pdf_path']}")

if __name__ == "__main__":
    main()