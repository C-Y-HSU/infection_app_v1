import streamlit as st
import google.generativeai as genai
import json

# 1. 頁面基本設定 (美化版面)
st.set_page_config(
    page_title="長照機構感染監測 AI 自動審核系統",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自訂 CSS 樣式美化
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #2563EB;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 安全讀取 API Key (直接從 Secrets 載入)
gemini_api_key = ""
if "GEMINI_API_KEY" in st.secrets:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]

with st.sidebar:
    # 修正原本圖片語法錯誤
    st.image("https://img.icons8.com/color/96/hospital-3.png", width=80)
    st.title("⚙️ 系統資訊")
    
    if gemini_api_key:
        st.success("🔒 AI 審核引擎服務中")
    else:
        st.error("⚠️ 系統尚未設定 API Key，請至 Streamlit Cloud 的 Secrets 後台設定。")
    
    st.info("💡 本系統根據《台灣長期照護機構之機構內感染監測定義》進行自動比對與 AI 語意判讀。")

# 3. 頁面標題
st.markdown('<div class="main-header">🏥 長照機構感染監測 AI 審核系統</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">護理站與服務台專用 — 快速填寫、自動檢核是否符合收案定義</div>', unsafe_allow_html=True)

# 4. 表單分區 (Step 1, 2, 3)
st.markdown("### 📋 臨床資料輸入")

tab1, tab2, tab3 = st.tabs(["**Step 1: 住民與管路基線**", "**Step 2: 臨床症狀與體徵**", "**Step 3: 護理紀錄與報告貼上**"])

with tab1:
    st.markdown("#### 👤 1. 基本與基線狀態評估")
    col1, col2, col3 = st.columns(3)
    with col1:
        patient_id = st.text_input("住民姓名 / 床號", placeholder="例如：102-1 李○○")
    with col2:
        eval_date = st.date_input("評估日期")
    with col3:
        catheter_status = st.radio("導尿管使用狀態", ["無使用", "有使用（留置導尿管）"])
    
    st.divider()
    col4, col5 = st.columns(2)
    with col4:
        old_symptoms = st.multiselect(
            "慢性 / 已知舊症狀 (用於排除舊疾)",
            ["慢性咳嗽", "慢性急尿 / 失禁", "慢性皮膚紅疹", "無相關舊疾"]
        )
    with col5:
        non_infectious = st.multiselect(
            "非感染疾病狀態 (用於排除非感染因素)",
            ["心衰竭診斷", "慢性阻塞性肺病(COPD)", "近期使用軟便劑/新藥物", "無"]
        )

with tab2:
    st.markdown("#### 🤒 2. 症狀與生命徵象勾選")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        temp_input = st.number_input("體溫量測數字 (℃)", min_value=35.0, max_value=42.0, value=36.5, step=0.1)
    with col_t2:
        temp_site = st.selectbox("量測部位", ["耳溫", "額溫", "腋溫", "肛溫"])
    
    st.markdown("**全身性與功能症狀：**")
    symptoms_general = st.multiselect(
        "選擇全身症狀 (可複選)",
        ["寒顫", "肌肉酸痛", "頭痛", "極度倦怠感", "意識狀態變差 (GCS下降)", "日常生活功能變差 (巴氏量表下降)"]
    )
    
    st.markdown("**各系統局部症狀勾選：**")
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        st.caption("🫁 呼吸道症狀")
        symptom_resp = st.multiselect("呼吸道相關", ["新發作/加劇咳嗽", "新產生/增加膿痰", "肋膜性胸痛", "新產生/加劇濕囉音或喘鳴", "呼吸速率>25次/分", "流鼻水/打噴嚏/喉嚨痛"])
        
    with col_s2:
        st.caption("🚽 泌尿道症狀")
        symptom_uti = st.multiselect("泌尿道相關", ["排尿灼熱感/頻尿/急尿", "肋脊角疼痛/恥骨上壓痛", "尿液血尿/惡臭/沉澱物"])
        
    with col_s3:
        st.caption("🤢 腸胃/皮膚/其他")
        symptom_gi_skin = st.multiselect("腸胃/皮膚/其他", ["24hr內稀便/水便 ≥2次", "24hr內嘔吐 ≥2次", "噁心/腹痛壓痛", "皮膚/傷口有膿性分泌物", "皮膚新發紅/腫/熱/痛", "眼睛/耳朵膿性分泌物"])

