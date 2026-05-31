import streamlit as st
import requests
import base64
import io
import json
import cv2
import numpy as np
from PIL import Image

def image_to_base64(img):
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=90)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def analyze_morphology(img, api_key, tooth_num="", mode="tech"):
    img_base64 = image_to_base64(img)

    mode_text = "зубного техника" if mode == "tech" else "врача-стоматолога"

    prompt = f"""You are a dental morphology expert analyzing tooth structure.
Analyze ONLY the geometric structure and surface morphology. 
IGNORE color, shade, transparency, opalescence completely.
{"Tooth number: " + tooth_num if tooth_num else ""}

Return ONLY a valid JSON object:
{{
  "elements": [
    {{
      "name": "название на русском",
      "type": "line or points or contour",
      "severity": "norm or attention or fix",
      "points": [[x1,y1],[x2,y2]],
      "color_bgr": [B,G,R],
      "description": "краткое описание"
    }}
  ],
  "for_{mode}": {{
    "summary": "общий вывод для {mode_text}",
    "actions": [
      {{
        "priority": "high or medium or low",
        "element": "название элемента",
        "problem": "что не так",
        "action": "что конкретно сделать"
      }}
    ]
  }}
}}

Identify these elements (coordinates as % of image 0-100):

RIDGES (vertical structures):
- Медиальный валик: vertical line on medial side, color [0,180,0]
- Центральный валик: central vertical line, color [100,220,100]
- Дистальный валик: vertical line on distal side, color [0,120,0]
- Вертикальные макроструктуры: overall vertical direction, color [150,200,150]

SURFACE TEXTURE:
- Перикиматы: horizontal growth lines, color [0,140,255] (orange in BGR)
- Горизонтальные макроструктуры: horizontal steps, color [0,160,220]
- Микротрещины: visible cracks ONLY, color [0,50,255] (red in BGR)

GEOMETRY:
- Контур зуба: outer contour shape, color [200,200,200]
- Экватор зуба: most prominent point line, color [255,200,0]
- Цервикальный контур: cervical line shape, color [150,100,255]
- Линия режущего края: incisal edge line, color [255,255,100]
- Медиальный угол: mark medial angle point, color [0,255,200]
- Дистальный угол: mark distal angle point, color [0,200,255]
- Контактные точки: contact points, color [0,165,255]
- Осевой наклон: axis line of tooth, color [255,0,150]
- Поверхностный блик: light reflection position, color [200,200,255]
- Зенит десны: gingival zenith if visible, color [150,100,255]

For severity use:
- norm: element looks natural and correct
- attention: minor deviation worth noting
- fix: clear problem needs correction

Return ONLY JSON, no markdown, no explanation."""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o",
        "max_tokens": 3000,
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_base64}"
                    }
                },
                {"type": "text", "text": prompt}
            ]
        }]
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Ошибка OpenAI {response.status_code}: {response.text}")

def draw_annotations(img, elements):
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    h, w = img_cv.shape[:2]

    for el in elements:
        color = tuple(el.get("color_bgr", [0, 255, 0]))
        points = el.get("points", [])
        el_type = el.get("type", "line")
        name = el.get("name", "")
        severity = el.get("severity", "norm")

        if len(points) < 1:
            continue

        pts = [(int(p[0] * w / 100), int(p[1] * h / 100)) for p in points]

        thickness = 2
        if severity == "fix":
            thickness = 3
        elif severity == "attention":
            thickness = 2

        if el_type == "line" and len(pts) >= 2:
            for i in range(len(pts) - 1):
                cv2.line(img_cv, pts[i], pts[i+1], color, thickness)
            cv2.arrowedLine(img_cv, pts[-2], pts[-1],
                           color, thickness, tipLength=0.2)
            cv2.putText(img_cv, name, (pts[0][0] + 5, pts[0][1] - 8),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)

        elif el_type == "points":
            for pt in pts:
                cv2.circle(img_cv, pt, 6, color, -1)
                cv2.putText(img_cv, name, (pt[0] + 8, pt[1]),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)

        elif el_type == "contour" and len(pts) >= 2:
            for i in range(len(pts) - 1):
                cv2.line(img_cv, pts[i], pts[i+1], color, 1)

    return Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))

