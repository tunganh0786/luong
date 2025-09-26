import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tính thưởng BIO/BPO", page_icon="🎯", layout="wide")
st.title("🎯 Tính thưởng BIO / BPO – nhiều mốc linh hoạt")

st.markdown(
    """
- **Logic**: Tra **mốc % theo Doanh thu *Tổng (BIO+BPO)*** → áp mốc cho từng bên.  
- **Hệ số theo % chi phí** tính **riêng từng bên** (ví dụ ≥30% chỉ nhận 80% phần *doanh số* theo bảng hệ số).  
- **Thưởng tối ưu chi phí** chỉ tính nếu **% chi phí của chính bên đó < ngưỡng** (mặc định 30%).  
- Có thể chỉnh các **mốc** & **hệ số** ở sidebar.
"""
)

# -------- Helpers --------
def safe_data_editor(df, **kwargs):
    """Dùng data_editor nếu có, không thì fallback experimental_data_editor."""
    if hasattr(st, "data_editor"):
        return st.data_editor(df, **kwargs)
    else:
        return st.experimental_data_editor(df, **kwargs)

def lookup_rate(total_rev_vnd: float, table_rates: pd.DataFrame) -> float:
    df = table_rates.dropna().sort_values("Min_DT_VND")
    pct = 0.0
    for _, row in df.iterrows():
        try:
            min_dt = float(row["Min_DT_VND"])
            if total_rev_vnd >= min_dt:
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
            min_r = float(row["Min_CostRatio"])
            if cost_ratio >= min_r:
                fac = float(row["Factor"])
            else:
                break
        except Exception:
            continue
    return fac

# -------- Sidebar config --------
st.sidebar.header("⚙️ Cấu hình mốc & ngưỡng")

st.sidebar.subheader("Mốc % theo Doanh thu TỔNG (VND)")
default_rates = pd.DataFrame(
    {
        "Min_DT_VND": [0, 150_000_000, 300_000_000, 500_000_000, 800_000_000, 1_000_000_000, 2_000_000_000],
        "Pct_Rate":   [0.00, 0.005,      0.01,        0.015,       0.02,        0.025,          0.03],
    }
)
rates_df = safe_data_editor(default_rates, use_container_width=True)

st.sidebar.subheader("Hệ số theo % Chi phí của BÊN (BIO/BPO)")
default_costf = pd.DataFrame(
    {"Min_CostRatio": [0.00, 0.30, 0.32, 0.35], "Factor": [1.00, 0.80, 0.50, 0.00]}
)
costf_df = safe_data_editor(default_costf, use_container_width=True)

elig_threshold = st.sidebar.number_input(
    "Ngưỡng được tính *tối ưu chi phí*",
    min_value=0.0, max_value=1.0, value=0.30, step=0.01,
)

st.sidebar.subheader("Đơn vị & chuyển đổi")
use_rm = st.sidebar.toggle("Nhập bằng RM và tự nhân tỉ giá", value=False)
rate_vnd = st.sidebar.number_input("Tỉ giá VND/RM", min_value=1, value=5200, step=100)

# -------- Input form --------
st.header("🧾 Nhập dữ liệu")
cols = st.columns([2, 1.2, 1.2, 1.2, 1.2])
with cols[0]: st.markdown("**Tên**")
with cols[1]: st.markdown("**DT BIO**" + (" (RM)" if use_rm else " (VND)"))
with cols[2]: st.markdown("**Chi phí BIO**" + (" (RM)" if use_rm else " (VND)"))
with cols[3]: st.markdown("**DT BPO**" + (" (RM)" if use_rm else " (VND)"))
with cols[4]: st.markdown("**Chi phí BPO**" + (" (RM)" if use_rm else " (VND)"))

