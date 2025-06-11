# منصة SCOR AI المتكاملة - مشروع التخرج
# تصميم: سُها ناصر سعيد عماره  |  إشراف: أ.د. عماد قمحاوي

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import io
import json

# ====== إعداد الصفحة ======
st.set_page_config(page_title="منصة SCOR الذكية", layout="centered")

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


# ====== PAGE 2: RESULTS & ANALYSIS ======
elif page == "📊 النتائج والتحليل":
    st.header("📊 النتائج ومصفوفات التحليل")
    results = st.session_state.results
    swot = st.session_state.swot
    iot_avg = st.session_state.iot_avg
    user = st.session_state.user_info

    if not results:
        st.warning("يرجى تنفيذ التقييم أولًا.")
        st.stop()

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
        labels_bcg, readiness, importance_vals, categories = [], [], [], []
        for phase in results:
            imp = st.slider(f"أهمية {phase_labels.get(phase, phase)}", 1, 5, 3, key=f"imp_{phase}")
            bcg_importance[phase] = imp
            labels_bcg.append(phase)
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
            mode='markers+text', text=labels_bcg, textposition="top center",
            marker=dict(size=18, color=['green' if c=="⭐ نجم" else 'orange' if c=="❓ استفهام" else 'blue' if c=="🐄 بقرة" else 'red' for c in categories])
        ))
        fig_bcg.update_layout(title="مصفوفة BCG", xaxis_title="الأهمية", yaxis_title="الجاهزية",
                              xaxis=dict(range=[0,5]), yaxis=dict(range=[0,5]))
        st.plotly_chart(fig_bcg)
        for i, label in enumerate(labels_bcg):
            st.markdown(f"- {phase_labels.get(label, label)}: {categories[i]}")

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

# ====== PAGE 3: AI Recommendations & Graduation Info ======
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

    st.markdown("---")
    st.subheader("📄 معلومات مشروع التخرج")
    st.markdown("""
    - **عنوان المشروع:** منصة تقييم جاهزية الذكاء الاصطناعي في سلاسل الإمداد باستخدام نموذج SCOR  
    - **الطالبة:** سُهى ناصر سعيد عماره  
    - **المشرف:** أ.د. عماد كمّاهى  
    - **الجامعة:** [اكتبي اسم الجامعة هنا]  
    - **العام الدراسي:** 2024 - 2025  
    """)

    st.markdown("🧾 **تم تصميم وتطوير هذه المنصة باستخدام Python وStreamlit مع دعم الذكاء الاصطناعي والتحليلات الذكية.**")
    st.success("✅ شكراً لاستخدامك المنصة. يمكنك الآن تحميل النتائج أو العودة لتعديل التقييم.")
