import pandas as pd
import streamlit as st

st.set_page_config(page_title="스마트 용돈 관리 앱", page_icon="💰")

# ==========================================
# 0. 상태 저장을 위한 session_state 초기화
# ==========================================
if "saved_money" not in st.session_state:
    st.session_state.saved_money = 0
if "expense_records" not in st.session_state:
    # 기본 예시 데이터를 넣어두어 처음 실행해도 화면 구성을 바로 확인할 수 있습니다.
    st.session_state.expense_records = [
        {"구분": "오늘 지출", "항목": "음식 (식비/간식)", "금액": 8500, "메모": "점심 및 편의점 간식"},
        {"구분": "오늘 지출", "항목": "여가 생활", "금액": 12000, "메모": "영화 예매"},
        {"구분": "이번 달 누적", "항목": "교통/통신", "금액": 35000, "메모": "교통카드 충전"},
    ]

st.title("💰 나만의 용돈 관리 앱")

# ==========================================
# 1. 하루 평균 & 월 평균 목표 금액 설정
# ==========================================
st.header("1. 목표 소비 금액 설정")

col1, col2 = st.columns(2)

with col1:
    daily_options = [5000, 10000, 15000, 20000, "직접 입력"]
    selected_daily = st.selectbox("하루 평균 쓰는 돈(목표) 선택", daily_options)
    if selected_daily == "직접 입력":
        daily_budget = st.number_input("하루 목표 금액 입력 (원)", min_value=0, step=1000, value=10000)
    else:
        daily_budget = selected_daily

with col2:
    monthly_options = [100000, 200000, 300000, 500000, "직접 입력"]
    selected_monthly = st.selectbox("월 평균 쓰는 돈(목표) 선택", monthly_options)
    if selected_monthly == "직접 입력":
        monthly_budget = st.number_input("월 목표 금액 입력 (원)", min_value=0, step=10000, value=300000)
    else:
        monthly_budget = selected_monthly

st.info(f"설정된 목표: 하루 **{daily_budget:,}원** / 한 달 **{monthly_budget:,}원**")

st.divider()

# ==========================================
# 2. 항목별 지출 기록 및 실시간 한도 점검
# ==========================================
st.header("2. 항목별 지출 기록 및 실시간 점검")

def check_spending_status(spent_amount, limit_amount, period_name):
    """쓴 돈을 매개변수로 받아 기준 금액 초과 여부 및 잔여 금액을 출력하는 함수"""
    diff = limit_amount - spent_amount
    if diff < 0:
        st.error(f"🚨 [{period_name} 기준] **{abs(diff):,}원을 초과했습니다!** 지출을 줄여야 해요.")
    else:
        st.success(f"✅ [{period_name} 기준] 목표 금액까지 **{diff:,}원** 남았습니다.")

categories = ["음식 (식비/간식)", "여가 생활", "쇼핑/의류", "교통/통신", "학용품/도서", "기타"]

col_cat1, col_cat2 = st.columns(2)
with col_cat1:
    period_type = st.radio("기록 구분", ["오늘 지출", "이번 달 누적"], horizontal=True)
    selected_category = st.selectbox("어디에 쓰셨나요? (항목 선택)", categories)

with col_cat2:
    spent_input = st.number_input("쓴 금액을 입력하세요 (원)", min_value=0, step=500, value=5000)
    memo_input = st.text_input("간단한 메모 (예: 떡볶이, PC방 등)", placeholder="내용을 입력하세요")

if st.button("지출 기록 추가 및 한도 확인", use_container_width=True):
    if spent_input > 0:
        # 내역 리스트에 추가
        st.session_state.expense_records.append({
            "구분": period_type,
            "항목": selected_category,
            "금액": spent_input,
            "메모": memo_input if memo_input else "-"
        })
        
        # 해당 구분의 총합 계산 후 매개변수로 전달하여 점검
        total_for_period = sum(
            item["금액"] for item in st.session_state.expense_records if item["구분"] == period_type
        )
        limit_to_check = daily_budget if period_type == "오늘 지출" else monthly_budget
        check_spending_status(total_for_period, limit_to_check, period_type)
    else:
        st.warning("0원보다 큰 금액을 입력해 주세요.")

st.divider()

# ==========================================
# 3. 어디에 얼마 썼는지 한눈에 보기 (내역 표 + 막대 그래프)
# ==========================================
st.header("3. 어디에 얼마 썼을까? (지출 분석)")

