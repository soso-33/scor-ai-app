# منصة SCOR AI المتكاملة - مشروع التخرج
# تصميم: سُها ناصر سعيد عماره  |  إشراف: أ.د. عماد قمحاوي

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import io
import json

# ====== إعداد الصفحة ======
# st.set_page_config(page_title="منصة SCOR الذكية", layout="centered")

# ====== التصميم العام والخط ======
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

# ====== تعريف تسميات مراحل SCOR ليتم استخدامها في كل الصفحات ======
phase_labels = {
    "Plan": "📘 التخطيط",
    "Source": "📗 التوريد",
    "Make": "📙 التصنيع",
    "Deliver": "📕 التوزيع",
    "Return": "📒 المرتجعات"
}

# ====== التنقل الجانبي ======
st.sidebar.title("🔍 أقسام المنصة")
page = st.sidebar.radio("اختر الصفحة:", [
    "🧪 التقييم",
    "📊 النتائج والتحليل",
    "🤖 التوصيات الذكية",
    "🏢 مقارنة الشركات"
])

# ====== حالة الجلسة ======
if 'results' not in st.session_state:
    st.session_state.results = {}
    st.session_state.iot_avg = 0
    st.session_state.swot = {"قوة": [], "ضعف": [], "فرصة": [], "تهديد": []}
    st.session_state.bcg_importance = {}
    st.session_state.user_info = {}

# ====== دالة لحفظ النتائج ======
def save_results_to_excel(user_name, company_name, sector, country, iot_avg, results):
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

# ====== PAGE 1: EVALUATION ======
if page == "🧪 التقييم":
    st.header("🧪 التقييم العام")
    st.sidebar.header("📌 بيانات المستخدم")

    # إعداد المتغيرات في الحالة
    if "started" not in st.session_state:
        st.session_state.started = False

    if not st.session_state.started:
        with st.sidebar.form("user_form"):
            user_name = st.text_input("الاسم الكامل")
            company_name = st.text_input("اسم الشركة أو المؤسسة")
            sector = st.selectbox("القطاع", ["الرعاية الصحية", "التصنيع", "اللوجستيات", "الخدمات", "أخرى"])
            country = st.text_input("الدولة")
            save_results = st.checkbox("أوافق على حفظ نتائجي للمقارنة لاحقًا")
            submitted = st.form_submit_button("ابدأ التقييم")

        if submitted:
            st.session_state.user_info = {
                'name': user_name,
                'company': company_name,
                'sector': sector,
                'country': country,
                'save_results': save_results
            }
            st.session_state.started = True
        else:
            st.warning("👈 برجاء إدخال البيانات والضغط على 'ابدأ التقييم' لعرض الأسئلة.")
            st.stop()

    # بعد ملء البيانات نبدأ عرض الأسئلة
    user_info = st.session_state.user_info
    save_results = user_info.get("save_results", False)

    try:
        df = pd.read_excel("SCOR_AI_Questions.xlsx")
    except:
        st.error("❌ تأكد من وجود ملف SCOR_AI_Questions.xlsx في نفس مجلد الكود.")
        st.stop()

    scor_phases = df['SCOR Phase'].unique()

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
        save_results_to_excel(user_info["name"], user_info["company"], user_info["sector"], user_info["country"], iot_avg, results)


# منصة SCOR AI المتكاملة - مشروع التخرج
# تصميم: سُهى ناصر سعيد عماره - تحت إشراف: د. عماد كمهاوي

import streamlit as st
import plotly.graph_objs as go
import pandas as pd
import json
from fpdf import FPDF
import base64
from io import BytesIO

# إعدادات الصفحة
st.set_page_config(page_title="SCOR AI Platform", layout="wide")

# تخزين الجلسة
if "results" not in st.session_state:
    st.session_state.results = {}
if "swot" not in st.session_state:
    st.session_state.swot = {"قوة": [], "ضعف": [], "فرصة": [], "تهديد": []}
if "iot_avg" not in st.session_state:
    st.session_state.iot_avg = 0
