# -*- coding: utf-8 -*-
"""
Created on Wed May 25 14:06:38 2022

@author: pjma024
"""

import pandas as pd
import json
import math

risks_df = pd.read_csv(r"risk_model_table.csv")

df_json = pd.DataFrame()
df_json.insert(0, 'variable1_type',risks_df['variable1'] )
df_json.insert(1, 'operator1',risks_df['operator1'])
df_json.insert(2, 'threshold1', risks_df['threshold1'])
df_json.insert(3, 'variable2_type', [i if not isinstance(i, float) else None for i in risks_df["variable2"] ])
df_json.insert(4, 'operator2', [i if not isinstance(i, float) else None for i in risks_df["operator2"] ] )
df_json.insert(5, 'threshold2',[str(i) if not math.isnan(i) else None for i in risks_df['threshold2'] ])
df_json.insert(6, 'technology',risks_df["tech"])
df_json.insert(7, 'period',0)
df_json.insert(8, 'event',risks_df['risk'])
df_json.insert(9, 'derating',risks_df['derating'].astype(str))


data_json =  {"risk_model":df_json.to_dict(orient='records')}
# line_to_add = "risk_model = "
# with open('output/risk_model.py', 'w') as file:
#     file.write(line_to_add + "\n") 
with open('output/risk_model.json', 'w') as json_file:
    json.dump(data_json, json_file, indent=1)

# df_final.to_csv(r'output/aggregated_capacity.csv', index = False)
