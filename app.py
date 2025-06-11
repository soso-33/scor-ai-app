import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
from datetime import datetime
from xhtml2pdf import pisa

# دالة لتحويل HTML إلى PDF
def convert_html_to_pdf(source_html, output_filename):
    with open(output_filename, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(source_html, dest=result_file)
    return pisa_status.err

# دالة لحفظ النتائج في قاعدة البيانات
def save_to_db(company, date, scores, total):
    conn = sqlite3.connect("ai_readiness.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS assessments (
                 company TEXT, date TEXT, plan INTEGER, source INTEGER, make INTEGER, deliver INTEGER, return_score INTEGER, total REAL)''')
    c.execute('''INSERT INTO assessments VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (company, date, scores[0], scores[1], scores[2], scores[3], scores[4], total))
    conn.commit()
    conn.close()

# دالة لجلب نتائج شركات أخرى للمقارنة
def get_all_assessments():
    conn = sqlite3.connect("ai_readiness.db")
    df = pd.read_sql_query("SELECT * FROM assessments", conn)
    conn.close()
    return df

# عنوان الصفحة
st.set_page_config(page_title="منصة تقييم جاهزية الذكاء الاصطناعي", layout="wide")
st.title("📊 منصة تقييم جاهزية الذكاء الاصطناعي - نموذج SCOR")

# إدخال اسم الشركة
company_name = st.text_input("🧾 أدخل اسم الشركة أو المؤسسة")

# نموذج تقييم SCOR
st.header("📝 نموذج تقييم جاهزية الذكاء الاصطناعي حسب SCOR")

with st.form("scor_form"):
    plan_score = st.slider("🔧 الخطة: هل تعتمد على تحليلات تنبؤية مدعومة بالذكاء الاصطناعي؟", 0, 100, 50)
    source_score = st.slider("📦 المصدر: هل يوجد تكامل مع موردين يستخدمون تقنيات ذكية؟", 0, 100, 50)
    make_score = st.slider("🏭 التصنيع: هل تستخدم الأتمتة أو الروبوتات الذكية في خطوط الإنتاج؟", 0, 100, 50)
    deliver_score = st.slider("🚚 التوصيل: هل يوجد نظام ذكي لتتبع الشحنات؟", 0, 100, 50)
    return_score = st.slider("♻️ الإرجاع: هل يوجد نظام لمعالجة المرتجعات باستخدام تحليلات متقدمة؟", 0, 100, 50)
    submit_btn = st.form_submit_button("⚙️ حساب التقييم")

if submit_btn:
    total_score = (plan_score + source_score + make_score + deliver_score + return_score) / 5
    st.success(f"✅ التقييم النهائي هو: {total_score:.1f}/100")
    st.metric("📊 الجاهزية الإجمالية", f"{total_score:.1f} / 100")

    # رسم بياني
    fig = go.Figure(go.Bar(
        x=["الخطة", "المصدر", "الصنع", "التوصيل", "الإرجاع"],
        y=[plan_score, source_score, make_score, deliver_score, return_score],
        marker_color='mediumseagreen'
    ))
    fig.update_layout(title="📈 توزيع درجات الجاهزية", yaxis_title="الدرجة")
    st.plotly_chart(fig)

    # إنشاء ملف Excel
    df = pd.DataFrame({
        "العنصر": ["الخطة", "المصدر", "الصنع", "التوصيل", "الإرجاع"],
        "الدرجة": [plan_score, source_score, make_score, deliver_score, return_score]
    })
    df.to_excel("تقرير جاهزية.xlsx", index=False)
    st.success("📊 تم إنشاء ملف Excel باسم 'تقرير جاهزية.xlsx'")

    # تصدير PDF
    if company_name:
        html_content = f"""
        <h1>تقرير تقييم جاهزية الذكاء الاصطناعي</h1>
        <p><strong>اسم الشركة:</strong> {company_name}</p>
        <p><strong>تاريخ التقييم:</strong> {datetime.today().date()}</p>
        <table border='1' cellpadding='5' cellspacing='0'>
            <tr><th>العنصر</th><th>الدرجة</th></tr>
            <tr><td>الخطة</td><td>{plan_score}</td></tr>
            <tr><td>المصدر</td><td>{source_score}</td></tr>
            <tr><td>الصنع</td><td>{make_score}</td></tr>
            <tr><td>التوصيل</td><td>{deliver_score}</td></tr>
            <tr><td>الإرجاع</td><td>{return_score}</td></tr>
        </table>
        <br><p><strong>التقييم النهائي:</strong> {total_score:.1f} / 100</p>
        """
        pdf_file = f"تقرير جاهزية {company_name}.pdf"
        if convert_html_to_pdf(html_content, pdf_file) == 0:
            st.success(f"📄 تم إنشاء ملف PDF باسم: {pdf_file}")
        else:
            st.error("❌ فشل في إنشاء ملف PDF.")

        # حفظ النتائج في قاعدة البيانات
        save_to_db(company_name, str(datetime.today().date()),
                   [plan_score, source_score, make_score, deliver_score, return_score], total_score)
    else:
        st.warning("⚠️ يرجى إدخال اسم الشركة أولاً.")

# عرض جميع الشركات المسجلة
st.header("📂 مقارنة مع شركات أخرى")
if st.checkbox("📋 عرض جميع التقييمات المسجلة"):
    data = get_all_assessments()
    st.dataframe(data)
