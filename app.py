import streamlit as st
from datetime import datetime
from streamlit_drawable_canvas import st_canvas

st.set_page_config(
    page_title="DxRadar Bedside",
    page_icon="🩺",
    layout="centered"
)

# --- REGULATORY & LEGAL SCOPE BANNER ---
st.warning(
    """
    ⚖️ **CLINICAL GOVERNANCE & STATUTORY DISCLAIMER:**  
    This software is an evidence-based Clinical Decision Support System (CDSS). **DxRadar does not possess clinical authority, does not make final clinical diagnoses, and does not provide drug or medication recommendations.** All diagnostic determinations, treatment choices, and pharmacological prescriptions remain the exclusive legal responsibility of the licensed treating physician.
    """
)

# --- 1. CLINICAL KNOWLEDGE BASE & BASE PRIORS ---
BASE_PRIORS = {
    "Acute Pancreatitis": 0.25,
    "Acute Cholecystitis": 0.25,
    "Perforated Peptic Ulcer": 0.25,
    "Acute Appendicitis": 0.25
}

CONFIRMATORY_TESTS = {
    "Acute Pancreatitis": "Bedside USG Abdomen + Serum Lipase (>3x ULN)",
    "Acute Cholecystitis": "Fasting Hepatobiliary USG (Gallbladder wall >4mm, sonographic Murphy's)",
    "Perforated Peptic Ulcer": "Urgent Erect Chest Radiograph (Subdiaphragmatic Free Air)",
    "Acute Appendicitis": "Targeted Grayscale Appendix USG / Non-Contrast CT Abdomen"
}

MANEUVERS = [
    {
        "id": "epigastric_guarding",
        "name": "Epigastric Guarding & Rigidity",
        "target": "Acute Pancreatitis",
        "lr_pos": 4.5,
        "lr_neg": 0.25
    },
    {
        "id": "murphys_sign",
        "name": "Murphy's Sign (Inspiratory Arrest)",
        "target": "Acute Cholecystitis",
        "lr_pos": 5.0,
        "lr_neg": 0.10
    },
    {
        "id": "board_rigidity",
        "name": "Board-Like Abdominal Rigidity",
        "target": "Perforated Peptic Ulcer",
        "lr_pos": 8.0,
        "lr_neg": 0.20
    },
    {
        "id": "mcburneys_sign",
        "name": "McBurney's Point Tenderness",
        "target": "Acute Appendicitis",
        "lr_pos": 4.2,
        "lr_neg": 0.15
    }
]

# --- 2. HEADER & ACTIVE PATIENT ANCHOR ---
st.title("DxRadar: Bedside Co-Pilot")
st.caption("Adaptive Bayesian Differential Navigator · Surgery Ward Rounds")

with st.container(border=True):
    col_p1, col_p2 = st.columns(2)
    col_p1.markdown("**Patient:** Bed 14 — Ramesh K. (58M)")
    col_p1.markdown("**Chief Complaint:** Epigastric Pain (22h)")
    col_p2.markdown("**Vitals:** BP 118/76 | HR 98 | SpO2 98%")
    col_p2.markdown("**Safety Net:** Inferior Wall MI Ruled Out (ECG Normal)")

st.divider()

# --- 3. BEDSIDE PHYSICAL EXAMINATION ---
st.subheader("1. Bedside Physical Maneuvers")
st.write("Record findings to dynamically adjust diagnostic probabilities:")

active_signs = {}
for m in MANEUVERS:
    col_name, col_input = st.columns([3, 2])
    col_name.markdown(f"**{m['name']}**")
    val = col_input.radio(
        label=m["name"],
        options=["0 (Neutral)", "+ (Present)", "− (Absent)"],
        horizontal=True,
        key=m["id"],
        label_visibility="collapsed"
    )
    active_signs[m["id"]] = val

# --- 4. BAYESIAN COMPUTATION ENGINE ---
raw_posteriors = {}
for condition, prior in BASE_PRIORS.items():
    odds = prior / (1.0 - prior)
    for m in MANEUVERS:
        if m["target"] == condition:
            state = active_signs.get(m["id"])
            if "+" in state:
                odds *= m["lr_pos"]
            elif "−" in state:
                odds *= m["lr_neg"]
    raw_posteriors[condition] = odds / (1.0 + odds)

# Normalize
total_weight = sum(raw_posteriors.values())
sorted_differentials = sorted(
    {k: v / total_weight for k, v in raw_posteriors.items()}.items(),
    key=lambda x: x[1],
    reverse=True
)

top_condition, top_prob = sorted_differentials[0]
second_condition, second_prob = sorted_differentials[1]
top_pct = int(top_prob * 100)
second_pct = int(second_prob * 100)

# Check for ambiguity (margin < 15% or top probability < 50%)
is_ambiguous = (top_prob < 0.50) or ((top_prob - second_prob) < 0.15)

# --- 5. DYNAMIC PROBABILITY RADAR ---
st.divider()
st.subheader("2. Dynamic Differential Radar")

