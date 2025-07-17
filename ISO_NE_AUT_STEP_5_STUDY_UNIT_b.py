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
# #     # Create_And_View=Create_And_View()
    #     ppl=ppl()
    # ppl.template_dfax_report_script()
class Study_Unit_Dispatch(cf,f):

    Create_And_View=Create_And_View()
    ppl=ppl()
    ppl.template_dfax_report_script()
    #create class variables for the study unit level and the inch file path for the output
    STUDY_UNIT_MW_LEVEL=f.json_dumps_function(f,'STUDY_UNIT_CRIS_LEVEL')#json template call
    STUDY_UNIT_INCH_FILE_PATH=f.json_dumps_function(f,'STUDY_UNIT_INCH_FILE')#json template call

    #Folders to loop through containingth esecured stressed cases both flow direction and reversal 
    SECURED_CASES_SUB_PARENT_PATH=f"{f.json_dumps_function(f,'Pre_Project_Parent_Folder_Path')}\{'SECURED_CASES'}"#json template call
    SECURED_CASES_SUB_PARENT_PATH_REVERSAL=f"{f.json_dumps_function(f,'Pre_Project_Parent_Folder_Path')}\{'SECURED_CASES_REVERSAL'}"#json template call


    FINAL_CASE_FOLDER=cf.create_single_folder(cf,f.json_dumps_function(f,'POST_PROJECT_PARENT_FOLDER_PATH'),'FINAL_CASES')#Helper function 0
    FLOW_GATE_DFAX_REPORTS_SUB_PARENT_PATH=f"{f.json_dumps_function(f,'POST_PROJECT_PARENT_FOLDER_PATH')}\{'FLOW_GATE_DFAX_REPORTS'}"#json template call
    FINAL_SECURED_WITH_STUDY_UNIT_DISPATCH_FILES=f"{f.json_dumps_function(f,'POST_PROJECT_PARENT_FOLDER_PATH')}\{'FINAL_CASES'}"#json template call

    def __init__(self):
        pass


    #AC Case 1
    #Objective Function 1
    def add_study_unit_using_inch_file(self,tara_api_instance):
        tara_api_instance.applyInchFile(inchFilePath=self.__class__.STUDY_UNIT_INCH_FILE_PATH)#tara API function

    #AC Case 2
    def cluster_mw_dispatch(self,cluster_mw,dataframe,instance):
        if cluster_mw>80:
            cluster_mw_count=80
            self.create_Harmer_dispatch(dataframe,instance,cluster_mw_count)
            instance.solveCase()
            cluster_mw_difference=cluster_mw-cluster_mw_count
            self.cluster_mw_dispatch(cluster_mw_difference,dataframe,instance)
        else:
            self.create_Harmer_dispatch(dataframe,instance,cluster_mw)
            instance.solveCase()
            if instance.isACSolutionConverged==True:
                print('TRUE')
            else:
                print("FALSE")
    #Implementation Function 2
    #this function bring together the project addition and project dispatch functions into one function that loops through all the secured, strssed cases and applies these functions. 
    #This generates new, final post project secured cases from which we can then extract the relevant loading for the mon/con pair. 
    def loop_secured_cases_perform_study_unit_dispatch(self):
        for folder in os.listdir(self.__class__.SECURED_CASES_SUB_PARENT_PATH):
            folder_path=os.path.join(self.__class__.SECURED_CASES_SUB_PARENT_PATH,folder)
            for filename in os.listdir(folder_path):
                file_full_path=os.path.join(folder_path,filename)
                tara_api_instance=self.__class__.Create_And_View.loadCase(rf"{file_full_path}")
                self.dispatch_for_study_unit(file_full_path,filename,tara_api_instance)

        for folder in os.listdir(self.__class__.SECURED_CASES_SUB_PARENT_PATH_REVERSAL):
            folder_path1=os.path.join(self.__class__.SECURED_CASES_SUB_PARENT_PATH_REVERSAL,folder)
            for filename in os.listdir(folder_path1):
                file_full_path=os.path.join(folder_path1,filename)
                tara_api_instance=self.__class__.Create_And_View.loadCase(rf"{file_full_path}")
                self.dispatch_for_study_unit(file_full_path,filename,tara_api_instance)
                
    #Implementation Function 1
    def dispatch_for_study_unit(self,secured_case_file_path,secured_file,tara_api_instance):
        folder_path2=self.__class__.FLOW_GATE_DFAX_REPORTS_SUB_PARENT_PATH#class variable for the dfax reports, post stressing, cases
        secured_file_sending_bus =secured_file.split('_')[1]
        secured_file_terminal_bus =secured_file.split('_')[2]
        secured_file_ckt_id =secured_file.split('_')[4]
        secured_file_contingency_number =secured_file.split('_')[5]
        secured_file_contingency_number=secured_file_contingency_number.split('.')[0]

        # deliverability_type=[]

        for folder_name in os.listdir(folder_path2):
            print(secured_file_contingency_number,secured_file_sending_bus,secured_file_terminal_bus,secured_file_ckt_id)
            
            folder_prefix=folder_name.split(" ")[0]
            #folder_ckt_id=folder_ckt_id.replace(" ", "")
            if folder_prefix.split("_")[0]==secured_file_sending_bus and folder_prefix.split('_')[1]==secured_file_terminal_bus and folder_prefix.split('_')[2]==secured_file_ckt_id:
                print("YESSS")
                folder_path3 =os.path.join(folder_path2,folder_name)
                for filename in os.listdir(folder_path3):
                    filename_list=filename.split('-')[0]
                    filename_list2=filename.split('-')[1]
                    filename_list2=filename_list2.split('.')[0]
                    filename_list2=filename_list2.split("_")
                    if filename_list.split('_')[5]==secured_file_contingency_number:
                        print(filename_list.split('_')[5])
                        # self.add_study_unit_using_inch_file(tara_api_instance) #OF1
                        entire_dataframe=self.__class__.Create_And_View.create_dataframe(folder_path3,filename)#Helper Function 1
                        entire_dataframe['Bus Name    ']=entire_dataframe['Bus Name    '].str.strip()
                        print(entire_dataframe)
                        ##CREATE CLUSTER HARMERS
                        print(entire_dataframe['Bus Name    '][0].split('_')) 
                        print(entire_dataframe['Bus Name    '][0])
                        
                        cluster_harmer_dataframe=entire_dataframe[entire_dataframe['Bus Name    '].isin(f.json_dumps_function(f,'CL_LIST'))]                                                      
                        cluster_harmer_dataframe=cluster_harmer_dataframe[cluster_harmer_dataframe[' Dfax']>=0.0001]
                        cluster_harmer_dataframe=cluster_harmer_dataframe.reset_index(drop=True)
                        cluster_mw=cluster_harmer_dataframe['    Pmax'].sum()

                        cluster_mw_impact=cluster_harmer_dataframe[' MaxGenImp']
                        # print(cluster_harmer_dataframe.head(10))
                        secured_file=secured_file.split('.')[0]
                        #tara_api_instance.saveRawCase(caseFilePath=f"{self.__class__.FINAL_SECURED_WITH_STUDY_UNIT_DISPATCH_FILES}\{secured_file}-{filename_list2[0]}_{filename_list2[1]}_{filename_list2[3]}_{filename_list2[4]}.raw",rawVerOut=33)#tara API function
                        #tara_api_instance=self.__class__.Create_And_View.loadCase(rf"{self.__class__.FINAL_SECURED_WITH_STUDY_UNIT_DISPATCH_FILES}\{secured_file}-{filename_list2[0]}_{filename_list2[1]}_{filename_list2[3]}_{filename_list2[4]}.raw")
                        #CREATE CLUSTER HARMERS DISPATCH
                        self.cluster_mw_dispatch(cluster_mw,cluster_harmer_dataframe,tara_api_instance)

                        resource_dataframe=entire_dataframe.sort_values(by=' Dfax')#pyfunc
                        resource_dataframe=resource_dataframe[resource_dataframe[' Dfax']<=0.03]
                        resource_dataframe=resource_dataframe[resource_dataframe['    Pgen']!=0]
                        resource_dataframe=resource_dataframe[~resource_dataframe['Bus Name    '].isin(f.json_dumps_function(f,'CL_LIST'))]

                        resource_dataframe.reset_index(drop=True, inplace=True)#pyfunc
                        # secure_file_name_output=secured_file.replace("SCRD_","").split('.')[0]#pyfunc
                        result=self.create_Balanced_Helper_dispatch(f"{self.__class__.FINAL_SECURED_WITH_STUDY_UNIT_DISPATCH_FILES}\{secured_file}-{filename_list2[0]}-{filename_list2[1]}_{filename_list2[3]}_{filename_list2[4]}.raw",resource_dataframe,cluster_mw,tara_api_instance)#Objective Function outside class
                        if result is not None:
                            # gen_count
                            imbalance=result
                            tara_api_instance.scaleLoad(1,f.json_dumps_function(f,"LOAD_SCALE_SUBSYSTEM"),2,pValue=imbalance)
                                                                               
                            tara_api_instance.saveRawCase(caseFilePath=f"{self.__class__.FINAL_SECURED_WITH_STUDY_UNIT_DISPATCH_FILES}\{imbalance}-{secured_file}-{filename_list2[0]}_{filename_list2[1]}_{filename_list2[3]}_{filename_list2[4]}.raw",rawVerOut=33)#tara API function
                            # tara_api_instance.restoreCase()
                            # rint(gen_count)
                        else:
                        # deliverability_type.append(imbalance)
                            tara_api_instance.saveRawCase(caseFilePath=f"{self.__class__.FINAL_SECURED_WITH_STUDY_UNIT_DISPATCH_FILES}\\NOSCALE-{secured_file}-{filename_list2[0]}_{filename_list2[1]}_{filename_list2[3]}_{filename_list2[4]}.raw",rawVerOut=33)
                            # tara_api_instance.restoreCase()
                            # #tara API function
                            print(result)
                    else:
                        print('no')
            else:
                continue


                #Implementation Function 1
    #Objective Function 2
    #This function finds the lowest available helpers to highest available helpers to dispatch (remove) against the study unit until the MW injected by the study unit are balanced
    #by the MW removed from the case 
    def create_Harmer_dispatch(self,dataframe,tara_api_instance,Harmer_gen):
        Harmer_Gen_Count=[]
        if Harmer_gen!=0:
            for i in range(len(dataframe)):
                Harmer_Gen_Bus=dataframe.loc[i,'  Bus#'].tolist()
                Harmer_Generator_Bus_Data=tara_api_instance.getBus(busNum=Harmer_Gen_Bus)
                Harmer_Bus_Equipment=tara_api_instance.getBusEquipment(busObj=Harmer_Generator_Bus_Data)
                Harmer_Bus_Gen_IDs=Harmer_Bus_Equipment.iGens
                if len(Harmer_Bus_Gen_IDs)!=1:
                    k=0
                    while k<=len(Harmer_Bus_Gen_IDs)-1:
                        Harmer_Generator_Instance=tara_api_instance.getGenerator(iGen=Harmer_Bus_Gen_IDs[k])
                        # Generator_ID=Harmer_Generator_Instance.id

                        # if Generator_ID in f.json_dumps_function(f,'CL_LIST'):
                        Harmer_Gen_Count.append(Harmer_Generator_Instance.pGen)
                        Harmer_Generator_Instance.pGen=Harmer_Generator_Instance.pMax
                        Harmer_Generator_Instance.status=1
                        tara_api_instance.updateCase(equipObj=Harmer_Generator_Instance)
                        k+=1
                else:
                        Harmer_Generator_Instance=tara_api_instance.getGenerator(iGen=Harmer_Bus_Gen_IDs[0])
                        # Generator_ID=Harmer_Generator_Instance.id
                        # if Generator_ID in f.json_dumps_function(f,'CL_LIST'):
                        Harmer_Gen_Count.append(Harmer_Generator_Instance.pGen)
                        Harmer_Generator_Instance.pGen=Harmer_Generator_Instance.pMax
                        Harmer_Generator_Instance.status=1
                        tara_api_instance.updateCase(equipObj=Harmer_Generator_Instance)
        else:
            return

    def create_Balanced_Helper_dispatch(self,PATH,dataframe,Harmer_gen,tara_api_instance):
        Helper_Buses_Dispatch_Running_Count=[]
        delta=0
        Gen_Count=0
        if Harmer_gen!=0:
            for i in range(len(dataframe)-1):
                print(sum(Helper_Buses_Dispatch_Running_Count))
                print(Harmer_gen-sum(Helper_Buses_Dispatch_Running_Count))
                if sum(Helper_Buses_Dispatch_Running_Count)<Harmer_gen:
                    Helper_Bus=dataframe.loc[i,'  Bus#'].tolist()
                    Helper_Bus_Object=tara_api_instance.getBus(busNum=Helper_Bus)
                    Helper_Bus_Equipment_Object=tara_api_instance.getBusEquipment(busObj=Helper_Bus_Object)
                    Helper_Bus_Gen_ID=Helper_Bus_Equipment_Object.iGens
                    delta=Harmer_gen-sum(Helper_Buses_Dispatch_Running_Count)
                    if len(Helper_Bus_Gen_ID)!=1:
                        k=0
                        while k<=len(Helper_Bus_Gen_ID)-1:
                            Helper_Generator_Object=tara_api_instance.getGenerator(iGen=Helper_Bus_Gen_ID[k])
                            status=Helper_Generator_Object.status
                            if delta>=Helper_Generator_Object.pGen-0 and status==1:
                                Helper_Buses_Dispatch_Running_Count.append(Helper_Generator_Object.pGen)
                                Helper_Generator_Object.pGen=0
                                tara_api_instance.updateCase(equipObj=Helper_Generator_Object)
                                Gen_Count+=1
                                                             #,outFile=f"{PATH}_{i}{k}.INCH")
                            elif status==1:
                                current_gen=Helper_Generator_Object.pGen
                                dispatch=current_gen-delta
                                Helper_Buses_Dispatch_Running_Count.append(delta)
                                Helper_Generator_Object.pGen=dispatch
                                tara_api_instance.updateCase(equipObj=Helper_Generator_Object)
                                Gen_Count+=1
                                                             #,outFile=f"{PATH}_{i}{k}.INCH")
                            k+=1
                            delta=Harmer_gen-sum(Helper_Buses_Dispatch_Running_Count)
                    else:
                        Helper_Generator_Object=tara_api_instance.getGenerator(iGen=Helper_Bus_Gen_ID[0])
                        status=Helper_Generator_Object.status
                        if delta>=Helper_Generator_Object.pGen and status==1:
                            Helper_Buses_Dispatch_Running_Count.append(Helper_Generator_Object.pGen)
                            Helper_Generator_Object.pGen=0
                            tara_api_instance.updateCase(equipObj=Helper_Generator_Object)
                            Gen_Count+=1
                                                         #,outFile=f"{PATH}_{i}.INCH")
                        elif status==1:
                            dispatch=Helper_Generator_Object.pGen-delta
                            Helper_Buses_Dispatch_Running_Count.append(delta)
                            Helper_Generator_Object.pGen=dispatch
                            tara_api_instance.updateCase(equipObj=Helper_Generator_Object)
                            Gen_Count+=1
                            #),outFile=f"{PATH}_{i}.INCH")
                else:
                    return
            if sum(Helper_Buses_Dispatch_Running_Count)<Harmer_gen:
               imbalance= round(Harmer_gen-sum(Helper_Buses_Dispatch_Running_Count))
               return imbalance
        else:
            return 

if __name__=="__main__":
    s=Study_Unit_Dispatch()
    s.loop_secured_cases_perform_study_unit_dispatch()