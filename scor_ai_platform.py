# منصة SCOR AI المتكاملة - مشروع التخرج
# تصميم: سُها ناصر سعيد عماره  |  إشراف: أ.د. عماد قمحاوي
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go  # <-- أضف هذا السطر
from fpdf import FPDF
from io import BytesIO
import base64

# ===== إعداد التصميم العام =====
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
    .centered {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        padding: 2rem;
        background-color: #f9f9f9;
        border-radius: 1rem;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
</style>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ===== تسميات مراحل SCOR =====
phase_labels = {
    "Plan": "📘 التخطيط",
    "Source": "📗 التوريد",
    "Make": "📙 التصنيع",
    "Deliver": "📕 التوزيع",
    "Return": "📒 المرتجعات"
}

# ===== حالة الجلسة =====
if 'results' not in st.session_state:
    st.session_state.results = {}
    st.session_state.iot_avg = 0
    st.session_state.swot = {"قوة": [], "ضعف": [], "فرصة": [], "تهديد": []}
    st.session_state.user_info = {}

# ===== دالة الحفظ =====
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

# **هنا نضيف اختيار الصفحة:**
page = st.sidebar.selectbox("📌 اختر الصفحة", [
    "🏠 الصفحة الرئيسية",
    "📝 التقييم",
    "📊 النتائج والتحليل",
    "🤖 التوصيات الذكية",
    "🏢 مقارنة الشركات",
    "📊 مصفوفة BCG"
])

)

if page == "🏠 الصفحة الرئيسية":
    st.title("🤖 منصة SCOR AI المتكاملة لتقييم جاهزية الذكاء الاصطناعي")


    st.markdown("""
    ### 👋 مرحبًا بك في منصتك الذكية!
    
    تهدف هذه المنصة إلى مساعدتك في:
    - تقييم مدى **جاهزية مؤسستك** لتطبيق تقنيات الذكاء الاصطناعي في سلاسل الإمداد.
    - استخدام نموذج **SCOR** العالمي كمقياس معياري.
    - دمج **تحليل إنترنت الأشياء (IoT)** لرؤية شاملة.
    - الحصول على **توصيات ذكية وتلقائية** مبنية على نتائج التقييم.

    ### 🧭 خطوات الاستخدام:
    1. انتقل إلى صفحة **📝 التقييم** وأجب عن الأسئلة.
    2. اطلع على نتائجك في صفحة **📊 النتائج والتحليل**.
    3. تصفح صفحة **💡 التوصيات الذكية** للحصول على اقتراحات مخصصة.
    4. جرّب صفحة **🏢 مقارنة الشركات** لمقارنة الأداء الرقمي بين شركاتك أو منافسيك.

    ---
    🎯 **ابدأ الآن وقيّم مدى استعدادك للتحول الذكي!**
    """)

    st.image("https://cdn-icons-png.flaticon.com/512/3208/3208711.png", width=200)

