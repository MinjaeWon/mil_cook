# streamlit run app.py
import streamlit as st
import pandas as pd
import altair as alt
import inspect

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
    .main .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }}
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
    .stDataFrame tbody tr td {{
        font-size: 0.95rem;
        padding-top: 6px; padding-bottom: 6px;
    }}
    hr {{
        margin: 0.8rem 0 1.2rem 0; border-color: #E6EAF2;
    }}
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

# ✅ 추가: 코스닥/시총 엑셀
PATH_MCAP   = "시가총액목록.csv"      # 업로드된 엑셀 파일명
PATH_KOSDAQ = "코스닥상장목록.csv"    # 업로드된 엑셀 파일명

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

def to_bool(x):
    """강소특구 여부 다양한 표기를 True/False로 변환"""
    if pd.isna(x): return False
    x = str(x).strip().upper()
    return x in ["Y", "YES", "TRUE", "1", "강소", "강소특구", "예"]

# ---- 이름/숫자 유틸 (추가) --------------------------------------------
import re
import math

def normalize_company_for_match(s: str) -> str:
    """코스닥/시총 매칭용: (주)/㈜/주식회사, 괄호내용, 우선주/전환/스팩 표기 제거 + 대문자화 + 특수문자 제거"""
    if pd.isna(s):
        return ""
    s = str(s).upper()
    for t in ["(주)", "㈜", "주식회사"]:
        s = s.replace(t, "")
    s = re.sub(r"\(.*?\)|\[.*?\]", "", s)  # 괄호/대괄호 내용 제거
    s = re.sub(r"(보통주|우선주|[0-9]+우|우|전환|스팩|SPAC|리츠)", "", s, flags=re.IGNORECASE)
    s = re.sub(r"[^0-9A-Z가-힣]", "", s)   # 특수문자 제거
    return s.strip()

def parse_money_kr(v):
    """시가총액 문자열을 정수(원)로 파싱: '1,234,567', '2.3조', '150억' 등 대응"""
    if pd.isna(v):
        return None
    s = str(v).strip().replace(",", "")
    # 단위 처리
    if "조" in s or "억" in s:
        # 숫자만 추출 (소수점 포함)
        m = re.findall(r"[0-9]+(?:\.[0-9]+)?", s)
        if not m:
            return None
        num = float(m[0])
        if "조" in s:
            return int(num * 1_0000_0000_0000)  # 1조 = 10^12 원
        if "억" in s:
            return int(num * 1_0000_0000)      # 1억 = 10^8 원
    # 원(숫자)으로 가정
    if s.isdigit():
        return int(s)
    try:
        return int(float(s))
    except:
        return None

# 기존 humanize_kr_won 을 교체
def humanize_kr_won(n):
    """정수 원 -> 가독성 포맷. 값이 없으면 빈 문자열 반환."""
    import math
    if n is None or (isinstance(n, float) and math.isnan(n)):
        return ""   # ← 값 없으면 표시하지 않음
    n = int(n)
    if n >= 1_0000_0000_0000:  # 조
        jo  = n // 1_0000_0000_0000
        rest = n %  1_0000_0000_0000
        eok = rest // 1_0000_0000
        return f"{jo}조 {eok:,}억" if eok else f"{jo}조"
    if n >= 1_0000_0000:       # 억
        eok = n // 1_0000_0000
        return f"{eok:,}억"
    return f"{n:,}원"




#-- 추가
import re

def normalize_company_for_match(s: str) -> str:
    """코스닥/시총 매칭용 회사명 정규화:
       (주)/㈜/주식회사/괄호내용/보통주/우선주/우/전환/스팩 등 제거 + 공백/특수문자 제거 + 대문자화"""
    if pd.isna(s):
        return ""
    s = str(s).upper()
    for t in ["(주)", "㈜", "주식회사"]:
        s = s.replace(t, "")
    # 괄호 내부 제거
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"\[.*?\]", "", s)
    # 주식 표기 제거
    s = re.sub(r"(보통주|우선주|[0-9]+우|우|전환|스팩|SPAC|리츠)", "", s, flags=re.IGNORECASE)
    # 공백/특수문자 제거
    s = re.sub(r"[^0-9A-Z가-힣]", "", s)
    return s.strip()

