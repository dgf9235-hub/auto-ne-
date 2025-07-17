import pandas as pd
import numpy as np
import pyPowerGEM.pyTARA as pt 
import os 
import gc
# import ISO_NE_AUT_STEP_2
# from ISO_NE_AUT_STEP_2 import Create_Flow_Gate_Tuple
#All Imports necessary for this python file
import ISO_NE_AUT_ALL_PATHs
from ISO_NE_AUT_ALL_PATHs import Files as f
#Import of the Python Files that will write the paths specified in the ISO_NE_AUT_PATHs .jsonc file
# import ISO_NE_AUT_STEP_2
# from ISO_NE_AUT_STEP_2 import Create_Flow_Gate_Tuple
#need function to pull all string names from the directory where the DFAX files are written 
# (['  Bus#', 'Bus Name    ', 'Volt', 'Area', 'Zone', '    Pgen',
#        '    Pmax', '   Pload', ' Dfax', ' GenType', ' CurGenImp',
#        ' MaxGenImp'],
#FOR WHEN P GEN HELPERS TOTAL IS LESS THAN P GEN HARMERS TOTAL  
    ##STATUS CHANGE WILL ALWAYS BE OFF, Helper Gen Total is less than Harmer Gen so ALL WILL BE TURNED OFF
class Create_And_View(f):
   #c=Create_Flow_Gate_Tuple()
   #c.execute_all('SCRIPTS','SCRIPTS_REVERSAL','STRESSED_CASES','STRESSED_CASES_REVERSAL','DFAX_REPORTS','DFAX_REPORTS_REVERSAL','SCRD_SCRIPTS','SCRD_SCRIPTS_REVERSAL','SECURED_CASES','SECURED_CASES_REVERSAL','ISO_NE_GENs','ISO_NE_Load')
    #define the a class variable that can be called explicitly, also is independent of the instantiation of the class because we don't want need to ever change the dll path
    dll_File_Path=f.json_dumps_function(f,"Tara_DLL_Path")
    #USER DEFINED PATH TO DLL, CAN BE ADJUSTED IN THE CLS METHODS
    aux_path= f.json_dumps_function(f,"auxiliary_files_folder_path")
    base_case=f.json_dumps_function(f,"Base Case")
    base_case_path=os.path.join(aux_path,base_case)
    DFAX_REPORTS_SUB_PARENT_FOLDER_PATH=f"{f.json_dumps_function(f,'Pre_Project_Parent_Folder_Path')}\DFAX_REPORTS"
    DFAX_REPORTS_SUB_PARENT_FOLDER_PATH_REVERSAL=f"{f.json_dumps_function(f,'Pre_Project_Parent_Folder_Path')}\DFAX_REPORTS_REVERSAL"
    MONITORED_ELEMENT_STRESSED_CASES_SUB_PARENT_FOLDER_PATH=f"{f.json_dumps_function(f,'Pre_Project_Parent_Folder_Path')}\STRESSED_CASES"
    MONITORED_ELEMENT_STRESSED_CASES_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL=f"{f.json_dumps_function(f,'Pre_Project_Parent_Folder_Path')}\STRESSED_CASES_REVERSAL"
    @classmethod
    def set_raw_case(cls,new_raw_file_path):
        cls.base_case_path=new_raw_file_path
    @classmethod
    def set_dll_file_path(cls,new_dll_file_path):
        cls.dll_File_Path=new_dll_file_path
    def create_dataframe(self,dfax_sub_parent_path,dfax_filename):#dfax_sub parent path not accurate
        #Need a function that clean the dataset so it can be looped when stressings
        dfax_file_path=rf"{os.path.join(dfax_sub_parent_path,dfax_filename)}"
        dfax_file=pd.read_csv(dfax_file_path, skiprows=15)
        DataFrame=pd.DataFrame(dfax_file)
        DataFrame.drop(DataFrame.columns[-3:], axis=1, inplace=True)
        return DataFrame
    def negative_and_globals_dfax_dataframe_for_helper_gen_SORTED(self,DataFrame,reversal):
        #creates pandas dataframe withonly negative dfaxes and status=1,but SORTsED
        if reversal=='Reversal':
            negative_globals_dfax_dataframe = DataFrame[(DataFrame[' Dfax'] < 0.0) & (DataFrame['    Pgen']!=DataFrame['    Pmax'])]
            negative_globals_dfax_dataframe=negative_globals_dfax_dataframe.sort_values(by=' Dfax')
            negative_globals_dfax_dataframe.reset_index(drop=True, inplace=True)
        elif reversal=='No_Reversal':
            negative_globals_dfax_dataframe = DataFrame[(DataFrame[' Dfax'] < 0.02) & (DataFrame['    Pgen']!=0)]
            negative_globals_dfax_dataframe=negative_globals_dfax_dataframe.sort_values(by=' Dfax')
            negative_globals_dfax_dataframe.reset_index(drop=True, inplace=True)
        print(negative_globals_dfax_dataframe)
        return negative_globals_dfax_dataframe
    #SORTED DFAX FOR ALL HARMERS ON AND OFF
    def harmer_dispatch_dfax_dataframe_for_harmer_gen_SORTED(self,DataFrame,reversal):
        harmer_dispatch_dfax_dataframe = DataFrame[DataFrame[' Dfax'] > 0.03]
        if reversal=='Reversal':
            harmer_dispatch_dfax_dataframe =harmer_dispatch_dfax_dataframe[(harmer_dispatch_dfax_dataframe['    Pgen'] != 0)]
            harmer_dispatch_dfax_dataframe=harmer_dispatch_dfax_dataframe.sort_values(by=' Dfax',ascending=False)
            harmer_dispatch_dfax_dataframe.reset_index(drop=True, inplace=True)
        elif reversal=='No_Reversal':
            harmer_dispatch_dfax_dataframe =harmer_dispatch_dfax_dataframe[(harmer_dispatch_dfax_dataframe['    Pgen'] != harmer_dispatch_dfax_dataframe['    Pmax'])]
            harmer_dispatch_dfax_dataframe=harmer_dispatch_dfax_dataframe.sort_values(by=' Dfax',ascending=False)
            harmer_dispatch_dfax_dataframe.reset_index(drop=True, inplace=True)
        return harmer_dispatch_dfax_dataframe
    def loadCase(self,case):
        #need a function that loads the raw case so we can get and write.
        #file=os.path.join(Create_And_View.base_case_path,Create_And_View.base_case_file)
        tara = pt.taraAPI(dllFilePath=Create_And_View.dll_File_Path)
        tara.loadRawCase(caseFilePath=case, rawVer=33)
        tara.solveCase()
        return tara
    #CHECK WHICH GEN LIST TOTAL PGEN IS LOWER
    ##NEXT STEP
