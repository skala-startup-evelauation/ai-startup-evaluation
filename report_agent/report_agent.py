# reportlab_report_agent.py
import os
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import logging
from pathlib import Path
import dotenv

# .env 파일 로드
dotenv.load_dotenv()

# ReportLab 라이브러리 (PDF 생성)
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm, cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.platypus import PageBreak, ListFlowable, ListItem
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("ReportLab 라이브러리가 설치되지 않았습니다. PDF 생성 기능이 제한됩니다.")

# 차트 생성 관련 라이브러리
try:
    import matplotlib
    matplotlib.use('Agg')  # 서버 환경에서 그래픽 창 없이 작동하도록 설정
    import matplotlib.pyplot as plt
    import numpy as np
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
    logging.warning("Matplotlib 라이브러리가 설치되지 않았습니다. 차트 생성 기능이 비활성화됩니다.")

class ReportLabReportAgent:
    """
    ReportLab 라이브러리를 활용한 PDF 투자 보고서 생성 에이전트
    """
    
    def __init__(self, 
                 output_dir: str = "outputs",
                 company_logo: Optional[str] = None,
                 font_path: Optional[str] = None,
                 color_scheme: Optional[Dict[str, str]] = None):
        """
        보고서 생성 에이전트 초기화
        
        Args:
            output_dir: 최종 보고서 출력 디렉토리
            company_logo: 회사 로고 파일 경로 (선택적)
            font_path: 폰트 파일 경로 (선택적)
            color_scheme: 보고서에 사용할 색상 스키마 (선택적)
        """
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 회사 로고 설정
        self.company_logo = company_logo
        
        # 색상 스키마 설정
        self.color_scheme = color_scheme or {
            "primary": "#1a73e8",           # 주 색상 (파란색)
            "secondary": "#34a853",         # 보조 색상 (녹색)
            "accent": "#ea4335",            # 강조 색상 (빨간색)
            "neutral": "#5f6368",           # 중립 색상 (회색)
            "background": "#f8f9fa",        # 배경 색상 (밝은 회색)
            "text_primary": "#202124",      # 주 텍스트 색상 (검정색)
            "text_secondary": "#5f6368",    # 보조 텍스트 색상 (회색)
            "success": "#34a853",           # 성공 색상 (녹색)
            "warning": "#fbbc04",           # 경고 색상 (노란색)
            "danger": "#ea4335"             # 위험 색상 (빨간색)
        }
        
        # 폰트 설정
        self.font_path = font_path
        self.fonts_registered = False
        self.setup_fonts()
    
    def setup_fonts(self):
        """폰트 설정 함수 - 한글 폰트 문제 해결"""
        if not PDF_AVAILABLE:
            return
            
        # 기본 폰트 등록 시도
        try:
            # 폰트 경로 후보들 (우선순위 순)
            font_candidates = [
                # 사용자 지정 폰트
                self.font_path,
                
                # Windows 경로
                'C:/Windows/Fonts/malgun.ttf',          # 맑은 고딕
                'C:/Windows/Fonts/gulim.ttf',           # 굴림
                'C:/Windows/Fonts/batang.ttf',          # 바탕
                'C:/Windows/Fonts/NanumGothic.ttf',     # 나눔고딕
                
                # macOS 경로
                '/Library/Fonts/AppleGothic.ttf',       # Apple 고딕
                '/Library/Fonts/NanumGothic.ttf',
                
                # Linux 경로
                '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
                '/usr/local/share/fonts/NanumGothic.ttf',
                
                # 현재 디렉토리
                'NanumGothic.ttf',
                'malgun.ttf',
                'gulim.ttf'
            ]
            
            # 사용 가능한 첫 번째 폰트 찾기
            found_font = None
            font_name = None
            
            for path in font_candidates:
                if path and os.path.exists(path):
                    found_font = path
                    font_name = os.path.basename(path).split('.')[0]
                    break
            
            if found_font:
                # 폰트 등록
                font_alias = 'KoreanFont'
                pdfmetrics.registerFont(TTFont(font_alias, found_font))
                
                # 폰트 패밀리 등록 - 이탤릭, 볼드 등의 변형을 처리하기 위함
                registerFontFamily(font_alias, normal=font_alias)
                
                self.font_path = found_font
                self.font_alias = font_alias
                self.fonts_registered = True
                
                logging.info(f"한글 폰트 등록 성공: {found_font} (별칭: {font_alias})")
            else:
                # 폰트를 찾지 못한 경우 내장 폰트 사용
                logging.warning("한글 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
                self.font_alias = 'Helvetica'
        except Exception as e:
            logging.error(f"폰트 등록 중 오류 발생: {e}")
            logging.warning("기본 내장 폰트를 사용합니다.")
            self.font_alias = 'Helvetica'
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """HEX 색상 코드를 RGB 튜플로 변환"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _create_pie_chart(self, 
                         data: Dict[str, float], 
                         title: str, 
                         filename: str = "pie_chart.png",
                         width: int = 640,
                         height: int = 480) -> str:
        """
        파이 차트 생성
        
        Args:
            data: 라벨과 값의 딕셔너리
            title: 차트 제목
            filename: 저장할 파일명
            width: 차트 너비
            height: 차트 높이
            
        Returns:
            저장된 차트 파일 경로
        """
        if not CHARTS_AVAILABLE:
            return ""
        
        # matplotlib 한글 폰트 설정
        try:
            # 맑은 고딕, 나눔고딕 등 한글 폰트 설정 시도
            font_candidates = [
                'NanumGothic', 'Malgun Gothic', 'AppleGothic', 
                'Gulim', 'Batang', 'Arial Unicode MS'
            ]
            
            for font in font_candidates:
                try:
                    matplotlib.rc('font', family=font)
                    # 테스트로 한글 렌더링
                    fig, ax = plt.subplots()
                    ax.text(0.5, 0.5, '한글 테스트')
                    plt.close(fig)
                    # 문제 없이 렌더링되면 break
                    break
                except:
                    continue
                    
            # 음수 부호 표시 문제 해결
            matplotlib.rcParams['axes.unicode_minus'] = False
        except Exception as e:
            logging.warning(f"Matplotlib 한글 폰트 설정 실패: {e}")
            
        labels = list(data.keys())
        values = list(data.values())
        
        # 색상 설정
        colors = [
            self._hex_to_rgb(self.color_scheme["primary"]),
            self._hex_to_rgb(self.color_scheme["secondary"]),
            self._hex_to_rgb(self.color_scheme["accent"]),
            self._hex_to_rgb(self.color_scheme["neutral"]),
            self._hex_to_rgb(self.color_scheme["success"]),
            self._hex_to_rgb(self.color_scheme["warning"]),
            self._hex_to_rgb(self.color_scheme["danger"])
        ]
        # RGB 값을 0-1 범위로 변환
        colors = [(r/255, g/255, b/255) for r, g, b in colors]
        
        # 파이 차트 생성
        plt.figure(figsize=(width/100, height/100), dpi=100)
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors[:len(labels)])
        plt.axis('equal')  # 원형으로 보이게 설정
        plt.title(title)
        
        # 차트 저장
        temp_dir = os.path.join(self.output_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        chart_path = os.path.join(temp_dir, filename)
        plt.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_bar_chart(self, 
                         data: Dict[str, float], 
                         title: str, 
                         xlabel: str = "",
                         ylabel: str = "",
                         filename: str = "bar_chart.png",
                         width: int = 640,
                         height: int = 480) -> str:
        """
        막대 차트 생성
        
        Args:
            data: 라벨과 값의 딕셔너리
            title: 차트 제목
            xlabel: X축 라벨
            ylabel: Y축 라벨
            filename: 저장할 파일명
            width: 차트 너비
            height: 차트 높이
            
        Returns:
            저장된 차트 파일 경로
        """
        if not CHARTS_AVAILABLE:
            return ""
            
        labels = list(data.keys())
        values = list(data.values())
        
        # 색상 설정
        color = self._hex_to_rgb(self.color_scheme["primary"])
        color = (color[0]/255, color[1]/255, color[2]/255)  # RGB 값을 0-1 범위로 변환
        
        # 막대 차트 생성
        plt.figure(figsize=(width/100, height/100), dpi=100)
        plt.bar(labels, values, color=color)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # 차트 저장
        temp_dir = os.path.join(self.output_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        chart_path = os.path.join(temp_dir, filename)
        plt.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def create_reportlab_pdf(self, report: Dict[str, Any], output_path: Optional[str] = None) -> Optional[str]:
        """
        ReportLab을 사용하여 PDF 보고서 생성
        
        Args:
            report: 보고서 데이터
            output_path: 출력 파일 경로 (없으면 기본 경로 사용)
            
        Returns:
            생성된 PDF 파일 경로 (또는 None)
        """
        if not PDF_AVAILABLE:
            logging.warning("ReportLab 라이브러리가 설치되지 않았습니다. PDF 생성 기능이 제한됩니다.")
            return None
        
        if output_path is None:
            # 기본 파일명 생성
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{report['selected_startup_name']}_report_{date_str}.pdf"
            output_path = os.path.join(self.output_dir, filename)
        
        try:
            # 디렉토리 생성 (필요한 경우)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # PDF 문서 생성
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )
            
            # 기본 스타일 정의
            styles = getSampleStyleSheet()
            
            # 한글 지원 스타일 추가
            if self.fonts_registered:
                # 한글 폰트가 등록된 경우 한글 스타일 추가
                styles.add(ParagraphStyle(
                    name='Korean',
                    fontName=self.font_alias,
                    fontSize=10,
                    leading=14,  # 행간 간격 증가
                    encoding='utf-8'  # UTF-8 인코딩 명시
                ))
                styles.add(ParagraphStyle(
                    name='KoreanTitle',
                    fontName=self.font_alias,
                    fontSize=16,
                    leading=20,
                    alignment=1,  # 가운데 정렬
                    encoding='utf-8'
                ))
                styles.add(ParagraphStyle(
                    name='KoreanHeading1',
                    fontName=self.font_alias,
                    fontSize=14,
                    leading=18,
                    spaceAfter=10,
                    encoding='utf-8'
                ))
                styles.add(ParagraphStyle(
                    name='KoreanHeading2',
                    fontName=self.font_alias,
                    fontSize=12,
                    leading=16,
                    spaceAfter=8,
                    encoding='utf-8'
                ))
            else:
                # 한글 폰트가 없는 경우 기본 스타일 사용
                logging.warning("한글 폰트가 등록되지 않아 기본 스타일을 사용합니다. 한글이 올바르게 표시되지 않을 수 있습니다.")
                styles.add(ParagraphStyle(
                    name='Korean',
                    fontName='Helvetica',
                    fontSize=10,
                    leading=12
                ))
                styles.add(ParagraphStyle(
                    name='KoreanTitle',
                    fontName='Helvetica-Bold',
                    fontSize=16,
                    leading=20,
                    alignment=1
                ))
                styles.add(ParagraphStyle(
                    name='KoreanHeading1',
                    fontName='Helvetica-Bold',
                    fontSize=14,
                    leading=16,
                    spaceAfter=10
                ))
                styles.add(ParagraphStyle(
                    name='KoreanHeading2',
                    fontName='Helvetica-Bold',
                    fontSize=12,
                    leading=14,
                    spaceAfter=8
                ))
            
            # 색상 정의
            primary_color = self._hex_to_rgb(self.color_scheme["primary"])
            secondary_color = self._hex_to_rgb(self.color_scheme["secondary"])
            accent_color = self._hex_to_rgb(self.color_scheme["accent"])
            
            # 내용 요소 목록 (flowables)
            elements = []
            
            # 로고 추가 (있는 경우)
            if self.company_logo and os.path.exists(self.company_logo):
                logo = Image(self.company_logo, width=150, height=50)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 10))
            
            # 제목
            title_style = styles["KoreanTitle"] if "KoreanTitle" in styles else styles["Title"]
            elements.append(Paragraph(report["title"], title_style))
            elements.append(Spacer(1, 10))
            
            # 생성일
            date_str = datetime.fromisoformat(report["date"]).strftime('%Y년 %m월 %d일')
            date_style = styles["Korean"] if "Korean" in styles else styles["Normal"]
            elements.append(Paragraph(f"생성일: {date_str}", date_style))
            elements.append(Spacer(1, 20))
            
            # 투자 결정 요약
            decision_style = styles["KoreanHeading1"] if "KoreanHeading1" in styles else styles["Heading1"]
            elements.append(Paragraph("투자 결정 요약", decision_style))
            
            # 투자 결정 테이블
            decision_data = [
                ["결정", "확신도"],
                [report["investment_decision"], f"{report['confidence']}%"]
            ]
            
            decision_table = Table(decision_data, colWidths=[200, 200])
            decision_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.HexColor(self.color_scheme["primary"])),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (1, 1), colors.HexColor(
                    self.color_scheme["success"] if report["investment_decision"] == "투자" else self.color_scheme["warning"]
                )),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(decision_table)
            elements.append(Spacer(1, 20))
            
            # 추천 요약
            summary_style = styles["KoreanHeading2"] if "KoreanHeading2" in styles else styles["Heading2"]
            elements.append(Paragraph("요약", summary_style))
            
            normal_style = styles["Korean"] if "Korean" in styles else styles["Normal"]
            elements.append(Paragraph(report["recommendation_summary"], normal_style))
            elements.append(Spacer(1, 15))
            
            # 차트 추가 (점수 비교)
            if report["charts"]["scores"] and os.path.exists(report["charts"]["scores"]):
                img = Image(report["charts"]["scores"], width=400, height=300)
                img.hAlign = 'CENTER'
                elements.append(img)
                elements.append(Spacer(1, 10))
            
            # 시장성 분석
            elements.append(PageBreak())
            elements.append(Paragraph("시장성 분석", summary_style))
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(report["market_analysis_summary"], normal_style))
            elements.append(Spacer(1, 15))
            
            # 기술 분석
            elements.append(Paragraph("기술 분석", summary_style))
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(report["technology_analysis_summary"], normal_style))
            elements.append(Spacer(1, 15))
            
            # 경쟁사 분석
            elements.append(Paragraph("경쟁사 분석", summary_style))
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(report["competitor_analysis_summary"], normal_style))
            elements.append(Spacer(1, 15))
            
            # 차트 추가 (시장 점유율)
            if report["charts"]["market_share"] and os.path.exists(report["charts"]["market_share"]):
                img = Image(report["charts"]["market_share"], width=400, height=300)
                img.hAlign = 'CENTER'
                elements.append(img)
                elements.append(Spacer(1, 10))
            
            # 창업자 분석
            elements.append(PageBreak())
            elements.append(Paragraph("창업자 분석", summary_style))
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(report["founder_analysis_summary"], normal_style))
            elements.append(Spacer(1, 15))
            
            # 투자 이유
            elements.append(Paragraph("투자 이유", summary_style))
            elements.append(Spacer(1, 10))
            
            # 리스트 항목으로 투자 이유 추가
            if report["investment_reasons"]:
                reason_items = []
                for reason in report["investment_reasons"]:
                    reason_items.append(ListItem(Paragraph(reason, normal_style)))
                
                reasons_list = ListFlowable(
                    reason_items,
                    bulletType='bullet',
                    leftIndent=20,
                    bulletFontName='Helvetica',
                    bulletFontSize=10
                )
                elements.append(reasons_list)
                elements.append(Spacer(1, 15))
            
            # 탈락 기업 정보 (있는 경우)
            if report.get("rejected_startups"):
                elements.append(PageBreak())
                elements.append(Paragraph("탈락 기업 분석", summary_style))
                elements.append(Spacer(1, 10))
                
                for idx, rejected in enumerate(report["rejected_startups"]):
                    elements.append(Paragraph(f"{idx+1}. {rejected.get('name', '기업명 없음')}", styles["Heading3"]))
                    elements.append(Spacer(1, 5))
                    
                    if "score" in rejected:
                        elements.append(Paragraph(f"점수: {rejected['score']}/100", normal_style))
                        elements.append(Spacer(1, 5))
                    
                    if "rejection_reasons" in rejected:
                        elements.append(Paragraph("탈락 이유:", normal_style))
                        
                        reason_items = []
                        for reason in rejected["rejection_reasons"]:
                            reason_items.append(ListItem(Paragraph(reason, normal_style)))
                        
                        reasons_list = ListFlowable(
                            reason_items,
                            bulletType='bullet',
                            leftIndent=20,
                            bulletFontName='Helvetica',
                            bulletFontSize=10
                        )
                        elements.append(reasons_list)
                        elements.append(Spacer(1, 10))
            
            # PDF 생성
            doc.build(elements)
            
            # 임시 파일 정리
            self._cleanup_temp_files(report)
            
            return output_path
        except Exception as e:
            logging.error(f"PDF 생성 중 오류 발생: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return None
    
    def _cleanup_temp_files(self, report: Dict[str, Any]):
        """임시 생성된 차트 파일 정리"""
        temp_dir = os.path.join(self.output_dir, "temp")
        if os.path.exists(temp_dir):
            for chart in [report["charts"]["market_share"], report["charts"]["scores"]]:
                if chart and os.path.exists(chart):
                    try:
                        os.remove(chart)
                    except:
                        pass
                
            try:
                if len(os.listdir(temp_dir)) == 0:
                    os.rmdir(temp_dir)
            except:
                pass
    
    def generate_recommendation_summary(self, 
                                       startup_data: Dict[str, Any], 
                                       market_analysis: Dict[str, Any], 
                                       tech_analysis: Dict[str, Any],
                                       founder_analysis: Dict[str, Any],
                                       investment_decision: Dict[str, Any]) -> str:
        """
        종합 추천 요약 생성
        
        Args:
            startup_data: 스타트업 정보
            market_analysis: 시장성 분석 정보
            tech_analysis: 기술력 분석 정보
            founder_analysis: 창업자 분석 정보
            investment_decision: 투자 결정 정보
            
        Returns:
            추천 요약 문자열
        """
        # 주요 정보 추출
        company_name = startup_data.get("name", "해당 기업")
        description = startup_data.get("description", "")
        market_size = market_analysis.get("market_size", "정보 없음")
        market_growth = market_analysis.get("growth_rate", 0)
        market_score = market_analysis.get("score", 0)
        tech_score = tech_analysis.get("score", 0)
        founder_score = founder_analysis.get("score", 0)
        investment_status = investment_decision.get("decision", "보류")
        confidence = investment_decision.get("confidence", 0)
        
        # 요약 생성
        summary = f"{company_name}({description})은 "
        
        if investment_status == "투자":
            summary += f"투자 추천 기업입니다. 시장 규모는 {market_size}이며, 연간 성장률은 {market_growth}%로 성장성이 높습니다. "
            
            if tech_score >= 80:
                summary += "기술력이 우수하며 "
            elif tech_score >= 60:
                summary += "기술력이 양호하며 "
            else:
                summary += "기술력 보완이 필요하나 "
                
            if founder_score >= 80:
                summary += "창업자의 역량이 뛰어납니다. "
            elif founder_score >= 60:
                summary += "창업자의 역량이 검증되었습니다. "
            else:
                summary += "창업자 역량 보완이 필요합니다. "
                
            summary += f"종합적으로 {confidence}% 확신도로 투자를 권장합니다."
        else:
            summary += f"투자 보류 기업입니다. "
            
            if market_score < 60:
                summary += f"시장 성장성이 제한적이며({market_growth}%), "
            
            if tech_score < 60:
                summary += "기술력이 부족하고 "
            
            if founder_score < 60:
                summary += "창업자 역량이 검증되지 않았습니다. "
                
            summary += f"종합적으로 {confidence}% 확신도로 투자를 보류합니다."
        
        return summary
    
    def generate_report(self, 
                      startup_data: Dict[str, Any],
                      market_analysis: Dict[str, Any],
                      tech_analysis: Dict[str, Any],
                      competitor_analysis: Dict[str, Any],
                      investment_decision: Dict[str, Any],
                      founder_analysis: Optional[Dict[str, Any]] = None,
                      output_pdf_path: Optional[str] = None) -> Dict[str, Any]:
        """
        투자 보고서 생성 통합 메서드
        
        Args:
            startup_data: 스타트업 정보
            market_analysis: 시장성 분석 정보
            tech_analysis: 기술력 분석 정보
            competitor_analysis: 경쟁사 분석 정보
            investment_decision: 투자 결정 정보
            founder_analysis: 창업자 분석 정보 (선택적)
            output_pdf_path: 출력 PDF 파일 경로 (선택적)
            
        Returns:
            생성된 보고서 정보를 포함하는 딕셔너리
        """
        # 창업자 분석 정보가 없는 경우 기본값 설정
        if founder_analysis is None:
            founder_analysis = {
                "experience": "정보 없음",
                "expertise": "정보 없음",
                "score": 0.0,
                "summary": "창업자 정보가 제공되지 않았습니다."
            }
        
        # 차트 생성
        market_share_chart = self._create_pie_chart(
            competitor_analysis["market_share"],
            "시장 점유율 분석",
            "market_share_chart.png"
        )
        
        scores_data = {
            "시장성": market_analysis["score"],
            "기술력": tech_analysis["score"],
            "창업자": founder_analysis.get("score", 0.0)
        }
        scores_chart = self._create_bar_chart(
            scores_data,
            "평가 점수 비교",
            xlabel="평가 항목",
            ylabel="점수",
            filename="scores_chart.png"
        )
        
        # 종합 추천 요약 생성
        recommendation_summary = self.generate_recommendation_summary(
            startup_data,
            market_analysis,
            tech_analysis,
            founder_analysis,
            investment_decision
        )
        
        # 보고서 데이터 생성
        report_data = {
            "title": f"{startup_data['name']} 투자 분석 보고서",
            "date": datetime.now().isoformat(),
            "selected_startup_name": startup_data["name"],
            "investment_decision": investment_decision["decision"],
            "confidence": investment_decision["confidence"],
            "recommendation_summary": recommendation_summary,
            "market_analysis_summary": market_analysis["summary"],
            "technology_analysis_summary": tech_analysis["summary"],
            "competitor_analysis_summary": competitor_analysis["summary"],
            "founder_analysis_summary": founder_analysis["summary"],
            "investment_reasons": investment_decision["reasons"],
            "charts": {
                "market_share": market_share_chart,
                "scores": scores_chart
            },
            "rejected_startups": []  # 선택적으로 탈락 기업 정보 추가 가능
        }
        
        # PDF 보고서 생성
        pdf_path = self.create_reportlab_pdf(report_data, output_pdf_path)
        
        # 결과 딕셔너리 생성
        result = {
            "pdf_path": pdf_path,
            "report_data": report_data
        }
        
        return result