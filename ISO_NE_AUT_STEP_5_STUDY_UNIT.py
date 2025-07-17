import pandas as pd
import numpy as np
import os 
from string import Template 
import pyPowerGEM.wrapper as tw
import ISO_NE_AUT_Folder_File_Creation_Auxiliary_File
from ISO_NE_AUT_Folder_File_Creation_Auxiliary_File import Create_Folders
import ISO_NE_AUT_STEP_2
from ISO_NE_AUT_STEP_2 import Create_Flow_Gate_Tuple as cft
import ISO_NE_AUT_STEP_3_Stressing  
from ISO_NE_AUT_STEP_3_Stressing import Create_And_View
import ISO_NE_AUT_STEP_1
from ISO_NE_AUT_STEP_1 import Template_And_Write_DC_CONT_File as tdc
import ISO_NE_AUT_STEP_4_LIMITING_FLOWGATE_SELECTION 
from ISO_NE_AUT_STEP_4_LIMITING_FLOWGATE_SELECTION import Pick_Limiting_FlowGate
import ISO_NE_AUT_ALL_PATHs
from ISO_NE_AUT_ALL_PATHs import Files as f
#Import of the Python Files that will write the paths specified in the ISO_NE_AUT_PATHs .jsonc files 
    # p=Pick_Limiting_FlowGate()#instantiate the step 4 class
    # p.clean_DCCONT_File_Create_Limiting_Flowgates()#call the STEP 4 function that creates the stressed cases and relevant flowgates list
