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
    # تعريف حالة البداية فقط مرة واحدة
    if 'user_submitted' not in st.session_state:
        st.session_state.user_submitted = False

    st.header("🧪 التقييم لتبني الذكاء الاصطناعي - SCOR")
    st.markdown("### 👤 بيانات المستخدم")

    with st.form("user_info_form", clear_on_submit=False):
        user_name = st.text_input("الاسم الكامل")
        company_name = st.text_input("اسم الشركة")
        sector = st.selectbox("القطاع", ["الرعاية الصحية","التصنيع","اللوجستيات","الخدمات","أخرى"])
        country = st.text_input("الدولة")
        save_results = st.checkbox("أوافق على حفظ نتائجي")
        submitted = st.form_submit_button("ابدأ التقييم")

        if submitted:
            st.session_state.user_info = {
                'name': user_name,
                'company': company_name,
                'sector': sector,
                'country': country
            }
            st.session_state.save_results = save_results
            st.session_state.user_submitted = True

    if not st.session_state.user_submitted:
        st.stop()

    # تحميل الأسئلة
    try:
        df = pd.read_excel("SCOR_AI_Questions.xlsx")
    except:
        st.error("❌ لا يوجد الملف SCOR_AI_Questions.xlsx")
        st.stop()

    phase_labels = {
        "Plan":"📘 التخطيط","Source":"📗 التوريد",
        "Make":"📙 التصنيع","Deliver":"📕 التوزيع","Return":"📒 المرتجعات"
    }
    results = {}
    swot = {"قوة":[],"ضعف":[],"فرصة":[],"تهديد":[]}

    st.markdown("## 📝 تقييم المراحل")
    for phase in df['SCOR Phase'].unique():
        st.markdown(f"### {phase_labels.get(phase, phase)}")
        total = 0
        phase_q = df[df['SCOR Phase']==phase]
        for i, row in enumerate(phase_q.itertuples(), start=1):
            score = st.radio(f"{i}. {row._3}", [1,2,3,4,5], index=2, key=f"{phase}_{i}", horizontal=True, format_func=lambda x:f"{x}⭐")
            total += score
        avg = total/len(phase_q)
        results[phase] = avg

        if avg>=4:
            st.success("🔹 ممتاز")
            swot["قوة"].append(phase_labels.get(phase))
        elif avg>=2.5:
            st.warning("🟠 جيد")
            swot["فرصة"].append(phase_labels.get(phase))
        else:
            st.error("🔴 ضعيف")
            swot["ضعف"].append(phase_labels.get(phase))

    st.markdown("## 📡 تقييم IoT")
    q1 = st.radio("1. أجهزة استشعار؟",[1,2,3,4,5],index=2,key="iot1",horizontal=True)
    q2 = st.radio("2. لوحات تحكم؟",[1,2,3,4,5],index=2,key="iot2",horizontal=True)
    q3 = st.radio("3. تحليل لحظي؟",[1,2,3,4,5],index=2,key="iot3",horizontal=True)
    q4 = st.radio("4. تكامل مع ERP؟",[1,2,3,4,5],index=2,key="iot4",horizontal=True)

    iot_avg = (q1+q2+q3+q4)/4
    st.markdown(f"**متوسط IoT: {iot_avg:.1f}/5**")

    # حفظ في الجلسة
    st.session_state.results = results
    st.session_state.iot_avg = iot_avg
    st.session_state.swot = swot

    # حفظ النتيجة في الملف لو موافقة
    if st.session_state.save_results:
        save_results_to_excel(
            st.session_state.user_info['name'],
            st.session_state.user_info['company'],
            st.session_state.user_info['sector'],
            st.session_state.user_info['country'],
            iot_avg,
            results
        )


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
        labels, readiness, importance_vals, categories = [], [], [], []
        for phase in results:
            imp = st.slider(f"أهمية {phase_labels.get(phase, phase)}", 1, 5, 3, key=f"imp_{phase}")
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

    st.subheader("✨ توصيات ذكية حسب الجاهزية")
    for phase, score in results.items():
        if score < 2.5:
            st.markdown(f"🔴 **{phase_labels.get(phase, phase)}:** منخفض الجاهزية. يُوصى باستخدام حلول ذكاء اصطناعي مثل التنبؤ التلقائي وRPA.")
        elif score < 4:
            st.markdown(f"🟡 **{phase_labels.get(phase, phase)}:** متوسط الجاهزية. يُوصى بتوسيع التكامل مع أنظمة ERP أو DSS.")
        else:
            st.markdown(f"🟢 **{phase_labels.get(phase, phase)}:** جاهزية عالية. يُوصى بتفعيل التعلم الآلي لتحسين الأداء.")

    st.subheader("🌐 جاهزية إنترنت الأشياء (IoT)")
    if iot_avg < 2:
        st.error("منخفضة جدًا. يُنصح بتركيب حساسات وربطها بالأنظمة.")
    elif iot_avg < 4:
        st.warning("متوسطة. يُنصح بتحسين الاتصالات وتحليل البيانات.")
    else:
        st.success("جاهزية ممتازة لإنترنت الأشياء.")

    st.subheader("🏁 مقترحات استراتيجية")
    if "ضعف" in swot and swot["ضعف"]:
        st.markdown("- 📉 يجب معالجة نقاط الضعف التالية: " + ", ".join(swot["ضعف"]))
    if "فرصة" in swot and swot["فرصة"]:
        st.markdown("- 🚀 يُوصى بالاستفادة من الفرص التالية: " + ", ".join(swot["فرصة"]))
    if "قوة" in swot and swot["قوة"]:
        st.markdown("- 🛡️ تعظيم الاستفادة من نقاط القوة: " + ", ".join(swot["قوة"]))

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
