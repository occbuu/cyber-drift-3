import subprocess
subprocess.run(["ls", "-l"])

for t in [0.85  0.87  0.90  0.92  0.95]
    subprocess.run(['python3', 'main.py', '--arch', 'CNN',\
                 '--valid', 'OpenMax', '--loss', 'softmax', '--openmax_treshold', t])
    subprocess.run(['cp' 'main.log', './results/openmax/'+t+'/'])

subprocess.run(['python3', 'main.py', '--arch', 'CNN',\
                 '--valid', 'DOC', '--loss', '1-vs-rest'])
subprocess.run(['cp' 'main.log', './results/doc/'])