class Post_Project_Loading(f):

    Create_And_View=Create_And_View()
    p=Pick_Limiting_FlowGate()#instantiate the step 4 class
    p.clean_DCCONT_File_Create_Limiting_Flowgates()#call the STEP 4 function that creates the stressed cases and relevant flowgates list
    exe_path=f.json_dumps_function(f,'tara_executable')#json template call

    RELEVANT_FLOWGATES_FILE=p.RELEVANT_FLOWGATES #create the relevant flowgates excel file using the class called after the completion of the function to generate it 
    DFAX_SUB_PARENT_FOLDER=p.FLOW_GATE_DFAX_REPORTS_SUB_PARENT_FOLDER # all dfax reports folder created in STEP 4 for storing post-secure dfax reports
    FLOW_GATE_DFAX_REPORT_SCRIPTS_SUB_PARENT_FOLDER=f"{f.json_dumps_function(f,'POST_PROJECT_PARENT_FOLDER_PATH')}\FLOW_GATE_DFAX_REPORTS_SCRIPTS"

    Sending_Sub=f.json_dumps_function(f,'POST_PROJECT_DISPATCH_GENS')#json template call
    Ref_Subsystem=f.json_dumps_function(f,'POST_PROJECT_DISPATCH_REFERENCE')#json template call

    POST_PJT_CASES_SUB_PARENT_FOLDER='' #Create a class variable for the sub parent folder that will hold all the separate monitored element folder that hold the post-project cases
    CLUSTER_INCH_FILE=f.json_dumps_function(f,'CL_INCH_FILE')
    #Helper Function 1
    def run_script(self,script_file):
        #tara instantiate the wrapper class, executable function, so that we can now use the c functionality contaained in the executable
        #to run the run script function ont the script file (YAML) to use the input files to generate the excel reports we want. 
        tara=tw.powerGemExe(exeFilePath=self.__class__.exe_path)
        tara.runScript(scriptFilePath=script_file)
     #Helper Function 2
    def split_flowgate_string(self,flow_gate):
        flow_gate_list=flow_gate.split()#will split at spaces, create a list out of the separate components
        if flow_gate_list[-1]=='case':
            new_file_name=f"{flow_gate_list[3]}" f"_" f"{flow_gate_list[6]}" f"_" f"{flow_gate_list[7]}_{flow_gate_list[8]}" f"_0"
        else:
            new_file_name=f"{flow_gate_list[3]}" f"_" f"{flow_gate_list[6]}" f"_" f"{flow_gate_list[7]}_{flow_gate_list[8]}" f"_" f"{flow_gate_list[-1]}"
        #catch erro exception
        #create a new file name out of the components of the flowgate string, now list,
        #to be used as naming for the raw files created in t
        return new_file_name #return the file when the function is called, but dont print. Stores the response in that call to the function. 

    #Objective Function 1
    def run_dfax_script(self,input_file_path,flow_gate,dfax_scripts_folder,dfax_report_output_path):
            template_fh=f"{self.json_dumps_function('Pre_Project_Parent_Folder_Path')}\{self.json_dumps_function('STEP_2_Script_Template_Name(.txt)')}"#Call the script template from the stressing stage to generate the dfax report
            template_fh = open(template_fh, "r")
            script_string=template_fh.read()
            script_template=Template(script_string)#pyfunc, make into template to write to
            config_dict={"Input_File_Full_Path":input_file_path,
            "Con_File_Full_Path":f"{self.__class__.p.AUX_PATH}\{self.__class__.p.CON_FILE}",
            "Subsystem_File_Full_Path":f"{self.__class__.p.AUX_PATH}\{self.__class__.p.SUB_FILE}",
            "Mon_File_Full_Path":f"{self.__class__.p.AUX_PATH}\{self.__class__.p.MON_FILE}",
            "Sending_Subsystem": f"{self.__class__.Sending_Sub}",#Write the exact name of the Sending Bus 
            "Ref_Subsystem":f"{self.__class__.Ref_Subsystem}",#Write the exact name of the reference subsystem 
            "flow_gate":flow_gate,
            "dfax_report":f"{dfax_report_output_path}"}
            new_script=script_template.substitute(config_dict) 
            NewFile=os.path.join(f"{self.__class__.FLOW_GATE_DFAX_REPORT_SCRIPTS_SUB_PARENT_FOLDER}\{dfax_scripts_folder}",f"{flow_gate}.txt")#Create the file name for each of the dfax reports
            output_fh = open(NewFile, "w")
            output_fh.write(new_script)
            self.run_script(NewFile)

    #Helper Function 3
    def group_flow_gates(self):
        HAVANA=pd.read_csv(self.__class__.RELEVANT_FLOWGATES_FILE)
        REL_FLOWGATES=pd.DataFrame(HAVANA)
        Flow_Gate_Lists = []
        Stress_ID_Names=[]
        grouped = REL_FLOWGATES.groupby(['Stress_ID'])
        for name, group in grouped:
            Stress_ID_Names.append(name)
            sublist = [f"branch from bus {row['Fr Bus']} to bus "f"{row['To Bus']} ckt "f"{row['CKT']} in contingency number {row['Contingency_Number']}" if row['Contingency_Number']!=0 else
            f"branch from bus {row['Fr Bus']} to bus "f"{row['To Bus']} ckt "f"{row['CKT']} in base case" for _, row in group.iterrows()]
            Flow_Gate_Lists.append(sublist)
        print(Flow_Gate_Lists)
        return Flow_Gate_Lists, Stress_ID_Names
    #Objective Function 1
    def add_study_unit_using_inch_file(self,tara_api_instance):
        tara_api_instance.applyInchFile(inchFilePath=self.__class__.CLUSTER_INCH_FILE)

    #Implementation Function 1
    def template_dfax_report_script(self):
        #create the flowgate list from the relevant flowgates file of the flowgates for each stress ID that are most constrained for that stressed case
        flow_gate,stress_ids =self.group_flow_gates()

        #folder path  of the folder containing the secured stressed cases which we will loop through
        #both normal flow direction and flow reversal securd cases must be included 
        directory=f"{self.json_dumps_function('Pre_Project_Parent_Folder_Path')}\SECURED_CASES"
        directory_reversal=f"{self.json_dumps_function('Pre_Project_Parent_Folder_Path')}\SECURED_CASES_REVERSAL"

        #introduce the paths for the flow gate dfax reports and the flowgate dfax report scripts to which we will write from the template nd run dfax reports function
        directory2=f"{self.json_dumps_function('POST_PROJECT_PARENT_FOLDER_PATH')}\FLOW_GATE_DFAX_REPORTS"
        directory3=f"{self.json_dumps_function('POST_PROJECT_PARENT_FOLDER_PATH')}\FLOW_GATE_DFAX_REPORTS_SCRIPTS"


        #create a list for the dfax reports folders for each mon within the dfax report sub parent folders to which we will write the dfax reports fotr each flowgate we gathered from dccont. 
        dfax_mon_folders=[name for name in os.listdir(directory2) if os.path.isdir(os.path.join(directory2, name))]
        dfax_script_folders=[name for name in os.listdir(directory3) if os.path.isdir(os.path.join(directory3, name))]

        #function that loops through the secured cases folders and files for bothflow direction and reversal and templates the scripts and creates the dfax report
        #uses the flowgate lists and indicies to write the dfax reports and dfax report scripts to thgeir respective folders within i the dfax folders 

        print(flow_gate)
        for folder in os.listdir(directory):
            folder1=folder
            folder_path1=os.path.join(directory,folder)

            for filename in os.listdir(folder_path1):
                file_path=os.path.join(folder_path1,filename)
                tara_api_instance=self.__class__.Create_And_View.loadCase(rf"{file_path}")
                self.add_study_unit_using_inch_file(tara_api_instance)
                tara_api_instance.saveRawCase(caseFilePath=file_path,rawVerOut=33)
                for i in range(len(flow_gate)):
                    

                    original_tuple = stress_ids[i]

                    # Convert tuple to string
                    stress_id_convert= original_tuple[0]

                    if stress_id_convert==filename.split('.')[0]:
                        for j in range(len(flow_gate[i])):
                            file_name_new=filename.split('.')[0]
                            self.run_dfax_script(file_path,flow_gate[i][j],folder1,f"{directory2}\{folder1}\{file_name_new}-{self.split_flowgate_string(flow_gate[i][j])}.csv")
                    else:
                        print(stress_ids[i])
                        print(filename.split('.')[0])
                        print("Does not match")
                        continue
            for folder in os.listdir(directory_reversal):
                folder1=folder
                folder_path1=os.path.join(directory_reversal,folder)

                for filename in os.listdir(folder_path1):
                    file_path=os.path.join(folder_path1,filename)
                    tara_api_instance=self.__class__.Create_And_View.loadCase(rf"{file_path}")
                    self.add_study_unit_using_inch_file(tara_api_instance)
                    tara_api_instance.saveRawCase(caseFilePath=file_path,rawVerOut=33)
                    for i in range(len(flow_gate)):
                        original_tuple = stress_ids[i]
                        # Convert tuple to string
                        stress_id_convert= original_tuple[0]

                        if stress_id_convert==filename.split('.')[0]:
                                for j in range(len(flow_gate[i])):
                                    file_name_new=filename.split('.')[0]
                                    self.run_dfax_script(file_path,flow_gate[i][j],folder1,f"{directory2}\{folder1}\{file_name_new}-{self.split_flowgate_string(flow_gate[i][j])}.csv")                            
                        else:
                            continue

# if __name__=="__main__":
#     ppl=Post_Project_Loading()
#     ppl.template_dfax_report_script()








































































