elif page == "🧪 التقييم":
    # يمكنك لاحقًا إضافة كود التقييم هنا
    st.markdown("""
        <style>
        .centered {
            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="centered">', unsafe_allow_html=True)
    st.header("🧪 التقييم العام")
    st.markdown('</div>', unsafe_allow_html=True)


# إدخال بيانات المستخدم
if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    with st.form("user_form"):
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

user_info = st.session_state.user_info
save_results = user_info.get("save_results", False)

# قراءة الأسئلة
try:
    df = pd.read_excel("SCOR_AI_Questions.xlsx")
except:
    st.error("❌ تأكد من وجود ملف SCOR_AI_Questions.xlsx في نفس مجلد التطبيق.")
    st.stop()

scor_phases = df['SCOR Phase'].unique()

results = {}
colors = []
swot = {"قوة": [], "ضعف": [], "فرصة": [], "تهديد": []}

# عرض الأسئلة حسب المرحلة
for phase in scor_phases:
    with st.expander(f"🔹 مرحلة: {phase_labels.get(phase, phase)}", expanded=False):
        phase_df = df[df['SCOR Phase'] == phase]
        total = 0
        for _, row in phase_df.iterrows():
            score = st.slider(f"🔘 {row['Question (AR)']}", 1, 5, 3, key=row['Question (AR)'])
            total += score
        avg = total / len(phase_df)
        results[phase] = avg

if avg >= 4:
    st.success("🟢 ممتاز جدًا! مؤسستك على الطريق الصحيح في هذه المرحلة 💪")
    colors.append("#2ECC71")  # لون أخضر مميز
    swot["قوة"].append(phase_labels[phase])

elif avg >= 3:
    st.info("🟡 جيد جدًا! يمكن تعزيز هذه المرحلة ببعض التحسينات")
    colors.append("#F1C40F")  # لون أصفر واضح
    swot["فرصة"].append(phase_labels[phase])

elif avg >= 2:
    st.warning("🟠 أداء مقبول، يُنصح بالتحسين في هذه المرحلة")
    colors.append("#E67E22")
    swot["فرصة"].append(phase_labels[phase])

else:
    st.error("🔴 ضعيف! تحتاج هذه المرحلة إلى إعادة نظر وتطوير جاد 🚨")
    colors.append("#E74C3C")
    swot["ضعف"].append(phase_labels[phase])

# تقييم IoT
with st.expander("📡 تقييم جاهزية IoT والتتبع اللحظي"):
    q1 = st.slider("هل تستخدم أجهزة استشعار؟", 1, 5, 3)
    q2 = st.slider("هل لديك لوحات تحكم لحظية؟", 1, 5, 3)
    q3 = st.slider("هل تحلل البيانات لحظيًا؟", 1, 5, 3)
    q4 = st.slider("هل تتكامل البيانات مع ERP؟", 1, 5, 3)
    iot_avg = (q1 + q2 + q3 + q4) / 4
    st.markdown(f"**متوسط جاهزية IoT: {iot_avg:.1f}/5**")

# حفظ النتائج في الجلسة
st.session_state.results = results
st.session_state.iot_avg = iot_avg
st.session_state.swot = swot

if save_results:
    save_results_to_excel(user_info["name"], user_info["company"], user_info["sector"], user_info["country"], iot_avg, results)
    
elif page == "📊 النتائج والتحليل":
    # ضع هنا جزء تحليل النتائج من: رسم بياني، SWOT، IFE/EFE، التوصيات، التصدير...

    st.markdown("## 📊 النتائج ومصفوفات التحليل")
    st.divider()

    # تحقق من وجود بيانات التقييم
    if "results" not in st.session_state or not st.session_state.results:
        st.warning("يرجى تنفيذ التقييم أولًا.")
        st.stop()

# ====== صفحة التقييم ======
elif page == "📝 التقييم":
    st.header("📝 تقييم جاهزية الذكاء الاصطناعي حسب نموذج SCOR")

    results = {}

    for phase, label in phase_labels.items():
        st.subheader(f"{label}")
        score = st.slider(f"قيّم مرحلة {label}", 1, 5, 3, key=phase)

        # عكس تقييم المرتجعات
        if phase == "Return":
            score = 6 - score  # تحويل 5 إلى 1، و1 إلى 5

        results[phase] = score

    # حفظ النتائج في session_state
    st.session_state.results = results

    # حفظ باقي البيانات
    swot = st.session_state.swot
    iot_avg = st.session_state.iot_avg

    if "user_info" not in st.session_state:
        st.warning("⚠️ يرجى تنفيذ التقييم أولًا.")
        st.stop()

    user = st.session_state.user_info

    # عرض ملخص سريع
    if st.button("📊 عرض النتائج"):
        avg_score = sum(results.values()) / len(results)
        st.success(f"✅ تم حفظ النتائج بنجاح. متوسط التقييم: {avg_score:.2f}")


    # --- 1. رسم بياني SCOR ---
    st.subheader("🎯 تقييم جاهزية مراحل SCOR")
    labels = list(results.keys())
    values = list(results.values())
    fig = go.Figure([go.Bar(x=labels, y=values, text=[f"{v:.1f}" for v in values], textposition='auto')])
    fig.update_layout(title="SCOR Readiness", yaxis_range=[0, 5], height=400)
    st.plotly_chart(fig)
    st.divider()

# --- 2. تحليل التقييم العام ---
st.subheader("🔍 تحليل التقييم العام")
for phase, score in results.items():
    status = "🔴 منخفضة" if score < 2 else "🟠 متوسطة" if score < 3.5 else "🟢 مرتفعة"
    st.markdown(f"- **{phase_labels.get(phase, phase)}**: {score:.1f} → {status}")
st.divider()

# --- 3. تحليل IoT ---
st.subheader("🤖 تقييم إنترنت الأشياء (IoT)")
if iot_avg:
    iot_status = "🔴 منخفضة" if iot_avg < 2 else "🟠 متوسطة" if iot_avg < 3.5 else "🟢 مرتفعة"
    st.markdown(f"متوسط تقييم IoT: **{iot_avg:.1f}** → {iot_status}")
else:
    st.markdown("⚠️ لم يتم تقييم IoT بعد.")
st.divider()

# --- 4. تقييم IFE و EFE ---
st.subheader("📌 تقييم IFE و EFE")
st.markdown("يرجى إدخال الوزن والتقييم لكل عامل داخلي وخارجي:")

ife_inputs = []
efe_inputs = []

# عوامل IFE
for i, item in enumerate(swot['قوة'] + swot['ضعف']):
    weight = st.number_input(f"📌 {item} (الوزن الداخلي)", 0.0, 1.0, 0.1, step=0.05, key=f"ife_weight_{i}")
    rating = st.slider(f"التقييم لـ {item} (1-4)", 1, 4, 3, key=f"ife_rating_{i}")
    ife_inputs.append(weight * rating)

# عوامل EFE
for i, item in enumerate(swot['فرصة'] + swot['تهديد']):
    weight = st.number_input(f"🌐 {item} (الوزن الخارجي)", 0.0, 1.0, 0.1, step=0.05, key=f"efe_weight_{i}")
    rating = st.slider(f"التقييم لـ {item} (1-4)", 1, 4, 3, key=f"efe_rating_{i}")
    efe_inputs.append(weight * rating)

ife_total = sum(ife_inputs)
efe_total = sum(efe_inputs)

st.success(f"✅ مجموع IFE: {ife_total:.2f} | مجموع EFE: {efe_total:.2f}")
st.divider()

# --- 5. رادار IFE vs EFE ---
st.subheader("📡 مقارنة IFE مقابل EFE (رادار)")
fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(r=[ife_total]*6, theta=list(results.keys()), fill='toself', name='IFE'))
fig_radar.add_trace(go.Scatterpolar(r=[efe_total]*6, theta=list(results.keys()), fill='toself', name='EFE'))
fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,5])), showlegend=True)
st.plotly_chart(fig_radar)
st.divider()

# --- 6. التوصيات الاستراتيجية ---
st.subheader("🧭 التوصيات الاستراتيجية")
if ife_total >= 3 and efe_total >= 3:
    strategy = "💼 استراتيجية النمو والفرص (Growth Strategy)"
elif ife_total < 3 and efe_total >= 3:
    strategy = "🔄 استراتيجية التحول والتحسين (Turnaround Strategy)"
elif ife_total >= 3 and efe_total < 3:
    strategy = "🛡️ استراتيجية الدفاع (Defensive Strategy)"
else:
    strategy = "⚠️ استراتيجية البقاء والنجاة (Survival Strategy)"
st.markdown(f"**الاستراتيجية المقترحة:** {strategy}")
st.divider()

# --- 7. تصدير PDF ---
st.subheader("📤 تحميل تقرير التوصيات PDF")
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt=f"AI Strategic Report - {st.session_state.user_info['الشركة']}", ln=True, align="C")
pdf.cell(200, 10, txt=f"User: {user['name']}", ln=True)
pdf.cell(200, 10, txt=f"IFE Total: {ife_total:.2f} | EFE Total: {efe_total:.2f}", ln=True)
pdf.multi_cell(0, 10, txt=f"Recommended Strategy: {strategy}")

buffer = BytesIO()
pdf_output = pdf.output(dest='S').encode('latin-1')  # ← تصحيح مهم
buffer.write(pdf_output)
b64_pdf = base64.b64encode(buffer.getvalue()).decode()

href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="SCOR_Strategy_{user["company"]}.pdf">📄 تحميل التقرير PDF</a>'
st.markdown(href, unsafe_allow_html=True)
st.divider()

# --- 8. تصدير Excel ---
st.subheader("📤 تحميل نتائج IFE و EFE Excel")
df_export = pd.DataFrame({
    "IFE Scores": ife_inputs + [None] * (len(efe_inputs) - len(ife_inputs)),
    "EFE Scores": efe_inputs + [None] * (len(ife_inputs) - len(efe_inputs))
})
excel_buffer = BytesIO()
df_export.to_excel(excel_buffer, index=False)
st.download_button("⬇️ تحميل Excel", data=excel_buffer.getvalue(), file_name="IFE_EFE_Scores.xlsx", mime="application/vnd.ms-excel")
if page == "🤖 التوصيات الذكية":
    # كود التوصيات

    # التوصيات الذكية بناءً على نتائج SCOR وIoT وSWOT

    st.header("🤖 التوصيات الذكية المدعومة بالذكاء الاصطناعي")
    st.divider()

    results = st.session_state.get("results", {})
    iot_avg = st.session_state.get("iot_avg", 0)
    swot = st.session_state.get("swot", {})

    if not results:
        st.warning("يرجى تنفيذ التقييم أولًا.")
        st.stop()

    # --- توصيات حسب مراحل SCOR ---
    st.subheader("✨ توصيات حسب الجاهزية في مراحل SCOR")
    for phase, score in results.items():
        label = phase_labels.get(phase, phase)
        if score < 2.5:
            st.markdown(f"🔴 **{label}:** منخفض الجاهزية. يُوصى باستخدام RPA، والتنبؤ الآلي بالطلب (AutoML)، وتبسيط العمليات.")
        elif score < 4:
            st.markdown(f"🟠 **{label}:** متوسط الجاهزية. يُوصى بتوسيع التكامل مع أنظمة ERP، وتفعيل لوحات تحكم ذكية، وتحليل بيانات الموردين باستخدام ML.")
        else:
            st.markdown(f"🟢 **{label}:** جاهزية عالية. يُوصى بتفعيل التعلم الآلي والتنبؤات الذكية، مثل الصيانة التنبؤية وتحسين توجيه الشحنات.")
    st.divider()

    # --- توصيات IoT ---
    st.subheader("🌐 جاهزية إنترنت الأشياء (IoT)")
    if iot_avg < 2:
        st.error("منخفضة جدًا. يُنصح بتركيب حساسات وربطها بالأنظمة الرقمية وبدء تجميع البيانات.")
    elif iot_avg < 4:
        st.warning("متوسطة. يُنصح بتحسين الاتصالات وتحليل البيانات باستخدام أنظمة Edge AI.")
    else:
        st.success("جاهزية ممتازة لإنترنت الأشياء. يُوصى بالانتقال إلى Digital Twin ونماذج محاكاة ذكية.")
    st.divider()

    # --- توصيات SWOT ---
    st.subheader("🏁 توصيات استراتيجية ذكية")
    if swot.get("ضعف"):
        st.markdown("- 📉 **نقاط الضعف:** " + ", ".join(swot["ضعف"]))
        st.markdown("  - 🛠️ **حلول:** أتمتة المعالجة اليدوية، بناء نظام DSS، تدريب الموظفين.")
    if swot.get("فرصة"):
        st.markdown("- 🚀 **الفرص:** " + ", ".join(swot["فرصة"]))
        st.markdown("  - 🌟 **استغلال:** تطوير خدمات مدعومة بالذكاء الاصطناعي وتحقيق ميزة تنافسية.")
    if swot.get("قوة"):
        st.markdown("- 🛡️ **نقاط القوة:** " + ", ".join(swot["قوة"]))
        st.markdown("  - ✅ **تعظيم:** استغلال الموارد الحالية لتوسيع التحول الرقمي واستخدام AI.")
    st.divider()


    # --- إعادة تصميم الخدمة ---
    st.subheader("🔧 حلول متقدمة لإعادة تصميم الخدمة")
    st.markdown("""
    - 🧩 **تحليل As-Is:** حصر نقاط الضعف والعمليات اليدوية.
    - 🔄 **إعادة تصميم:**
        - أتمتة العمليات بـ RPA وPython.
        - التكامل مع أنظمة ERP و DSS.
        - استخدام AutoML للتنبؤ وتحسين الأداء.
    - 🎯 **التحسين المستمر:** عبر لوحات تحكم تفاعلية وتحليلات الوقت الحقيقي.
    """)
    st.divider()

    # --- أدوات دعم القرار ---
    st.subheader("📊 دعم القرار بأدوات متقدمة")
    st.markdown("""
    - ⚖️ **خوارزمية الأولوية الذكية:**
        > `الأولوية = (الأهمية × التأثير × جاهزية الذكاء الاصطناعي) ÷ مستوى الخطر`
    - 🧠 **أدوات مقترحة:**
        - AutoML / Azure ML / Google Vertex AI
        - IoT Sensors / Digital Twin
        - Power BI + Python Dashboards
        - Reinforcement Learning لتحسين العمليات
        - Chatbots ذكية لخدمة العملاء والطلب
    """)
    st.success("✅ شكراً لاستخدامك المنصة. يمكنك الآن تحميل التوصيات أو العودة للتقييم.")
    st.divider()

    # --- تحميل PDF ---
    st.subheader("📥 تحميل تقرير التوصيات PDF")
    import io
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 800, "📄 تقرير توصيات الذكاء الاصطناعي - منصة SCOR AI")
    y = 770
    for phase, score in results.items():
        pdf.drawString(50, y, f"{phase_labels.get(phase, phase)}: {score:.1f}")
        y -= 20
    pdf.drawString(50, y - 10, f"متوسط تقييم IoT: {iot_avg:.2f}")
    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    st.download_button("📤 تحميل PDF التوصيات", buffer, file_name="توصيات_SCOR_AI.pdf", mime="application/pdf")

# ====== PAGE 4: Graduation Info ======
elif page == "📄 معلومات مشروع التخرج":
    st.header("📄 معلومات مشروع التخرج")

    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Graduation_hat.svg/800px-Graduation_hat.svg.png", width=100)
    with col2:
        st.markdown("""
        ### 🎓 **عنوان المشروع الكامل**  
        منصة تقييم جاهزية الذكاء الاصطناعي في سلاسل الإمداد باستخدام نموذج SCOR

        ### 🧕 **الطالبة**  
        سُها ناصر سعيد عماره

        ### 👨‍🏫 **إشراف**  
        أ.د. عماد قمحاوي

        ### 🏫 **الجامعة**  
        جامعة القاهرة – كلية [اسم الكلية]

        ### 📅 **العام الدراسي**  
        2024 – 2025
        """)

    st.markdown("---")
    st.subheader("🛠️ التقنيات والأدوات المستخدمة")
    st.markdown("""
    - لغة Python
    - مكتبة Streamlit لواجهة المستخدم
    - نماذج SCOR، SWOT، BCG
    - الذكاء الاصطناعي (AutoML) وإنترنت الأشياء (IoT)
    - تقارير PDF وExcel تفاعلية
    - قاعدة بيانات SQLite
    - Power BI لتحليل البيانات
    - دعم التوصيات الذكية وتحسين الخدمات الرقمية
    """)

    st.markdown("---")
    st.info("🧑‍💻 تم تطوير هذه المنصة كمشروع تخرج بهدف دعم المؤسسات في تقييم جاهزيتها للتحول الذكي والرقمي باستخدام أدوات الذكاء الاصطناعي والتحليلات الحديثة.")
    st.success("✅ شكراً لاهتمامك بمشروع التخرج 💚")


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

        st.subheader("📈 ملخص التقييم والتحليل")
        st.subheader("📌 ملخص التوصية الذكية:")

        if avg_score >= 4 and iot_avg >= 4:
            st.success(
                "🚀 مؤسستك جاهزة تمامًا لتطبيق الذكاء الاصطناعي الشامل ✅\n\n"
                "🔹 التوصية: ابدأ فورًا بتكامل حلول AI وERP، واستثمر في الأتمتة الذكية والتحليلات التنبؤية."
            )
        elif avg_score >= 3.5:
            st.info(
                "💡 مؤسستك تمتلك جاهزية قوية لكنها تحتاج بعض التحسينات 🔧\n\n"
                "🔹 التوصية: ركز على تحسين البنية الرقمية وتحسين جودة البيانات."
            )
        elif avg_score >= 2.5:
            st.warning(
                "📉 الجاهزية متوسطة حاليًا\n\n"
                "🔹 التوصية: ابدأ بتطبيقات بسيطة للذكاء الاصطناعي مثل Chatbots أو التنبؤ بالمخزون، مع تطوير بنية البيانات تدريجيًا."
            )
        else:
            st.error(
                "⚠️ الجاهزية منخفضة حاليًا\n\n"
                "🔹 التوصية: راجع العمليات الأساسية، وطوّر البنية التحتية الرقمية قبل البدء في أي تطبيقات ذكاء اصطناعي."
            )

        st.markdown(f"🔍 **متوسط SCOR:** {avg_score:.2f} / 5")
        st.markdown(f"📡 **متوسط IoT:** {iot_avg:.2f} / 5")

    else:
        st.warning("يرجى تنفيذ التقييم أولًا لعرض التوصيات.")

# ====== PAGE 4: BENCHMARKING ======
elif page == "📊 مصفوفة BCG":
    st.header("📊 مصفوفة BCG لتحليل المنتجات أو الوحدات")
    st.markdown("تحليل يساعدك في تحديد أولويات الاستثمار والتوسع بناءً على النمو والحصة السوقية.")

    # مثال بيانات يمكن تعديلها حسب شركتك
    data = pd.DataFrame({
        "المنتج": ["منتج A", "منتج B", "منتج C", "منتج D"],
        "النمو السوقي": [0.3, 0.1, 0.6, 0.05],
        "الحصة السوقية النسبية": [1.5, 0.4, 1.2, 0.3],
        "الإيرادات": [300, 150, 400, 100]
    })

    fig = px.scatter(
        data, 
        x="الحصة السوقية النسبية", 
        y="النمو السوقي", 
        size="الإيرادات", 
        color="المنتج",
        hover_name="المنتج",
        size_max=60,
        title="📊 مصفوفة BCG",
    )

    fig.add_shape(type="line", x0=1, x1=1, y0=0, y1=1, line=dict(dash="dash"))
    fig.add_shape(type="line", x0=0, x1=2, y0=0.2, y1=0.2, line=dict(dash="dash"))

    fig.update_layout(
        xaxis_title="الحصة السوقية النسبية",
        yaxis_title="معدل النمو السوقي",
        yaxis=dict(range=[0, 1]),
        xaxis=dict(range=[0, 2])
    )

    st.plotly_chart(fig)

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

