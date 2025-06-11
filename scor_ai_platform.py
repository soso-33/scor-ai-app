# منصة SCOR AI المتكاملة - مشروع التخرج
# تصميم: سُها ناصر سعيد عماره  |  إشراف: أ.د. عماد قمحاوي

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import io
import json

# ====== PAGE CONFIGURATION ======
st.set_page_config(page_title="منصة SCOR الذكية", layout="centered")

# ====== GLOBAL STYLE ======
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-family: 'Tajawal', sans-serif;
    direction: rtl;
}
h1, h2, h3, h4 {
    color: #2C3E50;
    text-align: center;
}
</style>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ====== SIDEBAR NAVIGATION ======
st.sidebar.title("🔍 أقسام المنصة")
page = st.sidebar.radio("اختر الصفحة:", [
    "🧪 التقييم",
    "📊 النتائج والتحليل",
    "🤖 التوصيات الذكية",
    "🏢 مقارنة الشركات"
])

# ====== SESSION STATE INIT ======
if 'results' not in st.session_state:
    st.session_state.results = {}
    st.session_state.iot_avg = 0
    st.session_state.swot = {"قوة": [], "ضعف": [], "فرصة": [], "تهديد": []}
    st.session_state.bcg_importance = {}
    st.session_state.user_info = {}

# ====== PAGE 1: EVALUATION ======
if page == "🧪 التقييم":
    st.header("🧪 التقييم العام")
    st.sidebar.header("📌 بيانات المستخدم")
    with st.sidebar.form("user_form"):
        user_name = st.text_input("الاسم الكامل")
        company_name = st.text_input("اسم الشركة أو المؤسسة")
        sector = st.selectbox("القطاع", ["الرعاية الصحية", "التصنيع", "اللوجستيات", "الخدمات", "أخرى"])
        country = st.text_input("الدولة")
        save_results = st.checkbox("أوافق على حفظ نتائجي للمقارنة لاحقًا")
        submitted = st.form_submit_button("ابدأ التقييم")

    if not submitted:
        st.stop()

    st.session_state.user_info = {
        'name': user_name,
        'company': company_name,
        'sector': sector,
        'country': country
    }

    try:
        df = pd.read_excel("SCOR_AI_Questions.xlsx")
    except:
        st.error("❌ تأكد من وجود ملف SCOR_AI_Questions.xlsx في نفس مجلد الكود.")
        st.stop()

    scor_phases = df['SCOR Phase'].unique()
    phase_labels = {
        "Plan": "📘 التخطيط",
        "Source": "📗 التوريد",
        "Make": "📙 التصنيع",
        "Deliver": "📕 التوزيع",
        "Return": "📒 المرتجعات"
    }

    results = {}
    colors = []
    swot = {"قوة": [], "ضعف": [], "فرصة": [], "تهديد": []}

    for phase in scor_phases:
        with st.expander(f"🔹 مرحلة: {phase_labels.get(phase, phase)}", expanded=True):
            phase_df = df[df['SCOR Phase'] == phase]
            total = 0
            for _, row in phase_df.iterrows():
                score = st.slider(f"🔘 {row['Question (AR)']}", 1, 5, 3, key=row['Question (AR)'])
                total += score
            avg = total / len(phase_df)
            results[phase] = avg

            if avg >= 4:
                st.success("🔵 ممتاز")
                colors.append("#3498DB")
                swot["قوة"].append(phase_labels[phase])
            elif avg >= 2.5:
                st.warning("🟠 جيد")
                colors.append("#F39C12")
                swot["فرصة"].append(phase_labels[phase])
            else:
                st.error("🔴 ضعيف")
                colors.append("#E74C3C")
                swot["ضعف"].append(phase_labels[phase])

    with st.expander("📡 تقييم جاهزية IoT والتتبع اللحظي"):
        q1 = st.slider("هل تستخدم أجهزة استشعار؟", 1, 5, 3)
        q2 = st.slider("هل لديك لوحات تحكم لحظية؟", 1, 5, 3)
        q3 = st.slider("هل تحلل البيانات لحظيًا؟", 1, 5, 3)
        q4 = st.slider("هل تتكامل البيانات مع ERP؟", 1, 5, 3)
        iot_avg = (q1 + q2 + q3 + q4) / 4
        st.markdown(f"**متوسط جاهزية IoT: {iot_avg:.1f}/5**")

    st.session_state.results = results
    st.session_state.iot_avg = iot_avg
    st.session_state.swot = swot

    if save_results:
        data = {
            "الاسم": [user_name],
            "الشركة": [company_name],
            "القطاع": [sector],
            "الدولة": [country],
            "التاريخ": [datetime.now().strftime("%Y-%m-%d %H:%M")],
            "متوسط IoT": [round(iot_avg, 2)]
        }
        for phase, score in results.items():
            data[phase] = [round(score, 2)]
        df_new = pd.DataFrame(data)
        try:
            df_existing = pd.read_excel("benchmark_data.xlsx")
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        except FileNotFoundError:
            df_combined = df_new
        df_combined.to_excel("benchmark_data.xlsx", index=False)
        st.success("✅ تم حفظ نتائج التقييم للمقارنة المستقبلية.")

