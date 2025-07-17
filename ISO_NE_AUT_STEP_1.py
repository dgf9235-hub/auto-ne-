import pandas as pd 
import numpy as np 
import os
from string import Template 
import pyPowerGEM.wrapper as tw
from ISO_NE_AUT_Folder_File_Creation_Auxiliary_File import *
#All Imports necessary for this python file
import ISO_NE_AUT_ALL_PATHs
from ISO_NE_AUT_ALL_PATHs import Files as f
#Import of the Python Files that will write the paths specified in the ISO_NE_AUT_PATHs .jsonc file

class Template_And_Write_DC_CONT_File(Create_File_Name_In_Path,f):
    exe_path=None#DEFINE THE PATH OF YOUR EXECUTABLE FILE, MUST CREATE THIS FOLDER BEFORE STARTING THE AUTOMATION
    aux_path=None#USER DEFINED PATH FOR ALL RAW AND AUXILIARY FILES
    def __init__(self):
        Template_And_Write_DC_CONT_File.change_class_variable_paths()
        self.Input_File_Path=f"{self.__class__.aux_path}\{self.json_dumps_function('Base Case')}" #This variable will be written to when the template_DCCONT_script method is used
        self.Con_File_Path=f"{self.__class__.aux_path}\{self.json_dumps_function('Con_File_Name')}" #This variable will be written to when the template_DCCONT_script method is used
        self.Sub_File_Path=f"{self.__class__.aux_path}\{self.json_dumps_function('Subsystem_File_Name')}" #This variable will be written to when the template DCCONT_script method is used
        self.Mon_File_Path=f"{self.__class__.aux_path}\{self.json_dumps_function('Mon_File_Name')}"#This method will be written to when the template DCCONT_script method is used 
        self.Sending_Subsystem=self.json_dumps_function('Study_Unit_Bus_Number')#This method will be written to when the template DCCONT_script method is useds
        self.Reference_Subsystem=self.json_dumps_function('Study_Unit_Load_Zone_Name')#This method will be written to when the template DCCONT_script method is used 
        self.STEP_1_PARENT_FOLDER_PATH=self.json_dumps_function('Pre_Project_Parent_Folder_Path')
        #"PARENT" FOLDER THAT HOLDS ALL THE FILES BELOW, DEFINED DURING INSTANTIATION
        #defined when you create the DCCONT Script File in the TARAViewer, Parent Path that holds that original Script 
        #defined when you create the DCCONT Script File in the TARAViewer, we are going to save it to the Parent Folder Path
        self.script_name=self.json_dumps_function('STEP_1_Output_Script_Name(.txt)')#THE NAME OF THE OUTPUT SCRIPT THAT GENERATES DCCONT FILE, DEFINED BY THE USER IN THE INSTANTIATION FO THE CLASS
        self.template_name=self.json_dumps_function('STEP_1_Script_Template_Name(.txt)')#THE NAME OPF THE SCRIPT TEMPLATE
        self.dccont_file_name=self.json_dumps_function('DC_CA_File_Name(.csv)')#THE NAME OF YOUR DCCONT FILE
        self.DCCONT_SCRIPT_TEMPLATE_FILE_PATH=os.path.join(self.STEP_1_PARENT_FOLDER_PATH,self.template_name)
        self.DCCONT_NEW_SCRIPT_PATH=self.create_file_name(self.STEP_1_PARENT_FOLDER_PATH,self.script_name)
        self.DCCONT_OUTPUT_REPORT_PATH=self.create_file_name(self.STEP_1_PARENT_FOLDER_PATH,self.dccont_file_name)
    @classmethod
    def change_class_variable_paths(cls):
        cls.exe_path=rf"{f.json_dumps_function(f,'tara_executable')}"
        cls.aux_path=rf"{f.json_dumps_function(f,'auxiliary_files_folder_path')}"
    @classmethod
    def change_exe_path(cls,new_path):
        cls.exe_path=rf"{new_path}"
    def run_script_wrapper_class(self,script_file):
        tara=tw.powerGemExe(exeFilePath=Template_And_Write_DC_CONT_File.exe_path)
        tara.runScript(scriptFilePath=script_file)
    def template_DCCONT_script(self):
       #This is the path of the new script file that will generate the DCCONT report to the DCCONT OUTPUT REPORT PATH 
        #template_fh = os.path.join(self.STEP_1_PARENT_FOLDER_PATH,self.DCCONT_SCRIPT_TEMPLATE_FILE_PATH)
        template_fh=self.DCCONT_SCRIPT_TEMPLATE_FILE_PATH
        template_fh = open(template_fh, "r")
        script_string = template_fh.read()
    # read entire script in one passs
        script_template=Template(script_string) 
        config_dict={"Input_File_Full_Path":f"{self.Input_File_Path}",
        "Contingency_File_Full_Path":f"{self.Con_File_Path}",
        "Subsystem_File_Full_Path":f"{self.Sub_File_Path}",
        "Monitor_File_Full_Path":f"{self.Mon_File_Path}",
        "Sending_Bus": f"{self.Sending_Subsystem}",#Write the exact name of the Sending Bus s
        "Reference_Subsystem":f"{self.Reference_Subsystem}",#Write the exact name of the reference subsystem 
        "DCCONT_OUTPUT_FILE_FULL_PATH":f"{self.DCCONT_OUTPUT_REPORT_PATH}"}
        #self.Input_File_Path,self.Con_File_Path,self.Sub_File_Path,self.Mon_File_Path=config_dict["Input_File_Full_Path"],config_dict["Contingency_File_Full_Path"],config_dict["Subsystem_File_Full_Path"],config_dict["Monitor_File_Full_Path"]
	# the template object takes a set of key value pairs
        new_script=script_template.substitute(config_dict) 
        NewFile=self.DCCONT_NEW_SCRIPT_PATH
        output_fh = open(NewFile, "w")
        output_fh.write(new_script)
        self.run_script_wrapper_class(NewFile)

