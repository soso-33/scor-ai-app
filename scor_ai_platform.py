import streamlit as st
import pandas as pd
import base64
from io import BytesIO
import sqlite3
from datetime import datetime

# --- إعداد اتصال قاعدة البيانات ---
conn = sqlite3.connect('scor_ai_assessments.db', check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    name TEXT,
    company TEXT,
    sector TEXT,
    country TEXT,
    consent INTEGER,
    plan_score REAL,
    source_score REAL,
    make_score REAL,
    deliver_score REAL,
    return_score REAL,
    iot_avg REAL,
    notes TEXT
)
''')
conn.commit()

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

st.set_page_config(page_title="منصة تقييم جاهزية الذكاء الاصطناعي في سلسلة التوريد - SCOR AI", layout="wide")

# --- قائمة الصفحات ---
pages = {
    "🏠 الصفحة الرئيسية": "home",
    "🧪 التقييم": "assessment",
    "🗄️ سجل التقييمات": "records",
    "ℹ️ معلومات التخرج": "graduation_info",
}

choice = st.sidebar.selectbox("اختر الصفحة", options=list(pages.keys()))
page = pages[choice]

def footer():
    st.markdown("---")
    st.markdown(
        """
        <p style='text-align:center; font-size:12px; color:gray;'>
        منصة تقييم جاهزية الذكاء الاصطناعي - مشروع التخرج | 
        مصمم المنصة: سُهى ناصر سعيد عماره | إشراف: أ.د. عماد كمهوي
        </p>
        """, unsafe_allow_html=True
    )

# --- الصفحة الرئيسية ---
if page == "home":
    st.title("مرحبًا في منصة تقييم جاهزية الذكاء الاصطناعي في سلسلة التوريد - SCOR AI")
    st.markdown("""
    هذه المنصة تساعدك على تقييم مدى جاهزية شركتك لتطبيق تقنيات الذكاء الاصطناعي في عمليات سلسلة التوريد 
    بناءً على نموذج SCOR، مع تحليل نقاط القوة والضعف، وعرض نتائج التقييم بالتفصيل.
    """)
    footer()

# --- صفحة التقييم ---
elif page == "assessment":
    st.header("🧪 تقييم جاهزية الذكاء الاصطناعي في سلسلة التوريد")

    with st.form("user_info_form"):
        name = st.text_input("الاسم الكامل")
        company = st.text_input("اسم الشركة")
        sector = st.text_input("القطاع")
        country = st.text_input("الدولة")
        consent = st.checkbox("أوافق على حفظ بياناتي ونتائج التقييم في قاعدة البيانات", value=False)
        submitted = st.form_submit_button("ابدأ التقييم")

    if submitted:
        if not (name and company and sector and country):
            st.error("يرجى ملء جميع الحقول أعلاه للمتابعة.")
            st.stop()

        st.session_state.user_info = {
            "name": name,
            "company": company,
            "sector": sector,
            "country": country,
            "consent": consent
        }

    if not st.session_state.get("user_info"):
        st.info("يرجى ملء النموذج أعلاه والضغط على 'ابدأ التقييم'.")
        st.stop()

    st.subheader("أسئلة تقييم الذكاء الاصطناعي في مراحل SCOR")

    plan_score = st.slider("درجة جاهزية التخطيط (Plan)", 0, 100, 50)
    source_score = st.slider("درجة جاهزية التوريد (Source)", 0, 100, 50)
    make_score = st.slider("درجة جاهزية التصنيع (Make)", 0, 100, 50)
    deliver_score = st.slider("درجة جاهزية التوزيع (Deliver)", 0, 100, 50)
    return_score = st.slider("درجة جاهزية المرتجعات (Return)", 0, 100, 50)

    iot_avg = st.slider("درجة جاهزية إنترنت الأشياء (IoT) في العمليات", 0, 100, 50)

    notes = st.text_area("ملاحظات إضافية (اختياري)")

    if st.button("حفظ نتائج التقييم"):
        st.session_state.results = {
            "Plan": plan_score,
            "Source": source_score,
            "Make": make_score,
            "Deliver": deliver_score,
            "Return": return_score,
        }
        st.session_state.iot_avg = iot_avg
        st.session_state.notes = notes

        if st.session_state.user_info.get("consent"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute('''
            INSERT INTO assessments (
                timestamp, name, company, sector, country, consent,
                plan_score, source_score, make_score, deliver_score, return_score,
                iot_avg, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                now,
                st.session_state.user_info.get("name"),
                st.session_state.user_info.get("company"),
                st.session_state.user_info.get("sector"),
                st.session_state.user_info.get("country"),
                int(st.session_state.user_info.get("consent")),
                plan_score,
                source_score,
                make_score,
                deliver_score,
                return_score,
                iot_avg,
                notes
            ))
            conn.commit()
            st.success("✅ تم حفظ نتائج التقييم بنجاح في قاعدة البيانات.")
        else:
            st.info("لم يتم حفظ البيانات لأن المستخدم لم يوافق على الحفظ.")

        st.markdown("### ملخص النتائج")
        df_summary = pd.DataFrame.from_dict(st.session_state.results, orient='index', columns=["الدرجة"])
        df_summary.loc["IoT"] = iot_avg
        st.table(df_summary.style.format("{:.2f}"))

        excel_data = to_excel(df_summary.reset_index().rename(columns={"index": "المرحلة"}))
        b64 = base64.b64encode(excel_data).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="نتائج_التقييم.xlsx">⬇️ تحميل نتائج التقييم Excel</a>', unsafe_allow_html=True)
    
    footer()

