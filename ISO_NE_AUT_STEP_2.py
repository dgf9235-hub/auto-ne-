import pandas as pd 
import numpy as np 
import os 
import asyncio
from string import Template
import ISO_NE_AUT_Folder_File_Creation_Auxiliary_File
from ISO_NE_AUT_Folder_File_Creation_Auxiliary_File import Create_Folders
import ISO_NE_AUT_STEP_1
from ISO_NE_AUT_STEP_1 import Template_And_Write_DC_CONT_File as twca
from io import StringIO
import pyPowerGEM.wrapper as tw
#All Imports necessary for this python file
import ISO_NE_AUT_ALL_PATHs
from ISO_NE_AUT_ALL_PATHs import Files as f
#Import of the Python Files that will write the paths specified in the ISO_NE_AUT_PATHs .jsonc file

class Create_Flow_Gate_Tuple(Create_Folders,f):
    STEP_1_Instance=twca()
    STEP_1_Instance.template_DCCONT_script()
    BASE_CASE=os.path.join(twca.exe_path,STEP_1_Instance.Input_File_Path)
    exe_path=f.json_dumps_function(f,'tara_executable')
    FLOW_GATE_PARENT_PATH=STEP_1_Instance.STEP_1_PARENT_FOLDER_PATH
    DCCONT_OUTPUT_REPORT_PATH=os.path.join(STEP_1_Instance.STEP_1_PARENT_FOLDER_PATH,STEP_1_Instance.dccont_file_name)
    DFAX_CUTOFF=f.json_dumps_function(f,"DFAX_CUTOFF_STRESS_CASE") #Can be adjusted in the change_df_cutoff method below
    DFAX_CUTOFF_FLOW_REVERSAL=f.json_dumps_function(f,"DFAX_CUTOFF_FLOW_REVERSAL")
    LOADING_CUTOFF=f.json_dumps_function(f,"MINIMUM_LOADING_STRESS_CASE") #can be adjusted in the change loading cutoff method 
    LOADING_CUTOFF_FLOW_REVERSAL=f.json_dumps_function(f,"MAXIMUM_LOADING_FLOW_REVERSAL")
    #This is where we will instantiate the class from step 1, isntead of running step 1 in isolation we can run it when this file is run
    #This is where we will create the new script, write the new script, and then return the path of the DCCONT Output report which we will need to create the flowgate scripts and generate dfax reports
    FLOW_GATE_SCRIPT_SUB_PARENT_FOLDER_PATH=''
    FLOW_GATE_SCRIPT_REVERSAL_SUB_PARENT_FOLDER=''
    FlOW_GATE_DFAX_REPORT_SUB_PARENT_FOLDER_PATH=''
    FLOW_GATE_DFAX_REPORT_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL=''
    FLOW_GATE_MONITORED_ELEMENT_STRESSED_CASES_SUB_PARENT_FOLDER_PATH=''
    FLOW_GATE_MONITORED_ELEMENT_STRESSED_CASES_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL=''
    FLOW_GATE_MONITORED_ELEMENT_SECURED_CASES_SUB_PARENT_FOLDER_PATH=''
    FLOW_GATE_MONITORED_ELEMENT_SECURED_CASES_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL=''
    FLOW_GATE_SCRD_SCRIPTS_SUB_PARENT_FOLDER_PATH=''
    FLOW_GATE_SCRD_SCRIPTS_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL=''
    FLOW_GATE_DFAX_REPORT_SCRIPTS_SUB_PARENT_FOLDER=''
    ISO_NE_AUT_STEP_2_Template=f.json_dumps_function(f,'STEP_2_Script_Template_Name(.txt)')
    def __init__(self):
        pass
    @classmethod
    def change_dfax_cutoff(cls,new_dfax_cutoff):
        cls.DFAX_CUTOFF=new_dfax_cutoff
    @classmethod
    def change_loading_cutoff(cls,new_loading_cutoff):
        cls.LOADING_CUTOFF=new_loading_cutoff
    @classmethod
    def overwrite_scripts_folder(cls,dfax_folder,dfax_reversal_folder,scripts_folder,scripts_reversal_folder,stressed_cases_folder,stressed_cases_folder_reversal,secured_cases_folder,secured_cases_folder_reversal,scrd_scripts_folder,scrd_scripts_folder_reversal):
        #No Reversal Folders
        cls.FlOW_GATE_DFAX_REPORT_SUB_PARENT_FOLDER_PATH=f"{os.path.join(cls.FLOW_GATE_PARENT_PATH,dfax_folder)}"
        os.makedirs(cls.FlOW_GATE_DFAX_REPORT_SUB_PARENT_FOLDER_PATH,exist_ok=True)

        cls.FLOW_GATE_SCRIPT_SUB_PARENT_FOLDER_PATH=f"{os.path.join(cls.FLOW_GATE_PARENT_PATH,scripts_folder)}"
        os.makedirs(cls.FLOW_GATE_SCRIPT_SUB_PARENT_FOLDER_PATH,exist_ok=True)

        cls.FLOW_GATE_MONITORED_ELEMENT_STRESSED_CASES_SUB_PARENT_FOLDER_PATH=f"{os.path.join(cls.FLOW_GATE_PARENT_PATH,stressed_cases_folder)}"
        os.makedirs(cls.FLOW_GATE_MONITORED_ELEMENT_STRESSED_CASES_SUB_PARENT_FOLDER_PATH,exist_ok=True)

        cls.FLOW_GATE_MONITORED_ELEMENT_SECURED_CASES_SUB_PARENT_FOLDER_PATH=f"{os.path.join(cls.FLOW_GATE_PARENT_PATH,secured_cases_folder)}"
        os.makedirs(cls.FLOW_GATE_MONITORED_ELEMENT_SECURED_CASES_SUB_PARENT_FOLDER_PATH,exist_ok=True)

        cls.FLOW_GATE_SCRD_SCRIPTS_SUB_PARENT_FOLDER_PATH=f"{os.path.join(cls.FLOW_GATE_PARENT_PATH,scrd_scripts_folder)}"
        os.makedirs(cls.FLOW_GATE_SCRD_SCRIPTS_SUB_PARENT_FOLDER_PATH,exist_ok=True)

        #Reversal Folders
        cls.FLOW_GATE_SCRIPT_REVERSAL_SUB_PARENT_FOLDER =f"{os.path.join(cls.FLOW_GATE_PARENT_PATH,scripts_reversal_folder)}"
        os.makedirs(cls.FLOW_GATE_SCRIPT_REVERSAL_SUB_PARENT_FOLDER,exist_ok=True)

        cls.FLOW_GATE_DFAX_REPORT_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL=f"{os.path.join(cls.FLOW_GATE_PARENT_PATH,dfax_reversal_folder)}"
        os.makedirs(cls.FLOW_GATE_DFAX_REPORT_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL,exist_ok=True)

        cls.FLOW_GATE_MONITORED_ELEMENT_STRESSED_CASES_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL=f"{os.path.join(cls.FLOW_GATE_PARENT_PATH,stressed_cases_folder_reversal)}"
        os.makedirs(cls.FLOW_GATE_MONITORED_ELEMENT_STRESSED_CASES_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL,exist_ok=True)

        cls.FLOW_GATE_MONITORED_ELEMENT_SECURED_CASES_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL=f"{os.path.join(cls.FLOW_GATE_PARENT_PATH,secured_cases_folder_reversal)}"
        os.makedirs(cls.FLOW_GATE_MONITORED_ELEMENT_SECURED_CASES_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL,exist_ok=True)

        cls.FLOW_GATE_SCRD_SCRIPTS_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL=f"{os.path.join(cls.FLOW_GATE_PARENT_PATH,scrd_scripts_folder_reversal)}"
        os.makedirs(cls.FLOW_GATE_SCRD_SCRIPTS_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL,exist_ok=True)

    def split_flowgate_string(self,flow_gate):
        flow_gate_list=flow_gate.split('in')[0]
        flow_gate_list_2=flow_gate_list[1].split()
        new_file_name=f"{flow_gate_list.split()[3]}_{flow_gate_list.split()[6]}_ckt_{flow_gate_list.split()[8]}_0"
        return new_file_name
    def split_flowgate_string1(self,flow_gate):
        flow_gate_list=flow_gate.split()
        new_file_name=f"{flow_gate_list[3]}" f"_" f"{flow_gate_list[6]}" f"_" f"{flow_gate_list[7]}_{flow_gate_list[8]}" f"_" f"{flow_gate_list[12]}"
        return new_file_name
    def clean_DCCONT_File_create_Flow_Gate_Tuple(self):

        DCCONT=pd.read_csv(self.DCCONT_OUTPUT_REPORT_PATH,skiprows=9)#ignore statement for first N rows)
        print(DCCONT.columns)
        DCCONT=DCCONT.rename(columns={'Dfax Harmer Positive (based on flow direction) Bus 113987':'Real DFAX'})
        print(DCCONT.head(10))
        DCCONT=DCCONT.drop(columns=['Unnamed: 20'])
        DCCONT=DCCONT[DCCONT['Real DFAX']>=Create_Flow_Gate_Tuple.DFAX_CUTOFF]
        DCCONT=DCCONT[DCCONT['Final DC %Loading']>=Create_Flow_Gate_Tuple.LOADING_CUTOFF]
        print(DCCONT.columns)
        print(DCCONT.head(30))
        # Initialize an empty list to store the sublistss
        Flow_Gate_Lists = []
        grouped = DCCONT.groupby(['Fr Bus','To Bus','CKT'])
        for name, group in grouped:
            self.create_single_folder(Create_Flow_Gate_Tuple.FLOW_GATE_SCRIPT_SUB_PARENT_FOLDER_PATH,f"{name[0]}_"f"{name[1]}_"f"{name[2]}_Scripts")
            self.create_single_folder(Create_Flow_Gate_Tuple.FlOW_GATE_DFAX_REPORT_SUB_PARENT_FOLDER_PATH,f"{name[0]}_"f"{name[1]}_"f"{name[2]}_DFAX_Reports")
            self.create_single_folder(Create_Flow_Gate_Tuple.FLOW_GATE_MONITORED_ELEMENT_STRESSED_CASES_SUB_PARENT_FOLDER_PATH,f"{name[0]}_"f"{name[1]}_"f"{name[2]}_Stressed_Cases")
            self.create_single_folder(Create_Flow_Gate_Tuple.FLOW_GATE_MONITORED_ELEMENT_SECURED_CASES_SUB_PARENT_FOLDER_PATH,f"{name[0]}_"f"{name[1]}_"f"{name[2]}_Secured_Cases")
            self.create_single_folder(Create_Flow_Gate_Tuple.FLOW_GATE_SCRD_SCRIPTS_SUB_PARENT_FOLDER_PATH,f"{name[0]}_"f"{name[1]}_"f"{name[2]}_SCRD_Scripts")
            sublist = [f"branch from bus {row['Fr Bus']} to bus "f"{row['To Bus']} ckt "f"{row['CKT']} in contingency number "f"{row['Cont ID']}" if row['Cont ID']!=0 else 
            f"branch from bus {row['Fr Bus']} to bus "f"{row['To Bus']} ckt "f"{row['CKT']} in base case" for _, row in group.iterrows()]
            Flow_Gate_Lists.append(sublist) 
        return Flow_Gate_Lists
    def REVERSAL_clean_DCCONT_File_create_Flow_Gate_Tuple(self):
        DCCONT=pd.read_csv(self.DCCONT_OUTPUT_REPORT_PATH,skiprows=9)#ignore statement for first N rows)
        DCCONT=DCCONT.rename(columns={'Dfax Harmer Positive (based on flow direction) Bus ' f'{self.json_dumps_function("Study_Unit_Bus_Number")}':'Real DFAX'})
        DCCONT=DCCONT.drop(columns=['Unnamed: 20'])
        DCCONT=DCCONT[DCCONT['Real DFAX']<=Create_Flow_Gate_Tuple.DFAX_CUTOFF_FLOW_REVERSAL]
        DCCONT=DCCONT[DCCONT['Final DC %Loading']<=Create_Flow_Gate_Tuple.LOADING_CUTOFF_FLOW_REVERSAL]
        print(DCCONT.columns)
        # Initialize an empty list to store the sublistss
        Flow_Gate_Lists = []
        grouped = DCCONT.groupby(['Fr Bus','To Bus','CKT'])
        for name, group in grouped:
            self.create_single_folder(Create_Flow_Gate_Tuple.FLOW_GATE_SCRIPT_REVERSAL_SUB_PARENT_FOLDER,f"{name[0]}_"f"{name[1]}_"f"{name[2]}_Reversal_Scripts")
            self.create_single_folder(Create_Flow_Gate_Tuple.FLOW_GATE_DFAX_REPORT_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL,f"{name[0]}_"f"{name[1]}_"f"{name[2]}_Reversal_DFAX_Reports")
            self.create_single_folder(Create_Flow_Gate_Tuple.FLOW_GATE_MONITORED_ELEMENT_STRESSED_CASES_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL,f"{name[0]}_"f"{name[1]}_"f"{name[2]}_Reversal_Stressed_Cases")
            self.create_single_folder(Create_Flow_Gate_Tuple.FLOW_GATE_SCRD_SCRIPTS_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL,f"{name[0]}_"f"{name[1]}_"f"{name[2]}_SCRD_Scripts")
            self.create_single_folder(Create_Flow_Gate_Tuple.FLOW_GATE_MONITORED_ELEMENT_SECURED_CASES_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL,f"{name[0]}_"f"{name[1]}_"f"{name[2]}_Secured_Cases")
            sublist = [f"branch from bus {row['Fr Bus']} to bus "f"{row['To Bus']} ckt "f"{row['CKT']} in contingency number "f"{row['Cont ID']}" if row['Cont ID']!=0 else 
            f"branch from bus {row['Fr Bus']} to bus "f"{row['To Bus']} ckt "f"{row['CKT']} in base case" for _, row in group.iterrows()]
            Flow_Gate_Lists.append(sublist) 
        return Flow_Gate_Lists
    def make_flowgate_scripts(self,Flow_Gate_Lists_Of_Lists,scripts_sub_parent_folder_name,stressed_cases_sub_parent_folder_name,dfax_reports_sub_parent_folder_name,scrd_scripts_sub_parent_folder_name,secured_cases_sub_parent_folder_name,Sending_Subsystem,Reference_Subsystem):
        dfax_sub_parent_path=f"{self.__class__.FLOW_GATE_PARENT_PATH}\{dfax_reports_sub_parent_folder_name}"
        DFAX_Sub_Parent_Folders=[name for name in os.listdir(dfax_sub_parent_path) if os.path.isdir(os.path.join(dfax_sub_parent_path, name))]
        script_sub_parent_path=f"{self.__class__.FLOW_GATE_PARENT_PATH}\{scripts_sub_parent_folder_name}"
        SCRIPT_Sub_Parent_Folders=[name for name in os.listdir(script_sub_parent_path) if os.path.isdir(os.path.join(script_sub_parent_path, name))]
        for i in range(len(Flow_Gate_Lists_Of_Lists)):
            for j in range(len(Flow_Gate_Lists_Of_Lists[i])):
                if Flow_Gate_Lists_Of_Lists[i][j].split()[-1]=='case':
                    script_file_name=self.split_flowgate_string(Flow_Gate_Lists_Of_Lists[i][j])
                    pass
                else:
                    script_file_name=self.split_flowgate_string1(Flow_Gate_Lists_Of_Lists[i][j])
                    pass
                template_fh = os.path.join(self.FLOW_GATE_PARENT_PATH,self.__class__.ISO_NE_AUT_STEP_2_Template )#Write the DFAX_Report_Taemplate to this path
                template_fh = open(template_fh, "r")
                script_string = template_fh.read()
                script_template=Template(script_string)
                DFAX_PATH=os.path.join(f"{self.__class__.FLOW_GATE_PARENT_PATH}\{dfax_reports_sub_parent_folder_name}\{DFAX_Sub_Parent_Folders[i]}")
                config_dict={"Input_File_Full_Path":self.__class__.STEP_1_Instance.Input_File_Path,
                "Subsystem_File_Full_Path":f"{self.__class__.STEP_1_Instance.Sub_File_Path}",
                "Con_File_Full_Path":self.__class__.STEP_1_Instance.Con_File_Path,
                "Mon_File_Full_Path":self.__class__.STEP_1_Instance.Mon_File_Path,
                "Sending_Subsystem": Sending_Subsystem,
                "Ref_Subsystem": Reference_Subsystem,"flow_gate":Flow_Gate_Lists_Of_Lists[i][j],
                'dfax_report':os.path.join(DFAX_PATH,f"{script_file_name}.csv")}
            # the template object takes a set of key value pairs
                new_script=script_template.substitute(config_dict)
                os.makedirs(SCRIPT_Sub_Parent_Folders[i],exist_ok=True)
                NewPath=os.path.join(f"{self.__class__.FLOW_GATE_PARENT_PATH}\{scripts_sub_parent_folder_name}",SCRIPT_Sub_Parent_Folders[i])
                NewFile=os.path.join(NewPath, f"{script_file_name}.txt")
                output_fh = open(NewFile, "w")
                output_fh.write(new_script)
                script_file=rf'{NewFile}'
                self.generate_DFAX_report(script_file)
    def generate_DFAX_report(self,script_file_path):
        tara=tw.powerGemExe(exeFilePath=self.__class__.exe_path)
        tara.runScript(scriptFilePath=script_file_path)
    def execute_all(self,scripts_sub_parent_folder_name,scripts_reversal_sub_parent_folder,stressed_cases_sub_parent_folder_name,stressed_cases_sub_parent_folder_name_reversal,dfax_reports_sub_parent_folder_name,dfax_reports_reversal_sub_parent_folder_name,scrd_scripts_sub_parent_folder_name,scrd_scripts_sub_parent_folder_name_reversal,secured_cases_sub_parent_folder_name,secured_cases_sub_parent_folder_name_reversal,
    Sending_Subsystem,Reference_Subsystem):
        Create_Flow_Gate_Tuple.overwrite_scripts_folder(dfax_reports_sub_parent_folder_name,dfax_reports_reversal_sub_parent_folder_name,scripts_sub_parent_folder_name,scripts_reversal_sub_parent_folder,stressed_cases_sub_parent_folder_name,stressed_cases_sub_parent_folder_name_reversal,secured_cases_sub_parent_folder_name,secured_cases_sub_parent_folder_name_reversal,scrd_scripts_sub_parent_folder_name,scrd_scripts_sub_parent_folder_name_reversal)
        non_reversal_flowgate_list=self.clean_DCCONT_File_create_Flow_Gate_Tuple()
        reversal_flowgate_list=self.REVERSAL_clean_DCCONT_File_create_Flow_Gate_Tuple()
        self.make_flowgate_scripts(non_reversal_flowgate_list,scripts_sub_parent_folder_name,stressed_cases_sub_parent_folder_name,dfax_reports_sub_parent_folder_name,scrd_scripts_sub_parent_folder_name,secured_cases_sub_parent_folder_name,Sending_Subsystem,Reference_Subsystem)
        self.make_flowgate_scripts(reversal_flowgate_list,scripts_reversal_sub_parent_folder,stressed_cases_sub_parent_folder_name_reversal,dfax_reports_reversal_sub_parent_folder_name,scrd_scripts_sub_parent_folder_name_reversal,secured_cases_sub_parent_folder_name_reversal,Sending_Subsystem,Reference_Subsystem)
# if __name__=="__main__":
    # c=Create_Flow_Gate_Tuple()
    # c.execute_all('SCRIPTS','SCRIPTS_REVERSAL','STRESSED_CASES','STRESSED_CASES_REVERSAL','DFAX_REPORTS','DFAX_REPORTS_REVERSAL','SCRD_SCRIPTS','SCRD_SCRIPTS_REVERSAL','SECURED_CASES','SECURED_CASES_REVERSAL','ISO_NE_GENs','ISO_NE_Load')