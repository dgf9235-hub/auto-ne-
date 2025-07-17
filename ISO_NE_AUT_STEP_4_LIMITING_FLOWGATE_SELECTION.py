import pandas as pd
import numpy as np
import os 
import asyncio
from string import Template 
import pyPowerGEM.wrapper as tw
import ISO_NE_AUT_Folder_File_Creation_Auxiliary_File
from ISO_NE_AUT_Folder_File_Creation_Auxiliary_File import Create_Folders as cf
import ISO_NE_AUT_STEP_2
from ISO_NE_AUT_STEP_2 import Create_Flow_Gate_Tuple 
import ISO_NE_AUT_STEP_3_Stressing  
from ISO_NE_AUT_STEP_3_Stressing import Create_And_View
import ISO_NE_AUT_STEP_1
from ISO_NE_AUT_STEP_1 import Template_And_Write_DC_CONT_File as tdc
import ISO_NE_AUT_STEP_3_b
from ISO_NE_AUT_STEP_3_b import Secure_the_Case as sns
#All Imports necessary for this python file
import ISO_NE_AUT_ALL_PATHs
from ISO_NE_AUT_ALL_PATHs import Files as f
#Import of the Python Files that will write the paths specified in the ISO_NE_AUT_PATHs .jsonc file
import itertools
from itertools import zip_longest
#import zip longest module so when we combine reversal and non reversal secured cases we can for loop through both, more efficient code 
class Pick_Limiting_FlowGate(cf,f):
    s=sns()
    s.SCRD_execution()#call the SCRD (Implementation function) on the instance of the class 
    POST_PJT_PARENT_FOLDER=f.json_dumps_function(f,'POST_PROJECT_PARENT_FOLDER_PATH')#json template call
    PRE_PROJECT_PARENT_FOLDER=f.json_dumps_function(f,"Pre_Project_Parent_Folder_Path")
    RELEVANT_FLOWGATES=f.json_dumps_function(f,'PRE_PROJECT_LOADINGS_CSV_FILE_PATH')#json template call
    AUX_PATH=f.json_dumps_function(f,"auxiliary_files_folder_path")
    SUB_FILE=f.json_dumps_function(f,"Subsystem_File_Name")
    MON_FILE=f.json_dumps_function(f,"Mon_File_Name")
    CON_FILE=f.json_dumps_function(f,"Con_File_Name")
    STUDY_UNIT_BUS=f.json_dumps_function(f,'Study_Unit_Bus_Number')#json template call
    REF_SUBSYSTEM=f.json_dumps_function(f,'Study_Unit_Load_Zone_Name')#json template call
    DFAX_CUTOFF_REL_FLOWGATES=Create_Flow_Gate_Tuple.DFAX_CUTOFF
    MIN_LOADING=f.json_dumps_function(f,'MINIMUM_LOADING_PRE_PROJECT_LOADING_CSV_FILE')#json template call

    SECURED_CASES_SUB_PARENT_PATH=os.path.join(PRE_PROJECT_PARENT_FOLDER,"SECURED_CASES")
    SECURED_CASES_SUB_PARENT_PATH_REVERSAL=os.path.join(PRE_PROJECT_PARENT_FOLDER,"SECURED_CASES_REVERSAL")

    # SECURED_CASES_SUB_PARENT_PATH=s.SECURED_CASES_SUB_PARENT_PATH
    # SECURED_CASES_SUB_PARENT_PATH_REVERSAL=s.SECURED_CASES_SUB_PARENT_PATH_FLOW_REVERSAL

    DCCONT_SCRIPT_TEMPLATE_FILE_PATH=f.json_dumps_function(f,'DCCONT_SCRIPT_PATH')#json template call

    #Initialize the constructor to instantiate the variables, use the helper function to create new paths for all the new folder relevant for the post project case 
    def __init__(self):
        self.DCCONT_REPORTS_SUB_PARENT_FOLDER=self.create_single_folder(self.__class__.PRE_PROJECT_PARENT_FOLDER,'DCCONT_REPORTS_SECURED_CASES')
        self.SCRIPTS_SUB_PARENT_FOLDER_GENERATE_DCCONT_REPORT=self.create_single_folder(self.__class__.PRE_PROJECT_PARENT_FOLDER,'SCRIPTS_DCCONT_SECURED_CASES')
        #Above are the commands to create the folders that contain the scripts and dccont file that will assist in creating the relevant flowgates sheet

        self.FLOW_GATE_DFAX_REPORTS_SUB_PARENT_FOLDER=self.create_single_folder(self.__class__.POST_PJT_PARENT_FOLDER,'FLOW_GATE_DFAX_REPORTS')
        self.FLOW_GATE_DFAX_REPORT_SCRIPTS_SUB_PARENT_FOLDER=self.create_single_folder(self.__class__.POST_PJT_PARENT_FOLDER,'FLOW_GATE_DFAX_REPORTS_SCRIPTS')
    #run script helper function, pytara functionality integrated into a native function
    def run_script(self,script_file):
        tara=tw.powerGemExe(exeFilePath=tdc.exe_path)
        tara.runScript(scriptFilePath=script_file)
    #create the DCCONT REPORTS for each stressed case by creating DCCONT scripts and Reports so that we can extract the relevant flowgate and template the dfax reports scripts to generate dfax reports
    #which will then be used to dispatch against the study unit
    def create_DCCONT_Reports(self):
        #PATHS for the secured cases for stress in flow direction and reversal
        directory=self.__class__.SECURED_CASES_SUB_PARENT_PATH
        directory_1=self.__class__.SECURED_CASES_SUB_PARENT_PATH_REVERSAL
        
        #loop through the folders and createnew folders for each monitored element to contain all the flowgate scripts, dccont reports, dfax reports, dfax report scripts
        for folder_name in os.listdir(directory):
            folder_path = os.path.join(directory, folder_name)  

            stressed_secured_dccont_folder_name=self.create_single_folder(self.DCCONT_REPORTS_SUB_PARENT_FOLDER,f"{folder_name}")#create the flowgate folders for each dccont report for each secured raw file
           
            scripts_folder_flowgate_selection=self.create_single_folder(self.SCRIPTS_SUB_PARENT_FOLDER_GENERATE_DCCONT_REPORT,f"{folder_name}")#create the script folders for the scripts that generate those dccont reports  
           
            dfax_reports_secured=self.create_single_folder(self.FLOW_GATE_DFAX_REPORTS_SUB_PARENT_FOLDER,f"{folder_name}")#create the dfax report folders for each mon, containing flowgate specific dfax reports
           
            scripts_folder_dfax_report=self.create_single_folder(self.FLOW_GATE_DFAX_REPORT_SCRIPTS_SUB_PARENT_FOLDER,f"{folder_name}")#create the dfax report script folders holding the scripts that generate each dfax report

            self.DCCONT_script(folder_path,stressed_secured_dccont_folder_name,scripts_folder_flowgate_selection,dfax_reports_secured,scripts_folder_dfax_report)

        for folder_name_1 in os.listdir(directory_1):
            #Create the mon specific folders within he respective sub parent folder in which the relevant raw and .txt files will be placed
            folder_path_1 = os.path.join(directory_1, folder_name_1)

            stressed_secured_dccont_folder_name_1=self.create_single_folder(self.DCCONT_REPORTS_SUB_PARENT_FOLDER,f"{folder_name_1}")#create the flowgate folders for each dccont report for each secured raw file

            scripts_folder_flowgate_selection_1=self.create_single_folder(self.SCRIPTS_SUB_PARENT_FOLDER_GENERATE_DCCONT_REPORT,f"{folder_name_1}")#create the script folders for the scripts that generate those dccont reports

            dfax_reports_secured_1=self.create_single_folder(self.FLOW_GATE_DFAX_REPORTS_SUB_PARENT_FOLDER,f"{folder_name_1}")#create the dfax report folders for each mon, containing flowgate specific dfax reports

            scripts_folder_dfax_report_1=self.create_single_folder(self.FLOW_GATE_DFAX_REPORT_SCRIPTS_SUB_PARENT_FOLDER,f"{folder_name_1}")#create the dfax report script folders holding the scripts that generate each dfax report
            
            self.DCCONT_script(folder_path_1,stressed_secured_dccont_folder_name_1,scripts_folder_flowgate_selection_1,dfax_reports_secured_1,scripts_folder_dfax_report_1)


    def DCCONT_script(self,folder_path,stressed_secured_dccont_folder_name,scripts_folder_flowgate_selection, dfax_reports_secured,scripts_folder_dfax_report):

        for filename in os.listdir(folder_path):
            #self.create_single_folder(dfax_reports_secured,f"{filename.split('.')[0]}")
            #We create a folder for each specific raw file name because we generate many different dfax reports for each raw file. 
            #We generate a dfax report for the N highest loading flowgates (mon not necessarily matching mon nor con matching con)
            #self.create_single_folder(scripts_folder_dfax_report,f"{filename.split('.')[0]}")
            dccont_name=filename.split('.')[0]#split the filename at '.raw'
            script_name=filename.split('.')[0]#split the filename at '.raw'
            flow_gate_list=filename.split('_')#split the filename 'SCRD_{Fr Bus}_{To_Bus}_ckt_{ckt#}_{contingency number}.raw'
            # read entire script in one passs
            template_fh=self.__class__.DCCONT_SCRIPT_TEMPLATE_FILE_PATH
            template_fh = open(template_fh, "r")
            script_string=template_fh.read()
            script_template=Template(script_string) 
            config_dict={"Input_File_Full_Path":f"{folder_path}\{filename}",
            "Con_File_Full_Path":f"{self.__class__.AUX_PATH}\{self.__class__.CON_FILE}",
            "Subsystem_File_Full_Path":f"{self.__class__.AUX_PATH}\{self.__class__.SUB_FILE}",
            "Mon_File_Full_Path":f"{self.__class__.AUX_PATH}\{self.__class__.MON_FILE}",
            "Sending_Subsystem": f"{self.__class__.STUDY_UNIT_BUS}",#Write the exact name of the Sending Bus 
            "Ref_Subsystem":f"{self.__class__.REF_SUBSYSTEM}",#Write the exact name of the reference subsystem 
            "Minimum_Loading":75,
            "DCCONT_OUTPUT_FILE_FULL_PATH":f"{stressed_secured_dccont_folder_name}\{dccont_name}.csv"}
            new_script=script_template.substitute(config_dict) 
            NewFile=os.path.join(f"{scripts_folder_flowgate_selection}",f"{script_name}.txt")
            output_fh = open(NewFile, "w")
            output_fh.write(new_script)
            self.run_script(NewFile)
    def clean_DCCONT_File_Create_Limiting_Flowgates(self):
        self.create_DCCONT_Reports()
        directory=self.DCCONT_REPORTS_SUB_PARENT_FOLDER
        DFAX_Sub_Parent_Folder_List=[name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]
        Limiting_FlowGate_List=pd.DataFrame()
        Limiting_FlowGate_List["Monitored Facility"]=None
        Limiting_FlowGate_List["Fr Bus"]=None
        Limiting_FlowGate_List["To Bus"]=None
        Limiting_FlowGate_List["CKT"]=None
        Limiting_FlowGate_List["Contingency_Name"]=None
        Limiting_FlowGate_List["Contingency_Number"]=None
        Limiting_FlowGate_List["Reference Loading"]=None
        Limiting_FlowGate_List["Study_Unit_DFAX"]=None
        Limiting_FlowGate_List["Rate A"]=None
        Limiting_FlowGate_List["Rate B"]=None
        Limiting_FlowGate_List.insert(0,'Stress_ID',None)
        for folder_name in os.listdir(directory):
            folder_path = os.path.join(directory, folder_name)
            for filename in os.listdir(folder_path):
                DCCONT=pd.read_csv(f"{folder_path}\{filename}",skiprows=9)#ignore statement for first N rows)
                DCCONT=DCCONT.rename(columns={'Dfax Harmer Positive (based on flow direction) Bus ' f'{self.json_dumps_function("Study_Unit_Bus_Number")}':'Real DFAX'})
                DCCONT=DCCONT.drop(columns=['Unnamed: 20'])
                DCCONT=DCCONT[DCCONT['Real DFAX']>=self.__class__.DFAX_CUTOFF_REL_FLOWGATES]
                DCCONT=DCCONT[DCCONT['Final DC %Loading']>=self.__class__.MIN_LOADING]
                print(DCCONT)
                limiting_columns=Limiting_FlowGate_List.columns
                for index, row in DCCONT.iterrows():
                    new_index=len(Limiting_FlowGate_List)
                    new_row = {limiting_columns[0]: filename.split('.')[0], limiting_columns[1]:row[' Monitored Facility                                   '],
                    limiting_columns[2]:row['Fr Bus'],limiting_columns[3]: row['To Bus'], limiting_columns[4]:row['CKT'],limiting_columns[5]:row[' Cont Name                                                      '],
                    limiting_columns[6]: row['Cont ID'],limiting_columns[7]: row['Final DC %Loading'],limiting_columns[8]:row['Real DFAX'],limiting_columns[9]:row['Rate Base (MVA)'],limiting_columns[10]:row['Rate Cont (MVA)']}
                    new_row=pd.DataFrame([new_row])
                    Limiting_FlowGate_List=pd.concat([Limiting_FlowGate_List,new_row], ignore_index=True)
        Limiting_FlowGate_List.to_csv(self.__class__.RELEVANT_FLOWGATES,index=False)
if __name__=='__main__':  
    p=Pick_Limiting_FlowGate()
    p.clean_DCCONT_File_Create_Limiting_Flowgates()

