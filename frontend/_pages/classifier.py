def _classify(file_obj, result_col):
    from utils import BACKEND_URL, get_headers
    import requests

    with st.spinner("🤖 Analyzing with AI — Step 1: Object detection..."):
        file_obj.seek(0)

        files = {
            "file": (
                getattr(file_obj, "name", "image.jpg"),
                file_obj,
                "image/jpeg"
            )
        }

        try:
            response = requests.post(
                f"{BACKEND_URL}/classify/",
                files=files,
                headers=get_headers(),
                timeout=180  # ← IMPORTANT FIX
            )
            resp = response.json()
        except requests.exceptions.Timeout:
            st.error("Backend is waking up (cold start). Please wait 30–60 seconds and try again.")
            return
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
            return

    if not resp or not resp.get("success"):
        st.error("Classification failed. Backend may still be warming up.")
        return

    result = resp.get("data", {})
    cat    = result.get("waste_category", "General Waste")
    conf   = result.get("confidence", 0)
    obj    = result.get("object_name", "Unknown Item")
    inst   = result.get("disposal_instructions", "")
    tip    = result.get("recycling_tip", "")
    mode   = result.get("mode", "heuristic")
    alts   = result.get("alternatives", [])

    with result_col:
        st.markdown(
            _result_cards(obj, cat, conf, inst, tip, "", mode, alts),
            unsafe_allow_html=True,
        )
        show_toast(f"{obj} → {cat} | +5 pts 🌱", "success")
