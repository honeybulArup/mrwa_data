import numpy as np 
from openpyxl import load_workbook 
import string 
import pandas as pd
import math 
import sys 
import json
import os

def normalize(vals):
    values = []
    for val in vals:
        if val != 'None':
            values.append(float(val))
        else:
            values.append(float('nan'))
    normalized = []
    for value in values:
        vv = float(value-min(values)) / (max(values) - min(values))
        normalized.append(vv)
    return normalized

def get_link_ids(sheet_name="Link IDs"):
    routeIds = pd.read_excel("data/xlsx/data.xlsx", sheetname=sheet_name)
    routeIds.to_csv('data/csv/route_ids.csv', index=False)
    return routeIds 

def load_wb(wb_name="data/xlsx/data.xlsx"):
        wb = load_workbook(filename=wb_name, data_only=True)
        sheet_names = wb.get_sheet_names()
        # print sheet_names
        del sheet_names[0]
        return wb

def parse_xlsx(
    workbook,
    sheet_name,
    write_to,
    search_for=False,
    search_term="",
    get_range=False,
    range_cols=[],
    range_rows = [],
    alpha=list(string.ascii_uppercase),
):

    if get_range and len(range_cols)!=0 and len(range_rows)!=0:
        
        row_indices = []
        i=range_rows[0]
        sheet_df = workbook[sheet_name]
        while not math.isnan(i):
            ref_idx = range_cols[0] + str(i)
            if(sheet_df[ref_idx].value is not None):
                row_indices.append(i)
                i+=1
            else:
                i = float('nan')
        
    cols = alpha[alpha.index(range_cols[0]):(alpha.index(range_cols[1])+1)]
    rows = map(str, row_indices)
    columns = []
    colnames = []
    for col in cols:
        column = []
        for row in rows:
            column.append(sheet_df[col+row].value)
        colnames.append(column[0])
        del column[0]
        columns.append(column)
    columns.append(colnames)
    
    with open('data/json/' + write_to + '.json', 'w') as f:
        json.dump(columns, f, indent=2)

    del columns[-1]

    datadict = {}
    for i, colname in enumerate(colnames):
        datadict[colname] = map(str, columns[i])

    df = pd.DataFrame(datadict)
    
    df.to_csv("data/csv/" + write_to + ".csv", index=False)

def get_master_data(
    rel_cols=['M_Link_ID', 'Row Labels'],
    data_dir='data/csv/',
    output_fn_json='data/master_files/master.json',
    output_fn_csv="data/master_files/master.csv",
    data_fn="data/master_files/data.csv"
):

    all_files = os.listdir(data_dir)

    data_dict = {}

    for fl in all_files:
        df = pd.read_csv(data_dir+fl)
        colnames = list(df)
        for rcol in rel_cols:
            if rcol in colnames:
                link_ids = df[rcol]
                del colnames[colnames.index(rcol)]
        idArr = []
        for link_id in link_ids:
            idArr.append(str(link_id))
        data_dict['ids'] = idArr
        for col in colnames:
            dataArr = []
            for val in df[col]:
                dataArr.append(val)
            data_dict[col] = dataArr
        
    master_df = pd.DataFrame(data_dict)

    df_names=list(master_df)
    df_names_master = ['ids']

    del df_names[df_names.index('ids')]
    
    for name in sorted(df_names):
        df_names_master.append(name)

    master_df = master_df[df_names_master]

    fr = master_df['From_Int']
    to = master_df['To_Int']

    fr_to = []
    for i, f, t in zip(master_df['ids'], fr, to):
        fr_to.append(i + ' - ' + f + ' - ' + t)
    
    """

    Normalize the following;

    - JTReliability 
    - SpeedPerc1 
    - SpeedPerc2 
    - NPI Efficiency

    """

    jtrel_normalized = normalize(master_df["JTReliability"])
    speed_perc_am_normal = normalize(master_df["SpeedPerc1"])
    speed_perc_pm_normal = normalize(master_df['SpeedPerc2'])
    npi_eff_normal = normalize(master_df['Average of PercLength'])

    master_df["Route"] = pd.Series(np.array(fr_to), index=master_df.index)
    master_df["JT_Normal"] = pd.Series(np.array(jtrel_normalized), index=master_df.index)
    master_df["Speed_am_Normal"] = pd.Series(np.array(speed_perc_am_normal), index=master_df.index)
    master_df["Speed_pm_Normal"] = pd.Series(np.array(speed_perc_pm_normal), index=master_df.index)
    master_df["NPI_Normal"] = pd.Series(np.array(npi_eff_normal), index=master_df.index)

    section_value = [] 
    for jt, s_am, s_pm, npi in zip(jtrel_normalized, speed_perc_am_normal, speed_perc_pm_normal, npi_eff_normal):
        section_value.append(jt + s_am + s_pm + npi)

    master_df["Section Value"] = pd.Series(np.array(section_value), index=master_df.index)

    master_df.to_csv(output_fn_csv, index=False)  

    info_master = master_df[['Route', 'Route_Name', 'JT_Normal', "Speed_am_Normal", "Speed_pm_Normal", "NPI_Normal", "Section Value"]]

    info_master.to_csv(data_fn, index=False)    

def process_data():

    get_link_ids()
    workbook = load_wb()
    parse_xlsx(workbook, "Travel Speed-Time", "travel_speed_time", get_range=True, range_cols=["H", "J"], range_rows=[9, float('nan')])
    parse_xlsx(workbook, "JT Reliability", "jt_reliability_am", get_range=True, range_cols=["L", "O"], range_rows=[9, float('nan')])
    parse_xlsx(workbook, "JT Reliability", "jt_reliability_pm", get_range=True, range_cols=["Q", "T"], range_rows=[9, float('nan')])
    parse_xlsx(workbook, "NPI Efficiency", "npi_efficiency", get_range=True, range_cols = ["G", "I"], range_rows=[9, float('nan')])
    df_colnames=get_master_data()


def main(
    get_data=False,
):
    if get_data:
        process_data()

if __name__ == '__main__':
    main(True)