import joblib
import os
import sys
sys.path.append('.')

# todo make it parametric I am too tired now
from loguru import logger
from tqdm import tqdm
import os
amass_path = '/is/cluster/work/nathanasiou/data/motion-language/amass/processed_amass_smplh_male_30fps/amass.pth.tar'
amass_data = joblib.load(amass_path)    
logger.info(f'Loading the dataset from {amass_path}')
babel_path = '/is/cluster/work/nathanasiou/data/motion-language/babel/babel_v2.1/id2fname/amass-path2babel.json'
from teach.utils.file_io import read_json
amass2babel = read_json(babel_path)
dataset_db_lists = {'train': [],
                    'val': [],
                    'test': []}
num_bad = 0
for sample in tqdm(amass_data):
    if sample['fname'] not in amass2babel:
        num_bad += 1
        continue

    split_of_seq = amass2babel[sample['fname']]['split']
    babel_key = amass2babel[sample['fname']]['babel_id']
    # construct babel key fro  amass keys and utils
    sample_babel = {}
    for k, v in sample.items():
        sample_babel[k] = v
    sample_babel['babel_id'] = babel_key
    dataset_db_lists[split_of_seq].append(sample_babel)

print(f'Percentage not found: {num_bad}/{len(amass_data)}')
out_path = '/is/cluster/work/nathanasiou/data/motion-language/babel/babel-smplh-30fps-male'
os.makedirs(out_path, exist_ok=True)
for k, v in dataset_db_lists.items():
    joblib.dump(v, f'{out_path}/{k}.pth.tar')
for k, v in dataset_db_lists.items():
    joblib.dump(v[:10], f'{out_path}/{k}_tiny.pth.tar')
