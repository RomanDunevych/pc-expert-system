# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from knowledge_base import DIAGNOSES, SYMPTOMS, KNOWLEDGE_MATRIX, RECOMMENDATIONS

# Налаштування сторінки
st.set_page_config(page_title="Експертна система діагностики ПК", layout="wide")

st.title("🖥️ Експертна система діагностики несправностей ПК")
st.caption("Моделювання роботи сервісного інженера з оцінкою ймовірностей несправностей")

st.markdown("""
---
### 📍 Введення симптомів (Дані огляду)
Оберіть симптоми, які ви спостерігаєте у роботі комп'ютера. На основі цих даних система розрахує коефіцієнти впевненості для різних поломок.
""")

# Створення форми вибору симптомів
selected_symptoms = []
col1, col2 = st.columns(2)

symptom_keys = list(SYMPTOMS.keys())
half_len = (len(symptom_keys) + 1) // 2

with col1:
    for key in symptom_keys[:half_len]:
        if st.checkbox(SYMPTOMS[key], key=key):
            selected_symptoms.append(key)

with col2:
    for key in symptom_keys[half_len:]:
        if st.checkbox(SYMPTOMS[key], key=key):
            selected_symptoms.append(key)

# Кнопки управління
st.write("")
btn_col1, btn_col2 = st.columns([1, 5])
with btn_col1:
    analyze_btn = st.button("🔍 Розрахувати діагноз", type="primary")

# Алгоритм Двигуна Висновків (Inference Engine)
def calculate_confidence(selected_keys):
    results = {}
    for diag_key, weight_map in KNOWLEDGE_MATRIX.items():
        score = 0
        for s_key in selected_keys:
            if s_key in weight_map:
                score += weight_map[s_key]
        results[diag_key] = min(score, 100)  # Обмеження максимум 100%
    return results

if analyze_btn:
    if not selected_symptoms:
        st.warning("Будь ласка, виберіть хоча б один симптом для проведення аналізу!")
    else:
        results = calculate_confidence(selected_symptoms)
        
        # Сортування за спаданням ймовірності
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        top_diag_key, top_score = sorted_results[0]
        
        st.markdown("---")
        st.subheader("📊 Результати аналізу діагностики")
        
        # Виведення вердикту
        if top_score > 0:
            st.success(f"**Найімовірніший діагноз:** {DIAGNOSES[top_diag_key]} — **{top_score}% впевненості**")
            st.info(f"💡 **Рекомендація експерта:** {RECOMMENDATIONS[top_diag_key]}")
        else:
            st.info("За обраними симптомами не вдалося підтвердити жодну з базових гіпотез. Спробуйте уточнити симптоми.")

        # Візуалізація результатів
        col_chart, col_table = st.columns([3, 2])
        
        # Підготовка даних для таблиці та графіка
        df_data = {
            "Можлива несправність": [DIAGNOSES[k] for k, _ in sorted_results],
            "Ймовірність (%)": [v for _, v in sorted_results]
        }
        df = pd.DataFrame(df_data)

        with col_chart:
            st.write("**Графічний розподіл ймовірностей гіпотез:**")
            fig, ax = plt.subplots(figsize=(7, 4))
            bars = ax.barh(df["Можлива несправність"], df["Ймовірність (%)"], color="#2b5c8f")
            ax.set_xlim(0, 100)
            ax.set_xlabel("Рівень впевненості (%)")
            ax.invert_yaxis()  # Найвищий результат вгорі
            
            # Підписи значень на барах
            for bar in bars:
                width = bar.get_width()
                ax.text(width + 1, bar.get_y() + bar.get_height()/2, f'{int(width)}%', 
                        va='center', ha='left', fontsize=9)
                
            st.pyplot(fig)

        with col_table:
            st.write("**Спідставлена таблиця оцінок:**")
            st.dataframe(df, hide_index=True, use_container_width=True)