def read_table_safe(paths_or_names):
    """CSV/Excel 자동 감지 로더. 여러 경로 후보를 받아 첫 성공 DF 반환. 실패 시 빈 DF."""
    import os
    if isinstance(paths_or_names, str):
        paths_or_names = [paths_or_names]

    # 후보 경로 확장: /mnt/data 및 xlsx/csv 교차 시도
    expanded = []
    for p in paths_or_names:
        expanded.append(p)
        # /mnt/data 폴백
        base = os.path.basename(p)
        expanded.append(os.path.join("/mnt/data", base))
        # 확장자 교차 시도
        if base.lower().endswith(".csv"):
            expanded.append(p[:-4] + ".xlsx")
            expanded.append(os.path.join("/mnt/data", base[:-4] + ".xlsx"))
        if base.lower().endswith((".xlsx", ".xls")):
            expanded.append(os.path.splitext(p)[0] + ".csv")
            expanded.append(os.path.join("/mnt/data", os.path.splitext(base)[0] + ".csv"))

    tried = set()
    for path in expanded:
        if path in tried:
            continue
        tried.add(path)
        try:
            lower = path.lower()
            if lower.endswith(".csv"):
                # 인코딩 여러 번 시도
                for enc in ["utf-8-sig", "cp949", "utf-8"]:
                    try:
                        return pd.read_csv(path, encoding=enc)
                    except Exception:
                        continue
                # 마지막 시도: 구분자 자동 추정
                try:
                    return pd.read_csv(path, encoding="utf-8", engine="python", sep=None)
                except Exception:
                    pass
            elif lower.endswith((".xlsx", ".xls")):
                try:
                    return pd.read_excel(path)
                except Exception:
                    pass
            else:
                # 확장자 불명: csv 먼저, 안되면 excel
                for enc in ["utf-8-sig", "cp949", "utf-8"]:
                    try:
                        return pd.read_csv(path, encoding=enc)
                    except Exception:
                        continue
                try:
                    return pd.read_excel(path)
                except Exception:
                    pass
        except Exception:
            continue
    return pd.DataFrame()


def pick_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None
#추가끝.


# -------------------- 데이터 로드 --------------------
firms = read_csv_kr(PATH_FIRMS)  # 번호, 지역, 기관명, 지구
labs  = read_csv_kr(PATH_LABS)   # 구분, 기업명, 사업자등록번호, 등록연도, 현행특구, 강소특구여부

#추가
# -------------------- 코스닥 기준표 구성 --------------------
mcap_raw   = read_table_safe([PATH_MCAP])
kosdaq_raw = read_table_safe([PATH_KOSDAQ])

if mcap_raw.empty or kosdaq_raw.empty:
    # 빈 DF여도 뒤에서 쓰는 컬럼(시총_원 포함)을 모두 갖춘 틀을 만든다
    kosdaq_df = pd.DataFrame(columns=["키","상장사","시가총액","업종","주요제품","시총_원"])