# ====== PAGE 2: RESULTS & ANALYSIS ======
elif page == "📊 النتائج والتحليل":
    st.header("📊 النتائج ومصفوفات التحليل")
    results = st.session_state.results
    swot = st.session_state.swot
    iot_avg = st.session_state.iot_avg
    user = st.session_state.user_info

    labels = list(results.keys())
    values = list(results.values())
    fig = go.Figure([go.Bar(x=labels, y=values, text=[f"{v:.1f}" for v in values], textposition='auto')])
    fig.update_layout(title="تقييم مراحل SCOR", yaxis_range=[0,5], height=400)
    st.plotly_chart(fig)

    st.subheader("🧠 مصفوفة SWOT الذكية")
    st.markdown(f"""
    - **نقاط القوة:** {', '.join(swot['قوة']) or 'لا توجد'}
    - **نقاط الضعف:** {', '.join(swot['ضعف']) or 'لا توجد'}
    - **الفرص:** {', '.join(swot['فرصة']) or 'لا توجد'}
    - **التهديدات:** يتم تحليلها لاحقًا
    """)

    with st.expander("📊 تحليل BCG Dashboard"):
        bcg_importance = {}
        labels, readiness, importance_vals, categories = [], [], [], []
        for phase in results:
            imp = st.slider(f"أهمية {phase}", 1, 5, 3)
            bcg_importance[phase] = imp
            labels.append(phase)
            readiness.append(results[phase])
            importance_vals.append(imp)
            if results[phase] >= 3 and imp >= 3:
                categories.append("⭐ نجم")
            elif results[phase] >= 3:
                categories.append("❓ استفهام")
            elif imp >= 3:
                categories.append("🐄 بقرة")
            else:
                categories.append("🐶 كلب")
        fig_bcg = go.Figure()
        fig_bcg.add_trace(go.Scatter(
            x=importance_vals, y=readiness,
            mode='markers+text', text=labels, textposition="top center",
            marker=dict(size=18, color=['green' if c=="⭐ نجم" else 'orange' if c=="❓ استفهام" else 'blue' if c=="🐄 بقرة" else 'red' for c in categories])
        ))
        fig_bcg.update_layout(title="مصفوفة BCG", xaxis_title="الأهمية", yaxis_title="الجاهزية",
                              xaxis=dict(range=[0,5]), yaxis=dict(range=[0,5]))
        st.plotly_chart(fig_bcg)
        for i, label in enumerate(labels):
            st.markdown(f"- {label}: {categories[i]}")

    with st.expander("🔗 تصدير البيانات (ERP/Odoo)"):
        export_data = {
            "user": user,
            "SCOR_results": results,
            "IoT_score": iot_avg,
            "SWOT": swot
        }
        json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
        st.code(json_str, language='json')
        st.download_button("⬇️ تحميل JSON", data=json_str, file_name="scor_ai_export.json", mime="application/json")

# ====== PAGE 3: AI RECOMMENDATIONS ======
elif page == "🤖 التوصيات الذكية":
    st.header("🤖 التوصيات الذكية")
    results = st.session_state.results
    iot_avg = st.session_state.iot_avg
    if results:
        avg_score = sum(results.values()) / len(results)
        if avg_score >= 4 and iot_avg >= 4:
            st.success("✅ جاهزية عالية لتوسيع تطبيقات الذكاء الاصطناعي والربط مع ERP")
        elif avg_score >= 3:
            st.info("🛠️ يُنصح بالتحول الرقمي التدريجي")
        elif avg_score < 3 and iot_avg < 3:
            st.warning("⚠️ تحتاج المؤسسة إلى إعادة بناء رقمية")
        else:
            st.info("📌 يمكن البدء بتطبيقات AI محدودة")
    else:
        st.warning("يرجى تنفيذ التقييم أولًا.")

# ====== PAGE 4: BENCHMARKING ======
elif page == "🏢 مقارنة الشركات":
    st.header("🏢 مقارنة نتائج الشركات")
    try:
        df_benchmark = pd.read_excel("benchmark_data.xlsx")
    except FileNotFoundError:
        st.error("❌ لا توجد بيانات محفوظة")
        st.stop()

    companies = df_benchmark["الشركة"].unique().tolist()
    selected = st.multiselect("اختر الشركات للمقارنة:", companies, default=companies[:3])

    if selected:
        df_filtered = df_benchmark[df_benchmark["الشركة"].isin(selected)]
        st.dataframe(df_filtered)

        phases = [col for col in df_filtered.columns if col in ['Plan', 'Source', 'Make', 'Deliver', 'Return']]
        fig = go.Figure()
        for company in selected:
            row = df_filtered[df_filtered["الشركة"] == company].iloc[0]
            fig.add_trace(go.Bar(name=company, x=phases, y=[row[p] for p in phases]))
        fig.update_layout(barmode='group', yaxis_range=[0,5], title="مقارنة SCOR")
        st.plotly_chart(fig)

        with st.expander("📥 تحميل كل النتائج Excel"):
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df_benchmark.to_excel(writer, index=False)
            st.download_button("⬇️ تحميل الملف", data=excel_buffer.getvalue(), file_name="SCOR_Benchmark_All.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