if st.session_state.expense_records:
    df_expenses = pd.DataFrame(st.session_state.expense_records)
    
    tab_chart, tab_list = st.tabs(["📊 항목별 지출 합계 (그래프 & 표)", "📝 상세 지출 내역서"])
    
    with tab_chart:
        # 항목별로 그룹화하여 총 얼마를 썼는지 계산
        category_summary = df_expenses.groupby("항목")["금액"].sum().reset_index()
        category_summary = category_summary.sort_values(by="금액", ascending=False)
        
        # 막대 그래프로 시각화
        st.bar_chart(category_summary.set_index("항목")["금액"])
        
        # 항목별 합계 금액 및 비율 계산
        total_all_spent = category_summary["금액"].sum()
        category_summary["비중 (%)"] = (category_summary["금액"] / total_all_spent * 100).round(1)
        category_summary["총 지출액"] = category_summary["금액"].apply(lambda x: f"{x:,}원")
        
        st.table(category_summary[["항목", "총 지출액", "비중 (%)"]])
        st.write(f"👉 **현재 기록된 총 지출 합계:** {total_all_spent:,}원")

    with tab_list:
        df_display = df_expenses.copy()
        df_display["금액"] = df_display["금액"].apply(lambda x: f"{x:,}원")
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        if st.button("지출 내역 모두 초기화"):
            st.session_state.expense_records = []
            st.rerun()
else:
    st.write("아직 기록된 지출 내역이 없습니다. 위에서 지출을 추가해 보세요!")

st.divider()

# ==========================================
# 4. 한 달 결산 (재입력, 초과/여유분 계산, 저축 여부 질문)
# ==========================================
st.header("4. 한 달 결산 및 저축하기")
st.write("한 달이 끝났습니다! 이번 달 실제 평균 지출을 입력해 결산해 보세요.")

# 위에서 기록한 총 지출액을 기본값으로 자동 반영
recorded_total = sum(item["금액"] for item in st.session_state.expense_records)

col3, col4 = st.columns(2)
with col3:
    actual_daily_avg = st.number_input("실제 하루 평균 쓴 돈 (원)", min_value=0, step=1000, value=int(recorded_total / 30) if recorded_total > 0 else daily_budget)
with col4:
    actual_monthly_spent = st.number_input("실제 한 달 동안 쓴 총 금액 (원)", min_value=0, step=10000, value=recorded_total if recorded_total > 0 else monthly_budget)

monthly_diff = monthly_budget - actual_monthly_spent
daily_diff = daily_budget - actual_daily_avg

if monthly_diff > 0:
    st.subheader(f"🎉 축하합니다! 이번 달 예산을 **{monthly_diff:,}원** 아꼈어요.")
    st.write(f"(하루 평균 기준으로도 매일 **{daily_diff:,}원**씩 덜 썼거나 여유가 있습니다.)")
    
    save_choice = st.radio(
        f"남은 돈 {monthly_diff:,}원을 저축하시겠습니까?",
        ["선택하세요", "예, 저축할래요!", "아니요, 다음 달에 쓸래요."]
    )
    
    if save_choice == "예, 저축할래요!":
        if st.button("저축 확정하기"):
            st.session_state.saved_money += monthly_diff
            st.balloons()
            st.success(f"💰 {monthly_diff:,}원이 저축되었습니다! (현재 총 누적 저축액: **{st.session_state.saved_money:,}원**)")
    elif save_choice == "아니요, 다음 달에 쓸래요.":
        st.info(f"다음 달 예산에 {monthly_diff:,}원을 보태어 더 여유롭게 사용할 수 있습니다!")

elif monthly_diff < 0:
    st.subheader(f"😥 이번 달 예산을 **{abs(monthly_diff):,}원** 초과해서 썼어요.")
    st.write(f"다음 달에는 목표를 지키기 위해 한 달에 **{abs(monthly_diff):,}원**을 덜 써야 합니다.")
else:
    st.subheader("👏 목표한 월 예산과 딱 맞게 사용하셨습니다!")

st.divider()

# ==========================================
# 5. for 반복문을 이용한 기간별 조정 금액 표 출력
# ==========================================
st.header("5. 다음 달 소비 가이드 표 (반복문 활용)")
st.write("이번 달 결산 결과를 바탕으로, 기간별로 얼마를 더 쓰거나 덜 써야 하는지 계산한 표입니다.")

periods = [("1일 (하루)", 1), ("7일 (1주일)", 7), ("15일 (보름)", 15), ("30일 (한 달)", 30)]
table_data = []
daily_adjustment = monthly_diff / 30

for period_label, days in periods:
    amount = int(daily_adjustment * days)
    if amount > 0:
        status = f"➕ {amount:,}원 더 쓸 수 있음 (여유)"
    elif amount < 0:
        status = f"➖ {abs(amount):,}원 덜 써야 함 (절약 필요)"
    else:
        status = "0원 (현재 유지)"
        
    table_data.append({
        "기간": period_label,
        "조정 가능 금액": f"{amount:,}원",
        "소비 가이드": status
    })

df_guide = pd.DataFrame(table_data)
st.table(df_guide)