else:
    # 이름/시총/업종/주요제품 컬럼 추출 (가능한 후보들)
    m_name = pick_col(mcap_raw,   ["기업명","종목명","회사명","상장사","상장사명","법인명"])
    m_mcap = pick_col(mcap_raw,   ["시가총액","시가총액(원)","시가총액(억원)","시가총액(백만원)"])
    m_ind  = pick_col(mcap_raw,   ["업종","업종명"])
    m_prod = pick_col(mcap_raw,   ["주요제품","주요 제품","주요사업","주요상품","주요 품목"])

    k_name = pick_col(kosdaq_raw, ["기업명","종목명","회사명","상장사","상장사명","법인명"])
    k_ind  = pick_col(kosdaq_raw, ["업종","업종명"])
    k_prod = pick_col(kosdaq_raw, ["주요제품","주요 제품","주요사업","주요상품","주요 품목"])

    # 베이스 DF들
    mc = pd.DataFrame()
    kd = pd.DataFrame()

    if m_name:
        mc["상장사_mc"] = mcap_raw[m_name].astype(str)
        mc["키"]        = mc["상장사_mc"].apply(normalize_company_for_match)
        if m_mcap: mc["시가총액"]   = mcap_raw[m_mcap]
        if m_ind:  mc["업종_mc"]    = mcap_raw[m_ind]
        if m_prod: mc["주요제품_mc"] = mcap_raw[m_prod]
        mc = mc.dropna(subset=["키"]).drop_duplicates(subset=["키"])

    if k_name:
        kd["상장사_kd"] = kosdaq_raw[k_name].astype(str)
        kd["키"]        = kd["상장사_kd"].apply(normalize_company_for_match)
        if k_ind:  kd["업종_kd"]    = kosdaq_raw[k_ind]
        if k_prod: kd["주요제품_kd"] = kosdaq_raw[k_prod]
        kd = kd.dropna(subset=["키"]).drop_duplicates(subset=["키"])

    # 코스닥 상장 목록의 키만 사용 (코스닥 한정)
    if not kd.empty:
        if not mc.empty:
            mc = mc[mc["키"].isin(set(kd["키"]))]

        # 병합 후 대표값 선택
        kosdaq_df = pd.merge(mc, kd, on="키", how="outer")
        kosdaq_df["상장사"]  = kosdaq_df["상장사_mc"].combine_first(kosdaq_df["상장사_kd"])
        kosdaq_df["업종"]    = kosdaq_df.get("업종_mc",  pd.Series(dtype=object)).combine_first(
                               kosdaq_df.get("업종_kd",  pd.Series(dtype=object)))
        kosdaq_df["주요제품"] = kosdaq_df.get("주요제품_mc", pd.Series(dtype=object)).combine_first(
                               kosdaq_df.get("주요제품_kd", pd.Series(dtype=object)))

        # ⬇️ 선택 전에 '없을 수도 있는' 컬럼을 먼저 채워넣어 KeyError 방지
        for col in ["시가총액","업종","주요제품"]:
            if col not in kosdaq_df.columns:
                kosdaq_df[col] = pd.NA

        kosdaq_df = kosdaq_df[["키","상장사","시가총액","업종","주요제품"]]
        kosdaq_df = kosdaq_df.dropna(subset=["상장사"]).drop_duplicates(subset=["키"])

        # ⬇️ 시총 숫자 컬럼 계산 (원 단위 정규화)
        kosdaq_df["시총_원"] = kosdaq_df["시가총액"].apply(parse_money_kr)

    else:
        # 코스닥 상장 목록이 없으면 빈 DF(필수 컬럼 포함)
        kosdaq_df = pd.DataFrame(columns=["키","상장사","시가총액","업종","주요제품","시총_원"])


# 원본 데이터에도 매칭 키 생성
firms["매칭키"] = firms["기관명"].apply(normalize_company_for_match)
labs["매칭키"]  = labs["기업명"].apply(normalize_company_for_match)
#추가끝



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

# -------------------- 핵심 변경 ① : 특구명 통합 --------------------
# 현행특구 + 강소특구여부 -> 특구명 (예: 대덕, 강소(김해))
# labs["강소_bool"] = labs["강소특구여부"].apply(to_bool)
import re

def to_bool(x):
    if pd.isna(x): return False
    x = str(x).strip().upper()
    return x in ["Y", "YES", "TRUE", "1", "강소", "강소특구", "예"]

labs["강소_bool"] = labs["강소특구여부"].apply(to_bool)

def normalize_small_zone_city(base: str) -> str:
    """현행특구에서 지명만 뽑아냄: 괄호/강소/특구/불필요 기호 제거"""
    if not isinstance(base, str): 
        return ""
    s = base.strip()
    s = re.sub(r"\s+", " ", s)
    # 괄호 안이 있으면 그걸 지명으로 사용
    m = re.search(r"\(([^)]+)\)", s)
    if m:
        return m.group(1).strip()
    # '강소특구', '강소 특구', '강소' 제거
    s = re.sub(r"강소\s*특구?", "", s)
    s = s.replace("특구", "")
    # 남은 기호류 정리
    s = s.strip(" ()·,/-")
    return s.strip()

def combine_zone(row):
    base = "" if pd.isna(row.get("현행특구")) else str(row["현행특구"]).strip()
    if row.get("강소_bool", False) or ("강소" in base):
        city = normalize_small_zone_city(base)
        return f"강소({city})" if city else "강소(미상)"
    # 일반 특구는 원문 유지
    return base if base else ""

