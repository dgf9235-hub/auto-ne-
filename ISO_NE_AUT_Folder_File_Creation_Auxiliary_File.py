import os
import pandas as pd
import pandas as np 
import shutil

class Create_Folders:
    pass
    def create_single_folder(self,parent_folder_path,folder_name):
        #Call this function upon 
        path = os.path.join(parent_folder_path,folder_name)
        if os.path.exists(path):
            print("PATH EXISTS")
            shutil.rmtree(path)
            os.makedirs(path,exist_ok=True)
        else:
            os.makedirs(path,exist_ok=True)
        return path
    #def create_group_of_folders(self,sub_parent_folder_path,folder_list):
class Create_File_Name_In_Path:
    def __init__(self,file_path,file_name):
        self.file_path=file_path
        self.file_name=file_name
    def create_file_name(self,folder_path,file):
        new_file=os.path.join(folder_path,file)
        return new_file

    