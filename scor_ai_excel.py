import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(page_title="منصة SCOR للذكاء الاصطناعي", layout="centered")

# ====== GLOBAL STYLE ======
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-family: 'Tajawal', sans-serif;
    direction: rtl;
}
h1, h2, h3, h4 {
    color: #2C3E50;
}
</style>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ====== USER INPUT FORM ======
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

# ====== MAIN PAGE HEADER ======
st.markdown("""
<h1 style='text-align: center; font-size: 38px;'>منصة تقييم جاهزية الذكاء الاصطناعي في سلاسل الإمداد - نموذج SCOR</h1>
""", unsafe_allow_html=True)

st.markdown(f"""
<p style='font-size:18px;'>
مرحبًا <strong>{user_name}</strong> 👋<br>
أنت الآن بصدد تقييم جاهزية شركتك <strong>{company_name}</strong> في قطاع <strong>{sector}</strong>.
يرجى تقييم مستوى تطبيق الذكاء الاصطناعي من خلال الإجابة على الأسئلة التالية لكل مرحلة، باختيار درجة من 1 (غير مطبق) إلى 5 (تطبيق متطور).
</p>
""", unsafe_allow_html=True)

# ====== LOAD QUESTIONS ======
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

# ====== QUESTIONS & AI RECOMMENDATIONS ======
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
            st.success("🔵 ممتاز: تستخدم الذكاء الاصطناعي بكفاءة عالية في هذه المرحلة.")
            colors.append("#3498DB")
            swot["قوة"].append(phase_labels[phase])
        elif avg >= 2.5:
            st.warning("🟠 جيد: يوجد تطبيق جزئي ويُنصح بتطويره.")
            colors.append("#F39C12")
            swot["فرصة"].append(phase_labels[phase])
        else:
            st.error("🔴 ضعيف: تحتاج إلى خطة تحول رقمي.")
            colors.append("#E74C3C")
            swot["ضعف"].append(phase_labels[phase])

# ====== SUMMARY DASHBOARD ======
st.markdown("""
<hr style='margin-top: 30px; margin-bottom: 20px;'>
<h3 style='text-align:center;'>📊 التقييم العام</h3>
""", unsafe_allow_html=True)

labels = [phase_labels[p].split()[-1] for p in scor_phases]
values = [results[p] for p in scor_phases]

fig = go.Figure(data=[
    go.Bar(x=labels, y=values, marker_color=colors, text=[f"{v:.1f}/5" for v in values], textfont_size=18, textposition='outside')
])
fig.update_layout(
    xaxis_title="مرحلة SCOR",
    yaxis_title="درجة الجاهزية",
    yaxis=dict(range=[0, 5]),
    template="plotly_white",
    font=dict(family="Tajawal", size=16),
    height=450
)
st.plotly_chart(fig)

# ====== SWOT MATRIX OUTPUT ======
st.markdown("""
<h4 style='margin-top: 30px;'>🧠 مصفوفة SWOT الذكية</h4>
<ul style='font-size:17px;'>
<li><strong>نقاط القوة:</strong> {}</li>
<li><strong>نقاط الضعف:</strong> {}</li>
<li><strong>الفرص:</strong> {}</li>
<li><strong>التهديدات:</strong> سيتم تحليلها لاحقًا بناءً على السوق.</li>
</ul>
""".format(', '.join(swot['قوة']) or 'لا توجد', ', '.join(swot['ضعف']) or 'لا توجد', ', '.join(swot['فرصة']) or 'لا توجد'), unsafe_allow_html=True)

# ====== SIGNATURE & FOOTER ======
st.markdown("""
<p style='text-align:center; font-size:16px; color:#555; margin-top: 40px;'>
💡 تم تطوير هذه المنصة بواسطة: <strong>سُها ناصر سعيد عماره</strong> – مشروع تخرج كلية التجارة 2025
</p>
""", unsafe_allow_html=True)

# Future extensions: PDF/Excel Export, Real-time tracking, ML decision model, ERP/Odoo integration, benchmarking DB (مرحلة قادمة) 
