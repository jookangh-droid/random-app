import pandas as pd
import streamlit as st

st.set_page_config(page_title="스마트 용돈 관리 앱", page_icon="💰")

# 1. 상태 저장을 위한 session_state 초기화
if "saved_money" not in st.session_state:
    st.session_state.saved_money = 0
if "savings_decided" not in st.session_state:
    st.session_state.savings_decided = False

st.title("💰 나만의 용돈 관리 앱")

# ==========================================
# 1. 하루 평균 & 월 평균 목표 금액 설정 (리스트 + 직접 입력)
# ==========================================
st.header("1. 목표 소비 금액 설정")

col1, col2 = st.columns(2)

with col1:
    daily_options = [5000, 10000, 15000, 20000, "직접 입력"]
    selected_daily = st.selectbox("하루 평균 쓰는 돈(목표) 선택", daily_options)

    if selected_daily == "직접 입력":
        daily_budget = st.number_input(
            "하루 목표 금액 입력 (원)", min_value=0, step=1000, value=10000
        )
    else:
        daily_budget = selected_daily

with col2:
    monthly_options = [100000, 200000, 300000, 500000, "직접 입력"]
    selected_monthly = st.selectbox(
        "월 평균 쓰는 돈(목표) 선택", monthly_options
    )

    if selected_monthly == "직접 입력":
        monthly_budget = st.number_input(
            "월 목표 금액 입력 (원)", min_value=0, step=10000, value=300000
        )
    else:
        monthly_budget = selected_monthly

st.info(
    f"설정된 목표: 하루 **{daily_budget:,}원** / 한 달 **{monthly_budget:,}원**"
)

st.divider()

# ==========================================
# 2. 쓴 돈을 매개변수로 받아 경고/잔여 금액을 알려주는 함수
# ==========================================
st.header("2. 소비 금액 실시간 점검")


def check_spending_status(spent_amount, limit_amount, period_name):
    """쓴 돈을 매개변수로 받아 기준 금액 초과 여부 및 잔여 금액을 출력하는 함수"""
    diff = limit_amount - spent_amount
    if diff < 0:
        st.error(
            f"🚨 [{period_name} 기준] **{abs(diff):,}원을 초과했습니다!** 지출을 줄여야 해요."
        )
    else:
        st.success(
            f"✅ [{period_name} 기준] 목표 금액까지 **{diff:,}원** 남았습니다."
        )


tab1, tab2 = st.tabs(["오늘 쓴 돈 점검", "이번 달 누적 지출 점검"])

with tab1:
    today_spent = st.number_input(
        "오늘 쓴 돈을 입력하세요 (원)", min_value=0, step=500, key="today_input"
    )
    if st.button("오늘 지출 확인"):
        check_spending_status(today_spent, daily_budget, "하루 평균")

with tab2:
    month_spent_now = st.number_input(
        "이번 달 현재까지 쓴 돈을 입력하세요 (원)",
        min_value=0,
        step=5000,
        key="month_input",
    )
    if st.button("이번 달 지출 확인"):
        check_spending_status(month_spent_now, monthly_budget, "월 평균")

st.divider()

# ==========================================
# 3. 한 달 결산 (재입력, 초과/여유분 계산, 저축 여부 질문)
# ==========================================
st.header("3. 한 달 결산 및 저축하기")
st.write(
    "한 달이 끝났습니다! 이번 달 실제 평균 지출을 다시 입력해 결산해 보세요."
)

col3, col4 = st.columns(2)
with col3:
    actual_daily_avg = st.number_input(
        "실제 하루 평균 쓴 돈 (원)", min_value=0, step=1000, value=daily_budget
    )
with col4:
    actual_monthly_spent = st.number_input(
        "실제 한 달 동안 쓴 총 금액 (원)",
        min_value=0,
        step=10000,
        value=monthly_budget,
    )

monthly_diff = monthly_budget - actual_monthly_spent
daily_diff = daily_budget - actual_daily_avg

# 결과 안내
if monthly_diff > 0:
    st.subheader(f"🎉 축하합니다! 이번 달 예산을 **{monthly_diff:,}원** 아꼈어요.")
    st.write(
        f"(하루 평균 기준으로도 매일 **{daily_diff:,}원**씩 덜 썼거나 여유가 있습니다.)"
    )

    # 더 쓸 수 있는 돈이 있을 때 저축 여부 물어보기
    save_choice = st.radio(
        f"남은 돈 {monthly_diff:,}원을 저축하시겠습니까?",
        ["선택하세요", "예, 저축할래요!", "아니요, 다음 달에 쓸래요."],
    )

    if save_choice == "예, 저축할래요!":
        if st.button("저축 확정하기"):
            st.session_state.saved_money += monthly_diff
            st.balloons()
            st.success(
                f"💰 {monthly_diff:,}원이 저축되었습니다! (현재 총 누적 저축액: **{st.session_state.saved_money:,}원**)"
            )
    elif save_choice == "아니요, 다음 달에 쓸래요.":
        st.info(
            f"다음 달 예산에 {monthly_diff:,}원을 보태어 더 여유롭게 사용할 수 있습니다!"
        )

elif monthly_diff < 0:
    st.subheader(
        f"😥 이번 달 예산을 **{abs(monthly_diff):,}원** 초과해서 썼어요."
    )
    st.write(
        f"다음 달에는 목표를 지키기 위해 한 달에 **{abs(monthly_diff):,}원**을 덜 써야 합니다."
    )
else:
    st.subheader("👏 목표한 월 예산과 딱 맞게 사용하셨습니다!")

st.divider()

# ==========================================
# 4. for 반복문을 이용한 기간별 조정 금액 표 출력
# ==========================================
st.header("4. 다음 달 소비 가이드 표 (반복문 활용)")
st.write(
    "이번 달 결산 결과를 바탕으로, 기간별로 얼마를 더 쓰거나 덜 써야 하는지 계산한 표입니다."
)

# 기간별 일수 정의 (1일, 1주일, 2주일, 1달)
periods = [("1일 (하루)", 1), ("7일 (1주일)", 7), ("15일 (보름)", 15), ("30일 (한 달)", 30)]

table_data = []
# 하루 평균 차액을 기준으로 기간별 금액을 for문으로 계산
daily_adjustment = monthly_diff / 30

for period_label, days in periods:
    amount = int(daily_adjustment * days)

    if amount > 0:
        status = f"➕ {amount:,}원 더 쓸 수 있음 (여유)"
    elif amount < 0:
        status = f"➖ {abs(amount):,}원 덜 써야 함 (절약 필요)"
    else:
        status = "0원 (현재 유지)"

    table_data.append(
        {"기간": period_label, "조정 가능 금액": f"{amount:,}원", "소비 가이드": status}
    )

# 표 형태로 화면에 출력
df = pd.DataFrame(table_data)
st.table(df)
