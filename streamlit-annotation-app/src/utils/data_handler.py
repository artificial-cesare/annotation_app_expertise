def load_speeches(file_path):
    import json
    with open(file_path, 'r') as file:
        speeches = json.load(file)
    return speeches

def save_annotations(file_path, annotations):
    import pandas as pd
    df = pd.DataFrame(annotations)
    df.to_csv(file_path, index=False)

def create_annotation(item_id, rater_id, score, justification, context, statement):
    return {
        'item_id': item_id,
        'rater_id': rater_id,
        'score': score,
        'justification': justification,
        'context': context,
        'statement': statement
    }