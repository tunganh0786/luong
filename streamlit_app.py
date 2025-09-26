# ---------- Sidebar config ----------
st.sidebar.header("⚙️ Cấu hình mốc & ngưỡng")

# Dữ liệu mặc định
default_rates = pd.DataFrame(
    {"Min_DT_VND": [0, 150_000_000, 300_000_000, 500_000_000, 800_000_000, 1_000_000_000, 2_000_000_000],
     "Pct_Rate":   [0.00, 0.005,      0.01,        0.015,       0.02,        0.025,          0.03]}
)
default_costf = pd.DataFrame(
    {"Min_CostRatio": [0.00, 0.30, 0.32, 0.35],
     "Factor":        [1.00, 0.80, 0.50, 0.00]}
)

# Toggle chỉnh sửa
edit_mode = st.sidebar.toggle("✏️ Chỉnh sửa mốc nâng cao", value=False)

with st.sidebar.expander("Mốc % theo Doanh thu TỔNG (VND)", expanded=False):
    if edit_mode and hasattr(st, "data_editor"):
        rates_df = st.data_editor(default_rates, use_container_width=True)
    else:
        # Bảng chỉ xem, format đẹp
        pretty = default_rates.copy()
        pretty["Min_DT_VND"] = pretty["Min_DT_VND"].map(lambda x: f"{int(x):,}".replace(",", "."))
        pretty["Pct_Rate"]   = pretty["Pct_Rate"].map(lambda x: f"{x*100:.2f}%")
        st.dataframe(pretty, use_container_width=True, hide_index=True)
        rates_df = default_rates  # vẫn dùng số gốc để tính

with st.sidebar.expander("Hệ số theo % chi phí của BÊN", expanded=False):
    if edit_mode and hasattr(st, "data_editor"):
        costf_df = st.data_editor(default_costf, use_container_width=True)
    else:
        pretty = default_costf.copy()
        pretty["Min_CostRatio"] = pretty["Min_CostRatio"].map(lambda x: f"{x*100:.2f}%")
        pretty["Factor"]        = pretty["Factor"].map(lambda x: f"{x*100:.0f}%")
        st.dataframe(pretty, use_container_width=True, hide_index=True)
        costf_df = default_costf

elig_threshold = st.sidebar.number_input(
    "Ngưỡng được tính *tối ưu chi phí*",
    min_value=0.0, max_value=1.0, value=0.30, step=0.01,
)

st.sidebar.subheader("Đơn vị nhập Doanh thu")
use_rm  = st.sidebar.toggle("Nhập DOANH THU bằng RM (chi phí luôn VND)", value=True)
rate_vnd = st.sidebar.number_input("Tỉ giá VND/RM", min_value=1, value=5200, step=100)