default_rows = 10
rows = []
for i in range(default_rows):
    c = st.columns([2, 1.2, 1.2, 1.2, 1.2])
    name = c[0].text_input(f"Tên_{i}", value="" if i>0 else "Người 1", label_visibility="collapsed")
    bio_rev = c[1].number_input(f"bio_rev_{i}", min_value=0.0, step=1.0, value=0.0, label_visibility="collapsed")
    bio_cost = c[2].number_input(f"bio_cost_{i}", min_value=0.0, step=1.0, value=0.0, label_visibility="collapsed")
    bpo_rev = c[3].number_input(f"bpo_rev_{i}", min_value=0.0, step=1.0, value=0.0, label_visibility="collapsed")
    bpo_cost = c[4].number_input(f"bpo_cost_{i}", min_value=0.0, step=1.0, value=0.0, label_visibility="collapsed")
    rows.append([name, bio_rev, bio_cost, bpo_rev, bpo_cost])

df_input = pd.DataFrame(rows, columns=["Tên", "DT_BIO", "CP_BIO", "DT_BPO", "CP_BPO"])

st.divider()
if st.button("📌 TÍNH THƯỞNG"):
    df = df_input.copy()
    if use_rm:
        df[["DT_BIO","CP_BIO","DT_BPO","CP_BPO"]] *= rate_vnd

    results = []
    for _, r in df.iterrows():
        name = str(r["Tên"]).strip()
        bio_rev_vnd = float(r["DT_BIO"])
        bio_cost_vnd = float(r["CP_BIO"])
        bpo_rev_vnd = float(r["DT_BPO"])
        bpo_cost_vnd = float(r["CP_BPO"])

        if (not name) and (bio_rev_vnd==0 and bpo_rev_vnd==0 and bio_cost_vnd==0 and bpo_cost_vnd==0):
            continue

        total_rev = bio_rev_vnd + bpo_rev_vnd

        # % mốc theo doanh thu tổng
        total_rate = lookup_rate(total_rev, rates_df)

        # % chi phí riêng từng bên
        bio_ratio = (bio_cost_vnd / bio_rev_vnd) if bio_rev_vnd else 0.0
        bpo_ratio = (bpo_cost_vnd / bpo_rev_vnd) if bpo_rev_vnd else 0.0

        # hệ số doanh số theo % chi phí bên
        bio_factor = lookup_factor(bio_ratio, costf_df)
        bpo_factor = lookup_factor(bpo_ratio, costf_df)

        # Thưởng doanh số
        bonus_sales_bio = bio_rev_vnd * total_rate * bio_factor
        bonus_sales_bpo = bpo_rev_vnd * total_rate * bpo_factor

        # Thưởng tối ưu chi phí (chỉ khi % cp bên < ngưỡng)
        bonus_opt_bio = (0.25 * (elig_threshold - bio_ratio) * bio_rev_vnd) if (bio_rev_vnd and bio_ratio < elig_threshold) else 0.0
        bonus_opt_bpo = (0.25 * (elig_threshold - bpo_ratio) * bpo_rev_vnd) if (bpo_rev_vnd and bpo_ratio < elig_threshold) else 0.0

        total_bonus = round(bonus_sales_bio + bonus_sales_bpo + bonus_opt_bio + bonus_opt_bpo)

        results.append({
            "Tên": name or f"Người",
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
            "Thưởng DS BIO": round(bonus_sales_bio),
            "Thưởng DS BPO": round(bonus_sales_bpo),
            "Thưởng tối ưu BIO": round(bonus_opt_bio),
            "Thưởng tối ưu BPO": round(bonus_opt_bpo),
            "TỔNG THƯỞNG (VND)": total_bonus
        })

    if not results:
        st.warning("Chưa có dòng hợp lệ. Vui lòng nhập ít nhất 1 người.")
    else:
        out = pd.DataFrame(results)
        st.success("✅ Đã tính xong")
        st.dataframe(out, use_container_width=True)
        st.download_button("📥 Tải CSV", out.to_csv(index=False).encode("utf-8"), "ket_qua_tinh_thuong.csv", "text/csv")
else:
    st.info("Nhập số liệu và bấm **TÍNH THƯỞNG**")

st.caption("© App tính thưởng BIO/BPO – tuỳ biến mốc, hệ số, ngưỡng tối ưu.")
