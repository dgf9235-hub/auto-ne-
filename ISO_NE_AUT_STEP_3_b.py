import pandas as pd 
import numpy as np 
import yaml
import os 
from string import Template 
import pyPowerGEM.wrapper as tw
import ISO_NE_AUT_Folder_File_Creation_Auxiliary_File
from ISO_NE_AUT_Folder_File_Creation_Auxiliary_File import Create_Folders
import ISO_NE_AUT_STEP_2
from ISO_NE_AUT_STEP_2 import Create_Flow_Gate_Tuple
import ISO_NE_AUT_STEP_3_Stressing  
from ISO_NE_AUT_STEP_3_Stressing import Create_And_View
import ISO_NE_AUT_STEP_1
from ISO_NE_AUT_STEP_1 import Template_And_Write_DC_CONT_File as tdc
#All Imports necessary for this python file
import ISO_NE_AUT_ALL_PATHs
from ISO_NE_AUT_ALL_PATHs import Files as f
#Import of the Python Files that will write the paths specified in the ISO_NE_AUT_PATHs .jsonc file
class Secure_the_Case(Create_Flow_Gate_Tuple,f):
    c=Create_Flow_Gate_Tuple()
    c.execute_all('SCRIPTS','SCRIPTS_REVERSAL','STRESSED_CASES','STRESSED_CASES_REVERSAL','DFAX_REPORTS','DFAX_REPORTS_REVERSAL','SCRD_SCRIPTS','SCRD_SCRIPTS_REVERSAL','SECURED_CASES','SECURED_CASES_REVERSAL','ISO_NE_GENs','ISO_NE_Load')
    x=Create_And_View()
    x.execution(x.DFAX_REPORTS_SUB_PARENT_FOLDER_PATH)
    x.execution(x.DFAX_REPORTS_SUB_PARENT_FOLDER_PATH_REVERSAL)
    def __init__(self):
        self.DFAX_REPORTS_SUB_PARENT_FOLDER_PATH=Create_Flow_Gate_Tuple.FlOW_GATE_DFAX_REPORT_SUB_PARENT_FOLDER_PATH
        self.FLOW_GATE_SCRD_SCRIPT_SUB_PARENT_FOLDER_PATH=os.path.join(self.__class__.c.FLOW_GATE_PARENT_PATH,self.__class__.c.FLOW_GATE_SCRD_SCRIPTS_SUB_PARENT_FOLDER_PATH)
        self.dll_File_Path=Create_And_View.dll_File_Path
        self.aux_path=self.__class__.c.STEP_1_Instance.aux_path
        self.scrd_script_template=os.path.join(self.__class__.c.FLOW_GATE_PARENT_PATH,'SCRD_Script.txt')
        self.sub_file=self.json_dumps_function('Subsystem_File_Name')
        self.mon_file=self.json_dumps_function('Mon_File_Name')
        self.con_file=self.json_dumps_function('Con_File_Name')
        self.re_dispatch_subsystem='ISO_NE_GENs'
        self.script_output_path=os.path.join(rf"{self.__class__.c.FLOW_GATE_PARENT_PATH}",'')
        self.STRESSED_CASE_sub_parent_folder=self.__class__.c.FLOW_GATE_MONITORED_ELEMENT_STRESSED_CASES_SUB_PARENT_FOLDER_PATH
        self.STRESSED_CASE_sub_parent_folder_reversal=self.__class__.c.FLOW_GATE_MONITORED_ELEMENT_STRESSED_CASES_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL
        self.SCRD_SCRIPT_SUB_PARENT_FOLDER_PATH=os.path.join(self.__class__.c.FLOW_GATE_PARENT_PATH,self.__class__.c.FLOW_GATE_SCRD_SCRIPTS_SUB_PARENT_FOLDER_PATH)
        self.SCRD_SCRIPT_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL =os.path.join(self.__class__.c.FLOW_GATE_PARENT_PATH,self.__class__.c.FLOW_GATE_SCRD_SCRIPTS_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL)
        self.SECURED_CASES_SUB_PARENT_PATH=os.path.join(self.__class__.c.FLOW_GATE_PARENT_PATH,self.__class__.c.FLOW_GATE_MONITORED_ELEMENT_SECURED_CASES_SUB_PARENT_FOLDER_PATH)
        self.SECURED_CASES_SUB_PARENT_PATH_FLOW_REVERSAL=os.path.join(self.__class__.c.FLOW_GATE_PARENT_PATH,self.__class__.c.FLOW_GATE_MONITORED_ELEMENT_SECURED_CASES_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL)

