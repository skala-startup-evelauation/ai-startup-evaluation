from founder_agent.founder_eval_agent import evaluate_founder


def main():
    startup_name = input("스타트업 이름: ").strip()
    founder_name = input("창업자 이름 (모르면 Enter): ").strip() or None

    result = evaluate_founder(startup_name, founder_name)
    
    # FounderInfo 객체 출력
    print("\n===== 창업자 평가 결과 =====")
    print(f"대표자명: {result.name}")
    print(f"학력: {result.education}")
    print(f"경력: {result.career}")
    print(f"리스크: {result.risk_factors}")
    print(f"주요 강점: {result.key_strengths}")


if __name__ == "__main__":
    main()
