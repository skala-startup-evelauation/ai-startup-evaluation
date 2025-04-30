import os
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# ReportLab 패키지
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus import PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class TextInvestmentReportGenerator:
    """다른 에이전트의 출력을 통합하여 텍스트 기반 투자 보고서를 생성하는 클래스"""

    def __init__(self, output_dir: str = "reports", font_path: Optional[str] = None):
        """
        보고서 생성기 초기화
        
        Args:
            output_dir: 보고서 저장 디렉토리
            font_path: 한글 폰트 파일 경로 (선택 사항)
        """
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        self.color_theme = {
            "primary": "#4285F4", "secondary": "#34A853", "warning": "#FBBC05", 
            "danger": "#EA4335", "light": "#F1F3F4", "dark": "#202124"
        }
        
        # 폰트 설정
        self.setup_fonts(font_path)
        
    def setup_fonts(self, font_path: Optional[str] = None):
        """한글 폰트 설정 - 간소화된 버전"""
        # 기본 폰트 설정
        self.base_font = "Helvetica"
        self.bold_font = "Helvetica-Bold"
        
        try:
            # 한글 폰트 설정 시도
            if font_path and os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('KoreanFont', font_path))
                self.base_font = 'KoreanFont'
                self.bold_font = 'KoreanFont'
        except:
            # 폰트 등록 실패시 기본 폰트 사용
            pass

    def generate_report(self, report_data: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """
        보고서 데이터를 기반으로 PDF 보고서 생성
        
        Args:
            report_data: 보고서 내용 데이터
            output_path: 출력 경로 (선택 사항)
            
        Returns:
            생성된 PDF 파일 경로
        """
        if output_path is None:
            company_name = report_data.get("company_name", "Report")
            company_name_safe = "".join(c for c in company_name if c.isalnum() or c in (' ', '_')).rstrip()
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(self.output_dir, f"{company_name_safe}_투자보고서_{date_str}.pdf")

        # PDF 문서 설정
        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            rightMargin=0.75*inch, leftMargin=0.75*inch,
            topMargin=0.75*inch, bottomMargin=0.75*inch
        )

        # 스타일 정의
        styles = getSampleStyleSheet()
        
        # 사용자 정의 스타일 생성
        custom_styles = {
            'Title': ParagraphStyle(
                name='CustomTitle',
                parent=styles['Title'],
                fontName=self.bold_font,
                fontSize=18,
                leading=24,
                alignment=1,
                spaceAfter=12,
                textColor=colors.HexColor(self.color_theme["dark"])
            ),
            'Heading1': ParagraphStyle(
                name='CustomHeading1',
                parent=styles['Heading1'],
                fontName=self.bold_font,
                fontSize=16,
                leading=20,
                spaceAfter=10,
                textColor=colors.HexColor(self.color_theme["primary"])
            ),
            'Heading2': ParagraphStyle(
                name='CustomHeading2',
                parent=styles['Heading2'],
                fontName=self.bold_font,
                fontSize=14,
                leading=18,
                spaceAfter=8,
                textColor=colors.HexColor(self.color_theme["secondary"])
            ),
            'Normal': ParagraphStyle(
                name='CustomNormal',
                parent=styles['Normal'],
                fontName=self.base_font,
                fontSize=10,
                leading=14,
                spaceBefore=6,
                spaceAfter=6
            ),
            'Bold': ParagraphStyle(
                name='Bold',
                parent=styles['Normal'],
                fontName=self.bold_font,
                fontSize=10,
                leading=14
            ),
            'Italic': ParagraphStyle(
                name='Italic',
                parent=styles['Normal'],
                fontName=self.base_font,
                fontSize=10,
                leading=14,
                textColor=colors.HexColor(self.color_theme["primary"])
            ),
            'Indented': ParagraphStyle(
                name='Indented',
                parent=styles['Normal'],
                fontName=self.base_font,
                fontSize=10,
                leading=14,
                leftIndent=20
            ),
            'Caption': ParagraphStyle(
                name='Caption',
                parent=styles['Normal'],
                fontName=self.base_font,
                fontSize=8,
                leading=10,
                textColor=colors.grey
            )
        }
        
        # 각 스타일을 스타일시트에 추가
        for style_name, style in custom_styles.items():
            try:
                styles.add(style)
            except KeyError:
                # 이미 존재하는 경우 무시
                pass
        
        elements = []
        
        # 표지 페이지
        title = report_data.get("title", f"{report_data.get('company_name', '기업')} 투자 분석 보고서")
        elements.append(Paragraph(title, custom_styles['Title']))
        elements.append(Spacer(1, 20))
        
        # 날짜 정보
        current_date = datetime.now().strftime('%Y년 %m월 %d일')
        elements.append(Paragraph(f"생성일: {current_date}", custom_styles['Caption']))
        elements.append(Spacer(1, 30))
        
        # 1. 투자 결정 요약
        elements.append(Paragraph("투자 결정 요약", custom_styles['Heading1']))
        elements.append(Spacer(1, 10))
        
        decision = report_data.get("investment_decision", "보류")
        confidence = report_data.get("confidence", 0)
        
        # 투자 결정 테이블
        decision_data = [["결정", "확신도"], [decision, f"{confidence}%"]]
        decision_color = self.color_theme["secondary"] if decision == "투자" else self.color_theme["warning"]
        
        decision_table = Table(decision_data, colWidths=[doc.width/2 - 20, doc.width/2 - 20])
        decision_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor(self.color_theme["primary"])),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), self.bold_font),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 8),
            ('TOPPADDING', (0, 0), (1, 0), 8),
            ('BACKGROUND', (0, 1), (1, 1), colors.HexColor(decision_color)),
            ('TEXTCOLOR', (0, 1), (1, 1), colors.white),
            ('ALIGN', (0, 1), (1, 1), 'CENTER'),
            ('FONTNAME', (0, 1), (1, 1), self.bold_font),
            ('FONTSIZE', (0, 1), (1, 1), 14),
            ('BOTTOMPADDING', (0, 1), (1, 1), 10),
            ('TOPPADDING', (0, 1), (1, 1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(self.color_theme["primary"])),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(decision_table)
        elements.append(Spacer(1, 20))
        
        # 요약 내용
        elements.append(Paragraph("핵심 요약", custom_styles['Heading2']))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(report_data.get("executive_summary", "요약 정보 없음"), custom_styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # 투자 점수 표시 (텍스트로)
        market_score = report_data.get("market_analysis", {}).get("score", 0)
        tech_score = report_data.get("technology_analysis", {}).get("score", 0)
        founder_score = report_data.get("founder_analysis", {}).get("score", 0)
        
        score_data = [
            ["평가 영역", "점수 (100점 만점)"],
            ["시장성", f"{market_score}"],
            ["기술력", f"{tech_score}"],
            ["창업자", f"{founder_score}"]
        ]
        
        score_table = Table(score_data, colWidths=[doc.width/2 - 20, doc.width/2 - 20])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor(self.color_theme["secondary"])),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), self.bold_font),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 8),
            ('TOPPADDING', (0, 0), (1, 0), 8),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor(self.color_theme["light"])),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (0, -1), self.bold_font),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(score_table)
        elements.append(PageBreak())
        
        # 2. 시장 분석
        elements.append(Paragraph("시장 분석", custom_styles['Heading1']))
        elements.append(Spacer(1, 10))
        
        market = report_data.get("market_analysis", {})
        market_info_data = [
            ["시장 규모", str(market.get("market_size", "N/A"))],
            ["성장률", f"{market.get('growth_rate', 0)}%"],
            ["시장성 점수", f"{market.get('score', 0)}/100"]
        ]
        
        market_info_table = Table(market_info_data, colWidths=[100, 400])
        market_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor(self.color_theme["light"])),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor(self.color_theme["dark"])),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), self.bold_font),
            ('FONTSIZE', (0, 0), (0, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(market_info_table)
        elements.append(Spacer(1, 15))
        elements.append(Paragraph(market.get("summary", "시장 분석 요약 없음"), custom_styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # 수평선 대신 구분선 텍스트 사용
        elements.append(Paragraph("_" * 70, custom_styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # 3. 기술 분석
        elements.append(Paragraph("기술 분석", custom_styles['Heading1']))
        elements.append(Spacer(1, 10))
        
        tech = report_data.get("technology_analysis", {})
        elements.append(Paragraph(f"기술력 점수: {tech.get('score', 0)}/100", custom_styles['Bold']))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(tech.get("summary", "기술 분석 요약 없음"), custom_styles['Normal']))
        elements.append(Spacer(1, 15))
        
        # 강점과 약점 표시
        strengths = tech.get("strengths", [])
        weaknesses = tech.get("weaknesses", [])
        
        if strengths:
            elements.append(Paragraph("기술적 강점:", custom_styles['Bold']))
            for strength in strengths:
                elements.append(Paragraph(f"• {strength}", custom_styles['Indented']))
            elements.append(Spacer(1, 10))
        
        if weaknesses:
            elements.append(Paragraph("기술적 약점:", custom_styles['Bold']))
            for weakness in weaknesses:
                elements.append(Paragraph(f"• {weakness}", custom_styles['Indented']))
            elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("_" * 70, custom_styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # 4. 경쟁사 분석
        elements.append(Paragraph("경쟁사 분석", custom_styles['Heading1']))
        elements.append(Spacer(1, 10))
        
        comp = report_data.get("competitor_analysis", {})
        elements.append(Paragraph(comp.get("summary", "경쟁사 분석 요약 없음"), custom_styles['Normal']))
        elements.append(Spacer(1, 15))
        
        # 주요 경쟁사 목록
        main_competitors = comp.get("main_competitors", [])
        if main_competitors:
            elements.append(Paragraph("주요 경쟁사:", custom_styles['Bold']))
            for competitor in main_competitors:
                elements.append(Paragraph(f"• {competitor}", custom_styles['Indented']))
            elements.append(Spacer(1, 15))
        
        # 시장 점유율 (테이블로 표시)
        market_share = comp.get("market_share", {})
        if market_share:
            elements.append(Paragraph("시장 점유율:", custom_styles['Bold']))
            elements.append(Spacer(1, 5))
            
            market_share_data = [["기업명", "점유율(%)"]]
            for company, share in market_share.items():
                # 한글 폰트 적용을 위해 Paragraph 객체 사용
                company_name = Paragraph(str(company), custom_styles['Normal'])
                share_value = Paragraph(f"{share}%", custom_styles['Normal'])
                market_share_data.append([company_name, share_value])
            
            market_share_table = Table(market_share_data, colWidths=[300, 100])
            market_share_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.HexColor(self.color_theme["primary"])),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), self.bold_font),
                ('FONTSIZE', (0, 0), (1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (1, 0), 6),
                ('TOPPADDING', (0, 0), (1, 0), 6),
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(market_share_table)
            elements.append(Spacer(1, 15))
        
        elements.append(PageBreak())
        
        # 5. 창업자 분석
        elements.append(Paragraph("창업자 분석", custom_styles['Heading1']))
        elements.append(Spacer(1, 10))
        
        founder = report_data.get("founder_analysis", {})
        elements.append(Paragraph(f"창업자 점수: {founder.get('score', 0)}/100", custom_styles['Bold']))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(founder.get("summary", "창업자 분석 요약 없음"), custom_styles['Normal']))
        elements.append(Spacer(1, 15))
        
        # 창업자 강점
        founder_strengths = founder.get("strengths", [])
        if founder_strengths:
            elements.append(Paragraph("창업자 강점:", custom_styles['Bold']))
            for strength in founder_strengths:
                elements.append(Paragraph(f"• {strength}", custom_styles['Indented']))
            elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("_" * 70, custom_styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # 6. 투자 분석
        elements.append(Paragraph("투자 분석", custom_styles['Heading1']))
        elements.append(Spacer(1, 10))
        
        # 투자 이유와 위험 요소 테이블
        reasons = report_data.get("investment_reasons", [])
        risks = report_data.get("risk_factors", [])
        
        if reasons or risks:
            pros_cons_data = [["투자 이유", "위험 요소"]]
            
            max_items = max(len(reasons), len(risks))
            for i in range(max_items):
                reason = reasons[i] if i < len(reasons) else ""
                risk = risks[i] if i < len(risks) else ""
                pros_cons_data.append([reason, risk])
            
            pros_cons_table = Table(pros_cons_data, colWidths=[doc.width/2 - 20, doc.width/2 - 20])
            pros_cons_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(self.color_theme["secondary"])),
                ('BACKGROUND', (1, 0), (1, 0), colors.HexColor(self.color_theme["danger"])),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), self.bold_font),
                ('FONTSIZE', (0, 0), (1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (1, 0), 6),
                ('TOPPADDING', (0, 0), (1, 0), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(pros_cons_table)
            elements.append(Spacer(1, 20))
        
        # 7. 종합 추천
        elements.append(Paragraph("종합 추천", custom_styles['Heading1']))
        elements.append(Spacer(1, 10))
        
        recommendation = report_data.get("recommendation", "종합 추천 내용 없음")
        elements.append(Paragraph(recommendation, custom_styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # 결론
        elements.append(Paragraph(f"이 보고서는 {decision} 결정을 {confidence}% 확신도로 권장합니다.", custom_styles['Bold']))
        
        # PDF 생성
        doc.build(elements)
        
        return output_path
            
    def create_investment_report(self, 
                              company_data: Dict[str, Any],
                              market_analysis: Dict[str, Any] = None, 
                              tech_analysis: Dict[str, Any] = None,
                              competitor_analysis: Dict[str, Any] = None,
                              founder_analysis: Dict[str, Any] = None,
                              output_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        다른 에이전트의 분석 결과를 통합하여 투자 보고서 생성
        
        Args:
            company_data: 기업 기본 정보
            market_analysis: 시장 분석 결과 (선택 사항)
            tech_analysis: 기술 분석 결과 (선택 사항)
            competitor_analysis: 경쟁사 분석 결과 (선택 사항)
            founder_analysis: 창업자 분석 결과 (선택 사항)
            output_path: 출력 파일 경로 (선택 사항)
            
        Returns:
            보고서 데이터 및 PDF 경로 딕셔너리
        """
        # 기본 정보
        company_name = company_data.get("name", "기업명 없음")
        
        # 점수 계산 (각 분석 결과의 점수 평균)
        market_score = market_analysis.get("score", 0) if market_analysis else 0
        tech_score = tech_analysis.get("score", 0) if tech_analysis else 0
        founder_score = founder_analysis.get("score", 0) if founder_analysis else 0
        
        # 평균 점수
        avg_score = 0
        score_count = 0
        
        if market_score > 0:
            avg_score += market_score
            score_count += 1
        
        if tech_score > 0:
            avg_score += tech_score
            score_count += 1
            
        if founder_score > 0:
            avg_score += founder_score
            score_count += 1
            
        avg_score = avg_score / score_count if score_count > 0 else 0
        
        # 투자 결정: 평균 점수가 60점 이상이면 투자, 그렇지 않으면 보류
        investment_decision = "투자" if avg_score >= 60 else "보류"
        
        # 확신도: 평균 점수와 유사하게 설정 (최소 50%, 최대 95%)
        confidence = min(95, max(50, round(avg_score * 0.95)))
        
        # 종합 보고서 데이터 생성
        report_data = {
            "title": f"{company_name} 투자 분석 보고서",
            "company_name": company_name,
            "investment_decision": investment_decision,
            "confidence": confidence,
            "executive_summary": self._generate_summary(company_data, market_analysis, tech_analysis, competitor_analysis, founder_analysis),
            "market_analysis": market_analysis or {"summary": "시장 분석 데이터 없음", "score": 0},
            "technology_analysis": tech_analysis or {"summary": "기술 분석 데이터 없음", "score": 0, "strengths": [], "weaknesses": []},
            "competitor_analysis": competitor_analysis or {"summary": "경쟁사 분석 데이터 없음", "main_competitors": [], "market_share": {}},
            "founder_analysis": founder_analysis or {"summary": "창업자 분석 데이터 없음", "score": 0, "strengths": []},
            "investment_reasons": self._extract_reasons(company_data, market_analysis, tech_analysis, competitor_analysis, founder_analysis),
            "risk_factors": self._extract_risks(company_data, market_analysis, tech_analysis, competitor_analysis, founder_analysis),
            "recommendation": self._generate_recommendation(investment_decision, company_data, market_analysis, tech_analysis, competitor_analysis, founder_analysis)
        }
        
        # PDF 보고서 생성
        pdf_path = self.generate_report(report_data, output_path)
        
        # 결과 반환
        return {
            "report_data": report_data,
            "pdf_path": pdf_path
        }
    
    def _generate_summary(self, company_data, market_analysis, tech_analysis, competitor_analysis, founder_analysis):
        """핵심 요약 생성"""
        company_name = company_data.get("name", "해당 기업")
        summary_parts = []
        
        # 기업 소개
        summary_parts.append(f"{company_name}은(는) {company_data.get('description', '설명 없음')}.")
        
        # 시장 관련 요약
        if market_analysis:
            summary_parts.append(market_analysis.get("summary", ""))
        
        # 투자 결정 이유
        market_score = market_analysis.get("score", 0) if market_analysis else 0
        tech_score = tech_analysis.get("score", 0) if tech_analysis else 0
        founder_score = founder_analysis.get("score", 0) if founder_analysis else 0
        
        avg_score = 0
        count = 0
        
        if market_score > 0:
            avg_score += market_score
            count += 1
        
        if tech_score > 0:
            avg_score += tech_score
            count += 1
            
        if founder_score > 0:
            avg_score += founder_score
            count += 1
            
        avg_score = avg_score / count if count > 0 else 0
        
        if avg_score >= 60:
            summary_parts.append(f"전반적인 평가 결과, {company_name}에 대한 투자가 권장됩니다.")
        else:
            summary_parts.append(f"전반적인 평가 결과, {company_name}에 대한 투자는 현 시점에서 보류하는 것이 권장됩니다.")
        
        return " ".join(summary_parts)
    
    def _extract_reasons(self, company_data, market_analysis, tech_analysis, competitor_analysis, founder_analysis):
        """투자 이유 추출"""
        reasons = []
        
        # 시장 분석에서 추출
        if market_analysis:
            market_score = market_analysis.get("score", 0)
            if market_score >= 70:
                reasons.append("시장 성장성 높음")
            elif market_score >= 60:
                reasons.append("시장 잠재력 있음")
            
            growth_rate = market_analysis.get("growth_rate", 0)
            if growth_rate >= 20:
                reasons.append(f"시장 성장률 높음 ({growth_rate}%)")
        
        # 기술 분석에서 추출
        if tech_analysis:
            tech_score = tech_analysis.get("score", 0)
            if tech_score >= 70:
                reasons.append("기술력 우수")
            elif tech_score >= 60:
                reasons.append("기술적 경쟁력 있음")
            
            strengths = tech_analysis.get("strengths", [])
            if strengths:
                # 첫 번째 강점 추가
                reasons.append(f"기술적 강점: {strengths[0]}")
        
        # 창업자 분석에서 추출
        if founder_analysis:
            founder_score = founder_analysis.get("score", 0)
            if founder_score >= 70:
                reasons.append("창업자 역량 우수")
            elif founder_score >= 60:
                reasons.append("창업자 배경 적합")
        
        # 최소 1개 이상 생성
        if len(reasons) < 1:
            reasons.append("잠재적 성장 가능성")
            
        return reasons
    
    def _extract_risks(self, company_data, market_analysis, tech_analysis, competitor_analysis, founder_analysis):
        """위험 요소 추출"""
        risks = []
        
        # 시장 분석에서 추출
        if market_analysis:
            market_score = market_analysis.get("score", 0)
            if market_score < 50:
                risks.append("시장 불확실성 높음")
            
            if "경쟁" in market_analysis.get("summary", "").lower():
                risks.append("시장 경쟁 치열")
        
        # 기술 분석에서 추출
        if tech_analysis:
            tech_score = tech_analysis.get("score", 0)
            if tech_score < 50:
                risks.append("기술적 검증 부족")
            
            weaknesses = tech_analysis.get("weaknesses", [])
            if weaknesses:
                # 첫 번째 약점 추가
                risks.append(f"기술적 약점: {weaknesses[0]}")
        
        # 창업자 분석에서 추출
        if founder_analysis:
            founder_score = founder_analysis.get("score", 0)
            if founder_score < 50:
                risks.append("창업자 경험 부족")
        
        # 경쟁사 분석에서 추출
        if competitor_analysis:
            market_share = competitor_analysis.get("market_share", {})
            company_name = company_data.get("name", "")
            
            # 시장 점유율이 낮은 경우
            if company_name in market_share and market_share[company_name] < 10:
                risks.append("낮은 시장 점유율")
            
            if len(competitor_analysis.get("main_competitors", [])) >= 3:
                risks.append("다수의 경쟁사 존재")
        
        # 최소 1개 이상 생성
        if len(risks) < 1:
            risks.append("운영 리스크")
            
        return risks
    
    def _generate_recommendation(self, decision, company_data, market_analysis, tech_analysis, competitor_analysis, founder_analysis):
        """투자 추천 생성"""
        company_name = company_data.get("name", "해당 기업")
        
        if decision == "투자":
            recommendation = f"{company_name}의 "
            
            # 강점 언급
            strength_parts = []
            
            if market_analysis and market_analysis.get("score", 0) >= 60:
                strength_parts.append("시장 잠재력")
            
            if tech_analysis and tech_analysis.get("score", 0) >= 60:
                strength_parts.append("기술적 경쟁력")
            
            if founder_analysis and founder_analysis.get("score", 0) >= 60:
                strength_parts.append("창업자 역량")
            
            if strength_parts:
                recommendation += ", ".join(strength_parts)
                recommendation += "을(를) 고려할 때 투자를 권장합니다."
            else:
                recommendation += "종합적인 평가를 고려할 때 투자를 권장합니다."
            
            # 보완점 추가
            risk_factors = self._extract_risks(company_data, market_analysis, tech_analysis, competitor_analysis, founder_analysis)
            if risk_factors:
                recommendation += f" 다만, {risk_factors[0]}에 대한 대책 마련이 필요합니다."
            
        else:  # 보류
            recommendation = f"{company_name}에 대한 투자는 현 시점에서 보류하는 것이 권장됩니다. "
            
            # 보류 이유 언급
            risk_factors = self._extract_risks(company_data, market_analysis, tech_analysis, competitor_analysis, founder_analysis)
            if risk_factors:
                recommendation += f"주요 이유는 {', '.join(risk_factors[:2])} 등입니다."
            else:
                recommendation += "충분한 검증이 필요합니다."
            
            # 미래 가능성 언급
            recommendation += " 향후 이러한 요소들이 개선된다면 재검토가 가능할 것입니다."
        
        return recommendation