# --- صفحة سجل التقييمات ---
elif page == "records":
    st.header("🗄️ سجل التقييمات المحفوظة")

    c.execute('SELECT * FROM assessments ORDER BY timestamp DESC')
    rows = c.fetchall()

    if rows:
        df_records = pd.DataFrame(rows, columns=[
            "ID", "تاريخ ووقت التقييم", "المستخدم", "الشركة", "القطاع", "الدولة", "الموافقة على الحفظ",
            "تقييم التخطيط", "تقييم التوريد", "تقييم التصنيع", "تقييم التوزيع", "تقييم المرتجعات",
            "متوسط IoT", "ملاحظات"
        ])
        df_records["الموافقة على الحفظ"] = df_records["الموافقة على الحفظ"].apply(lambda x: "نعم" if x == 1 else "لا")
        st.dataframe(df_records.style.set_properties(**{'text-align': 'right'}))

        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df_records.to_excel(writer, index=False)
        excel_data = excel_buffer.getvalue()
        b64_excel = base64.b64encode(excel_data).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64_excel}" download="سجل_التقييمات.xlsx">⬇️ تحميل سجل التقييمات Excel</a>', unsafe_allow_html=True)
    else:
        st.info("لا توجد تقييمات محفوظة حتى الآن.")

    footer()

# --- صفحة معلومات التخرج ---
elif page == "graduation_info":
    st.header("ℹ️ معلومات مشروع التخرج")

    st.markdown("""
    **عنوان المشروع:**  
    تأثير الذكاء الاصطناعي على عمليات سلسلة التوريد: منهجية قائمة على نموذج SCOR

    **مصممة المنصة:**  
    سُهى ناصر سعيد عماره

    **المشرف الأكاديمي:**  
    أ.د. عماد كمهوي

    **الجامعة:**  
    جامعة القاهرة، كلية الهندسة، قسم نظم المعلومات

    **ملخص:**  
    يهدف هذا المشروع إلى تقييم مدى جاهزية تطبيق تقنيات الذكاء الاصطناعي والإنترنت الصناعي للأشياء (IoT) في عمليات سلسلة التوريد باستخدام نموذج SCOR كإطار عمل. تشمل المنصة تقييم متعدد الجوانب مع إمكانية حفظ البيانات وتحليل نقاط القوة والضعف.

    **الاتصال:**  
    البريد الإلكتروني: soha.nasser@example.com  
    رقم الهاتف: 0123456789  
    """)

    footer()
