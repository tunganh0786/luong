import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tính thưởng BIO/BPO", page_icon="🎯", layout="wide")
st.title("🎯 Tính thưởng BIO / BPO – nhiều mốc linh hoạt")

st.markdown(
    """
- **Mốc thưởng % theo Doanh thu *TỔNG (BIO+BPO)*** → áp mốc cho từng bên.  
- **Hệ số theo % chi phí** tính **riêng từng bên** (ví dụ ≥30% chỉ nhận 80% phần *doanh số* nếu cấu hình như vậy).  
- **Thưởng tối ưu chi phí** chỉ tính khi **% chi phí của chính bên đó < ngưỡng** (mặc định 30%).  
- **Chi phí luôn nhập VND**. Doanh thu có thể nhập **RM** và app tự nhân tỉ giá sang VND.
"""
)

# ---------- Helpers ----------
def safe_data_editor(df, **kwargs):
    return st.data_editor(df, **kwargs) if hasattr(st, "data_editor") else st.experimental_data_editor(df, **kwargs)

def lookup_rate(total_rev_vnd: float, table_rates: pd.DataFrame) -> float:
    df = table_rates.dropna().sort_values("Min_DT_VND")
    pct = 0.0
    for _, row in df.iterrows():
        try:
            if total_rev_vnd >= float(row["Min_DT_VND"]):
                pct = float(row["Pct_Rate"])
            else:
                break
        except Exception:
            continue
    return pct

def lookup_factor(cost_ratio: float, table_f: pd.DataFrame) -> float:
    df = table_f.dropna().sort_values("Min_CostRatio")
    fac = 0.0
    for _, row in df.iterrows():
        try:
            if cost_ratio >= float(row["Min_CostRatio"]):
                fac = float(row["Factor"])
            else:
                break
        except Exception:
            continue
    return fac

def fmt_vnd(x):
    try:
        return f"{int(round(x)):,.0f} đ".replace(",", ".")
    except Exception:
        return x

# ---------- Sidebar config ----------
st.sidebar.header("⚙️ Cấu hình mốc & ngưỡng")

st.sidebar.subheader("Mốc % theo Doanh thu TỔNG (VND)")
default_rates = pd.DataFrame(
    {
        "Min_DT_VND": [0, 150_000_000, 300_000_000, 500_000_000, 800_000_000, 1_000_000_000, 2_000_000_000],
        "Pct_Rate":   [0.00, 0.005,      0.01,        0.015,       0.02,        0.025,          0.03],
    }
)
rates_df = safe_data_editor(default_rates, use_container_width=True)

st.sidebar.subheader("Hệ số theo % chi phí của BÊN")
default_costf = pd.DataFrame({"Min_CostRatio": [0.00, 0.30, 0.32, 0.35], "Factor": [1.00, 0.80, 0.50, 0.00]})
costf_df = safe_data_editor(default_costf, use_container_width=True)

elig_threshold = st.sidebar.number_input(
    "Ngưỡng được tính *tối ưu chi phí* (mặc định 0,30)",
    min_value=0.0, max_value=1.0, value=0.30, step=0.01,
)

st.sidebar.subheader("Đơn vị nhập Doanh thu")
use_rm = st.sidebar.toggle("Nhập DOANH THU bằng RM (chi phí luôn VND)", value=True)
rate_vnd = st.sidebar.number_input("Tỉ giá VND/RM", min_value=1, value=5200, step=100)

# ---------- Input form ----------
st.header("🧾 Nhập dữ liệu")
cols = st.columns([2, 1.1, 1.1, 1.1, 1.1])
with cols[0]: st.markdown("**Tên**")
with cols[1]: st.markdown(f"**DT BIO** ({'RM' if use_rm else 'VND'})")
with cols[2]: st.markdown("**Chi phí BIO (VND)**")
with cols[3]: st.markdown(f"**DT BPO** ({'RM' if use_rm else 'VND'})")
with cols[4]: st.markdown("**Chi phí BPO (VND)**")

default_rows = 10
rows = []
for i in range(default_rows):
    c = st.columns([2, 1.1, 1.1, 1.1, 1.1])
    name = c[0].text_input(f"Tên_{i}", value="" if i else "Anh Tùng", label_visibility="collapsed")
    # Doanh thu: cho format gọn không thập phân
    bio_rev = c[1].number_input(f"bio_rev_{i}", min_value=0.0, step=1.0, value=0.0, format="%.0f", label_visibility="collapsed")
    # Chi phí: VND, bước 1.000, format không thập phân
    bio_cost = c[2].number_input(f"bio_cost_{i}", min_value=0.0, step=1000.0, value=0.0, format="%.0f", label_visibility="collapsed")
    bpo_rev = c[3].number_input(f"bpo_rev_{i}", min_value=0.0, step=1.0, value=0.0, format="%.0f", label_visibility="collapsed")
    bpo_cost = c[4].number_input(f"bpo_cost_{i}", min_value=0.0, step=1000.0, value=0.0, format="%.0f", label_visibility="collapsed")
    rows.append([name, bio_rev, bio_cost, bpo_rev, bpo_cost])