if "user_info" not in st.session_state:
    st.session_state.user_info = {"name": "", "company": ""}
if "ife_scores" not in st.session_state:
    st.session_state.ife_scores = []
if "efe_scores" not in st.session_state:
    st.session_state.efe_scores = []

# --- واجهة المستخدم ---
pages = ["🏠 الصفحة الرئيسية", "📝 التقييم", "📊 النتائج والتحليل"]
page = st.sidebar.radio("انتقل إلى الصفحة:", pages)

phase_labels = {
    "Plan": "التخطيط (Plan)",
    "Make": "الإنتاج (Make)",
    "Source": "التوريد (Source)",
    "Deliver": "التوصيل (Deliver)",
    "Return": "الإرجاع (Return)",
    "Enable": "التمكين (Enable)"
}

# ====== PAGE: RESULTS & ANALYSIS ======
if page == "📊 النتائج والتحليل":
    st.header("📊 النتائج ومصفوفات التحليل")
    results = st.session_state.results
    swot = st.session_state.swot
    iot_avg = st.session_state.iot_avg
    user = st.session_state.user_info

    if not results:
        st.warning("يرجى تنفيذ التقييم أولًا.")
        st.stop()

    # --- رسم بياني: SCOR Readiness ---
    labels = list(results.keys())
    values = list(results.values())
    fig = go.Figure([go.Bar(x=labels, y=values, text=[f"{v:.1f}" for v in values], textposition='auto')])
    fig.update_layout(title="تقييم جاهزية مراحل SCOR", yaxis_range=[0,5], height=400)
    st.plotly_chart(fig)

    # --- تحليل جاهزية SCOR ---
    st.subheader("🔍 تحليل التقييم العام:")
    for phase, score in results.items():
        status = (
            "🔴 منخفضة" if score < 2 else
            "🟠 متوسطة" if score < 3.5 else
            "🟢 مرتفعة"
        )
        st.markdown(f"- **{phase_labels.get(phase, phase)}**: {score:.1f} → {status}")

    # --- تحليل IoT ---
    st.subheader("🤖 تقييم جاهزية إنترنت الأشياء IoT:")
    if iot_avg:
        iot_status = (
            "🔴 منخفضة" if iot_avg < 2 else
            "🟠 متوسطة" if iot_avg < 3.5 else
            "🟢 مرتفعة"
        )
        st.markdown(f"متوسط تقييم IoT: **{iot_avg:.1f}** → {iot_status}")
    else:
        st.markdown("لم يتم تقييم IoT بعد.")

    # --- تحليل SWOT إلى IFE و EFE ---
    st.subheader("📌 تقييم IFE و EFE")
    st.markdown("أدخل الأوزان والتقييم لكل عامل داخلي (IFE) وخارجي (EFE):")

    ife_inputs = []
    efe_inputs = []
    for i, item in enumerate(swot['قوة'] + swot['ضعف']):
        weight = st.number_input(f"📌 {item} (الوزن الداخلي)", 0.0, 1.0, 0.1, step=0.05, key=f"ife_weight_{i}")
        rating = st.slider(f"التقييم لـ {item} (1-4)", 1, 4, 3, key=f"ife_rating_{i}")
        ife_inputs.append(weight * rating)
    st.session_state.ife_scores = ife_inputs

    for i, item in enumerate(swot['فرصة'] + swot['تهديد']):
        weight = st.number_input(f"🌐 {item} (الوزن الخارجي)", 0.0, 1.0, 0.1, step=0.05, key=f"efe_weight_{i}")
        rating = st.slider(f"التقييم لـ {item} (1-4)", 1, 4, 3, key=f"efe_rating_{i}")
        efe_inputs.append(weight * rating)
    st.session_state.efe_scores = efe_inputs

    ife_total = sum(ife_inputs)
    efe_total = sum(efe_inputs)
    st.success(f"✅ مجموع IFE: {ife_total:.2f} | مجموع EFE: {efe_total:.2f}")

    # --- Radar Chart ---
    st.subheader("📡 مقارنة IFE مقابل EFE (رادار)")
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=[ife_total]*6, theta=list(results.keys()), fill='toself', name='IFE'))
    fig_radar.add_trace(go.Scatterpolar(r=[efe_total]*6, theta=list(results.keys()), fill='toself', name='EFE'))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,5])), showlegend=True)
    st.plotly_chart(fig_radar)

    # --- توصيات استراتيجية ---
    st.subheader("🧭 التوصيات الاستراتيجية:")
    strategy = ""
    if ife_total >= 3 and efe_total >= 3:
        strategy = "💼 استراتيجية النمو والفرص (Growth Strategy)"
    elif ife_total < 3 and efe_total >= 3:
        strategy = "🔄 استراتيجية التحول والتحسين (Turnaround Strategy)"
    elif ife_total >= 3 and efe_total < 3:
        strategy = "🛡️ استراتيجية الدفاع (Defensive Strategy)"
    else:
        strategy = "⚠️ استراتيجية البقاء والنجاة (Survival Strategy)"
    st.markdown(f"**الاستراتيجية المقترحة:** {strategy}")

    # --- تصدير PDF ---
    st.subheader("📤 تحميل تقرير التوصيات PDF")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"AI Strategic Report - {user['company']}", ln=True, align="C")
    pdf.cell(200, 10, txt=f"User: {user['name']}", ln=True)
    pdf.cell(200, 10, txt=f"IFE Total: {ife_total:.2f} | EFE Total: {efe_total:.2f}", ln=True)
    pdf.multi_cell(0, 10, txt=f"Recommended Strategy: {strategy}")

    buffer = BytesIO()
    pdf.output(buffer)
    b64_pdf = base64.b64encode(buffer.getvalue()).decode()
    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="SCOR_Strategy_{user['company']}.pdf">📄 Download PDF</a>'
    st.markdown(href, unsafe_allow_html=True)

    # --- تصدير Excel ---
    st.subheader("📤 تحميل Excel لنتائج IFE و EFE")
    df_export = pd.DataFrame({"IFE Scores": st.session_state.ife_scores, "EFE Scores": st.session_state.efe_scores})
    excel_buffer = BytesIO()
    df_export.to_excel(excel_buffer, index=False)
    st.download_button("⬇️ تحميل Excel", data=excel_buffer.getvalue(), file_name="IFE_EFE_Scores.xlsx", mime="application/vnd.ms-excel")