with tab3:
    st.markdown("#### 📝 3. 護理紀錄與事件報告貼上")
    st.info("💡 請直接複製貼上當班護理紀錄、檢驗報告 (如 U/A、X光、血培) 或事件描述，AI 會自動從中擷取關鍵數據與醫師診斷！")
    nursing_note = st.text_area("護理紀錄 / 檢驗數據 / 事件報告內容：", height=180, placeholder="例如：14:00 住民反映下腹部壓痛，導尿管引流液呈混濁且有嚴重惡臭沉澱物。採尿送檢 U/A 報告顯示 WBC 滿視野、膿尿。醫師開立抗生素治療...")

st.markdown("---")

# 5. 啟動 AI 審核按鈕與 Prompt 邏輯
if st.button("🚀 開始 AI 監測定義自動審核"):
    if not gemini_api_key:
        st.error("⚠️ 請先至 Streamlit Cloud 後台 Settings -> Secrets 設定 GEMINI_API_KEY！")
    elif not nursing_note and not (symptom_resp or symptom_uti or symptom_gi_skin or symptoms_general):
        st.warning("⚠️ 請至少在 Step 2 勾選症狀，或在 Step 3 貼上護理紀錄！")
    else:
        with st.spinner("🤖 AI 正在比對《台灣長期照護機構感染監測定義》中，請稍候..."):
            try:
                # 設定 API Key
                genai.configure(api_key=gemini_api_key)
                
                # 自動搜尋目前 API Key 底下可用且支援 generateContent 的模型名稱 (徹底避開 404)
                available_models = [
                    m.name for m in genai.list_models() 
                    if 'generateContent' in m.supported_generation_methods
                ]
                
                # 優先抓取含有 flash 或 pro 的模型，避免名稱不一致問題
                selected_model_name = next(
                    (m for m in available_models if 'flash' in m or 'pro' in m), 
                    available_models[0]
                )
                
                model = genai.GenerativeModel(selected_model_name)

                # 組合 Prompt 輸入內容
                user_payload = f"""
                【個案基本資料與基線】
                - 住民：{patient_id}
                - 導尿管狀態：{catheter_status}
                - 舊疾/慢性症狀：{", ".join(old_symptoms) if old_symptoms else "無"}
                - 非感染疾病背景：{", ".join(non_infectious) if non_infectious else "無"}

                【勾選症狀與數據】
                - 體溫：{temp_input} ℃ ({temp_site})
                - 全身症狀：{", ".join(symptoms_general) if symptoms_general else "無"}
                - 呼吸道症狀：{", ".join(symptom_resp) if symptom_resp else "無"}
                - 泌尿道症狀：{", ".join(symptom_uti) if symptom_uti else "無"}
                - 腸胃/皮膚/其他症狀：{", ".join(symptom_gi_skin) if symptom_gi_skin else "無"}

                【護理紀錄與報告 (Step 3)】
                {nursing_note if nursing_note else "未提供自由文字紀錄"}
                """

                system_prompt = """
                你是一名專業的「長照機構感染管制專任人員與醫療審核 AI 助手」。你的任務是嚴格根據《台灣長期照護機構內感染監測定義》指南，審核使用者輸入的資料，判斷是否符合收案定義。

                請嚴格執行三大全局原則：
                1. 症狀必須是新發作或急性惡化（排除舊疾）。
                2. 排除非感染因素（如心衰竭引起的呼吸困難、軟便劑引發的腹瀉等）。
                3. 不可僅靠單一證據。

                請對照 7 大類定義（呼吸道、UTI、腸胃道、眼耳鼻口、皮膚、血流、無法解釋發燒）。

                請用清晰的 Markdown 格式輸出以下區塊：
                ### 📌 1. 審核判定結果
                - **結果**：【🟢 符合收案】/【🟡 疑義待補充】/【🔴 不符合收案】
                - **符合之監測項目**：(例如：有症狀的泌尿道感染 - 使用導尿管)

                ### 🔍 2. 資訊抽取與門檻比對
                - **從護理紀錄/勾選抽取的關鍵點**：
                - **符合之症狀/徵象條目計數**：

                ### ⚖️ 3. 判定邏輯與三大原則檢核
                - **新發作與舊疾排除說明**：
                - **非感染因素排除說明**：

                ### 📋 4. 標準化通報摘要 (可直接複製)
                ```text
                (提供一段簡短標準的文字通報格式)
                ```
                """

                # 呼叫 AI 產生審核報告
                response = model.generate_content(f"{system_prompt}\n\n以下為待審核的個案資料：\n{user_payload}")
                
                # 顯示結果
                st.success("✅ 審核完成！")
                st.markdown("### 📊 審核報告產出")
                
                with st.container(border=True):
                    st.markdown(response.text)

            except Exception as e:
                st.error(f"❌ 執行過程發生錯誤：{str(e)}")
