import json

with open('Temp/TF_IDF+SVM_Training (2).ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        
        # Add class_weight to LinearSVC
        if 'LinearSVC(max_iter=3000, random_state=SEED)' in source:
            new_source = source.replace(
                'LinearSVC(max_iter=3000, random_state=SEED)',
                'LinearSVC(max_iter=3000, random_state=SEED, class_weight="balanced")'
            )
            # Change scoring metric to f1_macro
            new_source = new_source.replace(
                'scoring="accuracy"',
                'scoring="f1_macro"'
            )
            
            lines = []
            for line in new_source.split('\n'):
                lines.append(line + '\n')
            if lines:
                lines[-1] = lines[-1].rstrip('\n')
                
            cell['source'] = lines

with open('Temp/TF_IDF+SVM_Training (2).ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)
print("TF-IDF SVM Notebook optimized!")