elif page == "🤖 التوصيات الذكية":
    st.header("🤖 التوصيات الذكية بناءً على نتائج التقييم")

    if not st.session_state.results:
        st.warning("يرجى تنفيذ التقييم أولًا.")
        st.stop()

    st.subheader("🔍 توصيات خاصة بكل مرحلة من SCOR:")
    for phase, score in st.session_state.results.items():
        if score < 2:
            st.error(f"🔴 {phase_labels[phase]}: تحتاج إلى إعادة تصميم شاملة.")
        elif score < 3.5:
            st.warning(f"🟠 {phase_labels[phase]}: يُنصح بتحسين العمليات باستخدام أدوات الذكاء الاصطناعي.")
        else:
            st.success(f"🟢 {phase_labels[phase]}: أداء جيد ويمكن تعزيزه بالتحسين المستمر.")

    st.subheader("🤖 أدوات الذكاء الاصطناعي المقترحة:")
    st.markdown("""
    - التخطيط: استخدام **التحليلات التنبؤية (Predictive Analytics)** لتحسين توقعات الطلب.
    - التوريد: أنظمة **الشراء التلقائي (Automated Procurement)** باستخدام AI.
    - التصنيع: دمج **الروبوتات الذكية (Smart Robotics)** في خطوط الإنتاج.
    - التوزيع: تطبيق **تحسين المسارات بالذكاء الاصطناعي** لتقليل وقت التسليم.
    - المرتجعات: نظام **إدارة المرتجعات الذكي** لتحديد أسباب الإرجاع وتقليلها.
    """)

    st.subheader("📡 توصيات IoT والتكامل اللحظي:")
    if st.session_state.iot_avg < 3:
        st.warning("⚠️ يوصى بدمج تقنيات IoT مثل المستشعرات ولوحات البيانات اللحظية لرفع الكفاءة.")
    else:
        st.success("✅ جاهزية IoT جيدة. يمكن تعزيز التكامل مع ERP/DSS.")
