"""9주차 과제: 나만의 데이터 분석 대시보드.

수업 코드 활용: st.title, st.write, np.random.randn, pd.DataFrame, st.line_chart.
응용 기능: 입력 위젯, 데이터 표, 요약 통계, 그래프 선택, CSV 저장.

필요한 패키지: streamlit, pandas, numpy
실행: python -m streamlit run streamlit_app_final.py
GitHub에 이 파일과 requirements.txt를 올리면 별도 자료 파일 없이 배포 가능.
"""

import streamlit as st
import pandas as pd
import numpy as np


def make_sample_data(row_count):
    """수업의 20행·3열 데이터 예제를 사용자가 지정한 행 수로 확장한다."""
    data = pd.DataFrame(
        np.random.randn(row_count, 3),
        columns=["A", "B", "C"],
    )
    data.index = pd.RangeIndex(1, row_count + 1, name="번호")
    return data


def main():
    # [수업 응용] 웹페이지 설정과 화면 제목.
    st.set_page_config(
        page_title="나만의 데이터 분석 대시보드",
        page_icon="📊",
        layout="wide",
    )

    # [수업 코드] 웹 화면에 제목과 설명 출력.
    st.title("📊 나만의 데이터 분석 대시보드")
    st.write(
        "NumPy로 데이터를 만들고, Pandas로 정리한 뒤 "
        "Streamlit으로 표와 그래프를 보여주는 웹앱입니다."
    )
    st.caption("A·B·C는 무작위로 생성한 학습용 데이터이며 실제 조사 자료가 아닙니다.")

    # [수업 응용] 왼쪽 메뉴의 입력으로 화면을 바꾼다.
    st.sidebar.title("분석 설정")
    row_count = st.sidebar.slider(
        "데이터 개수", min_value=10, max_value=100, value=20, step=10
    )
    new_data = st.sidebar.button("새 데이터 생성")
    st.sidebar.caption("새 데이터 생성 또는 데이터 개수 변경 시에만 값이 바뀝니다.")

    # [수업 응용] 선택 메뉴를 바꿀 때마다 원본 데이터가 바뀌지 않도록 보관.
    # 각 접속자의 세션에만 보관되며, 외부 서버나 파일에는 저장하지 않는다.
    if (
        "sample_data_ch9" not in st.session_state
        or len(st.session_state["sample_data_ch9"]) != row_count
        or new_data
    ):
        st.session_state["sample_data_ch9"] = make_sample_data(row_count)

    data = st.session_state["sample_data_ch9"]

    selected_columns = st.sidebar.multiselect(
        "분석할 항목", options=["A", "B", "C"], default=["A", "B", "C"]
    )
    start, end = st.sidebar.slider(
        "표시할 데이터 번호",
        min_value=1,
        max_value=row_count,
        value=(1, row_count),
    )
    chart_type = st.sidebar.selectbox(
        "그래프 종류", ["선 그래프", "막대 그래프", "영역 그래프"]
    )
    show_table = st.sidebar.checkbox("데이터 표 보기", value=True)
    show_statistics = st.sidebar.checkbox("요약 통계 보기", value=True)

    # 아무 항목도 선택하지 않았을 때 오류 대신 안내한다.
    if not selected_columns:
        st.warning("왼쪽에서 A, B, C 중 분석할 항목을 하나 이상 선택해 주세요.")
        return

    # [수업 코드 응용] DataFrame에서 사용자가 선택한 행과 열을 가져온다.
    selected_data = data.loc[start:end, selected_columns]

    # [수업 응용] 현재 분석 범위를 숫자로 요약한다.
    first, second, third = st.columns(3)
    first.metric("표시 데이터 수", f"{len(selected_data)}개")
    second.metric("선택한 항목 수", f"{len(selected_columns)}개")
    third.metric("선택 데이터 전체 평균", f"{selected_data.to_numpy().mean():.2f}")

    st.subheader("1. 데이터 시각화")
    st.write(
        f"{start}번부터 {end}번까지의 데이터 · "
        f"분석 항목: {', '.join(selected_columns)}"
    )

    # [수업 코드] 기본 화면은 수업의 st.line_chart를 그대로 활용한다.
    if chart_type == "선 그래프":
        st.line_chart(selected_data)
    # [수업 응용] 같은 데이터를 다른 형태의 그래프로 비교한다.
    elif chart_type == "막대 그래프":
        st.bar_chart(selected_data)
    else:
        st.area_chart(selected_data)

    if show_table:
        st.subheader("2. 데이터 표")
        st.write("그래프에 표시된 값을 표로 확인할 수 있습니다.")
        st.dataframe(selected_data)

    if show_statistics:
        st.subheader("3. 항목별 요약 통계")
        # 원본 값은 유지하고, 화면에 보여줄 통계 값만 소수 둘째 자리로 표시.
        statistics = pd.DataFrame(
            {
                "평균": selected_data.mean(),
                "최솟값": selected_data.min(),
                "최댓값": selected_data.max(),
            }
        )
        statistics.index.name = "항목"
        st.dataframe(statistics.round(2))
        st.write("평균이 가장 높은 항목:", statistics["평균"].idxmax())

    st.subheader("4. 분석 데이터 저장")
    st.write("현재 선택한 항목과 범위의 원본 값을 CSV 파일로 저장합니다.")
    # Excel에서도 한글 '번호'가 깨지지 않도록 UTF-8 BOM을 포함한다.
    csv_data = selected_data.to_csv(index=True).encode("utf-8-sig")
    st.download_button(
        label="선택한 데이터 CSV 다운로드",
        data=csv_data,
        file_name="my_dashboard_data.csv",
        mime="text/csv",
    )

    with st.expander("사용 방법과 수업 코드 활용"):
        st.write("① 왼쪽에서 데이터 개수와 A·B·C 항목을 선택합니다.")
        st.write("② 표시할 데이터 번호와 그래프 종류를 바꿔 봅니다.")
        st.write("③ 표와 요약 통계를 확인하고, 필요한 데이터를 저장합니다.")
        st.write("④ 다른 값으로 비교하려면 '새 데이터 생성' 버튼을 누릅니다.")
        st.write(
            "수업 코드의 흐름: np.random.randn → pd.DataFrame → st.line_chart. "
            "여기에 입력 위젯, 통계, CSV 저장을 응용 기능으로 추가했습니다."
        )


if __name__ == "__main__":
    main()
