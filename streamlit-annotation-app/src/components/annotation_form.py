from streamlit import st
import pandas as pd

def annotation_form(speech_id, context, statement):
    with st.form(key='annotation_form'):
        rater_id = st.text_input("Rater ID")
        score = st.slider("Score", min_value=1, max_value=5)
        justification = st.text_area("Justification")
        
        submit_button = st.form_submit_button("Submit Annotation")
        
        if submit_button:
            if rater_id and justification:
                # Load existing annotations
                try:
                    annotations = pd.read_csv('data/annotations.csv')
                except FileNotFoundError:
                    annotations = pd.DataFrame(columns=['item_id', 'rater_id', 'score', 'justification', 'context', 'statement'])
                
                # Create a new annotation entry
                new_annotation = {
                    'item_id': speech_id,
                    'rater_id': rater_id,
                    'score': score,
                    'justification': justification,
                    'context': context,
                    'statement': statement
                }
                
                # Append the new annotation to the DataFrame
                annotations = annotations.append(new_annotation, ignore_index=True)
                
                # Save the updated annotations to CSV
                annotations.to_csv('data/annotations.csv', index=False)
                
                st.success("Annotation submitted successfully!")
            else:
                st.error("Please fill in all required fields.")