elif page == "🏢 مقارنة الشركات":
    st.header("🏢 مقارنة الأداء بين الشركات")

    try:
        df_bench = pd.read_excel("benchmark_data.xlsx")
    except:
        st.warning("⚠️ لا توجد بيانات مقارنة محفوظة حتى الآن.")
        st.stop()

    st.dataframe(df_bench)

    st.subheader("📈 مقارنة حسب المرحلة:")
    selected_phase = st.selectbox("اختر المرحلة", list(phase_labels.keys()))
    if selected_phase in df_bench.columns:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_bench["الشركة"],
            y=df_bench[selected_phase],
            text=df_bench[selected_phase],
            textposition="auto"
        ))
        fig.update_layout(title=f"مقارنة جاهزية الشركات - {phase_labels[selected_phase]}")
        st.plotly_chart(fig)

    st.subheader("📉 متوسط IoT لكل شركة:")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=df_bench["الشركة"],
        y=df_bench["متوسط IoT"],
        text=df_bench["متوسط IoT"],
        textposition="auto"
    ))
    st.plotly_chart(fig2)

# ====== PAGE 3: AI Recommendations ======
elif page == "🤖 التوصيات الذكية ومعلومات التخرج":
    st.header("🤖 التوصيات الذكية المدعومة بالذكاء الاصطناعي")

    results = st.session_state.results
    iot_avg = st.session_state.iot_avg
    swot = st.session_state.swot

    if not results:
        st.warning("يرجى تنفيذ التقييم أولًا.")
        st.stop()

    st.subheader("✨ توصيات ذكية حسب الجاهزية في مراحل SCOR")
    for phase, score in results.items():
        label = phase_labels.get(phase, phase)
        if score < 2.5:
            st.markdown(f"🔴 **{label}:** منخفض الجاهزية. يُوصى باستخدام RPA، والتنبؤ الآلي بالطلب (AutoML)، وتبسيط العمليات.")
        elif score < 4:
            st.markdown(f"🟡 **{label}:** متوسط الجاهزية. يُوصى بتوسيع التكامل مع أنظمة ERP، وتفعيل لوحات تحكم ذكية، وتحليل بيانات الموردين باستخدام ML.")
        else:
            st.markdown(f"🟢 **{label}:** جاهزية عالية. يُوصى بتفعيل التعلم الآلي والتنبؤات الذكية، مثل الصيانة التنبؤية وتحسين توجيه الشحنات.")

    st.subheader("🌐 جاهزية إنترنت الأشياء (IoT)")
    if iot_avg < 2:
        st.error("منخفضة جدًا. يُنصح بتركيب حساسات وربطها بالأنظمة الرقمية وبدء تجميع البيانات.")
    elif iot_avg < 4:
        st.warning("متوسطة. يُنصح بتحسين الاتصالات وتحليل البيانات باستخدام أنظمة Edge AI.")
    else:
        st.success("جاهزية ممتازة لإنترنت الأشياء. يُوصى بالانتقال إلى Digital Twin ونماذج محاكاة ذكية.")

    st.subheader("🏁 توصيات استراتيجية ذكية")
    if "ضعف" in swot and swot["ضعف"]:
        st.markdown("- 📉 **نقاط الضعف:** " + ", ".join(swot["ضعف"]))
        st.markdown("  - 🛠️ **حلول مقترحة:** أتمتة المعالجة اليدوية، بناء نظام DSS متكامل، تدريب المستخدمين.")
    if "فرصة" in swot and swot["فرصة"]:
        st.markdown("- 🚀 **الفرص:** " + ", ".join(swot["فرصة"]))
        st.markdown("  - 🌟 **استغلال مقترح:** تطوير خدمات جديدة مدعومة بالذكاء الاصطناعي وتحقيق ميزة تنافسية.")
    if "قوة" in swot and swot["قوة"]:
        st.markdown("- 🛡️ **نقاط القوة:** " + ", ".join(swot["قوة"]))
        st.markdown("  - ✅ **تعظيم الاستفادة:** استخدام القدرات الحالية لتسريع التحول الرقمي وتوسيع استخدام AI.")

    st.markdown("---")
    st.subheader("🔧 حلول متقدمة لإعادة تصميم الخدمة (Service Redesign)")
    st.markdown("""
    - 🧩 **تحليل الوضع الحالي (As-Is):** تحديد نقاط الفشل والعمليات اليدوية.
    - 🔄 **إعادة تصميم الخدمة:**
      - أتمتة العمليات باستخدام RPA وPython.
      - التكامل مع أنظمة ERP/DSS.
      - إدخال طبقة ذكاء اصطناعي AutoML للتنبؤ وتحسين الأداء.
    - 🎯 **تفعيل التحسين المستمر:** باستخدام لوحات التحكم التفاعلية وتحليلات الوقت الحقيقي.
    """)

    st.markdown("---")
    st.subheader("📊 توصيات دعم القرار باستخدام أدوات متقدمة")
    st.markdown("""
    - ⚖️ **خوارزمية الأولوية الذكية:**
      > `الأولوية = (الأهمية × التأثير × جاهزية الذكاء الاصطناعي) / مستوى الخطر`
    - 🧠 **توصيات أدوات وتقنيات:**
        - AutoML / Azure ML / Google Vertex AI
        - IoT Sensors / Digital Twin
        - Power BI + Python Dashboards
        - Reinforcement Learning لتحسين العمليات
        - Chatbots ذكية للطلب والتفاعل
    """)

    st.success("✅ شكراً لاستخدامك المنصة. يمكنك الآن تحميل التوصيات أو العودة للتقييم.")

    # PDF download button
    import io
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 800, "📄 توصيات الذكاء الاصطناعي بناءً على تقييم SCOR")
    y = 770
    for phase, score in results.items():
        pdf.drawString(50, y, f"{phase_labels.get(phase, phase)}: {score}")
        y -= 20
    pdf.drawString(50, y-10, f"متوسط IoT: {iot_avg:.2f}")
    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    st.download_button("📥 تحميل التوصيات PDF", buffer, file_name="توصيات_SCOR_AI.pdf", mime="application/pdf")