# MonBranPenaltyBase   $mon_overload_penalty //Penalty for base case branch overloads
#  MonBranPenaltyCont   $con_overload_penalty //Penalty for contingency branch overloads
#  fixBidsWithNoRange   1 //Fix dispatch of generators with no range in cost curve at initial LF case dispatch(0-no,1-yes)
#  GEN_SEG_SLOPE        $gen_redispatch_penalty //Penalty for generation redispatch in SCRD
    def SCRD_Template_And_Run(self,input_file_path,output_file_path,script_folder_name):
        template_fh=self.scrd_script_template
        template_fh=open(template_fh,'r')
        script_string=template_fh.read()
        script_template=Template(script_string)
        config_dict={"Input_File_Full_Path":f"{input_file_path}",
        "Subsystem_File_Full_Path":f"{self.aux_path}\{self.sub_file}",
        "Mon_File_Full_Path":f"{self.aux_path}\{self.mon_file}",
        "Contingency_File_Full_Path":f"{self.aux_path}\{self.con_file}",
        "Output_File_Full_Path":output_file_path,
        "mon_overload_penalty":self.json_dumps_function("BASE_OVERLOAD_PEN_SCRD"),
        "con_overload_penalty":self.json_dumps_function("CON_OVERLOAD_PEN_SCRD"),
        "gen_redispatch_penalty":self.json_dumps_function("GEN_REDISPATCH_PEN_SCRD")
        }
        new_script=script_template.safe_substitute(config_dict)
        script_name=input_file_path.split('\\')[-1]
        script_name=script_name.split('.')[0]
        NewFile=os.path.join(script_folder_name,f"{script_name}_SCRD.txt")
        output_fh = open(NewFile, "w")
        output_fh.write(new_script)
        script_file=rf'{NewFile}'
        tdc.run_script_wrapper_class(self,script_file)
    def SCRD_execution(self):
        directory=self.STRESSED_CASE_sub_parent_folder
        secured_sub_parent_path=self.SECURED_CASES_SUB_PARENT_PATH
        secured_sub_parent_list=[name for name in os.listdir(secured_sub_parent_path) if os.path.isdir(os.path.join(secured_sub_parent_path, name))]
        directory_reversal =self.STRESSED_CASE_sub_parent_folder_reversal
        secured_sub_parent_path_reversal=self.SECURED_CASES_SUB_PARENT_PATH_FLOW_REVERSAL
        secured_sub_parent_list_reversal=[name for name in os.listdir(secured_sub_parent_path_reversal) if os.path.isdir(os.path.join( secured_sub_parent_path_reversal,name))]
        i=0
        Scripts_Cases_Sub_Parent=self.SCRD_SCRIPT_SUB_PARENT_FOLDER_PATH
        scripts_sub_parent_folder_list=[name for name in os.listdir(Scripts_Cases_Sub_Parent) if os.path.isdir(os.path.join(Scripts_Cases_Sub_Parent, name))]
        Scripts_Cases_Sub_Parent_Reversal =self.SCRD_SCRIPT_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL
        scripts_sub_parent_folder_list_reversal=[name for name in os.listdir(Scripts_Cases_Sub_Parent_Reversal) if os.path.isdir(os.path.join(Scripts_Cases_Sub_Parent_Reversal, name))]
        for folder_name in os.listdir(directory):
            folder_path = os.path.join(directory, folder_name)
            for filename in os.listdir(folder_path):
                file_path=os.path.join(folder_path,filename)
                self.SCRD_Template_And_Run(f"{file_path}",f"{self.SECURED_CASES_SUB_PARENT_PATH}\{secured_sub_parent_list[i]}\SCRD_{filename}",f"{self.SCRD_SCRIPT_SUB_PARENT_FOLDER_PATH}\{scripts_sub_parent_folder_list[i]}")
            i+=1
        i=0
        for folder_name in os.listdir(directory_reversal):
            folder_path = os.path.join(directory_reversal, folder_name)
            for filename in os.listdir(folder_path):
                file_path=os.path.join(folder_path,filename)
                self.SCRD_Template_And_Run(f"{file_path}",f"{self.SECURED_CASES_SUB_PARENT_PATH_FLOW_REVERSAL}\{secured_sub_parent_list_reversal[i]}\SCRD_{filename}",f"{self.SCRD_SCRIPT_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL}\{scripts_sub_parent_folder_list_reversal[i]}")
            i+=1







