# منصة SCOR AI المتكاملة - مشروع التخرج
# تصميم: سُها ناصر سعيد عماره  |  إشراف: أ.د. عماد قمحاوي

# ======================= #
#       استيراد المكتبات
# ======================= #
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
from fpdf import FPDF
from io import BytesIO
import base64
import os
import streamlit as st

# ======================= #
#        إعداد الصفحة
# ======================= #
st.set_page_config(
    page_title="منصة SCOR الذكية",
    page_icon="🤖",
    layout="wide",  # أو "centered" حسب تفضيلك
    initial_sidebar_state="expanded"
)

from streamlit_option_menu import option_menu


# ======================= #
#     التنسيق العام (CSS)
# ======================= #
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

# ======================= #
#     تسميات مراحل SCOR
# ======================= #
phase_labels = {
    "Plan": "📘 التخطيط",
    "Source": "📗 التوريد",
    "Make": "📙 التصنيع",
    "Deliver": "📕 التوزيع",
    "Return": "📒 المرتجعات"
}

# ======================= #
#   حالة الجلسة (Session)
# ======================= #
if "results" not in st.session_state:
    st.session_state.results = {}
if "iot_avg" not in st.session_state:
    st.session_state.iot_avg = 0
if "swot" not in st.session_state:
    st.session_state.swot = {"قوة": [], "ضعف": [], "فرصة": [], "تهديد": []}
if "user_info" not in st.session_state:
    st.session_state.user_info = {}
if "started" not in st.session_state:
    st.session_state.started = False

