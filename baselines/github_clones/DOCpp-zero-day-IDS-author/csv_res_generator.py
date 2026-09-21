import ast

f = open("main_openmax_noNormal.log", "r")
content = f.read()

content_list = content.splitlines()
f.close()

expriments = []
midlines = []


def extract_data(expriment_lines):
    data = {}
    data['wrong_classified'] = {}
    for i, line in enumerate(expriment_lines):
        if 'Validate' in line:
            valid_split = line.split('[')
            
            labels = valid_split[1][:-1].split(',')
            labels = [label.strip()[1:-1] for label in labels]
            data['labels'] = labels
        if 'Accuracy' in line:
            total_acc = float(line.split()[-1][:-1])
            accs = ast.literal_eval(expriment_lines[i+1])
            data['accs'] = accs
            data['total_acc'] = total_acc
        if 'Truth: 4' in line:
            openmax_pred = line.split()[3]
            if openmax_pred in data['wrong_classified'].keys():
                data['wrong_classified'][openmax_pred] += 1
            else:
                data['wrong_classified'][openmax_pred] = 1
    # print(data)
    return data

def parse_data(data):
    res = {
        'Label1': None,
        'N1': None,
        'Acc1': None,
        'Label2': None,
        'Acc2': None,
        'N2': None,
        'Label3': None,
        'N3': None,
        'Acc3': None, 
        'Label4': None,
        'N4': None,
        'Acc4': None,
        'Label5': None,
        'N5': None,
        'Acc5': None,
        'Total Acc': None
    }
    for i in range(5):
        res['Label'+ str(i+1)] = data['labels'][i]
        if str(i) in data['wrong_classified'].keys():
            res['N'+ str(i+1)] = data['wrong_classified'][str(i)]
        else:
            res['N'+ str(i+1)] = 0
        res['Acc'+ str(i+1)] = data['accs'][i][-1]
    
    res['Total Acc'] = data['total_acc']
    
    return res


for line in content_list:
    if midlines and 'Validate' in line:
        expriments.append(midlines)
        midlines = []
    midlines.append(line)

datas = []
for expriment in expriments:
    data = extract_data(expriment)
    datas.append(data)

print(len(datas))

results = []
for data in datas:
    res = parse_data(data)
    results.append(res)

print(results)

# print(expriments[0])
# print(expriments[1])

import csv
def generate_csv(results):
    csv_columns = results[0].keys()
    csv_file = "out.csv"
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in results:
                writer.writerow(data)
    except IOError:
        print("I/O error")

generate_csv(results)