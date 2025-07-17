import pandas as pd 
import numpy as np
import os
import pyPowerGEM.pyTARA as pt 
from string import Template 
import pyPowerGEM.wrapper as tw

import ISO_NE_AUT_Folder_File_Creation_Auxiliary_File
from ISO_NE_AUT_Folder_File_Creation_Auxiliary_File import Create_Folders as cf

import ISO_NE_AUT_ALL_PATHs
from ISO_NE_AUT_ALL_PATHs import Files as f

# import ISO_NE_AUT_STEP_5_STUDY_UNIT_b
# from ISO_NE_AUT_STEP_5_STUDY_UNIT_b import Study_Unit_Dispatch

class FINAL(cf):

    # s=Study_Unit_Dispatch()
    # s.loop_secured_cases_perform_study_unit_dispatch()

    exe_path=f.json_dumps_function(f,"tara_executable")

    REL_FLOWGATES="C:\\Appl\\Python39\\ISO_NE_Automation\\Scripts\\Python Files\\Py Files ISO-NE\\ISO_NE_AUT_Parent_2\\Relevant_Flowgates_TEWK_115.csv"
    # REL_FLOWGATES=pd.DataFrame(REL_FLOWGATES_old)

    FINAL_CASES_DCCONT_REPORTS_FOLDER_PATH=cf.create_single_folder(cf, f.json_dumps_function(f,"POST_PROJECT_PARENT_FOLDER_PATH"),"FINAL_CASES_DC_CONT_REPORTS")
    # # FINAL_CASES_DCCONT_REPORTS_FOLDER_PATH=f"{f.json_dumps_function(f,'POST_PROJECT_PARENT_FOLDER_PATH')}/FINAL_CASES_DC_CONT_REPORTS"
    FINAL_CASES_SCRIPTS_PATH=cf.create_single_folder(cf, f.json_dumps_function(f,"POST_PROJECT_PARENT_FOLDER_PATH"),"FINAL_CASES_SCRIPT_FILES_PATH")
    #FINAL_CASES_DCCONT_REPORTS_FOLDER_PATH="c:\Appl\Python39\ISO_NE_Automation\Scripts\Python Files\Py Files ISO-NE\ISO_NE_AUT_Post_PJT_Parent\FINAL_CASES_DC_CONT_REPORTS"

    FINAL_CASES_PATH=os.path.join(f.json_dumps_function(f,"POST_PROJECT_PARENT_FOLDER_PATH"),'FINAL_CASES')
    
    POST_PROJECT_PATH=f.json_dumps_function(f,"POST_PROJECT_PARENT_FOLDER_PATH")

    DCCONT_SCRIPT_TEMPLATE_FILE_PATH=f"{f.json_dumps_function(f,'Pre_Project_Parent_Folder_Path')}\\{f.json_dumps_function(f,'STEP_1_Script_Template_Name(.txt)')}"

    def run_script(self,script_file):
        tara=tw.powerGemExe(exeFilePath=self.__class__.exe_path)
        tara.runScript(scriptFilePath=script_file)

    def create_DCCONT_Report(self):
        for filename in os.listdir(self.__class__.FINAL_CASES_PATH):
            dccont_name=filename.split('.')[0]
            script_name=filename.split('.')[0]
            final_case_path=os.path.join(self.__class__.FINAL_CASES_PATH,filename)
            # flow_gate_list=filename.split("-")[1]
            # flow_gate_list=flow_gate_list.split('.')[0]
            # flow_gate_list=flow_gate_list.split("_")
            # flow_gate_name=f"branch from bus {flow_gate_list[0]} to bus {flow_gate_list[1]} ckt {flow_gate_list[3]} in contingency number {flow_gate_list[4]}"
            template_fh=self.__class__.DCCONT_SCRIPT_TEMPLATE_FILE_PATH
            template_fh = open(template_fh, "r")
            script_string=template_fh.read()
            script_template=Template(script_string) 
            config_dict={
                "Input_File_Full_Path":f"{final_case_path}",
                "Contingency_File_Full_Path":f"{f.json_dumps_function(f,'auxiliary_files_folder_path')}\{f.json_dumps_function(f,'Con_File_Name')}",
                "Subsystem_File_Full_Path":f"{f.json_dumps_function(f,'auxiliary_files_folder_path')}\{f.json_dumps_function(f,'Subsystem_File_Name')}",
                "Monitor_File_Full_Path":f"{f.json_dumps_function(f,'auxiliary_files_folder_path')}\{f.json_dumps_function(f,'Mon_File_Name')}",
                "Sending_Bus": f"{f.json_dumps_function(f,'POST_PROJECT_DISPATCH_REFERENCE')}",
                "Reference_Subsystem":f"{f.json_dumps_function(f,'POST_PROJECT_DISPATCH_GENS')}",
                "DCCONT_OUTPUT_FILE_FULL_PATH":f"{self.__class__.FINAL_CASES_DCCONT_REPORTS_FOLDER_PATH}\{dccont_name}.csv"
            }
            new_script=script_template.substitute(config_dict) 
            NewFile=os.path.join(f"{self.__class__.FINAL_CASES_SCRIPTS_PATH}",f"{script_name}.txt")
            output_fh = open(NewFile, "w")
            output_fh.write(new_script)
            self.run_script(NewFile)

    def create_dataframe_limiting(self,pre_project_file,post_project_file_path):
        self.create_DCCONT_Report()
        folder_path=self.__class__.FINAL_CASES_DCCONT_REPORTS_FOLDER_PATH
        pre_project_dataframe=pd.read_csv(pre_project_file)
        pre_project_dataframe.insert(9,'Pmax Restricted',0)
        pre_project_dataframe.insert(8,'Study Loading',0)
        pre_project_dataframe.insert(1,'Stress Monitored Facility',0)
        pre_project_dataframe['Load Deliverability']=0
    
        pre_project_dataframe['Rate A']=0
        pre_project_dataframe['Rate B']=0
        pre_project_dataframe['Loading Delta']=0

        post_project_dataframe=pre_project_dataframe
        for filename in os.listdir(folder_path): #looping the DCCONT reports 
            print("The SAGA continues")


            file_path=os.path.join(folder_path,filename)
            dccont_report=pd.read_csv(file_path, skiprows=9)
            dccont_report=pd.DataFrame(dccont_report)
