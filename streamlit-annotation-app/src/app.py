import streamlit as st
import pandas as pd
import json
from pathlib import Path
import hashlib

# ============================================================================
# Configuration
# ============================================================================
DATA_DIR = Path(__file__).parent.parent / "data"
SPEECHES_FILE = DATA_DIR / "sampled_speeches.json"
ANNOTATIONS_FILE = DATA_DIR / "annotations.csv"

# TEST MODE: Set to True to only load 3 speeches for testing
TEST_MODE = True
TEST_SPEECHES_COUNT = 3

# ============================================================================
# Data Handling
# ============================================================================
def load_speeches():
    """Load speeches from JSON file."""
    try:
        with open(SPEECHES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        speeches = data['speeches']
        
        # In test mode, only return first N speeches
        if TEST_MODE:
            speeches = speeches[:TEST_SPEECHES_COUNT]
        
        return speeches
    except FileNotFoundError:
        st.error(f"❌ File not found: {SPEECHES_FILE}")
        st.info("Please copy sampled_speeches.json to the data/ directory")
        st.stop()
    except json.JSONDecodeError:
        st.error(f"❌ Invalid JSON file: {SPEECHES_FILE}")
        st.info("The JSON file appears to be empty or corrupted.")
        st.stop()

def get_annotation(item_id, rater_id):
    """Get specific annotation for this item_id + rater_id combination."""
    if not ANNOTATIONS_FILE.exists():
        return None
    
    try:
        df = pd.read_csv(ANNOTATIONS_FILE)
        mask = (df['item_id'] == item_id) & (df['rater_id'] == rater_id)
        
        if mask.any():
            row = df[mask].iloc[0]
            return {
                'score': int(row['score']),
                'justification': str(row['justification'])
            }
    except Exception as e:
        st.error(f"Error reading annotations: {e}")
    
    return None

def get_annotations_for_rater(rater_id):
    """Get all annotations by this rater as a dict indexed by item_id."""
    if not ANNOTATIONS_FILE.exists():
        return {}
    
    try:
        df = pd.read_csv(ANNOTATIONS_FILE)
        rater_df = df[df['rater_id'] == rater_id]
        
        annotations = {}
        for _, row in rater_df.iterrows():
            annotations[row['item_id']] = {
                'score': int(row['score']),
                'justification': row['justification']
            }
        
        return annotations
    except Exception as e:
        st.error(f"Error reading annotations: {e}")
        return {}

def update_annotation(item_id, rater_id, score, justification, context, statement):
    """Update existing annotation or create new one."""
    if not ANNOTATIONS_FILE.exists():
        # Create new file with this annotation
        annotation = {
            "item_id": item_id,
            "rater_id": rater_id,
            "score": score,
            "justification": justification,
            "context": context,
            "statement": statement
        }
        df = pd.DataFrame([annotation])
        ANNOTATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(ANNOTATIONS_FILE, index=False)
        return
    
    df = pd.read_csv(ANNOTATIONS_FILE)
    
    # Check if annotation exists
    mask = (df['item_id'] == item_id) & (df['rater_id'] == rater_id)
    
    if mask.any():
        # Update existing row - OVERWRITE the data
        df.loc[mask, 'score'] = score
        df.loc[mask, 'justification'] = justification
        df.loc[mask, 'context'] = context
        df.loc[mask, 'statement'] = statement
    else:
        # Append new row
        new_row = pd.DataFrame([{
            "item_id": item_id,
            "rater_id": rater_id,
            "score": score,
            "justification": justification,
            "context": context,
            "statement": statement
        }])
        df = pd.concat([df, new_row], ignore_index=True)
    
    # Save back to file
    df.to_csv(ANNOTATIONS_FILE, index=False)

# ============================================================================
# UI Components
# ============================================================================
def show_introduction():
    """Display introduction page."""
    st.title("🎤 Speech Expertise Annotation Tool")
    
    if TEST_MODE:
        st.warning(f"🧪 **TEST MODE ACTIVE** - Only {TEST_SPEECHES_COUNT} speeches loaded")
    
    st.markdown("---")
    
    st.markdown("""
    ## Welcome,
    
    You are assisting a research study on **deliberative communication**. Your task is to assess how much 
    a given speech act demonstrates **domain expertise** on the topic under discussion.
    
    ### What is "Expertise"?
    
    "Expertise" here refers to the expression of **specialized knowledge**, **technical accuracy**, 
    and the ability to **reason with evidence or well-informed arguments**, as shown through language use.
    
    ### Your Task
    
    You will evaluate speaker statements in the context of ongoing deliberations. Please refer to the 
    **previous context** to assess how the current speech act signifies expertise in the current discussion topics.
    
    ⚠️ *Note: The input may include minor transcription errors (from speech-to-text).*
    
    ### Linguistic Indicators of Expertise
    
    When deciding, rely on well-established linguistic indicators such as:
    
    - **Domain-specific or technical vocabulary** (precision, correct terminology)
    
    - **Structured reasoning and inferential coherence**, including:
      - *Cause–effect:* because, since, therefore, thus, hence
      - *Entailment or consequence:* it follows that, as a consequence, this implies that
      - *Conditional inference:* if … then …, given that … we can conclude …
      - *Syllogistic reasoning:* all X are Y; this is X; therefore …
    
    - **Evidence or citation markers** (according to, studies show, data suggest)
    
    - **Epistemic calibration** (balanced use of hedges like "may", "might", "suggests", showing awareness of uncertainty)
    
    - **Syntactic and lexical complexity** (varied sentence structure, advanced word choice)
    
    - **Analytical focus over personal anecdote or emotion**
    
    - **Relevance to current topic** (staying on-topic with informed contributions)
    
    ### What to Avoid
    
    ❌ Do **NOT** judge based on:
    - Fluency or confidence tone
    - Opinion alignment
    - Personal agreement with the content
    
    ✅ Focus purely on **linguistic cues** that signal expertise or informed reasoning.
    
    ### Rating Scale (1–5 Likert)
    
    **1** — Strongly Disagree: clearly non-expert  
    *(uninformed, vague, anecdotal, incorrect, or purely emotional)*
    
    **2** — Disagree: likely non-expert  
    *(limited reasoning, lacks technical or evidential language)*
    
    **3** — Undecided: ambiguous or generic statement  
    *(no clear expert or non-expert cues)*
    
    **4** — Agree: likely expert  
    *(some specialized reasoning, accurate and structured)*
    
    **5** — Strongly Agree: clearly expert  
    *(precise terminology, well-reasoned, supported by evidence)*
    
    ### Justification
    
    For each rating, provide a **one-sentence justification** referencing specific linguistic or reasoning cues.
    
    ---
    """)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("✅ I Understand - Start Annotating", type="primary", use_container_width=True):
            st.session_state.show_intro = False
            st.rerun()

def display_context(context):
    """Display context speeches - always visible."""
    st.markdown("#### 📝 Previous Context")
    if context:
        context_text = "\n\n".join([f"{i+1}. {ctx}" for i, ctx in enumerate(context)])
        st.text_area(
            "Context speeches:",
            value=context_text,
            height=200,
            disabled=True,
            label_visibility="collapsed"
        )
    else:
        st.info("No previous context available")

def display_speech(speech, idx, total):
    """Display speech details."""
    st.markdown(f"### Speech {idx + 1} of {total}")
    st.markdown(f"**Topic:** {speech['topic']}")
    
    st.markdown("---")
    
    # Display context first (always visible)
    display_context(speech['context'])
    
    st.markdown("---")
    
    # Display the main speech with speaker
    st.markdown("#### 🎤 Statement to Annotate:")
    st.info(f"**{speech['speaker']}:** {speech['text']}")

# ============================================================================
# Main App
# ============================================================================
def main():
    st.set_page_config(page_title="Speech Expertise Annotation", page_icon="🎤", layout="wide")
    
    # Initialize session state
    if 'show_intro' not in st.session_state:
        st.session_state.show_intro = True
    if 'current_idx' not in st.session_state:
        st.session_state.current_idx = 0
    if 'rater_id' not in st.session_state:
        st.session_state.rater_id = ""
    
    # Show introduction page first
    if st.session_state.show_intro:
        show_introduction()
        return
    
    # Main annotation interface
    st.title("🎤 Speech Expertise Annotation Tool")
    
    if TEST_MODE:
        st.warning(f"🧪 **TEST MODE ACTIVE** - Only {TEST_SPEECHES_COUNT} speeches loaded")
    
    st.markdown("---")
    
    # Sidebar for rater ID and guidelines
    with st.sidebar:
        st.header("👤 Rater Information")
        
        # Use session state to persist rater_id
        rater_id_input = st.text_input(
            "Enter your Rater ID:", 
            value=st.session_state.rater_id,
            key="rater_id_input"
        )
        
        # Update session state when input changes
        if rater_id_input != st.session_state.rater_id:
            st.session_state.rater_id = rater_id_input
            st.rerun()
        
        rater_id = st.session_state.rater_id
        
        if not rater_id:
            st.warning("⚠️ Please enter your Rater ID to begin")
            st.stop()
        
        st.success(f"✓ Logged in as: **{rater_id}**")
        
        if TEST_MODE:
            st.warning(f"⚠️ TEST MODE: Only loading {TEST_SPEECHES_COUNT} speeches")
        
        st.markdown("---")
        st.markdown("### 📊 Expertise Rating Scale")
        st.markdown("""
        **1** — No expertise  
        *(vague, anecdotal, emotional)*
        
        **2** — Minimal expertise  
        *(limited reasoning, lacks technical language)*
        
        **3** — Moderate expertise  
        *(ambiguous, no clear expert cues)*
        
        **4** — Strong expertise  
        *(specialized reasoning, accurate)*
        
        **5** — Very strong expertise  
        *(precise terminology, well-reasoned)*
        """)
        
        st.markdown("---")
        st.markdown("### 🔍 What to Look For")
        st.markdown("""
        **Indicators of expertise:**
        - Domain-specific vocabulary
        - Structured reasoning:
          - Cause-effect (because, thus)
          - Conditional (if...then)
          - Evidence markers (studies show)
        - Epistemic hedges (may, might, suggests)
        - Syntactic complexity
        - Analytical vs. emotional focus
        - Topic relevance
        
        **Avoid judging:**
        - Fluency or confidence tone
        - Opinion alignment
        - Personal agreement
        """)
        
        if st.button("📖 Show Instructions Again"):
            st.session_state.show_intro = True
            st.rerun()
    
    # Load speeches (respects TEST_MODE)
    speeches = load_speeches()
    total_speeches = len(speeches)
    
    # Get existing annotations for this rater
    annotations = get_annotations_for_rater(rater_id)
    
    # Get list of speech IDs we're actually working with
    speech_ids_to_annotate = [s['speech_id'] for s in speeches]
    
    # Count how many of THESE speeches have been annotated
    completed = sum(1 for sid in speech_ids_to_annotate if sid in annotations)
    
    st.markdown(f"### Progress: {completed}/{total_speeches} speeches annotated")
    st.progress(completed / total_speeches if total_speeches > 0 else 0)
    
    # Check if all completed
    if completed >= total_speeches:
        st.success("🎉 You have completed all annotations!")
        st.balloons()
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("✅ Finish and Close", type="primary", use_container_width=True):
                st.success(f"✅ All annotations saved to {ANNOTATIONS_FILE}")
                st.info("You can now close this browser tab.")
                # Close the app by stopping execution
                st.stop()
        st.stop()
    
    # Get current speech
    current_idx = st.session_state.current_idx
    
    # Ensure index is valid
    if current_idx < 0:
        current_idx = 0
        st.session_state.current_idx = 0
    elif current_idx >= total_speeches:
        current_idx = total_speeches - 1
        st.session_state.current_idx = current_idx
    
    current_speech = speeches[current_idx]
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Previous", disabled=(current_idx == 0), use_container_width=True):
            st.session_state.current_idx -= 1
            st.rerun()
    
    with col3:
        if st.button("Next ➡️", disabled=(current_idx >= total_speeches - 1), use_container_width=True):
            st.session_state.current_idx += 1
            st.rerun()
    
    st.markdown("---")
    
    # Display speech
    display_speech(current_speech, current_idx, total_speeches)
    
    st.markdown("---")
    
    # Annotation form
    st.markdown("### ✍️ Your Annotation")
    
    # FETCH existing annotation from CSV for this specific speech_id + rater_id
    existing = get_annotation(current_speech['speech_id'], rater_id)
    
    # Use existing values if present, otherwise use neutral defaults
    default_score = existing['score'] if existing else 3
    default_justification = existing['justification'] if existing else ''
    
    # Create a stable hash for the form key (avoid special characters)
    speech_hash = hashlib.md5(
        f"{current_speech['speech_id']}_{rater_id}_{current_idx}".encode()
    ).hexdigest()[:8]
    
    form_key = f"annotation_form_{speech_hash}"
    
    with st.form(key=form_key):
        col1, col2 = st.columns([1, 3])
        
        with col1:
            score = st.slider(
                "Expertise Score", 
                1, 5, 
                default_score, 
                help="Rate the expertise level (1=lowest, 5=highest)"
            )
        
        with col2:
            justification = st.text_area(
                "Justification", 
                value=default_justification,
                height=150,
                placeholder="Explain your rating. What linguistic evidence of expertise (or lack thereof) do you see?",
                help="Provide reasoning for your score based on the indicators in the sidebar"
            )
        
        submitted = st.form_submit_button("✅ Submit Annotation", use_container_width=True)
        
        if submitted:
            if not justification.strip():
                st.error("❌ Please provide a justification for your score")
            else:
                # Save/update annotation (will OVERWRITE if exists)
                context_str = " | ".join(current_speech['context']) if current_speech['context'] else ""
                
                update_annotation(
                    current_speech['speech_id'],
                    rater_id,
                    score,
                    justification.strip(),
                    context_str,
                    current_speech['text']
                )
                
                st.success("✅ Annotation saved!")
                
                # Auto-advance to next speech if not at the end
                if current_idx < total_speeches - 1:
                    st.session_state.current_idx += 1
                
                # Always rerun to update progress and check if complete
                st.rerun()

if __name__ == "__main__":
    main()