# streamlit run app.py
import streamlit as st
import pandas as pd
import altair as alt

# -------------------- 페이지/스타일 --------------------
st.set_page_config(
    page_title="특구 옵저버",
    page_icon="📊",
    layout="wide"
)


# 글로벌 Altair 테마(폰트/색/그리드)
alt.themes.enable("opaque")

PRIMARY   = "#2E69FF"
SECONDARY = "#7B8AB8"
ACCENT    = "#FF7A59"
NEUTRAL   = "#F5F7FB"
BAR_A     = "#4C72B0"  # 입주기업
BAR_B     = "#C44E52"  # 연구소기업
BAR_C     = "#937860"  # 전환율

# 공통 CSS
st.markdown(
    f"""
    <style>
    /* 전체 폰트/여백 */
    .main .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }}
    /* KPI 카드 느낌 */
    .metric-card {{
        background: {NEUTRAL};
        border: 1px solid #E6EAF2;
        padding: 16px 18px;
        border-radius: 14px;
        text-align: center;
    }}
    .metric-caption {{
        font-size: 13px; color: #6E7786; margin-top: 4px;
    }}
    /* 표 가독성 */
    .stDataFrame tbody tr td {{
        font-size: 0.95rem;
        padding-top: 6px; padding-bottom: 6px;
    }}
    /* 구분선 */
    hr {{
        margin: 0.8rem 0 1.2rem 0; border-color: #E6EAF2;
    }}
    /* 작은 배지 */
    .badge {{
        display: inline-block; padding: 4px 8px; border-radius: 999px;
        background: #EEF2F8; color: #41536B; font-size: 12px; margin-right: 6px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------- 파일 경로 --------------------
PATH_FIRMS = "(재)연구개발특구진흥재단_특구입주기업현황_20250825.csv"     # 번호,지역,기관명,지구
PATH_LABS  = "(재)연구개발특구진흥재단_연구소기업 운영현황_20250731.csv"  # 구분,기업명,사업자등록번호,등록연도,현행특구,강소특구여부

# -------------------- 유틸 --------------------
def read_csv_kr(path):
    for enc in ["utf-8-sig", "cp949", "utf-8"]:
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception:
            continue
    return pd.read_csv(path)

def norm_name(s):
    if pd.isna(s): return ""
    s = str(s).upper().strip()
    for t in ["(주)", "㈜", "주식회사"]:
        s = s.replace(t, "")
    s = s.replace(" ", "")
    return s

# -------------------- 데이터 로드 --------------------
firms = read_csv_kr(PATH_FIRMS)  # 번호, 지역, 기관명, 지구
labs  = read_csv_kr(PATH_LABS)   # 구분, 기업명, 사업자등록번호, 등록연도, 현행특구, 강소특구여부

# 최소 컬럼 방어
need_f = {"지역","기관명","지구"}
need_l = {"기업명","등록연도","현행특구","강소특구여부"}
assert need_f.issubset(set(firms.columns)), f"입주기업 파일 컬럼 확인 필요: {need_f}"
assert need_l.issubset(set(labs.columns)),  f"연구소기업 파일 컬럼 확인 필요: {need_l}"

# 정규화
firms["기업명_norm"] = firms["기관명"].apply(norm_name)
labs["기업명_norm"]  = labs["기업명"].apply(norm_name)

# 등록연도 숫자 변환(안전 캐스팅)
labs["등록연도"] = pd.to_numeric(labs["등록연도"], errors="coerce").astype("Int64")

# -------------------- 헤더 --------------------
left, right = st.columns([0.75, 0.25])
with left:
    st.markdown("### 📊 특구 인사이트 정보제공")
    st.caption("입주기업 & 연구소기업 **빠른 조회 + 데이터 분석 3종**")
with right:
    st.markdown(
        '<div style="text-align:right;">'
        '<span class="badge">조회 중심</span>'
        '<span class="badge">경량</span>'
        '<span class="badge">정책 활용</span>'
        '</div>',
        unsafe_allow_html=True
    )
st.markdown("<hr/>", unsafe_allow_html=True)
import inspect
# -------------------- 사이드바(통합 필터) --------------------
# ▼ 이 줄을 st.sidebar.header("사용자 요구사항") 보다 위에 넣으세요.
with st.sidebar:
    # st.image가 use_container_width를 지원하는지 체크
    if "use_container_width" in inspect.signature(st.image).parameters:
        st.image("로고.png", use_container_width=True)
    else:
        st.image("로고.png", use_column_width=True)  # 구버전 호환
    st.markdown("<hr/>", unsafe_allow_html=True)

st.sidebar.header("사용자 요구사항")
regions_all = sorted(
    set(firms["지역"].dropna().astype(str)) |
    set(labs["현행특구"].dropna().astype(str))
)
sel_region = st.sidebar.selectbox("지역/특구", ["전체"] + regions_all, index=0)

# 지구 목록(입주기업 기준)
if sel_region != "전체":
    firms_base = firms[firms["지역"] == sel_region]
else:
    firms_base = firms
zones = ["전체"] + sorted(firms_base["지구"].dropna().unique().tolist())
sel_zone = st.sidebar.selectbox("지구(입주기업)", zones, index=0)

keyword = st.sidebar.text_input("기업명 키워드", "")

# -------------------- KPI 카드 --------------------
m1, m2, m3 = st.columns(3)
with m1:
    # st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("입주기업 수", f"{len(firms):,}")
    st.markdown('<div class="metric-caption">입주기업 총계</div></div>', unsafe_allow_html=True)

with m2:
    # st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("연구소기업 수", f"{len(labs):,}")
    st.markdown('<div class="metric-caption">연구소기업 총계</div></div>', unsafe_allow_html=True)

with m3:
    lab_set = set(labs["기업명_norm"])
    conv_ratio = (firms["기업명_norm"].isin(lab_set)).mean() if len(firms) else 0
    # st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("전환 비율(참고)", f"{conv_ratio*100:.1f}%")
    st.markdown('<div class="metric-caption">이름기반 매칭(참고용)</div></div>', unsafe_allow_html=True)

st.markdown("<hr/>", unsafe_allow_html=True)

# -------------------- 탭 --------------------
tab1, tab2, tab3 = st.tabs(["입주기업 조회", "연구소기업 조회", "데이터 심층분석"])

# ===== 탭1: 입주기업 조회 =====
with tab1:
    df = firms.copy()
    if sel_region != "전체":
        df = df[df["지역"] == sel_region]
    if sel_zone != "전체":
        df = df[df["지구"] == sel_zone]
    if keyword:
        df = df[df["기관명"].astype(str).str.contains(keyword, case=False, na=False)]

    st.subheader("입주기업 목록")
    if len(df) == 0:
        st.info("선택 조건에 해당하는 입주기업이 없습니다. 필터를 조정해 보세요.")
    else:
        view_cols = ["번호","지역","지구","기관명"]
        view_cols = [c for c in view_cols if c in df.columns]
        st.dataframe(
            df[view_cols].sort_values(["지역","지구","기관명"]),
            use_container_width=True,
            hide_index=True
        )
        st.download_button(
            "⬇️ 현재 목록 다운로드 (CSV)",
            data=df[view_cols].to_csv(index=False).encode("utf-8-sig"),
            file_name="입주기업_조회결과.csv",
            mime="text/csv",
            key="dl_firms"
        )

# ===== 탭2: 연구소기업 조회 =====
with tab2:
    df = labs.copy()
    if sel_region != "전체":
        # 표기 불일치에 대비해 contains
        df = df[df["현행특구"].astype(str).str.contains(sel_region, na=False)]
    if keyword:
        df = df[df["기업명"].astype(str).str.contains(keyword, case=False, na=False)]

    st.subheader("연구소기업 목록")
    show_cols = ["구분","기업명","사업자등록번호","등록연도","현행특구","강소특구여부"]
    show_cols = [c for c in show_cols if c in df.columns]

    if len(df) == 0:
        st.info("선택 조건에 해당하는 연구소기업이 없습니다. 필터를 조정해 보세요.")
    else:
        st.dataframe(
            df[show_cols].sort_values(["현행특구","등록연도","기업명"]),
            use_container_width=True,
            hide_index=True
        )
        st.download_button(
            "⬇️ 현재 목록 다운로드 (CSV)",
            data=df[show_cols].to_csv(index=False).encode("utf-8-sig"),
            file_name="연구소기업_조회결과.csv",
            mime="text/csv",
            key="dl_labs"
        )

# ===== 탭3: 간단 분석 =====
with tab3:
    # --- 지역별 기업 수(입주 vs 연구소기업) ---
    st.subheader("지역별 기업 수 비교")
    g1 = firms.groupby("지역").size().reset_index(name="입주기업")
    g2 = labs.groupby("현행특구").size().reset_index(name="연구소기업").rename(columns={"현행특구":"지역"})
    g = pd.merge(g1, g2, on="지역", how="outer").fillna(0)
    g = g.sort_values("입주기업", ascending=False)
    g_melt = g.melt(id_vars="지역", var_name="구분", value_name="수")

    chart1 = (alt.Chart(g_melt)
              .mark_bar(size=18, cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
              .encode(
                    x=alt.X("지역:N", sort="-y", title=None),
                    y=alt.Y("수:Q", title="기업 수"),
                    color=alt.Color("구분:N", scale=alt.Scale(range=[BAR_A, BAR_B])),
                    tooltip=["지역","구분","수"]
              )
              .properties(height=340)
              )
    st.altair_chart(chart1, use_container_width=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # --- 연도별 연구소기업 추이 ---
    st.subheader("연구소기업 연도별 추이")
    t = labs.dropna(subset=["등록연도"]).copy()
    if len(t) == 0:
        st.info("연구소기업 데이터에 '등록연도' 유효값이 없어 추세 그래프를 표시할 수 없습니다.")
    else:
        ts = t.groupby("등록연도").size().reset_index(name="건수")
        line = (alt.Chart(ts)
                .mark_line(point=True, strokeWidth=3, color=PRIMARY)
                .encode(
                    x=alt.X("등록연도:O", title=None),
                    y=alt.Y("건수:Q", title="건수"),
                    tooltip=["등록연도","건수"]
                )
                .properties(height=280)
                )
        st.altair_chart(line, use_container_width=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # --- 전환 비율(참고용, 이름기반) ---
    st.subheader("전환 비율(참고용, 이름기반)")
    firms2 = firms.copy()
    lab_set = set(labs["기업명_norm"])
    firms2["is_lab"] = firms2["기업명_norm"].isin(lab_set)
    conv = (firms2.groupby("지역")
            .agg(입주수=("기관명","count"), 연구소기업수=("is_lab","sum"))
            .assign(전환율=lambda d: (d["연구소기업수"]/d["입주수"]).round(3))
            .reset_index())
    c2 = (alt.Chart(conv)
          .mark_bar(size=18, cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color=ACCENT)
          .encode(
              x=alt.X("지역:N", sort="-y", title=None),
              y=alt.Y("전환율:Q", axis=alt.Axis(format="%"), title="전환율(%)"),
              tooltip=["지역","입주수","연구소기업수",alt.Tooltip("전환율:Q", format=".1%")]
          )
          .properties(height=280)
          )
    st.altair_chart(c2, use_container_width=True)
    st.caption("※ 사업자등록번호 기반이 아니므로 참고용입니다(동명이인/표기 차이 가능).")