df_input = pd.DataFrame(rows, columns=["Tên", "DT_BIO_IN", "CP_BIO_VND", "DT_BPO_IN", "CP_BPO_VND"])

st.divider()
if st.button("📌 TÍNH THƯỞNG"):
    df = df_input.copy()

    # Chuyển doanh thu sang VND nếu đang nhập RM; CHI PHÍ GIỮ NGUYÊN VND
    if use_rm:
        df["DT_BIO_VND"] = df["DT_BIO_IN"] * rate_vnd
        df["DT_BPO_VND"] = df["DT_BPO_IN"] * rate_vnd
    else:
        df["DT_BIO_VND"] = df["DT_BIO_IN"]
        df["DT_BPO_VND"] = df["DT_BPO_IN"]

    results = []
    for _, r in df.iterrows():
        name = str(r["Tên"]).strip()
        bio_rev_vnd = float(r["DT_BIO_VND"])
        bio_cost_vnd = float(r["CP_BIO_VND"])
        bpo_rev_vnd = float(r["DT_BPO_VND"])
        bpo_cost_vnd = float(r["CP_BPO_VND"])

        # Bỏ dòng trống
        if (not name) and (bio_rev_vnd==0 and bpo_rev_vnd==0 and bio_cost_vnd==0 and bpo_cost_vnd==0):
            continue

        total_rev = bio_rev_vnd + bpo_rev_vnd
        total_rate = lookup_rate(total_rev, rates_df)  # mốc %
        bio_ratio = (bio_cost_vnd / bio_rev_vnd) if bio_rev_vnd else 0.0
        bpo_ratio = (bpo_cost_vnd / bpo_rev_vnd) if bpo_rev_vnd else 0.0
        bio_factor = lookup_factor(bio_ratio, costf_df)
        bpo_factor = lookup_factor(bpo_ratio, costf_df)

        # Doanh số (mốc tổng × factor của từng bên)
        bonus_sales_bio = bio_rev_vnd * total_rate * bio_factor
        bonus_sales_bpo = bpo_rev_vnd * total_rate * bpo_factor

        # Tối ưu chi phí – chỉ khi %CP bên < ngưỡng
        bonus_opt_bio = (0.25 * (elig_threshold - bio_ratio) * bio_rev_vnd) if (bio_rev_vnd and bio_ratio < elig_threshold) else 0.0
        bonus_opt_bpo = (0.25 * (elig_threshold - bpo_ratio) * bpo_rev_vnd) if (bpo_rev_vnd and bpo_ratio < elig_threshold) else 0.0

        total_bonus = round(bonus_sales_bio + bonus_sales_bpo + bonus_opt_bio + bonus_opt_bpo)

        results.append({
            "Tên": name or "Người",
            "DT BIO (VND)": round(bio_rev_vnd),
            "CP BIO (VND)": round(bio_cost_vnd),
            "%CP BIO": f"{bio_ratio*100:.2f}%",
            "DT BPO (VND)": round(bpo_rev_vnd),
            "CP BPO (VND)": round(bpo_cost_vnd),
            "%CP BPO": f"{bpo_ratio*100:.2f}%",
            "DT Tổng (VND)": round(total_rev),
            "Mốc % theo DT Tổng": f"{total_rate*100:.2f}%",
            "Factor BIO": bio_factor,
            "Factor BPO": bpo_factor,
            "Thưởng DS BIO (VND)": round(bonus_sales_bio),
            "Thưởng DS BPO (VND)": round(bonus_sales_bpo),
            "Thưởng tối ưu BIO (VND)": round(bonus_opt_bio),
            "Thưởng tối ưu BPO (VND)": round(bonus_opt_bpo),
            "TỔNG THƯỞNG (VND)": total_bonus
        })

    if not results:
        st.warning("Chưa có dòng hợp lệ. Vui lòng nhập ít nhất 1 người.")
    else:
        out = pd.DataFrame(results)

        # Bảng hiển thị đẹp (định dạng VND)
        pretty = out.copy()
        for col in [
            "DT BIO (VND)","CP BIO (VND)","DT BPO (VND)","CP BPO (VND)",
            "DT Tổng (VND)","Thưởng DS BIO (VND)","Thưởng DS BPO (VND)",
            "Thưởng tối ưu BIO (VND)","Thưởng tối ưu BPO (VND)","TỔNG THƯỞNG (VND)"
        ]:
            pretty[col] = pretty[col].map(fmt_vnd)

        st.success("✅ Đã tính xong")
        st.dataframe(pretty, use_container_width=True)

        # CSV raw số (không format) để anh tải về
        st.download_button("📥 Tải CSV (raw số)", out.to_csv(index=False).encode("utf-8"), "ket_qua_tinh_thuong.csv", "text/csv")
else:
    st.info("Nhập số liệu và bấm **TÍNH THƯỞNG**")

st.caption("© App tính thưởng BIO/BPO – chi phí luôn VND, doanh thu có thể nhập RM để tự nhân tỉ giá.")