# ======================= #
#   دالة حفظ النتائج Excel
# ======================= #
def save_results_to_excel(user_info, iot_avg, results):
    data = {
        "الاسم": [user_info["name"]],
        "الشركة": [user_info["company"]],
        "القطاع": [user_info["sector"]],
        "الدولة": [user_info["country"]],
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

# ======================= #
#     دالة صفحة التقييم
# ======================= #
def show_assessment_page():
    st.header("📝 التقييم العام")
    st.markdown("""
    <div style="background-color:#fff9db; padding:15px; border-radius:10px; border:1px solid #ffe58f; margin-bottom:20px;">
        <h4 style="color:#8a6d3b;">📌 قبل أن تبدأ التقييم:</h4>
        <ul style="color:#856404; font-size:15px;">
            <li>اقرأ كل سؤال بعناية.</li>
            <li>اختر تقييم من 1 إلى 5 حسب واقع شركتك.</li>
            <li>اضغط على السهم لإظهار كل مرحلة من مراحل SCOR.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.started:
        with st.form("user_form"):
            user_name = st.text_input("الاسم الكامل")
            company_name = st.text_input("اسم الشركة أو المؤسسة")
            sector = st.selectbox("القطاع", ["الرعاية الصحية", "التصنيع", "اللوجستيات", "الخدمات", "أخرى"])
            country = st.text_input("الدولة")
            save_results = st.checkbox("أوافق على حفظ نتائجي للمقارنة لاحقًا")
            submitted = st.form_submit_button("ابدأ التقييم")

        if not submitted:
            st.stop()

        st.session_state.user_info = {
            "name": user_name,
            "company": company_name,
            "sector": sector,
            "country": country,
            "save_results": save_results
        }
        st.session_state.started = True

    try:
        df = pd.read_excel("SCOR_AI_Questions.xlsx")
    except:
        st.error("❌ تأكد من وجود ملف SCOR_AI_Questions.xlsx في نفس مجلد التطبيق.")
        st.stop()

    scor_phases = df['SCOR Phase'].unique()
    results = {}
    swot = {"قوة": [], "ضعف": [], "فرصة": [], "تهديد": []}
    colors = []

    for phase in scor_phases:
        with st.expander(f"🔹 مرحلة: {phase_labels.get(phase, phase)}", expanded=True):
            phase_df = df[df['SCOR Phase'] == phase]
            total = 0
            for idx, row in phase_df.iterrows():
                score = st.slider(f"🔘 {row['Question (AR)']}", 1, 5, 3, key=f"{phase}_{idx}")
                total += score
            avg = total / len(phase_df)
            results[phase] = avg
            if avg >= 4:
                st.success("🔵 ممتاز")
                colors.append("#3498DB")
                swot["قوة"].append(f"{phase_labels[phase]}: تعمل بكفاءة عالية (متوسط: {avg:.1f}/5).")
            elif avg >= 2.5:
                st.warning("🟠 جيد")
                colors.append("#F39C12")
                swot["فرصة"].append(f"{phase_labels[phase]}: مقبول ويوجد فرصة للتحسين (متوسط: {avg:.1f}/5).")
            else:
                st.error("🔴 ضعيف")
                colors.append("#E74C3C")
                swot["ضعف"].append(f"{phase_labels[phase]}: جاهزية منخفضة (متوسط: {avg:.1f}/5).")

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

    if st.session_state.user_info.get("save_results"):
        save_results_to_excel(st.session_state.user_info, iot_avg, results)

# ======================= #
#    تنسيق Sidebar ثابت
# ======================= #

# --- تنسيقات CSS مخصصة للخط والحجم ---
st.markdown("""
    <style>
    /* تغيير حجم الخط لعناصر القائمة */
    section[data-testid="stSidebar"] .css-1d391kg {
        font-size: 20px !important;
    }

    /* تحسين مظهر القائمة الجانبية */
    [data-testid="stSidebar"] {
        background-color: #f9f9f9;
        border-right: 2px solid #CCC;
        padding: 15px;
    }

    /* عنوان واضح ومميز في الـ sidebar */
    .sidebar-title {
        font-size: 26px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 20px;
        text-align: center;
    }

    </style>
""", unsafe_allow_html=True)

# --- عنوان أكاديمي واضح ---
st.sidebar.markdown('<div class="sidebar-title">🎓 لوحة التنقل الأكاديمية</div>', unsafe_allow_html=True)

# --- قائمة التنقل الرئيسية (باستخدام radio لتكون ظاهرة وثابتة) ---
page = st.sidebar.radio("📌 اختر الصفحة", [
    "🏠 الصفحة الرئيسية",
    "📊 لوحة التحكم الرئيسية",
    "📝 التقييم",
    "📊 النتائج والتحليل",
    "🤖 التوصيات الذكية",
    "🏢 مقارنة الشركات",
    "🧾 سجل التقييمات",
    "📆 تحليل الأداء الزمني",
    "📈 تحليل الأداء حسب القطاع",
    "🛠️ لوحة تحكم المشرف",
    "📄 معلومات مشروع التخرج"
])


# ======================= #
#     استدعاء الصفحات
# ======================= #
if page == "🏠 الصفحة الرئيسية":
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    
    # عنوان المشروع الرئيسي بخط أكبر
    st.markdown("""
    <div style='
        background-color:#e0f7fa;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    '>
        <h1 style='text-align: center; color: #004d61;'>منصة التحليل الذكي لأداء سلاسل الإمداد</h1>
    </div>
    """, unsafe_allow_html=True)

    # بيانات الطالبة
    st.markdown("""
    <div style='
        background-color: #fefefe;
        padding: 20px;
        border-left: 6px solid #4db6ac;
        border-radius: 10px;
        margin-bottom: 20px;
    '>
        <h3 style='color:#00796b;'>🧑‍🎓 بيانات الطالبة</h3>
        <ul style='font-size:18px; line-height:1.8; color:#333;'>
            <li><strong>الاسم:</strong> سها ناصر سعيد عماره</li>
            <li><strong>الكلية:</strong> كلية التجارة – جامعة القاهرة</li>
            <li><strong>الفرقة:</strong> ماجستير مهني – رعاية صحية</li>
            <li><strong>مشرف المشروع:</strong> أ.د. عماد قمحاوي</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # عنوان المشروع
    st.markdown("""
    <div style='
        background-color: #fff3e0;
        padding: 20px;
        border-left: 6px solid #ffa726;
        border-radius: 10px;
        margin-bottom: 20px;
    '>
        <h3 style='color:#ef6c00;'>📘 عنوان مشروع التخرج</h3>
        <p style='font-size:18px; color:#444;'>
        <strong>Smart AI Benchmarking Platform for Supply Chain Excellence using SCOR Model</strong><br>
        منصة ذكية لتقييم وتحليل أداء سلاسل الإمداد باستخدام نموذج SCOR والذكاء الاصطناعي.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # فكرة المشروع
    st.markdown("""
    <div style='
        background-color: #e8f5e9;
        padding: 20px;
        border-left: 6px solid #66bb6a;
        border-radius: 10px;
        margin-bottom: 20px;
    '>
        <h3 style='color:#388e3c;'>🎯 فكرة المشروع</h3>
        <p style='font-size:18px; color:#333; line-height:1.8;'>
        يقوم المشروع بتحليل جاهزية الشركات عبر مراحل SCOR (التخطيط، التوريد، التصنيع، التوزيع، المرتجعات)، 
        مع إدماج تقنيات الذكاء الاصطناعي وإنترنت الأشياء، وتقديم توصيات ذكية، مقارنة تنافسية، ولوحات تحكم تفاعلية، 
        بالإضافة إلى التكامل مع أنظمة مثل <strong>Odoo</strong> و<strong>Power BI</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # وسيلة التواصل
    st.markdown("""
    <div style='
        background-color: #f3e5f5;
        padding: 20px;
        border-left: 6px solid #ab47bc;
        border-radius: 10px;
        margin-bottom: 30px;
    '>
        <h3 style='color:#8e24aa;'>📬 تواصل معي</h3>
        <p style='font-size:18px; color:#333;'>📧 البريد الإلكتروني: <strong>sohaemara22@gmail.com</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # إشعار جاهزية المنصة
    st.success("✨ المنصة جاهزة للعرض 💪")

elif page == "📝 التقييم":
    show_assessment_page()
elif page == "📊 لوحة التحكم الرئيسية":
    st.header("📊 لوحة التحكم الرئيسية")

    # === استرجاع البيانات ===
    user = st.session_state.get("user_info", {})
    results = st.session_state.get("results", {})
    iot_avg = st.session_state.get("iot_avg", 0)
    swot = st.session_state.get("swot", {})
    cpm_results = st.session_state.get("cpm_results", {})  # من صفحة CPM
    company_name = user.get("company", "شركتي")

    # حساب المتوسط العام لـ SCOR
    scor_avg = round(sum(results.values()) / len(results), 2) if results else 0
    cpm_score = cpm_results.get(company_name, "لم يتم التقييم")

    # === KPIs الرئيسية ===
    st.subheader("📈 مؤشرات الأداء الرئيسية (KPIs)")
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 متوسط SCOR", f"{scor_avg}/5")
    col2.metric("🌐 جاهزية IoT", f"{iot_avg}/5")
    col3.metric("🏁 نتيجة CPM", cpm_score if isinstance(cpm_score, str) else f"{cpm_score}/5")

    st.subheader("🧠 تحليل SWOT - ملخص")
    col4, col5, col6, col7 = st.columns(4)
    col4.metric("✅ القوة", len(swot.get("قوة", [])))
    col5.metric("⚠️ الضعف", len(swot.get("ضعف", [])))
    col6.metric("🚀 الفرص", len(swot.get("فرصة", [])))
    col7.metric("⛔ التهديدات", len(swot.get("تهديد", [])))

    # === رسم بياني لأداء SCOR ===
st.subheader("📊 أداء شركتي حسب مراحل SCOR")

results = st.session_state.get("results", {})
phase_labels = {
    "Plan": "📘 التخطيط",
    "Source": "📦 التوريد",
    "Make": "🏭 التصنيع",
    "Deliver": "🚚 التوزيع",
    "Return": "🔁 المرتجعات"
}

if results:
    labels = list(results.keys())
    values = list(results.values())
    
    # تحويل أسماء SCOR إلى تسميات بالعربية
    labels_arabic = [phase_labels.get(l, l) for l in labels]

    fig = go.Figure([go.Bar(
        x=labels_arabic,
        y=values,
        text=[f"{v:.1f}" for v in values],
        textposition='auto',
        marker_color='lightblue'
    )])
    fig.update_layout(
        title="📊 تقييم الجاهزية الرقمية حسب مراحل SCOR",
        xaxis_title="المرحلة",
        yaxis_title="التقييم",
        yaxis=dict(range=[0, 5]),
        height=450
    )
    st.plotly_chart(fig)
else:
    st.warning("⚠️ لم يتم تنفيذ تقييم SCOR بعد.")

    # === رسم بياني لمقارنة CPM بين شركتي والمنافسين ===
st.subheader("🏁 مقارنة شركتي مع المنافسين - مصفوفة CPM")

cpm_results = st.session_state.get("cpm_results", {})
company_name = st.session_state.get("user_info", {}).get("company", "شركتي")

if cpm_results:
    names = list(cpm_results.keys())
    values = list(cpm_results.values())
    colors = ["green" if name == company_name else "orange" for name in names]

    fig = go.Figure([go.Bar(
        x=names,
        y=values,
        text=[f"{v:.2f}" for v in values],
        textposition='auto',
        marker_color=colors
    )])
    fig.update_layout(
        title="🔎 المقارنة التنافسية حسب CPM",
        xaxis_title="الشركة",
        yaxis_title="النتيجة النهائية",
        yaxis=dict(range=[0, 5]),
        height=450
    )
    st.plotly_chart(fig)

    # ملاحظة حسب الموقع
    top_company = max(cpm_results, key=cpm_results.get)
    if top_company == company_name:
        st.success("👏 شركتك في المركز الأول مقارنة بالمنافسين!")
    else:
        st.info(f"👀 الشركة الأفضل حاليًا: **{top_company}**. يُوصى بتحليل الفجوات وتحسين جاهزية SCOR.")
else:
    st.warning("⚠️ لم يتم تسجيل نتائج CPM بعد. الرجاء إدخالها من صفحة '🏢 مقارنة الشركات'.")
# ✅ تأكد من جلب البيانات من الـ session قبل أي استخدام
user = st.session_state.get("user_info", {})
company_name = user.get("company", "شركتي")
iot_avg = st.session_state.get("iot_avg", 0)
scor_avg = st.session_state.get("scor_avg", 0)
cpm_results = st.session_state.get("cpm_results", {})

# === تجهيز البيانات للتصدير ===
export_data = {
    "اسم المستخدم": "غير متاح",
    "الدولة": user.get("country", ""),
    "القطاع": user.get("sector", ""),
    "SCOR": st.session_state.get("results", {}),
    "IoT": iot_avg,
    "SWOT": st.session_state.get("swot", {}),
    "CPM": cpm_results
}


# JSON
json_str = json.dumps(export_data, ensure_ascii=False, indent=2)

# Excel
excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
    pd.DataFrame([export_data]).to_excel(writer, sheet_name="Dashboard", index=False)

# --- تصدير PDF يدعم اللغة العربية ---
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import arabic_reshaper
from bidi.algorithm import get_display

# === تجهيز البيانات ===
company_name = user.get("company", "شركتي")
country = user.get("country", "")
sector = user.get("sector", "")
scor_avg = st.session_state.get("scor_avg", 0)
iot_avg = st.session_state.get("iot_avg", 0)
cpm_score = st.session_state.get("cpm_results", {}).get(company_name, "غير متاحة")

# === إنشاء ملف PDF ===
pdf_path = "dashboard_report.pdf"
c = canvas.Canvas(pdf_path, pagesize=A4)

y = 800
c.setFont("Helvetica", 14)

for line in [
    f"📄 تقرير الشركة: {company_name}",
    f"الدولة: {country}",
    f"القطاع: {sector}",
    f"متوسط SCOR: {scor_avg}",
    f"متوسط IoT: {iot_avg}",
    f"نتيجة CPM: {cpm_score}"
]:
    reshaped_text = arabic_reshaper.reshape(line)
    bidi_text = get_display(reshaped_text)
    c.drawRightString(550, y, bidi_text)
    y -= 30

c.save()

# === زر تحميل PDF ===
with open(pdf_path, "rb") as f:
    st.download_button("⬇️ تحميل تقرير PDF", data=f.read(), file_name="dashboard_report.pdf", mime="application/pdf")


# === تصدير النتائج والتقارير ===
st.subheader("📤 تصدير النتائج والتقارير")

with st.expander("📁 تحميل البيانات"):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            label="⬇️ تحميل JSON",
            data=json_str,
            file_name="dashboard_data.json",
            mime="application/json",
            key="download_json"
        )

    with col2:
        st.download_button(
            label="⬇️ تحميل Excel",
            data=excel_buffer.getvalue(),
            file_name="dashboard_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_excel"
        )

    with col3:
        try:
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            st.download_button(
                label="⬇️ تحميل تقرير PDF",
                data=pdf_bytes,
                file_name="dashboard_report.pdf",
                mime="application/pdf",
                key="download_pdf"
            )
        except FileNotFoundError:
            st.error("❌ لم يتم العثور على ملف التقرير PDF. تأكد من أنه تم إنشاؤه بنجاح.")



# === روابط تنقل ذكية داخل المنصة ===
st.subheader("🔗 روابط سريعة")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔄 إعادة التقييم"):
        st.switch_page("📝 التقييم")
with col2:
    if st.button("📊 تحليل النتائج"):
        st.switch_page("📊 النتائج والتحليل")
with col3:
    if st.button("🏢 مقارنة الشركات"):
        st.switch_page("🏢 مقارنة الشركات")

st.markdown("---")

# === QR Code لفتح لوحة خارجية مثل Power BI أو ERP ===
st.subheader("📱 فتح النتائج على الجوال - QR Code")

qr_link = st.text_input("🔗 أدخل رابط لوحة خارجية (مثل Power BI أو ERP)", placeholder="https://example.com/dashboard")

if qr_link:
    import qrcode
    from PIL import Image

    qr = qrcode.make(qr_link)
    qr_path = "qr_code_dashboard.png"
    qr.save(qr_path)
    st.image(qr_path, caption="امسح QR لفتح الرابط", width=200)



if page == "📊 النتائج والتحليل":
   
 def show_results_page():
    st.header("📊 النتائج ومصفوفات التحليل")

    if not st.session_state.results:
        st.warning("⚠️ يرجى تنفيذ التقييم أولًا.")
        st.stop()

    results = st.session_state.results
    swot = st.session_state.swot
    iot_avg = st.session_state.iot_avg
    user = st.session_state.user_info

    # --- تقييم مراحل SCOR ---
    st.subheader("📈 تقييم مراحل SCOR")
    labels = list(results.keys())
    values = list(results.values())
    fig = go.Figure([go.Bar(x=labels, y=values, text=[f"{v:.1f}" for v in values], textposition='auto')])
    fig.update_layout(title="مستوى الجاهزية في مراحل SCOR", yaxis_range=[0, 5], height=400)
    st.plotly_chart(fig)
    st.divider()

    # --- تحليل SWOT ---
    st.subheader("🧠 تحليل SWOT")
    for key, title in {"قوة": "✅ نقاط القوة", "ضعف": "⚠️ نقاط الضعف", "فرصة": "🚀 الفرص", "تهديد": "⛔ التهديدات"}.items():
        st.markdown(f"### {title}")
        if swot.get(key):
            for i, item in enumerate(swot[key], 1):
                st.markdown(f"**{i}.** {item}")
        else:
            st.markdown("- لا توجد بيانات.")
    st.divider()

    # --- تقييم IFE و EFE ---
    st.subheader("📌 تقييم IFE و EFE")
    ife_inputs, efe_inputs = [], []
    for i, item in enumerate(swot["قوة"] + swot["ضعف"]):
        weight = st.number_input(f"📌 {item} (الوزن الداخلي)", 0.0, 1.0, 0.1, step=0.05, key=f"ife_weight_{i}")
        rating = st.slider(f"التقييم لـ {item}", 1, 4, 3, key=f"ife_rating_{i}")
        ife_inputs.append(weight * rating)
    for i, item in enumerate(swot["فرصة"] + swot["تهديد"]):
        weight = st.number_input(f"🌐 {item} (الوزن الخارجي)", 0.0, 1.0, 0.1, step=0.05, key=f"efe_weight_{i}")
        rating = st.slider(f"التقييم لـ {item}", 1, 4, 3, key=f"efe_rating_{i}")
        efe_inputs.append(weight * rating)
    ife_total = sum(ife_inputs)
    efe_total = sum(efe_inputs)
    st.success(f"✅ مجموع IFE: {ife_total:.2f} | مجموع EFE: {efe_total:.2f}")
    st.divider()

    # --- الاستراتيجية المقترحة ---
    st.subheader("🧭 الاستراتيجية المقترحة")
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

    # --- مصفوفة BCG ---
    st.subheader("📊 BCG Matrix – Strategic Positioning of SCOR Phases")
    bcg_data = []
    for phase in results:
        x = round(results[phase], 2)
        y = round(iot_avg, 2)
        quadrant = "🌟 Star" if x >= 3 and y >= 3 else \
                   "❓ Question Mark" if x < 3 and y >= 3 else \
                   "💰 Cash Cow" if x >= 3 and y < 3 else "🐶 Dog"
        bcg_data.append({"SCOR Phase": phase, "IFE (X)": x, "EFE (Y)": y, "Quadrant": quadrant})
    bcg_df = pd.DataFrame(bcg_data)
    st.dataframe(bcg_df, use_container_width=True)

    fig = go.Figure()
    for row in bcg_data:
        fig.add_trace(go.Scatter(x=[row["IFE (X)"]], y=[row["EFE (Y)"]],
                                 mode="markers+text",
                                 marker=dict(size=20, color="blue"),
                                 text=[row["SCOR Phase"]],
                                 textposition="middle center"))
    fig.add_shape(type="line", x0=3, y0=0, x1=3, y1=5, line=dict(color="gray", width=2, dash="dash"))
    fig.add_shape(type="line", x0=0, y0=3, x1=5, y1=3, line=dict(color="gray", width=2, dash="dash"))
    fig.update_layout(title="BCG Matrix", xaxis_title="IFE", yaxis_title="EFE (IoT)",
                      xaxis=dict(range=[1, 5]), yaxis=dict(range=[1, 5]),
                      height=600, showlegend=False)
    st.plotly_chart(fig)
    st.divider()

    # --- مصفوفة IE ---
    st.subheader("📊 IE Matrix – Strategic Positioning")
    def get_ie_region(ife, efe):
        if efe >= 3.0:
            return "I (Grow)" if ife >= 3.0 else "II (Grow)" if ife >= 2.0 else "III (Hold)"
        elif efe >= 2.0:
            return "IV (Grow)" if ife >= 3.0 else "V (Hold)" if ife >= 2.0 else "VI (Harvest)"
        else:
            return "VII (Hold)" if ife >= 3.0 else "VIII (Harvest)" if ife >= 2.0 else "IX (Exit)"
    region = get_ie_region(ife_total, efe_total)
    st.markdown(f"📍 **IFE Score:** {ife_total:.2f} | **EFE Score:** {efe_total:.2f}")
    st.markdown(f"🧭 **Strategic Region:** {region}")
    fig = go.Figure()
    strategies = [("I (Grow)", "green"), ("II (Grow)", "green"), ("III (Hold)", "yellow"),
                  ("IV (Grow)", "green"), ("V (Hold)", "yellow"), ("VI (Harvest)", "orange"),
                  ("VII (Hold)", "yellow"), ("VIII (Harvest)", "orange"), ("IX (Exit)", "red")]
    idx = 0
    for y in reversed(range(3)):
        for x in range(3):
            fig.add_shape(type="rect", x0=x, y0=y, x1=x + 1, y1=y + 1,
                          line=dict(color="black", width=1),
                          fillcolor=strategies[idx][1], opacity=0.3)
            fig.add_annotation(x=x + 0.5, y=y + 0.5, text=strategies[idx][0],
                               showarrow=False, font=dict(size=13))
            idx += 1
    fig.add_trace(go.Scatter(x=[min(max((ife_total - 1), 0), 3)],
                             y=[min(max((efe_total - 1), 0), 3)],
                             mode="markers+text",
                             marker=dict(color="black", size=14, symbol="x"),
                             text=["Your Position"],
                             textposition="top center"))
    fig.update_layout(title="IE Matrix",
                      xaxis=dict(title="IFE", range=[0, 3], tickvals=[0.5, 1.5, 2.5], ticktext=["Weak", "Average", "Strong"]),
                      yaxis=dict(title="EFE", range=[0, 3], tickvals=[0.5, 1.5, 2.5], ticktext=["Low", "Medium", "High"]),
                      width=600, height=600, showlegend=False)
    st.plotly_chart(fig)
    st.divider()

    # --- تصدير شامل PDF ---
    st.subheader("📤 تحميل تقرير PDF شامل")
    pdf = FPDF()
    pdf.add_page()
    font_path = os.path.join(os.path.dirname(__file__), "amiri.ttf")
    pdf.add_font('Amiri', '', font_path, uni=True)
    pdf.set_font('Amiri', '', 14)
    pdf.cell(200, 10, txt="📄 تقرير الاستراتيجية الكاملة", ln=True, align="C")
    pdf.cell(200, 10, txt=f"المستخدم: {user.get('name', '')}", ln=True)
    pdf.cell(200, 10, txt=f"IFE: {ife_total:.2f} | EFE: {efe_total:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"BCG Region: {strategy}", ln=True)
    pdf.cell(200, 10, txt=f"IE Matrix Region: {region}", ln=True)
    buffer = BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin-1')
    buffer.write(pdf_output)
    b64_pdf = base64.b64encode(buffer.getvalue()).decode()
    st.markdown(f'<a href="data:application/pdf;base64,{b64_pdf}" download="Strategic_Report.pdf">📄 تحميل التقرير PDF</a>', unsafe_allow_html=True)

    # --- تصدير Excel ---
    st.subheader("📥 تحميل ملفات Excel")
    export_df = pd.DataFrame({
        "IFE Scores": ife_inputs + [None] * (len(efe_inputs) - len(ife_inputs)),
        "EFE Scores": efe_inputs + [None] * (len(ife_inputs) - len(efe_inputs))
    })
    ie_df = pd.DataFrame({
        "IFE Total": [round(ife_total, 2)],
        "EFE Total": [round(efe_total, 2)],
        "IE Region": [region],
        "Strategy": [
            "Grow" if "Grow" in region else "Hold" if "Hold" in region else "Harvest/Exit"
        ]
    })
    with pd.ExcelWriter("strategic_outputs.xlsx", engine='xlsxwriter') as writer:
        export_df.to_excel(writer, sheet_name="IFE_EFE", index=False)
        bcg_df.to_excel(writer, sheet_name="BCG", index=False)
        ie_df.to_excel(writer, sheet_name="IE", index=False)
        writer.save()
        with open("strategic_outputs.xlsx", "rb") as f:
            st.download_button("⬇️ تحميل النتائج Excel", f.read(), file_name="strategic_outputs.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
elif page == "🤖 التوصيات الذكية":
    st.header("🤖 التوصيات الذكية المدعومة بالذكاء الاصطناعي")

    results = st.session_state.get("results", {})
    iot_avg = st.session_state.get("iot_avg", 0)
    swot = st.session_state.get("swot", {})

    if not results:
        st.warning("⚠️ يرجى تنفيذ التقييم أولًا.")
        st.stop()

    # --- توصيات SCOR ---
    st.subheader("✨ توصيات حسب الجاهزية في مراحل SCOR")

    categories = []
    for phase, score in results.items():
        label = phase_labels.get(phase, phase)
        if score < 2.5:
            categories.append("منخفضة")
            st.markdown(f"🔴 **{label}:** منخفض الجاهزية. يُوصى باستخدام RPA، والتنبؤ الآلي بالطلب (AutoML)، وتبسيط العمليات.")
        elif score < 4:
            categories.append("متوسطة")
            st.markdown(f"🟠 **{label}:** متوسط الجاهزية. يُوصى بتوسيع التكامل مع أنظمة ERP، وتفعيل لوحات تحكم ذكية، وتحليل بيانات الموردين باستخدام ML.")
        else:
            categories.append("مرتفعة")
            st.markdown(f"🟢 **{label}:** جاهزية عالية. يُوصى بتفعيل التعلم الآلي والتنبؤات الذكية، مثل الصيانة التنبؤية وتحسين توجيه الشحنات.")

    st.divider()

    # --- Dashboard بصري للتوصيات ---
    st.subheader("📊 ملخص التوصيات (Dashboard)")
    from collections import Counter
    import plotly.express as px

    summary = Counter(categories)
    dash_df = pd.DataFrame({
        "مستوى الجاهزية": list(summary.keys()),
        "عدد المراحل": list(summary.values())
    })

    fig = px.pie(dash_df, names="مستوى الجاهزية", values="عدد المراحل",
                 color_discrete_sequence=["#E74C3C", "#F1C40F", "#2ECC71"])
    fig.update_traces(textinfo="label+percent", pull=[0.05, 0.05, 0.1])
    st.plotly_chart(fig)

    st.divider()

    # --- توصيات IoT ---
    st.subheader("🌐 توصيات إنترنت الأشياء (IoT)")
    if iot_avg < 2:
        st.error("جاهزية IoT منخفضة. يُنصح بتركيب حساسات وربطها بالأنظمة الرقمية وبدء تجميع البيانات.")
    elif iot_avg < 4:
        st.warning("جاهزية متوسطة. يُنصح بتحسين الاتصالات وتحليل البيانات باستخدام أنظمة Edge AI.")
    else:
        st.success("جاهزية ممتازة لإنترنت الأشياء. يُوصى بالانتقال إلى Digital Twin ونماذج محاكاة ذكية.")
    st.divider()

    # --- توصيات استراتيجية حسب SWOT ---
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

    # --- أدوات دعم القرار وروابط مفيدة ---
    st.subheader("📚 أدوات وتقنيات مقترحة")
    st.markdown("""
    - 🔗 [Google AutoML](https://cloud.google.com/automl) – بناء نماذج ذكاء صناعي تلقائيًا.
    - 🔗 [Azure Machine Learning](https://azure.microsoft.com/en-us/services/machine-learning/) – منصة مايكروسوفت للذكاء الاصطناعي المؤسسي.
    - 🔗 [Power BI](https://powerbi.microsoft.com/ar-sa/) – لوحات تحكم تفاعلية وتحليل بيانات بصري.
    - 🔗 [Digital Twin Technology](https://www.ibm.com/topics/digital-twin) – لإنشاء نماذج رقمية لمحاكاة العمليات.
    - 🔗 [Edge AI Concepts](https://www.edge-ai-vision.com/) – التحليل على الأجهزة الطرفية دون إرسال البيانات للسحابة.
    """)
    st.success("✅ شكراً لاستخدامك المنصة. يمكنك تحميل التوصيات أو الرجوع للنتائج.")
elif page == "🏢 مقارنة الشركات":
    st.header("🏢 مقارنة الشركات - مصفوفة CPM")

    st.markdown("""
    - قارن شركتك مع المنافسين باستخدام **مصفوفة الملف التعريفي التنافسي (CPM)**.
    - أدخل التقييم لكل عامل SCOR، واحصل على تحليلك الاستراتيجي الكامل.
    """)

    # --- إعداد الشركات ---
    company_names = [st.session_state.user_info.get("company", "شركتي")]
    competitor_1 = st.text_input("🆚 اسم المنافس 1", "منافس A")
    competitor_2 = st.text_input("🆚 اسم المنافس 2 (اختياري)", "منافس B")
    company_names.append(competitor_1)
    if competitor_2.strip():
        company_names.append(competitor_2)

    # --- عوامل SCOR ---
    st.markdown("### ⚖️ الأوزان النسبية لعوامل SCOR")
    factors = ["Plan", "Source", "Make", "Deliver", "Return"]
    phase_weights = {f: st.slider(f"{phase_labels[f]}", 0.0, 1.0, 0.2, step=0.05) for f in factors}
    total_weight = sum(phase_weights.values())
    if not 0.95 <= total_weight <= 1.05:
        st.warning(f"⚠️ مجموع الأوزان = {total_weight:.2f}. يجب أن يساوي 1 تقريبًا.")
        st.stop()

    # --- التقييمات لكل شركة ---
    st.markdown("### ✍️ أدخل التقييمات لكل شركة (من 1 إلى 5)")
    scores = {name: {} for name in company_names}
    for f in factors:
        cols = st.columns(len(company_names) + 1)
        cols[0].markdown(f"**{phase_labels[f]}** ({phase_weights[f]})")
        for i, name in enumerate(company_names):
            scores[name][f] = cols[i+1].slider(f"{name} - {f}", 1.0, 5.0, 3.0, step=0.1, key=f"{name}_{f}")

    # --- حساب النتائج النهائية ---
    st.markdown("### ✅ النتائج النهائية")
    final_results = {name: round(sum(phase_weights[f] * scores[name][f] for f in factors), 2) for name in company_names}
    result_df = pd.DataFrame({
        "الشركة": list(final_results.keys()),
        "النتيجة النهائية (CPM)": list(final_results.values())
    })
    st.dataframe(result_df, use_container_width=True)

    # --- رسم بياني للمقارنة ---
    st.subheader("📊 مقارنة بصرية بين الشركات")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(final_results.keys()),
        y=list(final_results.values()),
        marker_color=["green" if name == company_names[0] else "orange" for name in final_results],
        text=[f"{v:.2f}" for v in final_results.values()],
        textposition="auto"
    ))
    fig.update_layout(title="تحليل تنافسي باستخدام CPM", xaxis_title="الشركة", yaxis_title="النتيجة النهائية", yaxis=dict(range=[0, 5]))
    st.plotly_chart(fig)

    # --- توصيات ذكية حسب النتائج ---
    st.subheader("🧠 توصيات ذكية حسب الأداء التنافسي")
    for name, score in final_results.items():
        if score >= 4:
            st.success(f"✅ {name}: أداء قوي. يُوصى بالاستمرار وتوسيع التكامل الذكي.")
        elif score >= 3:
            st.warning(f"🟡 {name}: أداء جيد نسبيًا. يُوصى بتحسين الجاهزية التشغيلية والتحليل اللحظي.")
        else:
            st.error(f"🔴 {name}: أداء ضعيف. يُنصح بإعادة بناء العمليات وتكامل RPA وAutoML.")

    # --- تصدير JSON ---
    st.subheader("📤 تحميل ملف JSON للتكامل")
    export_data = {
        "user": st.session_state.user_info,
        "SCOR_scores": st.session_state.results,
        "IoT_score": st.session_state.iot_avg,
        "SWOT": st.session_state.swot,
        "CPM_Results": final_results
    }
    json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
    st.code(json_str, language='json')
    st.download_button("⬇️ تحميل JSON", data=json_str, file_name="scor_ai_export.json", mime="application/json")

    # --- Webhook إرسال ---
    st.subheader("📡 إرسال النتائج إلى نظام خارجي (Webhook)")
    webhook_url = st.text_input("🔗 رابط Webhook (ERP/Odoo)", placeholder="https://example.com/webhook")
    def log_company_data(status="نجاح", method="Webhook"):
        log_file = "data_log.xlsx"
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        user = st.session_state.user_info
        log_entry = {
            "الاسم": user.get("name", ""),
            "الشركة": user.get("company", ""),
            "القطاع": user.get("sector", ""),
            "الدولة": user.get("country", ""),
            "التاريخ": now,
            "متوسط IoT": st.session_state.get("iot_avg", 0),
            "نتيجة CPM": final_results.get(user.get("company", "شركتي"), 0),
            "حالة العملية": status,
            "الطريقة": method
        }
        for phase, score in st.session_state.results.items():
            log_entry[f"SCOR - {phase}"] = score
        df_log_entry = pd.DataFrame([log_entry])
        try:
            df_existing = pd.read_excel(log_file)
            df_combined = pd.concat([df_existing, df_log_entry], ignore_index=True)
        except FileNotFoundError:
            df_combined = df_log_entry
        df_combined.to_excel(log_file, index=False)
        st.success("📝 تم تسجيل العملية في سجل البيانات.")

    if st.button("📨 إرسال البيانات"):
        if webhook_url:
            import requests
            try:
                response = requests.post(webhook_url, json=export_data)
                if response.status_code == 200:
                    st.success("✅ تم الإرسال بنجاح.")
                    log_company_data("نجاح")
                else:
                    st.error(f"❌ فشل في الإرسال. الكود: {response.status_code}")
                    log_company_data("فشل")
            except Exception as e:
                st.error(f"⚠️ خطأ في الإرسال: {e}")
                log_company_data("خطأ")
        else:
            st.warning("يرجى إدخال رابط Webhook.")

    # --- QR Code لفتح الرابط الخارجي (BI / ERP) ---
    st.subheader("📱 فتح رابط Power BI أو ERP عبر QR")
    qr_link = st.text_input("🔗 أدخل الرابط", placeholder="https://powerbi.com/report?id=123")
    if qr_link:
        import qrcode # type: ignore
        from PIL import Image
        qr = qrcode.make(qr_link)
        qr_path = "qr_code.png"
        qr.save(qr_path)
        st.image(qr_path, caption="امسح QR لفتح الرابط", width=200)
elif page == "🧾 سجل التقييمات":
    st.header("🧾 سجل التقييمات والعمليات السابقة")

    import os
    import pandas as pd
    from io import BytesIO
    from fpdf import FPDF
    import plotly.graph_objects as go  # تأكدي إنه مضاف

    log_file = "data_log.xlsx"

    if os.path.exists(log_file):
        df_log = pd.read_excel(log_file)

        st.success(f"✅ تم تحميل السجل. عدد العمليات: {len(df_log)}")

        # --- تصفية حسب الشركة ---
        companies = df_log["الشركة"].dropna().unique().tolist()
        selected_company = st.selectbox("🔍 اختر شركة لعرض سجلها:", ["كل الشركات"] + companies)

        if selected_company != "كل الشركات":
            df_log = df_log[df_log["الشركة"] == selected_company]

        st.dataframe(df_log, use_container_width=True)

        # --- تصدير Excel ---
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df_log.to_excel(writer, index=False, sheet_name="Log")
            writer.close()
        st.download_button("⬇️ تحميل Excel", data=excel_buffer.getvalue(), file_name="data_log_export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # --- تصدير PDF مبسط ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="📄 سجل التقييمات - تقرير مبسط", ln=True, align="C")
        for i, row in df_log.iterrows():
            pdf.cell(200, 10, txt=f"{row['الشركة']} - {row['التاريخ']} - {row['حالة العملية']}", ln=True)
        pdf_output = pdf.output(dest="S").encode("latin-1")
        st.download_button("⬇️ تحميل PDF", data=pdf_output, file_name="data_log_report.pdf", mime="application/pdf")

        # ✅ ✅ ✅ تحليل إحصائي هنا جوا نفس الشرط
        st.subheader("📊 تحليل بصري للسجل")

        if not df_log.empty:
            # --- عدد التقييمات لكل شركة ---
            company_counts = df_log["الشركة"].value_counts().reset_index()
            company_counts.columns = ["الشركة", "عدد التقييمات"]

            fig1 = go.Figure([go.Bar(
                x=company_counts["الشركة"],
                y=company_counts["عدد التقييمات"],
                text=company_counts["عدد التقييمات"],
                textposition="auto",
                marker_color='teal'
            )])
            fig1.update_layout(title="📦 عدد التقييمات حسب الشركة", height=400)
            st.plotly_chart(fig1)

            # --- حالات العمليات ---
            status_counts = df_log["حالة العملية"].value_counts().reset_index()
            status_counts.columns = ["الحالة", "عدد العمليات"]

            fig2 = go.Figure([go.Pie(
                labels=status_counts["الحالة"],
                values=status_counts["عدد العمليات"],
                hole=0.4
            )])
            fig2.update_layout(title="🧮 توزيع حالات العمليات (نجاح / فشل / خطأ)", height=400)
            st.plotly_chart(fig2)

    else:
        st.warning("⚠️ لا يوجد سجل حتى الآن. سيتم إنشاء السجل تلقائيًا عند تصدير أو إرسال نتائج.")
elif page == "📈 تحليل الأداء حسب القطاع":
    st.header("📈 تحليل الأداء حسب القطاع أو الدولة")

    import pandas as pd
    import plotly.express as px
    import os

    log_file = "data_log.xlsx"

    if os.path.exists(log_file):
        df_log = pd.read_excel(log_file)

        if df_log.empty:
            st.warning("⚠️ لا توجد بيانات في السجل.")
            st.stop()

        # اختيار نوع التحليل
        filter_by = st.radio("🔍 تحليل حسب:", ["القطاع", "الدولة"])
        filter_column = "القطاع" if filter_by == "القطاع" else "الدولة"

        # إزالة الصفوف الفارغة أو المفقودة
        df_filtered = df_log.dropna(subset=[filter_column, "نتيجة CPM"])

        # حساب المتوسط لكل قطاع/دولة
        avg_scores = df_filtered.groupby(filter_column).agg({
            "نتيجة CPM": "mean",
            "متوسط IoT": "mean",
            "SCOR - Plan": "mean",
            "SCOR - Source": "mean",
            "SCOR - Make": "mean",
            "SCOR - Deliver": "mean",
            "SCOR - Return": "mean"
        }).reset_index()

        avg_scores.rename(columns={
            "نتيجة CPM": "متوسط CPM",
            "متوسط IoT": "متوسط IoT",
            "SCOR - Plan": "📘 التخطيط",
            "SCOR - Source": "📦 التوريد",
            "SCOR - Make": "🏭 التصنيع",
            "SCOR - Deliver": "🚚 التوزيع",
            "SCOR - Return": "🔁 المرتجعات"
        }, inplace=True)

        # عرض الجدول
        st.dataframe(avg_scores, use_container_width=True)

        # رسم بياني تفاعلي
        st.subheader("📊 المقارنة البصرية")
        fig = px.bar(
            avg_scores,
            x=filter_column,
            y=["متوسط CPM", "متوسط IoT"],
            barmode="group",
            title=f"متوسط الأداء حسب {filter_column}",
            height=450
        )
        st.plotly_chart(fig)

    else:
        st.warning("⚠️ لا يوجد سجل بيانات حتى الآن.")
elif page == "🛠️ لوحة تحكم المشرف":
    st.header("🛠️ لوحة تحكم المشرف - System Admin")

    import os
    import pandas as pd
    from io import BytesIO
    import plotly.express as px

    log_file = "data_log.xlsx"

    if os.path.exists(log_file):
        df = pd.read_excel(log_file)

        if df.empty:
            st.warning("⚠️ لا توجد بيانات في السجل.")
            st.stop()

        # --- تصفية حسب الشركة / الدولة / القطاع ---
        col1, col2, col3 = st.columns(3)
        companies = df["الشركة"].dropna().unique().tolist()
        sectors = df["القطاع"].dropna().unique().tolist()
        countries = df["الدولة"].dropna().unique().tolist()

        selected_company = col1.selectbox("🏢 اختر شركة:", ["كل الشركات"] + companies)
        selected_sector = col2.selectbox("🏭 اختر قطاع:", ["كل القطاعات"] + sectors)
        selected_country = col3.selectbox("🌍 اختر دولة:", ["كل الدول"] + countries)

        filtered_df = df.copy()
        if selected_company != "كل الشركات":
            filtered_df = filtered_df[filtered_df["الشركة"] == selected_company]
        if selected_sector != "كل القطاعات":
            filtered_df = filtered_df[filtered_df["القطاع"] == selected_sector]
        if selected_country != "كل الدول":
            filtered_df = filtered_df[filtered_df["الدولة"] == selected_country]

        st.success(f"✅ عدد النتائج المعروضة: {len(filtered_df)}")
        st.dataframe(filtered_df, use_container_width=True)

        # --- تحميل Excel للنتائج المصفاة ---
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name="AdminView")
            writer.close()
        st.download_button("⬇️ تحميل Excel للتقرير الحالي", data=excel_buffer.getvalue(), file_name="admin_filtered_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # --- رسم بياني: CPM حسب الشركة
        st.subheader("📊 مقارنة CPM بين الشركات")
        if "نتيجة CPM" in filtered_df.columns:
            fig = px.bar(filtered_df, x="الشركة", y="نتيجة CPM", color="القطاع", text="نتيجة CPM", height=400)
            st.plotly_chart(fig)

    else:
        st.warning("⚠️ لا يوجد ملف سجل بيانات حتى الآن.")
elif page == "📆 تحليل الأداء الزمني":
    st.header("📆 تحليل تطور الأداء عبر الزمن")

    import os
    import pandas as pd
    import plotly.express as px

    log_file = "data_log.xlsx"

    if os.path.exists(log_file):
        df = pd.read_excel(log_file)

        if df.empty:
            st.warning("⚠️ لا توجد بيانات كافية.")
            st.stop()

        # --- تأكيد وجود التاريخ بصيغة صحيحة ---
        if not pd.api.types.is_datetime64_any_dtype(df["التاريخ"]):
            df["التاريخ"] = pd.to_datetime(df["التاريخ"], errors='coerce')

        df = df.dropna(subset=["التاريخ", "نتيجة CPM", "متوسط IoT"])

        # اختيار الشركة / القطاع للتحليل
        companies = df["الشركة"].dropna().unique().tolist()
        selected_company = st.selectbox("🏢 اختر شركة:", companies)

        df_filtered = df[df["الشركة"] == selected_company]

        if df_filtered.empty:
            st.warning("⚠️ لا توجد تقييمات سابقة لهذه الشركة.")
            st.stop()

        # --- رسم تطور CPM بمرور الوقت ---
        st.subheader("📈 تطور نتيجة CPM بمرور الوقت")
        fig_cpm = px.line(df_filtered, x="التاريخ", y="نتيجة CPM", markers=True, title="📉 CPM Trend")
        st.plotly_chart(fig_cpm)

        # --- رسم تطور IoT بمرور الوقت ---
        st.subheader("📡 تطور متوسط IoT")
        fig_iot = px.line(df_filtered, x="التاريخ", y="متوسط IoT", markers=True, title="🌐 IoT Trend", color_discrete_sequence=["green"])
        st.plotly_chart(fig_iot)

        # --- تطور SCOR Phases (اختياري) ---
        if "SCOR - Plan" in df_filtered.columns:
            st.subheader("🔄 تطور تقييم مراحل SCOR")
            phases = ["SCOR - Plan", "SCOR - Source", "SCOR - Make", "SCOR - Deliver", "SCOR - Return"]
            for phase in phases:
                if phase in df_filtered.columns:
                    fig = px.line(df_filtered, x="التاريخ", y=phase, markers=True, title=f"📊 {phase}", height=350)
                    st.plotly_chart(fig)

    else:
        st.warning("⚠️ لا يوجد سجل بيانات.")