for condition, prob in sorted_differentials:
    pct = int(prob * 100)
    st.write(f"**{condition}** — `{pct}%`")
    st.progress(prob)

# --- AMBIGUITY / DOMINANT CONDITIONAL RENDERING ---
if is_ambiguous:
    st.warning(
        f"""
        🚩 **CLINICAL AMBIGUITY FLAG DETECTED:**  
        The diagnostic profile shows overlapping probabilities:  
        • **{top_condition}** ({top_pct}%) vs. **{second_condition}** ({second_pct}%)  
        **Recommendation:** Clinical findings are equivocal. Do not rush diagnostic closure. Order cross-sectional imaging (CT Abdomen) and escalate to senior surgical registrar for comprehensive re-evaluation.
        """
    )
else:
    st.success(f"**Dominant Working Impression ({top_pct}%): {top_condition}**")
    st.info(f"🎯 **Targeted Confirmatory Protocol (Investigative Only):** {CONFIRMATORY_TESTS[top_condition]}")

# --- 6. PHYSICIAN ATTESTATION & VISUAL SIGNATURE ---
st.divider()
st.subheader("3. Physician Sign-Off & Verification")

with st.container(border=True):
    st.markdown(
        f"""
        **Provisional Impression:** `{top_condition}` ({top_pct}% post-test confidence)  
        *Clinical Verification Notice: The software does not take clinical decisions or prescribe regimens. The diagnosis is authenticated solely upon clinician signature.*
        """
    )
    
    chk_exam = st.checkbox("Bedside examination and acute surgical signs personally verified.")
    chk_corr = st.checkbox("Objective lab and imaging markers clinically correlate with this working diagnosis.")
    chk_no_auto = st.checkbox("I acknowledge that medical orders and treatment plans are determined solely by the treating medical team.")

    st.markdown("##### Visual Signature")
    st.caption("Sign below using touchscreen, stylus, or cursor:")

    canvas_result = st_canvas(
        stroke_width=2,
        stroke_color="#1E293B",
        background_color="#F8FAFC",
        height=120,
        width=360,
        drawing_mode="freedraw",
        key="canvas_sig",
    )

    # Clinical stamp placeholder
    st.markdown(
        """
        <div style="border: 2px dashed #94A3B8; border-radius: 8px; padding: 12px; margin-top: 10px; background-color: #F8FAFC; color: #475569; font-family: monospace; font-size: 13px;">
            <div>CLINICAL ATTESTATION STAMP:</div>
            <div style="margin-top: 8px;">Physician Name: ___________________________</div>
            <div style="margin-top: 6px;">Registration ID: ___________________________</div>
            <div style="margin-top: 6px;">Date & Time: &nbsp;&nbsp;&nbsp;&nbsp;____ / ____ / 2026 &nbsp;&nbsp;____:____</div>
            <div style="margin-top: 8px;">Signature: &nbsp;&nbsp;&nbsp;&nbsp;[ Hand-drawn Above ]</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    can_lock = chk_exam and chk_corr and chk_no_auto and (canvas_result.image_data is not None)

    if st.button("🔒 Authorize & Lock Working Diagnosis", disabled=not can_lock, type="primary"):
        st.success(f"Working impression of {top_condition} officially authenticated by attending clinician.")

# --- 7. AUTOMATED 5:00 PM SBAR HANDOVER ---
st.divider()
with st.expander("4. View Automated 5:00 PM SBAR Handover Note", expanded=False):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    status_label = "CLINICALLY AMBIGUOUS - REQUIRES RE-EVALUATION" if is_ambiguous else f"DOMINANT WORKING IMPRESSION: {top_condition}"
    sbar_text = f"""====================================================
DXRADAR SHIFT HANDOVER REPORT (SBAR) - {timestamp}
====================================================
[S] SITUATION:
    Bed 14: Ramesh K., 58M.
    Chief Complaint: Epigastric pain radiating to back (22h duration).

[B] BACKGROUND:
    Admitted to Surgical Ward. Bedside decision radar applied.
    Safety Net: Inferior Wall MI ruled out via ECG.

[A] ASSESSMENT:
    Status: {status_label} ({top_pct}% Bayesian Confidence).
    Investigative Pathway: {CONFIRMATORY_TESTS[top_condition]}.
    Clinical Ambiguity Flag: {"YES - Close Differential Match" if is_ambiguous else "NO - Clear Divergence"}.
    Notice: Software does not prescribe medication or finalize clinical diagnosis.

[R] RECOMMENDATION & ON-CALL ACTION PLAN:
    [ ] Treating physician to independently determine clinical management and drug orders.
    [ ] Check pending Serum Lipase and Bedside USG reports.
    [ ] Re-examine abdomen if guarding becomes generalized or pain score increases.
    [ ] Escalate to on-call surgical registrar if MAP drops < 65 mmHg.
"""
    st.text_area("Handoff Note (Ready for EMR / Duty Handover):", sbar_text, height=230)
    st.download_button(
        label="Download SBAR Handoff (.txt)",
        data=sbar_text,
        file_name="SBAR_Bed14_Ramesh.txt",
        mime="text/plain"
    )