# ====== PAGE 4: Graduation Info ======
elif page == "📄 معلومات مشروع التخرج":
    st.header("📄 معلومات مشروع التخرج")

    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Graduation_hat.svg/800px-Graduation_hat.svg.png", width=100)
    with col2:
        st.markdown("""
        ### 🎓 العنوان الكامل للمشروع:
        **منصة تقييم جاهزية الذكاء الاصطناعي في سلاسل الإمداد باستخدام نموذج SCOR**

        ### 🧕 الطالبة:
        **سُها ناصر سعيد عماره**

        ### 👨‍🏫 المشرف:
        **أ.د. عماد كمّاهى**

        ### 🏫 الجامعة:
        **[القاهرة]**

        ### 📅 العام الدراسي:
        **2024 - 2025**
        """)

    st.markdown("---")
    st.subheader("🛠️ تقنيات وأدوات التطوير المستخدمة")
    st.markdown("""
    - لغة Python
    - مكتبة Streamlit لواجهة المستخدم
    - تحليل SCOR وSWOT وBCG
    - الذكاء الاصطناعي AutoML + IoT
    - تقارير PDF وExcel تفاعلية
    - قاعدة بيانات SQLite
    - Dashboards وPower BI
    - دعم توصيات ذكية وتحسين الخدمات
    """)

    st.markdown("---")
    st.info("🧑‍💻 تم تطوير هذه المنصة كجزء من مشروع تخرج بكلية [اسم الكلية]، وتهدف إلى تمكين المؤسسات من تقييم جاهزيتها للتحول الذكي باستخدام أحدث الأدوات.")
    st.success("✅ شكراً لاهتمامك بمشروع التخرج 💚")