## 1) Put the INCH Files together in a single inch file, add a header, write a specific flowgate folder
    def execution(self,directory):
        i=0
        tara=self.loadCase(Create_And_View.base_case_path)
        stressed_cases_folders = [f for f in os.listdir(self.MONITORED_ELEMENT_STRESSED_CASES_SUB_PARENT_FOLDER_PATH) if os.path.isdir(os.path.join(self.MONITORED_ELEMENT_STRESSED_CASES_SUB_PARENT_FOLDER_PATH, f))]
        stressed_cases_folders_reversal=[f for f in os.listdir(self.MONITORED_ELEMENT_STRESSED_CASES_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL) if os.path.isdir(os.path.join(self.MONITORED_ELEMENT_STRESSED_CASES_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL, f))]

        for folder_name in os.listdir(directory):
            folder_path = os.path.join(directory, folder_name)
            for filename in os.listdir(folder_path):
            #file_path = os.path.join(directory, filename)
                if directory==self.DFAX_REPORTS_SUB_PARENT_FOLDER_PATH:
                    dataframe=self.create_dataframe(folder_path,filename)
                    negative_and_globals_dataframe=self.negative_and_globals_dfax_dataframe_for_helper_gen_SORTED(dataframe,'No_Reversal')
                    harmer_dataframe=self.harmer_dispatch_dfax_dataframe_for_harmer_gen_SORTED(dataframe,'No_Reversal')
                    stressed_case_folder_name=stressed_cases_folders[i]
                    stressed_case_folder_path=os.path.join(self.MONITORED_ELEMENT_STRESSED_CASES_SUB_PARENT_FOLDER_PATH,stressed_case_folder_name)
                    stressed_file_name=filename.split('.')[0]
                    self.gen_dispatch_capability(tara,stressed_case_folder_path,stressed_file_name,harmer_dataframe,negative_and_globals_dataframe,0.0)
                else:
                    dataframe=self.create_dataframe(folder_path,filename)
                    negative_and_globals_dataframe=self.negative_and_globals_dfax_dataframe_for_helper_gen_SORTED(dataframe,'Reversal')
                    harmer_dataframe=self.harmer_dispatch_dfax_dataframe_for_harmer_gen_SORTED(dataframe,'Reversal')
                    stressed_case_folder_name=stressed_cases_folders_reversal[i]
                    stressed_case_folder_path=os.path.join(self.MONITORED_ELEMENT_STRESSED_CASES_SUB_PARENT_FOLDER_PATH_FLOW_REVERSAL,stressed_case_folder_name)
                    stressed_file_name=filename.split('.')[0]
                    self.gen_dispatch_capability(tara,stressed_case_folder_path,stressed_file_name,negative_and_globals_dataframe,harmer_dataframe,0.0)

            i+=1
            print("stressed")
        return

    def gen_dispatch_capability(self,tara,stressed_case_folder_path,stressed_file_name,harmer_dfax,negative_globals_dfax,dispatch_correction):
        Helper_global_gen=negative_globals_dfax['    Pgen'].sum()-dispatch_correction
        #Current Helper Gen ON
        try:
            pmax_total = harmer_dfax['    Pmax'].sum()
            pgen_total = harmer_dfax['    Pgen'].sum()
            Harmer_gen = float(pmax_total - pgen_total - dispatch_correction)
            print(type(pmax_total))
            print(type(pgen_total))
            print(type(dispatch_correction))
        except ValueError as e:
            return

        #Harmer_gen=float(harmer_dfax['    Pmax'].sum())-float(harmer_dfax['    Pgen'].sum())-float(dispatch_correction)
        #current Harmer Gen ON
        #1859.0000000000002 2851.2)
        if Helper_global_gen<Harmer_gen:
            self.create_helper_dispatch(negative_globals_dfax,tara,Helper_global_gen)
            self.create_balanced_harmer_dispatch(harmer_dfax,Helper_global_gen,tara)
            tara.solveCase()
            if tara.isACSolutionConverged==True:
                output_file_path=os.path.join(stressed_case_folder_path,f"{stressed_file_name}.raw")
                tara.saveRawCase(caseFilePath=output_file_path, rawVerOut=33)
            else:
                dispatch_correction=dispatch_correction+50.0
                # del tara
                # gc.collect()
                new_tara=self.loadCase(Create_And_View.base_case_path)
                return self.gen_dispatch_capability(new_tara,stressed_case_folder_path,stressed_file_name,harmer_dfax,negative_globals_dfax,dispatch_correction)
        elif Helper_global_gen>Harmer_gen:
            self.create_Harmer_dispatch(harmer_dfax,tara,Harmer_gen)
            self.create_Balanced_Helper_dispatch(negative_globals_dfax,Harmer_gen,tara)
            tara.solveCase()
            if tara.isACSolutionConverged==True:
                output_file_path=os.path.join(stressed_case_folder_path,f"{stressed_file_name}.raw")
                tara.saveRawCase(caseFilePath=output_file_path, rawVerOut=33)
            else:
                dispatch_correction=dispatch_correction+50.0
                new_tara=self.loadCase(Create_And_View.base_case_path)
                return self.gen_dispatch_capability(new_tara,stressed_case_folder_path,stressed_file_name,harmer_dfax,negative_globals_dfax,dispatch_correction)
        else:
            print("nothing to dispathch")

    def create_helper_dispatch(self,dataframe,tara_api_instance,helper_gen):
        Helper_Gen_Count=[]
        if helper_gen!=0:
            for i in range(len(dataframe)-1):
                Helper_Gen_Bus=dataframe.loc[i,'  Bus#'].tolist()
                Helper_Generator_Bus_Data=tara_api_instance.getBus(busNum=Helper_Gen_Bus)
                Helper_Bus_Equipment=tara_api_instance.getBusEquipment(busObj=Helper_Generator_Bus_Data)
                Helper_Bus_Gen_IDs=Helper_Bus_Equipment.iGens
                if sum(Helper_Gen_Count)<=helper_gen:
                    for k in range(len(Helper_Bus_Gen_IDs)):
                        Helper_Generator_Instance=tara_api_instance.getGenerator(iGen=Helper_Bus_Gen_IDs[k])
                        status=Helper_Generator_Instance.status
                        if status==1:
                            Helper_Gen_Count.append(Helper_Generator_Instance.pGen)
                            Helper_Generator_Instance.pGen=0
                            tara_api_instance.updateCase(equipObj=Helper_Generator_Instance)
                        else: 
                            continue
                else:
                    return 
        else:
            return
    def create_balanced_harmer_dispatch(self,dataframe,Helper_gen,tara_api_instance):
        print("HELPER-DISPATCH")
        print(Helper_gen)
        Harmer_Buses_Dispatch_Running_Count=[]
        delta=0
        if Helper_gen!=0:
            for i in range(len(dataframe)-1):
                if sum(Harmer_Buses_Dispatch_Running_Count)<Helper_gen:
                    Harmer_Bus=dataframe.loc[i,'  Bus#'].tolist()
                    Harmer_Bus_Object=tara_api_instance.getBus(busNum=Harmer_Bus)
                    Harmer_Bus_Equipment_Object=tara_api_instance.getBusEquipment(busObj=Harmer_Bus_Object)
                    Harmer_Bus_Gen_ID=Harmer_Bus_Equipment_Object.iGens
                    delta=Helper_gen-sum(Harmer_Buses_Dispatch_Running_Count)
                    if len(Harmer_Bus_Gen_ID)!=1:
                        k=0
                        while k<=len(Harmer_Bus_Gen_ID)-1:
                            Harmer_Generator_Object=tara_api_instance.getGenerator(iGen=Harmer_Bus_Gen_ID[k])
                            if delta>=Harmer_Generator_Object.pMax-Harmer_Generator_Object.pGen:
                                Harmer_Buses_Dispatch_Running_Count.append(Harmer_Generator_Object.pMax-Harmer_Generator_Object.pMin)
                                Harmer_Generator_Object.pGen=Harmer_Generator_Object.pMax
                                Harmer_Generator_Object.status=1
                                tara_api_instance.updateCase(equipObj=Harmer_Generator_Object)
                                delta=Helper_gen-sum(Harmer_Buses_Dispatch_Running_Count)
                            else:
                                Harmer_Generator_Object.pGen=delta
                                Harmer_Buses_Dispatch_Running_Count.append(delta)
                                Harmer_Generator_Object.status=1
                                tara_api_instance.updateCase(equipObj=Harmer_Generator_Object)
                            k+=1
                    else:
                        Harmer_Generator_Object=tara_api_instance.getGenerator(iGen=Harmer_Bus_Gen_ID[0])
                        if delta>=Harmer_Generator_Object.pMax-Harmer_Generator_Object.pMin:
                            Harmer_Buses_Dispatch_Running_Count.append(Harmer_Generator_Object.pMax-Harmer_Generator_Object.pMin)
                            Harmer_Generator_Object.pGen=Harmer_Generator_Object.pMax
                            Harmer_Generator_Object.status=1
                            tara_api_instance.updateCase(equipObj=Harmer_Generator_Object)
                        else:
                            dispatch=Harmer_Generator_Object.pGen+delta
                            Harmer_Generator_Object.pGen=dispatch
                            Harmer_Buses_Dispatch_Running_Count.append(delta)
                            Harmer_Generator_Object.status=1
                            tara_api_instance.updateCase(equipObj=Harmer_Generator_Object)
                else:
                    print("HARMER_DISPATCH_BALANCE")
                    print(sum(Harmer_Buses_Dispatch_Running_Count))
                    return
        else:
            return

    def create_Harmer_dispatch(self,dataframe,tara_api_instance,Harmer_gen):
        print(Harmer_gen)
        Harmer_Gen_Count=[]
        if Harmer_gen!=0:
            for i in range(len(dataframe)-1):
                Harmer_Gen_Bus=dataframe.loc[i,'  Bus#'].tolist()
                Harmer_Generator_Bus_Data=tara_api_instance.getBus(busNum=Harmer_Gen_Bus)
                Harmer_Bus_Equipment=tara_api_instance.getBusEquipment(busObj=Harmer_Generator_Bus_Data)
                Harmer_Bus_Gen_IDs=Harmer_Bus_Equipment.iGens
                if len(Harmer_Bus_Gen_IDs)!=1:
                    k=0
                    while k<=len(Harmer_Bus_Gen_IDs)-1:
                        Harmer_Generator_Instance=tara_api_instance.getGenerator(iGen=Harmer_Bus_Gen_IDs[k])
                        Harmer_Gen_Count.append(Harmer_Generator_Instance.pMax-Harmer_Generator_Instance.pGen)
                        Harmer_Generator_Instance.pGen=Harmer_Generator_Instance.pMax
                        Harmer_Generator_Instance.status=1
                        tara_api_instance.updateCase(equipObj=Harmer_Generator_Instance)
                        k+=1
                else:
                        Harmer_Generator_Instance=tara_api_instance.getGenerator(iGen=Harmer_Bus_Gen_IDs[0])
                        Harmer_Gen_Count.append(Harmer_Generator_Instance.pMax-Harmer_Generator_Instance.pGen)
                        Harmer_Generator_Instance.pGen=Harmer_Generator_Instance.pMax
                        Harmer_Generator_Instance.status=1
                        tara_api_instance.updateCase(equipObj=Harmer_Generator_Instance)
        else:
            return
    def create_Balanced_Helper_dispatch(self,dataframe,Harmer_gen,tara_api_instance):
        Helper_Buses_Dispatch_Running_Count=[]
        delta=0
        print("HARMER_DISPATVCH")
        print(Harmer_gen)
        if Harmer_gen!=0:
            for i in range(len(dataframe)-1):
                if sum(Helper_Buses_Dispatch_Running_Count)<Harmer_gen:
                    Helper_Bus=dataframe.loc[i,'  Bus#'].tolist()
                    Helper_Bus_Object=tara_api_instance.getBus(busNum=Helper_Bus)
                    Helper_Bus_Equipment_Object=tara_api_instance.getBusEquipment(busObj=Helper_Bus_Object)
                    Helper_Bus_Gen_ID=Helper_Bus_Equipment_Object.iGens
                    delta=Harmer_gen-sum(Helper_Buses_Dispatch_Running_Count)
                    print(delta)
                    if len(Helper_Bus_Gen_ID)!=1:
                        k=0
                        try:
                            while k<=len(Helper_Bus_Gen_ID)-1:
                                Helper_Generator_Object=tara_api_instance.getGenerator(iGen=Helper_Bus_Gen_ID[k])
                                status=Helper_Generator_Object.status
                                if delta>=Helper_Generator_Object.pGen-0 and status==1:
                                    Helper_Buses_Dispatch_Running_Count.append(Helper_Generator_Object.pGen)
                                    Helper_Generator_Object.pGen=0
                                    tara_api_instance.updateCase(equipObj=Helper_Generator_Object)
                                                                 #outFile=f"{PATH}_{i}{k}.INCH")
                                    delta=Harmer_gen-sum(Helper_Buses_Dispatch_Running_Count)
                                elif status==1:
                                    current_gen=Helper_Generator_Object.pGen
                                    dispatch=current_gen-delta
                                    Helper_Buses_Dispatch_Running_Count.append(delta)
                                    Helper_Generator_Object.pGen=dispatch
                                    tara_api_instance.updateCase(equipObj=Helper_Generator_Object)
                                                                 #outFile=f"{PATH}_{i}{k}.INCH")
                                k+=1
                        except Exception as e:
                            print(f"An error occurred: {e}")
                    else:
                        try:    
                            Helper_Generator_Object=tara_api_instance.getGenerator(iGen=Helper_Bus_Gen_ID[0])
                            status=Helper_Generator_Object.status
                            if delta>=Helper_Generator_Object.pGen and status==1:
                                Helper_Buses_Dispatch_Running_Count.append(Helper_Generator_Object.pGen)
                                Helper_Generator_Object.pGen=0
                                tara_api_instance.updateCase(equipObj=Helper_Generator_Object)
                                                             #,outFile=f"{PATH}_{i}.INCH")
                            elif status==1:
                                dispatch=Helper_Generator_Object.pGen-delta
                                Helper_Buses_Dispatch_Running_Count.append(delta)
                                Helper_Generator_Object.pGen=dispatch
                                tara_api_instance.updateCase(equipObj=Helper_Generator_Object)
                                                             #,outFile=f"{PATH}_{i}.INCH")
                        except Exception as e:
                            print(f"An error occurred: {e}")
                else:
                    print("HELPER_DISPATCH")
                    print(sum(Helper_Buses_Dispatch_Running_Count))
                    return
        else:
            return
#if __name__=="__main__":
#     # c=Create_Flow_Gate_Tuple()
#     # c.make_flowgate_scripts('DFAX_REPORTS','SCRIPTS','STRESSED_CASES','SECURED_CASES','SCRD_SCRIPTS','ISO_NE_GENs','ISO_NE_Load')
#     x=Create_And_View()
#     x.execution(x.DFAX_REPORTS_SUB_PARENT_FOLDER_PATH)
#     x.execution(x.DFAX_REPORTS_SUB_PARENT_FOLDER_PATH_REVERSAL)