#LOAD DELIVERABILITY
            load_del=filename.split('.')[0]
            load_del=load_del.split('-')[0]

#STRESS ID
            stress_id_cont=filename.split('.')[0]
            stress_id=stress_id_cont.split('-')[1]


            limiting_fg=filename.split('.')[0]
            limiting_flowgate=limiting_fg.split('-')[2]

            
            limiting_flowgate_list=limiting_flowgate.split('_')
            limiting_sending_bus=limiting_flowgate_list[0]
            limiting_terminal_bus=limiting_flowgate_list[1]
            limiting_ckt_id=limiting_flowgate_list[2]
            limiting_ckt_id=limiting_ckt_id.strip()
            limiting_cont=limiting_flowgate_list[3]
        
            post_project_dataframe['CKT'] = post_project_dataframe['CKT'].astype(str)
                        # post_project_dataframe['Stress Monitored Facility']=post_project_dataframe['Stress Monitored Facility'].astype(str)
            limiting_sending_bus=int(limiting_sending_bus)
            limiting_terminal_bus=int(limiting_terminal_bus)
            limiting_cont=int(limiting_cont)

            stress_id_list=stress_id.split('_')

            stress_sending_bus=stress_id_list[1]

            stress_terminal_bus=stress_id_list[2]

            stress_id_ckt=stress_id_list[4]
            #strip
            stress_id_ckt=stress_id_ckt.strip()

            stress_id_cont=stress_id_list[5]

            #strip
            # # dccont_report['CKT']=dccont_report['CKT'].str.strip()
            # try:
            #     dccont_report['CKT']=dccont_report['CKT'].str.strip()
            # except AttributeError:
            #     continue 
                

            stress_match=dccont_report.loc[
                (dccont_report['Fr Bus']==int(stress_sending_bus))&
                (dccont_report['To Bus']==int(stress_terminal_bus))&
                (dccont_report['CKT']==stress_id_ckt)&
                (dccont_report['Cont ID']==int(stress_id_cont))
            ]
            #strip
            post_project_dataframe['CKT']==post_project_dataframe['CKT'].str.strip()

            # monitored_facility=stress_match[' Monitored Facility                                   '].values[0]

            #strips
            stress_id=stress_id.strip()

            matching_row = post_project_dataframe.loc[
                (post_project_dataframe['Stress_ID'] ==stress_id ) &
                (post_project_dataframe['Fr Bus'] == limiting_sending_bus) &
                (post_project_dataframe['To Bus'] == limiting_terminal_bus) &
                (post_project_dataframe['CKT'] == limiting_ckt_id) &
                (post_project_dataframe['Contingency_Number'] == limiting_cont)
            ]
            print(matching_row)
            dccont_report['CKT']=dccont_report['CKT'].astype(str)
            dccont_report['CKT']=dccont_report['CKT'].str.strip()
            filtered_dccont_report = dccont_report[dccont_report['CKT'] == limiting_ckt_id]            
            filtered_dccont_report2=filtered_dccont_report[filtered_dccont_report['Fr Bus'].astype(int) == limiting_sending_bus]
            filtered_dccont_report3=filtered_dccont_report2[filtered_dccont_report2['To Bus'].astype(int)==limiting_terminal_bus]
            filtered_dccont_report4=filtered_dccont_report3[filtered_dccont_report3['Cont ID'].astype(int)==limiting_cont]

            print(limiting_sending_bus)
            print(filtered_dccont_report)

            try:
                post_project_loading=filtered_dccont_report4['Final DC %Loading'].values[0]
                rate_A=filtered_dccont_report4['Rate Base (MVA)'].values[0]
                rate_B=filtered_dccont_report4['Rate Cont (MVA)'].values[0]
            except IndexError:
                continue


            post_project_dataframe.loc[matching_row.index,'Study Loading']=post_project_loading
            post_project_dataframe.loc[matching_row.index,'Rate A']=rate_A
            post_project_dataframe.loc[matching_row.index,'Rate B']=rate_B
            # post_project_dataframe.loc[matching_row.index,'Stress Monitored Facility']=monitored_facility

            print(matching_row['DC Loading'].values[0])
            if limiting_cont==0:
                threshold=float(rate_A)-matching_row['DC Loading']*(.01)*(float(rate_A))
                print(threshold)
                if (threshold>0).any():
                    post_project_dataframe.loc[matching_row.index,'Pmax Restricted']=threshold
            else: 
                threshold=float(rate_B)-matching_row['DC Loading']*(.01)*(float(rate_B))
                if (threshold>0).any():
                    post_project_dataframe.loc[matching_row.index,'Pmax Restricted']=threshold
            try:
                post_project_dataframe.loc[matching_row.index,'Loading Delta']=post_project_loading-post_project_dataframe.loc[matching_row.index,'DC Loading']
            except IndexError as e:
                print(f"Mon Facility can't be written: {e}")
            print("The SAGA continues")

#LOAD DELIVERABILITY
            post_project_dataframe.loc[matching_row.index,'Load Deliverability']=load_del

        # post_project_dataframe.rename(columns={'DC Loading','Reference Loading'},inp#ace=True)

        post_project_dataframe.index=post_project_dataframe.index+1

        post_project_dataframe.to_csv(post_project_file_path,index=True, index_label='Index')
        

if __name__=="__main__":
    final=FINAL()
    final.create_dataframe_limiting(final.REL_FLOWGATES, f"{final.POST_PROJECT_PATH}/Final_Loadings.csv")