labs["특구명"] = labs.apply(combine_zone, axis=1)
labs["특구유형"] = labs["특구명"].apply(lambda x: "강소" if isinstance(x, str) and x.startswith("강소(") else "일반")

# labs["특구명"] = labs.apply(combine_zone, axis=1)

# -------------------- 헤더 --------------------
left, right = st.columns([0.75, 0.25])
with left:
    st.markdown("### 📊 특구 인사이트 정보제공")
    st.caption("입주기업 & 연구소기업 **빠른 조회 + 데이터 분석 5종**")
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

# -------------------- 사이드바(통합 필터) --------------------
with st.sidebar:
    if "use_container_width" in inspect.signature(st.image).parameters:
        st.image("로고.png", use_container_width=True)
    else:
        st.image("로고.png", use_column_width=True)  # 구버전 호환
    st.markdown("<hr/>", unsafe_allow_html=True)

st.sidebar.header("사용자 요구사항")

# 지역/특구 풀: 입주기업의 '지역' + 연구소기업의 '특구명'
regions_all = sorted(
    set(firms["지역"].dropna().astype(str)) |
    set(labs["특구명"].dropna().astype(str))
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
    st.metric("입주기업 수", f"{len(firms):,}")
    st.markdown('<div class="metric-caption">입주기업 총계</div></div>', unsafe_allow_html=True)

with m2:
    st.metric("연구소기업 수", f"{len(labs):,}")
    st.markdown('<div class="metric-caption">연구소기업 총계</div></div>', unsafe_allow_html=True)

with m3:
    lab_set = set(labs["기업명_norm"])
    conv_ratio = (firms["기업명_norm"].isin(lab_set)).mean() if len(firms) else 0
    st.metric("전환 비율(참고)", f"{conv_ratio*100:.1f}%")
    st.markdown('<div class="metric-caption">이름기반 매칭(참고용)</div></div>', unsafe_allow_html=True)

st.markdown("<hr/>", unsafe_allow_html=True)

# -------------------- 탭 --------------------
tab1, tab2, tab3, tab4 = st.tabs(["입주기업 조회", "연구소기업 조회", "데이터 심층분석", "코스닥 기업 분석"])


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
    # ✅ 변경: 지역/특구 필터는 '특구명' 기준으로
    if sel_region != "전체":
        df = df[df["특구명"].astype(str).str.contains(sel_region, case=False, na=False, regex=False)]
        city = sel_region[3:-1] if sel_region.startswith("강소(") and sel_region.endswith(")") else sel_region
        m1 = df["특구명"].astype(str).str.contains(sel_region, case=False, na=False, regex=False)
        m2 = df["특구명"].astype(str).str.contains(city,      case=False, na=False, regex=False)
        df = df[m1 | m2]


    if keyword:
        df = df[df["기업명"].astype(str).str.contains(keyword, case=False, na=False)]

    st.subheader("연구소기업 목록")
    # ✅ 변경: 강소특구여부는 표시 안 하고, '특구명'만 노출
    show_cols = ["구분","기업명","사업자등록번호","등록연도","특구명"]
    show_cols = [c for c in show_cols if c in df.columns]

    if len(df) == 0:
        st.info("선택 조건에 해당하는 연구소기업이 없습니다. 필터를 조정해 보세요.")
    else:
        st.dataframe(
            df[show_cols].sort_values(["특구명","등록연도","기업명"]),
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

# ===== 탭3: 데이터 심층분석 =====
with tab3:
    # --- 지역별 기업 수(입주 vs 연구소기업) ---
    st.subheader("지역별 기업 수 비교")
    g1 = firms.groupby("지역").size().reset_index(name="입주기업")
    # ✅ 변경: 연구소기업은 '특구명'으로 집계
    g2 = labs.groupby("특구명").size().reset_index(name="연구소기업").rename(columns={"특구명":"지역"})
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
    st.subheader("입주기업 대비 연구소기업 비율(참고용, 이름기반)")
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

    # -------------------- 추가 ①: 버블 스캐터 (발표형) --------------------
    st.markdown("<br/>", unsafe_allow_html=True)
    st.subheader("입주 vs 연구소기업 규모·효율 동시 비교 (버블 스캐터)")

    conv2 = conv.merge(g2.rename(columns={"지역":"지역", "연구소기업":"연구소기업"}), on="지역", how="left")
    # conv에는 이미 '입주수','연구소기업수','전환율' 존재
    # 산점도에 텍스트 라벨 추가를 위해 데이터 준비
    scatter = alt.Chart(conv).mark_circle().encode(
        x=alt.X("입주수:Q", title="입주기업 수"),
        y=alt.Y("연구소기업수:Q", title="연구소기업 수"),
        size=alt.Size("전환율:Q", legend=None),
        color=alt.value(BAR_A),
        tooltip=[
            "지역",
            alt.Tooltip("입주수:Q", title="입주기업"),
            alt.Tooltip("연구소기업수:Q", title="연구소기업"),
            alt.Tooltip("전환율:Q", title="전환율", format=".1%"),
        ],
    ).properties(height=360)

    labels = alt.Chart(conv).mark_text(dy=-8, fontWeight="bold").encode(
        x="입주수:Q",
        y="연구소기업수:Q",
        text="지역:N"
    )

    st.altair_chart(scatter + labels, use_container_width=True)
    st.caption("● 점 크기=전환율. 우상향·큰 원 = 규모와 효율이 모두 높은 지역.")

    # -------------------- 추가 ②: Heatmap (연도×특구) --------------------
    st.markdown("<br/>", unsafe_allow_html=True)
    st.subheader("연구소기업 발생 패턴 (연도×특구 Heatmap)")

    heat_df = labs.dropna(subset=["등록연도","특구명"]).groupby(["등록연도","특구명"]).size().reset_index(name="건수")
    if len(heat_df) == 0:
        st.info("Heatmap을 그릴 데이터가 부족합니다.")
    else:
        heat = (alt.Chart(heat_df)
                .mark_rect()
                .encode(
                    x=alt.X("등록연도:O", title="연도"),
                    y=alt.Y("특구명:N", sort="-x", title="특구"),
                    color=alt.Color("건수:Q"),
                    tooltip=["등록연도","특구명","건수"]
                )
                .properties(height=480)
                )
        st.altair_chart(heat, use_container_width=True)
        st.caption("색이 진할수록 해당 연도·특구에서 연구소기업이 많이 설립됨을 의미합니다.")


# ===== 탭4: 코스닥 기업 분석 =====
# ===== 탭4: 코스닥 기업 분석 =====
with tab4:
    st.subheader("코스닥 기업 매칭 결과")

    if kosdaq_df.empty:
        st.info("코스닥/시가총액 파일을 읽지 못했습니다. 폴더/파일명을 확인하세요: "
                f"'{PATH_MCAP}', '{PATH_KOSDAQ}'")
    else:
        # ---- 매칭: 입주/연구소기업 ----------------------------------
        match_firms = pd.merge(
            firms[["지역","지구","기관명","매칭키"]],
            kosdaq_df, left_on="매칭키", right_on="키", how="inner"
        ).drop_duplicates(subset=["매칭키"])

        match_labs = pd.merge(
            labs[["특구명","기업명","매칭키"]],
            kosdaq_df, left_on="매칭키", right_on="키", how="inner"
        ).drop_duplicates(subset=["매칭키"])

        # ---- 보기 좋게 컬럼 정리 ------------------------------------
        view_firms = match_firms.rename(columns={"기관명":"원본명","상장사":"기업명"})[
            ["지역","지구","원본명","기업명","시가총액","시총_원","업종","주요제품"]
        ].sort_values(["지역","지구","기업명"])

        view_labs = match_labs.rename(columns={"기업명":"원본명","상장사":"기업명"})[
            ["특구명","원본명","기업명","시가총액","시총_원","업종","주요제품"]
        ].sort_values(["특구명","기업명"])

        # ---- 요약 KPI 카드 ------------------------------------------
        total_cnt = len(view_firms) + len(view_labs)
        total_cap = (view_firms["시총_원"].fillna(0).sum()
                    +view_labs["시총_원"].fillna(0).sum())
        top_cap_firm = (pd.concat([view_firms[["기업명","시총_원"]],
                                   view_labs[["기업명","시총_원"]]])
                         .sort_values("시총_원", ascending=False).head(1))

        k1,k2,k3 = st.columns(3)
        with k1:
            st.metric("총 매칭 기업 수", f"{total_cnt:,}")
            st.caption("입주기업 + 연구소기업")
        with k2:
            st.metric("합계 시가총액", humanize_kr_won(total_cap))
            st.caption("두 집합 합산(원화)")
        with k3:
            if not top_cap_firm.empty and not pd.isna(top_cap_firm.iloc[0]["시총_원"]):
                st.metric("최대 시총 기업",
                          f"{top_cap_firm.iloc[0]['기업명']}",
                          humanize_kr_won(top_cap_firm.iloc[0]["시총_원"]))
            else:
                st.metric("최대 시총 기업", "-", "-")

        st.markdown("<hr/>", unsafe_allow_html=True)

        # ---- 서브탭: 요약/그래프 | 입주기업 | 연구소기업 --------------
        sub1, sub2, sub3 = st.tabs(["요약·그래프", "입주기업", "연구소기업"])

        # ===== (1) 요약·그래프 ======================================
        with sub1:
            # 필터 UI
            left, right = st.columns([0.7, 0.3])
            with right:
                top_n = st.slider("Top N (시가총액 순)", 5, 30, 15, 1)

            # 결합 DF (그래프용)
            vf = view_firms.assign(구분="입주기업").rename(columns={"지역":"지역/특구"})
            vl = view_labs.assign(구분="연구소기업").rename(columns={"특구명":"지역/특구"})
            both = pd.concat([vf, vl], ignore_index=True)

            # 1) Top-N 시가총액 막대(가로)
            top_df = both.dropna(subset=["시총_원"]).sort_values("시총_원", ascending=False).head(top_n)
            bar = (alt.Chart(top_df)
                   .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
                   .encode(
                       x=alt.X("시총_원:Q", title="시가총액(원)"),
                       y=alt.Y("기업명:N", sort="-x", title=None),
                       color=alt.Color("구분:N", scale=alt.Scale(range=[BAR_A, BAR_B])),
                       tooltip=[
                           "구분","기업명","지역/특구",
                           alt.Tooltip("시가총액:N", title="시가총액(서식)"),
                           alt.Tooltip("시총_원:Q", title="시가총액(원, 원시값)")
                       ]
                   ).properties(height=40*len(top_df) if len(top_df)>0 else 200)
                  )
            # 보기좋게 시총 서식 컬럼 추가
            top_df["시가총액"] = top_df["시총_원"].apply(humanize_kr_won)
            st.subheader("Top-N 시가총액 기업")
            st.altair_chart(bar, use_container_width=True)

            st.markdown("<br/>", unsafe_allow_html=True)

            # 2) 업종 분포 (도넛: count vs 시총합 선택)
            agg_mode = st.radio("업종 집계 기준", ["기업 수", "시총 합계"], horizontal=True, index=0)
            if agg_mode == "기업 수":
                pie_df = (both.groupby("업종").size().reset_index(name="값")
                          .sort_values("값", ascending=False).head(12))
            else:
                pie_df = (both.groupby("업종")["시총_원"].sum().reset_index(name="값")
                          .sort_values("값", ascending=False).head(12))

            # 결측 업종 처리
            pie_df["업종"] = pie_df["업종"].fillna("미분류")

            donut = (alt.Chart(pie_df)
                     .mark_arc(innerRadius=60)
                     .encode(
                         theta=alt.Theta("값:Q"),
                         color=alt.Color("업종:N"),
                         tooltip=["업종","값:Q"]
                     ).properties(height=360))
            st.subheader("업종 분포 (상위 12)")
            st.altair_chart(donut, use_container_width=True)

            st.markdown("<br/>", unsafe_allow_html=True)

            # # 3) 특구/지역별 매칭 수 (연구소기업만)
            # if len(view_labs) > 0:
            #     zc = (view_labs.groupby("특구명").size().reset_index(name="매칭수")
            #           .sort_values("매칭수", ascending=False).head(20))
            #     zbar = (alt.Chart(zc)
            #             .mark_bar(size=18, cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color=PRIMARY)
            #             .encode(
            #                 x=alt.X("특구명:N", sort="-y", title=None),
            #                 y=alt.Y("매칭수:Q", title="연구소기업 매칭 수"),
            #                 tooltip=["특구명","매칭수"]
            #             ).properties(height=280))
            #     st.subheader("특구별 연구소기업 매칭 수 (Top 20)")
            #     st.altair_chart(zbar, use_container_width=True)

        # ===== (2) 입주기업 표 =======================================
        with sub2:
            st.markdown("#### 입주기업 매칭")
            q = st.text_input("검색(기업명/원본명/업종/제품 등)", key="q_firms")
            df_show = view_firms.copy()

            # 검색어 필터
            if q:
                q2 = q.strip()
                mask = (
                    df_show["기업명"].astype(str).str.contains(q2, case=False, na=False, regex=False) |
                    df_show["원본명"].astype(str).str.contains(q2, case=False, na=False, regex=False) |
                    df_show["업종"].astype(str).str.contains(q2, case=False, na=False, regex=False)  |
                    df_show["주요제품"].astype(str).str.contains(q2, case=False, na=False, regex=False)
                )
                df_show = df_show[mask]

            # ⬇️ 시총 없는 행 제거 (숫자화 → NaN/0 제외)
            df_show = df_show.assign(시총_원=pd.to_numeric(df_show["시총_원"], errors="coerce"))
            df_show = df_show[df_show["시총_원"].notna() & (df_show["시총_원"] > 0)]

            if df_show.empty:
                st.info("표시할 시가총액 정보가 없습니다.")
            else:
                # 시총표시(문자열) 생성
                df_show = df_show.assign(시총표시=df_show["시총_원"].apply(humanize_kr_won))
                cols = ["지역","지구","원본명","기업명","시총표시","업종","주요제품"]
                st.dataframe(df_show[cols], use_container_width=True, hide_index=True)
                st.download_button(
                    "⬇️ 입주기업 매칭 결과 (CSV)",
                    data=df_show[cols].to_csv(index=False).encode("utf-8-sig"),
                    file_name="코스닥매칭_입주기업.csv",
                    mime="text/csv",
                    key="dl_kosdaq_firms_v3"
                )



        # ===== (3) 연구소기업 표 =====================================
        with sub3:
            st.markdown("#### 연구소기업 매칭")
            q = st.text_input("검색(기업명/원본명/업종/제품 등)", key="q_labs")
            df_show = view_labs.copy()

            # 검색어 필터
            if q:
                q2 = q.strip()
                mask = (
                    df_show["기업명"].astype(str).str.contains(q2, case=False, na=False, regex=False) |
                    df_show["원본명"].astype(str).str.contains(q2, case=False, na=False, regex=False) |
                    df_show["업종"].astype(str).str.contains(q2, case=False, na=False, regex=False)  |
                    df_show["주요제품"].astype(str).str.contains(q2, case=False, na=False, regex=False)
                )
                df_show = df_show[mask]

            # ⬇️ 시총 없는 행 제거
            df_show = df_show.assign(시총_원=pd.to_numeric(df_show["시총_원"], errors="coerce"))
            df_show = df_show[df_show["시총_원"].notna() & (df_show["시총_원"] > 0)]

            if df_show.empty:
                st.info("표시할 시가총액 정보가 없습니다.")
            else:
                df_show = df_show.assign(시총표시=df_show["시총_원"].apply(humanize_kr_won))
                cols = ["특구명","원본명","기업명","시총표시","업종","주요제품"]
                st.dataframe(df_show[cols], use_container_width=True, hide_index=True)
                st.download_button(
                    "⬇️ 연구소기업 매칭 결과 (CSV)",
                    data=df_show[cols].to_csv(index=False).encode("utf-8-sig"),
                    file_name="코스닥매칭_연구소기업.csv",
                    mime="text/csv",
                    key="dl_kosdaq_labs_v3"
                )



        st.caption("※ 회사명 비교는 `(주)·㈜·주식회사·괄호·우선주/전환/스팩` 등을 제거한 **정규화 키**로 수행합니다.")