def show_page():
    st.title("🔬 Морфология")
    st.info("Загрузи фото зуба — GPT-4o определит морфологические элементы и нанесёт аннотации на фото.")

    if st.button("🗑️ Очистить"):
        for key in ["morph_img", "morph_data", "morph_annotated"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📷 Фото зуба")
        st.caption("Лучший результат — чёрный фон, зуб крупно")

        img_file = st.camera_input("Сфотографировать", key="cam_morph")
        if not img_file:
            img_file = st.file_uploader(
                "Или загрузить из галереи",
                type=["jpg","jpeg","png"],
                key="morph_upload"
            )
        if img_file:
            st.session_state["morph_img"] = img_file

        if st.session_state.get("morph_img"):
            st.image(st.session_state["morph_img"],
                    use_container_width=True)

    with col2:
        st.subheader("⚙️ Параметры")

        tooth_num = st.text_input(
            "Номер зуба",
            placeholder="Например: 11 или 21",
            key="morph_tooth"
        )

        mode = st.radio(
            "Режим анализа",
            ["👨‍🔧 Для техника", "👨‍⚕️ Для врача"],
            horizontal=True,
            key="morph_mode"
        )
        mode_key = "tech" if "техника" in mode else "doctor"

    if st.session_state.get("morph_img"):
        st.divider()

        api_key = st.session_state.get("openai_api_key", "")

        if api_key:
            if st.button("🔍 Анализировать морфологию", type="primary"):
                with st.spinner("GPT-4o анализирует структуру зуба..."):
                    try:
                        img = Image.open(
                            st.session_state["morph_img"]
                        ).convert("RGB")

                        result_text = analyze_morphology(
                            img, api_key, tooth_num, mode_key
                        )

                        clean = result_text.strip()
                        if "```" in clean:
                            parts = clean.split("```")
                            for part in parts:
                                if "{" in part:
                                    clean = part
                                    if clean.startswith("json"):
                                        clean = clean[4:]
                                    break

                        data = json.loads(clean)
                        st.session_state["morph_data"] = data

                        annotated = draw_annotations(
                            img, data.get("elements", [])
                        )
                        st.session_state["morph_annotated"] = annotated

                    except json.JSONDecodeError as e:
                        st.error(f"Ошибка парсинга JSON: {str(e)}")
                        st.text(result_text)
                    except Exception as e:
                        st.error(f"Ошибка: {str(e)}")
        else:
            st.warning("Перейди в ⚙️ Настройки и введи OpenAI API ключ")

    if st.session_state.get("morph_annotated"):
        st.divider()
        st.subheader("📊 Результат анализа")

        col_orig, col_ann = st.columns(2)
        with col_orig:
            st.caption("Оригинал")
            st.image(st.session_state["morph_img"],
                    use_container_width=True)
        with col_ann:
            st.caption("С аннотациями")
            st.image(st.session_state["morph_annotated"],
                    use_container_width=True)

    if st.session_state.get("morph_data"):
        data = st.session_state["morph_data"]
        mode_key = "tech" if "техника" in st.session_state.get(
            "morph_mode", "техника") else "doctor"
        mode_data = data.get(f"for_{mode_key}", {})

        if mode_data:
            st.divider()
            st.subheader("📋 Выводы и рекомендации")
            st.markdown(f"**{mode_data.get('summary', '')}**")

            actions = mode_data.get("actions", [])
            if actions:
                high = [a for a in actions if a.get("priority") == "high"]
                medium = [a for a in actions if a.get("priority") == "medium"]
                low = [a for a in actions if a.get("priority") == "low"]

                if high:
                    st.markdown("### 🔴 Исправить")
                    for a in high:
                        st.error(f"**{a.get('element')}** — {a.get('problem')}\n\n➡️ {a.get('action')}")

                if medium:
                    st.markdown("### 🟡 Обратить внимание")
                    for a in medium:
                        st.warning(f"**{a.get('element')}** — {a.get('problem')}\n\n➡️ {a.get('action')}")

                if low:
                    st.markdown("### 🟢 Норма")
                    for a in low:
                        st.success(f"**{a.get('element')}** — {a.get('description', 'всё хорошо')}")

        st.divider()
        col_leg1, col_leg2 = st.columns(2)
        with col_leg1:
            st.markdown("**Легенда:**")
            for el in data.get("elements", [])[:8]:
                severity_icon = {"norm": "🟢", "attention": "🟡", "fix": "🔴"}.get(
                    el.get("severity", "norm"), "⚪")
                st.markdown(f"{severity_icon} {el.get('name')} — {el.get('description', '')}")
        with col_leg2:
            for el in data.get("elements", [])[8:]:
                severity_icon = {"norm": "🟢", "attention": "🟡", "fix": "🔴"}.get(
                    el.get("severity", "norm"), "⚪")
                st.markdown(f"{severity_icon} {el.get('name')} — {el.get('description', '')}")
