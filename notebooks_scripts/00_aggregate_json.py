import pandas as pd
import json
import re
from pathlib import Path

# Set paths
raw_data_path = Path('../01_raw_data')
processed_data_path = Path('../02_processed_data')
processed_data_path.mkdir(exist_ok=True)

def extract_probability(option_a: str) -> str:
    """Extract probability from optionA (e.g., "85% Chance of $33")"""
    match = re.search(r'(\d+)%', option_a)
    return str(int(match.group(1)) / 100) if match else ''

def extract_certain_amount(option_b: str) -> str:
    """Extract certain amount from optionB (e.g., "100% Chance of $28")"""
    match = re.search(r'\$(\d+(?:\.\d+)?)', option_b)
    return match.group(1) if match else ''

def get_task_label(label: str) -> str:
    """Extract task label from the full label"""
    return label.split()[1].lower() if label else 'money'

# Process all JSON files
json_files = list(raw_data_path.glob('*.json'))
json_dfs = []

for json_file in json_files:
    try:
        print(f"\nProcessing {json_file}")
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Process task results
        task_data = []
        participant_id = data.get('participantId', '')
        
        # Process fixed choice questions
        if 'fixedChoiceQuestions' in data:
            for q in data['fixedChoiceQuestions']:
                task_data.append({
                    'participantId': participant_id,
                    'prolificId': '',  # Not in JSON data
                    'eventType': 'fixedChoice',
                    'questionId': q.get('id', ''),
                    'question': q.get('question', ''),
                    'optionA': q.get('optionA', ''),
                    'optionB': q.get('optionB', ''),
                    'choice': q.get('choice', ''),
                    'taskLabel': get_task_label(q.get('optionA', '')),
                    'probability': extract_probability(q.get('optionA', '')),
                    'certainAmount': extract_certain_amount(q.get('optionB', '')),
                    'trialIndex': 'NA',
                    'indifferencePoint': 'NA'
                })
        
        # Process discounting task trials
        if 'taskResults' in data:
            for task in data['taskResults']:
                label = task.get('label', '')
                max_value = task.get('maxValue', 0)
                unit = task.get('unit', '$')
                
                if 'probabilityData' in task:
                    for prob_data in task['probabilityData']:
                        probability = prob_data.get('probability', 0)
                        indifference_point = prob_data.get('indifferencePoint', '')
                        
                        if 'trials' in prob_data:
                            for idx, trial in enumerate(prob_data['trials']):
                                certain_amount = trial.get('certainAmount', 0)
                                choice = trial.get('choice', '')
                                
                                # Format the options
                                optionA = f"{int(probability * 100)}% Chance of {unit}{max_value}"
                                optionB = f"100% Chance of {unit}{certain_amount}"
                                
                                # Map choice to A/B format
                                mapped_choice = 'A' if choice == 'probabilistic' else 'B'
                                
                                task_data.append({
                                    'participantId': participant_id,
                                    'prolificId': '',  # Not in JSON data
                                    'eventType': 'discountingTrial',
                                    'questionId': '',
                                    'question': 'Which would you prefer?',
                                    'optionA': optionA,
                                    'optionB': optionB,
                                    'choice': mapped_choice,
                                    'taskLabel': get_task_label(label),
                                    'probability': probability,
                                    'certainAmount': certain_amount,
                                    'trialIndex': idx,
                                    'indifferencePoint': indifference_point if indifference_point is not None else ''
                                })
        
        if task_data:
            # Create DataFrame from the list of dictionaries
            df = pd.DataFrame(task_data)
            json_dfs.append(df)
            print(f"Successfully processed {json_file} - {len(task_data)} records")
            print(f"Fixed choice questions: {len([d for d in task_data if d['eventType'] == 'fixedChoice'])}")
            print(f"Discounting trials: {len([d for d in task_data if d['eventType'] == 'discountingTrial'])}")
        else:
            print(f"No task data found in {json_file}")
            
    except Exception as e:
        print(f"Error processing {json_file}: {str(e)}")
        import traceback
        print(traceback.format_exc())

# Combine all JSON data
if json_dfs:
    combined_json = pd.concat(json_dfs, ignore_index=True)
    
    # Save the combined data
    combined_json.to_csv(processed_data_path / 'combined_json_data.csv', index=False)
    
    # Print summary
    print(f"\nTotal JSON records: {len(combined_json)}")
    print(f"Unique participants in JSON: {combined_json['participantId'].nunique()}")
    print(f"Number of fixed-choice questions: {len(combined_json[combined_json['eventType'] == 'fixedChoice'])}")
    print(f"Number of discounting trials: {len(combined_json[combined_json['eventType'] == 'discountingTrial'])}")
    
    print("\nSample of JSON data (transformed to CSV format):")
    print(combined_json.head())
    
    print("\nColumns in JSON data:")
    print(combined_json.columns.tolist())
else:
    print("No JSON files were successfully processed.") 