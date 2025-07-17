import pandas as pd
import numpy as np
import os
import pyPowerGEM.pyTARA as pt 
from string import Template 
import pyPowerGEM.wrapper as tw
import ISO_NE_AUT_Folder_File_Creation_Auxiliary_File
from ISO_NE_AUT_Folder_File_Creation_Auxiliary_File import Create_Folders as cf
import ISO_NE_AUT_STEP_3_Stressing  
from ISO_NE_AUT_STEP_3_Stressing import Create_And_View
import ISO_NE_AUT_ALL_PATHs
from ISO_NE_AUT_ALL_PATHs import Files as f
import ISO_NE_AUT_STEP_5_STUDY_UNIT
from ISO_NE_AUT_STEP_5_STUDY_UNIT import Post_Project_Loading as ppl

class Study_Unit_Dispatch(cf,f):

    # Create_And_View=Create_And_View()
    # ppl=ppl()
    # ppl.template_dfax_report_script()
    #create class variables for the study unit level and the inch file path for the output
    STUDY_UNIT_MW_LEVEL=f.json_dumps_function(f,'STUDY_UNIT_CRIS_LEVEL')#json template call
    STUDY_UNIT_INCH_FILE_PATH=f.json_dumps_function(f,'STUDY_UNIT_INCH_FILE')#json template call

    #Folders to loop through containingth esecured stressed cases both flow direction and reversal 
    SECURED_CASES_SUB_PARENT_PATH=f"{f.json_dumps_function(f,'Pre_Project_Parent_Folder_Path')}\{'SECURED_CASES'}"#json template call
    SECURED_CASES_SUB_PARENT_PATH_REVERSAL=f"{f.json_dumps_function(f,'Pre_Project_Parent_Folder_Path')}\{'SECURED_CASES_REVERSAL'}"#json template call


    FINAL_CASE_FOLDER=cf.create_single_folder(cf,f.json_dumps_function(f,'POST_PROJECT_PARENT_FOLDER_PATH'),'FINAL_CASES')#Helper function 0
    FLOW_GATE_DFAX_REPORTS_SUB_PARENT_PATH=f"{f.json_dumps_function(f,'POST_PROJECT_PARENT_FOLDER_PATH')}\{'FLOW_GATE_DFAX_REPORTS'}"#json template call
    FINAL_SECURED_WITH_STUDY_UNIT_DISPATCH_FILES=f"{f.json_dumps_function(f,'POST_PROJECT_PARENT_FOLDER_PATH')}\{'FINAL_CASES'}"#json template call

    REL_FLOWGATES=f.json_dumps_function(f,"PRE_PROJECT_LOADINGS_CSV_FILE_PATH")

    def __init__(self):
        pass  
    def create_dataframe(self,dfax_sub_parent_path,dfax_filename):#dfax_sub parent path not accurate
        #Need a function that clean the dataset so it can be looped when stressings
        dfax_file_path=rf"{os.path.join(dfax_sub_parent_path,dfax_filename)}"
        dfax_file=pd.read_csv(dfax_file_path, skiprows=15)
        DataFrame=pd.DataFrame(dfax_file)
        DataFrame.drop(DataFrame.columns[-3:], axis=1, inplace=True)
        return DataFrame
    #Implementation Function 1
    def dispatch_for_study_unit(self):
        folder_path2=self.__class__.FLOW_GATE_DFAX_REPORTS_SUB_PARENT_PATH#class variable for the dfax reports, post stressing, cases
        post_project_dataframe=pd.read_csv(self.__class__.REL_FLOWGATES)
        post_project_dataframe.insert(9,'Study Loading',0)
        for folder_name in os.listdir(folder_path2):
            folder_prefix=folder_name.split("_")[0]
        

            folder_path3 =os.path.join(folder_path2,folder_name)
            for filename in os.listdir(folder_path3):
                
                filename_list=filename.split('-')[0]

                filename_list2=filename.split('-')[1]
                filename_list2=filename_list2.split('.')[0]
                filename_list2=filename_list2.split("_")

                #CREATE LIMITING VALUES FROM FILENAME
                stress_id=filename_list
                limiting_sending_bus=filename_list2[0]
                limiting_terminal_bus=filename_list2[1]
                limiting_ckt_id=filename_list2[3]
                limiting_cont=filename_list2[4]


                stress_id=str(stress_id)
                stress_id=stress_id.strip()
                limiting_sending_bus=int(limiting_sending_bus)
                limiting_terminal_bus=int(limiting_terminal_bus)
                limiting_ckt_id=int(limiting_ckt_id)
                limiting_cont=int(limiting_cont)

                print(stress_id)
                print(limiting_ckt_id)
                print(limiting_sending_bus)
                print(limiting_terminal_bus)

                print(type(post_project_dataframe['Stress_ID'][0]))
                print(post_project_dataframe['Fr Bus'][0])
                print(type(post_project_dataframe['To Bus'][0]))
                print(type(post_project_dataframe['CKT'][0]))
                print(type(post_project_dataframe['Contingency_Number'][0]))


                ##GET MATCHING DATAFRAME ROW FROM THE RELEVANT FLOWGATES FILE 
                matching_row = post_project_dataframe.loc[
                    (post_project_dataframe['Stress_ID'] ==stress_id ) &
                    (post_project_dataframe['Fr Bus'] == limiting_sending_bus) &
                    (post_project_dataframe['To Bus'] == limiting_terminal_bus) &
                    (post_project_dataframe['CKT'] == limiting_ckt_id) &
                    (post_project_dataframe['Contingency_Number'] == limiting_cont)
                ]
                #CREATE INITIAL DATAFRAME 
                entire_dataframe=self.create_dataframe(folder_path3,filename)#Helper Function 1
                entire_dataframe['Bus Name    ']=entire_dataframe['Bus Name    '].str.strip()
                ##CREATE CLUSTER HARMERS
                cluster_harmer_dataframe=entire_dataframe[entire_dataframe['Bus Name    '].isin(f.json_dumps_function(f,'CL_LIST'))]                                                      
                cluster_harmer_dataframe=cluster_harmer_dataframe[cluster_harmer_dataframe[' Dfax']>=0.0001]
                #ORDER CLUSTER HARMERS
                cluster_harmer_dataframe=cluster_harmer_dataframe
                cluster_harmer_dataframe=cluster_harmer_dataframe.reset_index(drop=True)

                #CALCULATE TOTAL SUMS
                cluster_mw=cluster_harmer_dataframe['    Pmax'].sum()
                cluster_mw_impact=cluster_harmer_dataframe[' MaxGenImp'].sum()


                # #CREATE DISPATCH HELPERS
                resource_dataframe=entire_dataframe.sort_values(by=' Dfax')#pyfunc
                resource_dataframe=resource_dataframe[resource_dataframe[' Dfax']<=0.03]
                resource_dataframe=resource_dataframe[resource_dataframe['    Pgen']!=0]
                resource_dataframe=resource_dataframe[~resource_dataframe['Bus Name    '].isin(f.json_dumps_function(f,'CL_LIST'))]
                resource_dataframe.reset_index(drop=True, inplace=True)#pyfunc

                ##RATE INSERTION
                if matching_row['Contingency_Number'].values[0]==0:
                    rate=matching_row['Rate A']
                else:
                    rate=matching_row['Rate B']

                #RUN EXECUTION SCRIPT AND CREATE FINAL LOADINGS DATAFRAME
                post_project_dataframe=self.execution(cluster_harmer_dataframe,rate,entire_dataframe,matching_row,post_project_dataframe)

                helper_mw1=self.create_Balanced_Helper_dispatch(resource_dataframe,cluster_mw)
                helper_mw=helper_mw1[0]
                helper_mw=int(helper_mw)

                post_project_dataframe.loc[matching_row.index,'Study Loading']=matching_row['Reference Loading']+((cluster_mw_impact+abs(helper_mw))/rate)*100
                post_project_dataframe.loc[matching_row.index,'Harmer Impact']=cluster_mw_impact
                post_project_dataframe.loc[matching_row.index,'Helper Impact']=helper_mw
                post_project_dataframe.loc[matching_row.index,'MW to Load']=helper_mw1[1]

                ref=float(matching_row['Reference Loading'].values[0])
                rate=float(rate)

                if ref*(.01)*rate < rate:
                    post_project_dataframe.loc[matching_row.index,'Pmax Restricted']=rate-ref*(.01)*rate
                else:
                    post_project_dataframe.loc[matching_row.index,'Pmax Restricted']=0

        post_project_dataframe.to_csv(os.path.join(self.json_dumps_function("POST_PROJECT_PARENT_FOLDER_PATH"),'Final Loadings_2.csv'),index=True, index_label='Index')
    def execution(self,cluster_harmer_dataframe,rate,resource_dataframe,matching_row,post_project_dataframe):
            

                for i in range(len(cluster_harmer_dataframe)):
                    cluster_harmer_mw=cluster_harmer_dataframe['    Pmax'][i]
                    cluster_mw_impact=cluster_harmer_dataframe[' MaxGenImp'][i]
                    helper_mw1=self.create_Balanced_Helper_dispatch(resource_dataframe,cluster_harmer_mw)
                    helper_mw=helper_mw1[0]
                    #CLUSTER HARMER NAMES
                    cluster_harmer_name=f"{cluster_harmer_dataframe['  Bus#']}_{cluster_harmer_dataframe['Bus Name    ']}"
                    #TALLY INDIVIDUAL IMPACT 
                    total_impact=cluster_mw_impact+abs(helper_mw)
                    loading=(total_impact/rate)*100
                    post_project_dataframe.loc[matching_row.index,f"{cluster_harmer_name}"]=loading
                return post_project_dataframe

    def create_Balanced_Helper_dispatch(self,dataframe,Harmer_gen):
        Helper_Buses_Dispatch_Running_Count=[]
        helper_impacts_list=[]
        delta=0
        Gen_Count=0
        if Harmer_gen!=0:
            i=0
            while i < len(dataframe) and sum(Helper_Buses_Dispatch_Running_Count)<Harmer_gen:
                new_gen=dataframe['    Pgen'][i]
                print(i)
                print(new_gen)
                new_impact=abs(dataframe[' Dfax'][i]*new_gen)
                print(new_impact)
                if Harmer_gen-sum(Helper_Buses_Dispatch_Running_Count)>new_gen:
                    helper_impacts_list.append(new_impact)
                    Helper_Buses_Dispatch_Running_Count.append(new_gen)
                    i+=1
        
                elif Harmer_gen-sum(Helper_Buses_Dispatch_Running_Count) == 0: 
                    print(sum(helper_impacts_list))
                    print(sum(Helper_Buses_Dispatch_Running_Count))
                    print(Harmer_gen)
                    return [sum(helper_impacts_list),Harmer_gen-sum(Helper_Buses_Dispatch_Running_Count)]
                else:
                    Helper_Buses_Dispatch_Running_Count.append(Harmer_gen-sum(Helper_Buses_Dispatch_Running_Count))
                    new_impact_2=(Harmer_gen-sum(Helper_Buses_Dispatch_Running_Count))*dataframe[' Dfax'][i]
                    helper_impacts_list.append(new_impact_2)
                    print(sum(helper_impacts_list))
                    print(sum(Helper_Buses_Dispatch_Running_Count))
                    print(Harmer_gen)
                    i+=1
                    # return sum(helper_impacts_list)
    
        if Harmer_gen-sum(Helper_Buses_Dispatch_Running_Count)==0:
            print("BALANCE")
        else:
            print("LOAD_DEL")
        return [sum(helper_impacts_list), Harmer_gen-sum(Helper_Buses_Dispatch_Running_Count)]

if __name__=="__main__":
    s=Study_Unit_Dispatch()
    s.dispatch_for_study_unit()