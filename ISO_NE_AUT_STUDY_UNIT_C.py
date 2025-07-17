import pandas as pd
import numpy as np
import os
import pyPowerGEM.pyTARA as pt 
from string import Template 
import pyPowerGEM.wrapper as tw
import ISO_NE_AUT_Folder_File_Creation_Auxiliary_File
from ISO_NE_AUT_Folder_File_Creation_Auxiliary_File import Create_Folders
import ISO_NE_AUT_ALL_PATHs
from ISO_NE_AUT_ALL_PATHs import Files as f
import ISO_NE_AUT_STEP_5_STUDY_UNIT
from ISO_NE_AUT_STEP_5_STUDY_UNIT import Post_Project_Loading as ppl


FINAL_CASE_FOLDER=self.create_single_folder(Study_Unit_Dispatch.FINAL_SECURED_WITH_STUDY_UNIT_DISPATCH_FILES,'Final_Raw_Cases')

class Final_Results(f):
    FLOW_GATE_DFAX_REPORTS_SUB_PARENT_PATH=self.json_dumps_function('POST_PROJECT_PARENT_FOLDER_PATH')'\FLOW_GATE_DFAX_REPORTS'
    FINAL_SECURED_WITH_STUDY_UNIT_DISPATCH_FILES=self.json_dumps_function('POST_PROJECT_PARENT_FOLDER_PATH')'\FINAL_CASES'
    #Import all relevant json dumps files 
    FINAL_CASES_SUB_PARENT_PATH=self.json_dumps_function('POST_PROJECT_PARENT_FOLDER_PATH')'\FINAL_CASES\Final_Raw_Cases'
    FINAL_CASES_DCCONT_REPORTS_PATH=self.json_dumps_function('POST_PROJECT_PARENT_FOLDER_PATH')'\FINAL_CASES_DCCONT_REPORTS_VFINAL'

    DCCONT_SCRIPT_TEMPLATE_FILE_PATH=f"{self.json_dumps_function('Pre_Project_Parent_Folder_Path')}{self.json_dumps_function('STEP_1_Script_Template_Name(.txt)')}"


    FINAL_CASES_SCRIPTS_PATH=f"{self.json_dumps_function('POST_PROJECT_PARENT_FOLDER_PATH')}\FINAL_CASES_DCCONT_SCRIPTS_VFINAL"

    AUX_PATH=self.json_dumps_function('auxiliary_files_folder_path')
    exe_path=self.json_dumps_function("tara_executable")
    MON_FILE=self.json_dumps_function("Mon_File_Name")
    CON_FILE=self.json_dumps_function("Con_File_Name")
    STUDY_UNIT_BUS=self.json_dumps_function("Study_Unit_Bus_Number")
    REF_SUBSYSTEM=self.json_dumps_function("Study_Unit_Load_Zone_Name")
    #Define both the existing relevant flowgates file (pre-project) and the new .csv file to show pre-project and post-project resultss
    Relevant_Flowgates=ppl.RELEVANT_FLOWGATES_FILE
    FINAL_FLOWGATE_CSV='FINAL_RESULTS_FINAL.csv'
    #Define functions to wrtite the DCCONT scripts, generate the DCCONT reports, so we can appropriately loop through those mon/con pairs, and then generate the post-project loading corresponding to that
    def run_script(self,script_file):
        tara=tw.powerGemExe(exeFilePath=self.__class__.exe_path)
        tara.runScript(scriptFilePath=script_file)
    def create_DCCONT_Reports(self):
        directory=self.__class__.FINAL_CASES_SUB_PARENT_PATH
        for filename in os.listdir(directory):
            dccont_name=filename.split('.')[0]
            script_name=filename.split('.')[0]
            flow_gate_list=filename.split('_')
            flow_gate_name=f"branch from bus {flow_gate_list[1]} to bus {flow_gate_list[2]} ckt {flow_gate_list[3]} in contingency number {flow_gate_list[4]}"
            template_fh=self.__class__.DCCONT_SCRIPT_TEMPLATE_FILE_PATH
            template_fh = open(template_fh, "r")
            script_string=template_fh.read()
            script_template=Template(script_string) 
            config_dict={"Input_File_Full_Path":f"{directory}\{filename}",
            "Con_File_Full_Path":f"{self.__class__.AUX_PATH}\{self.__class__.CON_FILE}",
            "Subsystem_File_Full_Path":f"{self.__class__.AUX_PATH}\{self.__class__.SUB_FILE}",
            "Mon_File_Full_Path":f"{self.__class__.AUX_PATH}\{self.__class__.MON_FILE}",
            "Sending_Subsystem": f"{self.__class__.STUDY_UNIT_BUS}",#Write the exact name of the Sending Bus 
            "Ref_Subsystem":f"{self.__class__.REF_SUBSYSTEM}",#Write the exact name of the reference subsystem 
            "DCCONT_OUTPUT_FILE_FULL_PATH":f"{self.__class__.FINAL_CASES_DCCONT_REPORTS_PATH}\{dccont_name}.csv"}
            new_script=script_template.substitute(config_dict) 
            NewFile=os.path.join(f"{self.__class__.FINAL_CASES_SCRIPTS_PATH}",f"{script_name}.txt")
            output_fh = open(NewFile, "w")
            output_fh.write(new_script)
            self.run_script(NewFile)

     #Helper Function 3
    def group_flow_gates(self,csv_file_name):
        csv_file_pandas_now=pd.read_csv(self.__class__.RELEVANT_FLOWGATES_FILE)
        csv_file_pandas_now=pd.DataFrame(csv_file_pandas_now)
        Flow_Gate_Lists = []
        grouped = csv_file_pandas.groupby(['Stress_ID'])
        for name, group in grouped:
            sublist = [f" {row['Fr Bus']}_{row['To Bus']}_{row['CKT']}_"]
            Flow_Gate_Lists.append(sublist)
        return Flow_Gate_Lists

    def create_dataframe_limiting(self,Limiting_Flowgate_dataframe):
        self.create_DCCONT_Reports()#create the DCCONT reports for each of the final stressed cases and send each dccont report to a respective flowgfate folder 
        Pre_Project_File=self.__class.__Relevant_Flowgates
        directory=self.__class__.FINAL_CASES_DCCONT_REPORTS_PATH

        for filename in os.listdir(directory):
            flowgate_list=filename.split('__')[2]
            file=os.path.join(directory,filename)
            DCCONT=pd.read_csv(file,skiprows=9)#ignore statement for first N rows)
            if "Dfax Harmer Positive (based on flow direction) Bus 113987" in DCCONT.columns:
                DCCONT=DCCONT.rename(columns={'Dfax Harmer Positive (based on flow direction) Bus 113987':'Real DFAX'})
                DCCONT=DCCONT.drop(columns=['Unnamed: 20'])
                DCCONT=DCCONT[DCCONT['Real DFAX']>=.03]
                DCCONT=DCCONT[DCCONT['Fr Bus']==flowgate_list[0]]
                DCCONT=DCCONT[DCCONT['To Bus']==flowgate_list[1]]
                DCCONT=DCCONT[DCCONT['CKT']==flowgate_list[3]]
                DCCONT=DCCONT[DCCONT['Cont ID']==flow_gate_list[4]]
                DCCONT=DCCONT[DCCONT['Final DC %Loading']>=95]
                limiting_columns=Limiting_Flowgate_dataframe.columns
                for index, row in DCCONT.iterrows():
                    new_index=len(Limiting_Flowgate_dataframe)
                    new_row = {limiting_columns[0]: filename.split('.')[0], limiting_columns[1]:row[' Monitored Facility                                   '],
                    limiting_columns[2]:row['Fr Bus'],limiting_columns[3]: row['To Bus'], limiting_columns[4]:row['CKT'],limiting_columns[5]:row[' Cont Name                                                      '],
                    limiting_columns[6]: row['Cont ID'],limiting_columns[7]: row['Final DC %Loading'],limiting_columns[8]:row['Real DFAX']}
                    new_row=pd.DataFrame([new_row])
                    Limiting_Flowgate_dataframe=pd.concat([Limiting_Flowgate_dataframe,new_row], ignore_index=True)
            else:
                continue
        Limiting_Flowgate_dataframe.to_csv(self.__class__.FINAL_FLOWGATE_CSV,index=False)
if __name__=="__main__":
    Limiting_FlowGate_List=pd.DataFrame()
    Limiting_FlowGate_List["Monitored Facility"]=None
    Limiting_FlowGate_List["Fr Bus"]=None
    Limiting_FlowGate_List["To Bus"]=None
    Limiting_FlowGate_List["CKT"]=None
    Limiting_FlowGate_List["Contingency_Name"]=None
    Limiting_FlowGate_List["Contingency_Number"]=None
    Limiting_FlowGate_List["DC Loading"]=None
    Limiting_FlowGate_List["Study_Unit_DFAX"]=None
    Limiting_FlowGate_List.insert(0,'Stress_ID',None)
    fr=Final_Results()
    fr.create_dataframe_limiting(Limiting_FlowGate_List)
