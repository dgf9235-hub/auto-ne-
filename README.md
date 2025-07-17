# Conducting an ISO-NE Overlapping Impact Analysis using the Equinor Automation Tool
Hello, the following document explains the steps necessary to use the Equinor automation tool in order to run an "overlapping impact analysis" consistent with the procedures and methodologies employed by ISO-NE to support the Forward Capacity Market.[^1] 

[^1]: https://www.iso-ne.com/static-assets/documents/2020/02/pp-10.pdf

##  Preliminary Steps : Configuration, Files and Paths (JSON)

## Configuration
#### **1. Configuration Step 1**
Ensure that you have **Python 3.9** (Python 3.9 is preferred) or higher installed on your local drive.
as the **Tara.dll**, essential to running this analysis, requires a 64 bit version of the python interpreter. 

Here is a link to the videos onm TARA configuration created by Biagio Pinto of PowerGEM. [^3]

    [^3]: https://www.power-gem.com/videos/pythonvideos

Also, if you would like to see the internal contents of the
.py files, it is recommended that you download the latest version of Microsoft VS Code as it is likely the best IDE this strict purpose. It is not necessary you do this to open the .py files as Python comes with its own IDLE (Integrated Development and Learning Environment), nor is it necessary to have one at all as we will be running the entire analysis from a pre-compiled executable!


#### **2. Configuration Step 2: Working Directory Navigation**
Open your command prompt by typing 'cmd' in the Windows search bar after which a black "command line interface" will appear on your screen. Navigate to the interface command line, and check what drive you are working in and ensure that the drive is the same drive in which the python package exists. After verifying this, please enter the following 

    cd this/is/my/path/drive

Please note that you should be entering your desired path in the mock above!

Verify that the path in your cmd prompt is reflective of the Python installation location, with the terminal folder being the installed Python folder. 

This folder path will be the base folder path for configuration, do not close the cmd prompt or you will need to repeat this step again!

#### **3. Configuration Step 3: Virtual Environment Creation**

Now that we have installed Python, we will create a virtual environment which will contain our project, dependencies and allow us manueverability we desire.    

Type into your command prompt the following:

    python -m venv ISO-NE_Automation

This command will create a virtual environment, which you can check by going into your computer directory.

Once you have verified that the creation of this virtual environment has occured, please type the following,

    cd Scripts

Now wait for response and then type the following,

    activate

Once that is completed,verify at the beginning of your working directory, i.e. the relevant drive, there is a parenthesized *(ISO-NE_Automation)*. Once you see this, you are officially working in what in your new virtual environment, which is essentially a copy of the standard python library that came with your downloaded python 3.9 or higher, in which you may package dependencies and code specific to your project *(ISO-NE Automation)* in a separate place. 

please type the following commands in the command prompt

    pip3 install pandas
    pip3 install numpy
    pip3 install asyncio
    pip3 install yaml
    pip3 install pyinstaller

#### **4. Configuration Step 3: Install pyPowerGEM.pyTARA using the .whl file**
Each TARA version release, a pyPowerGEM zip distribution is included. Please locate the latest release and extract the zip distribution to your C drive. Once you have extracted the pyPowerGEM distribution you will see that there is "wheel" file named ***pyPowerGEM-2302.1-py3-none-any.whl*** . This file is the primary installation/configuration file for **pyPowerGem**.

Please copy the path to this file and then re-navigate to this path in the command prompt, ensuring that you are still working within your ISO-NE automation environment by verifying that the parenthesized ***(ISO_NE_Automation)*** is still present at the beginning of the directory path. 

Please enter the following,

    cd path/to/your/whl_file
...

    pip3 install pyPowerGEM-2302.1-py3-none-any.whl

The typed directions for this configuration process are also present in the *pyPowerGEM* documentation below. 




 [^4]:https://en.wikipedia.org/wiki/YAML
 [^5]:https://www.power-gem.com/videos/pythonvideos
 [^6]:https://en.wikipedia.org/wiki/YAML

## Cluster Inch File and Subsystem Preparation 
Once you have determined which projects in the cluster are relevant to the respective load zone in study, please create an inch file containing these projects injecting at their own buses, with respective lines added, i.e. generatorbus.,line to POI. Also, the bus names must be in the following format 

    CL_{number 1...99}
Once the generators, buses and gen-ties have been created please add the bus numbers to the ISO_NE_GENs subsystem in the .sub file and label those projects so T&I can refer back easily. 
Please create a key that corresponds names to bus numbers. 

## Files and Paths (JSON)

### Files and Folders
#### **1. Python Files Step 1: Download the .exe from Sharepoint and the .json file**
 Please naviagate to the Sharepoint T&I Analytics folder[^4], and please download the folder labeled **ISO-NE Automation** and place that folder in the Scripts folder present in your installed python environment.

Once you have completed this, please inspect the contents of the folder ensuring the presence of the following, 

1) ***ISO_NE_Automain-main***
    - present within this folder should be another folder called **dist**, please navigate to this folder and ensure the presence of the executable, the .json path file and another folder populated with dependencies. 
2) ***ISO_NE_AUT_Parent_2***
    - present within this folder should be multiple .txt files
3) ***ISO_NE_AUT_Post_PJT_Parent***
    - empty 

### Paths (JSON)
#### **2. Introduction to the .JSON file**
JSON is an abbreviation for *Java Script Object Notation* and, in short, is way of structuring data into,

    key:value


pairs in a hierarchical, organized, and human readable format. Fortuantely, python developers have built many solid integrations between python and json data formats, allowing us to leverage the convenient structure of json so we don't have to write the paths for the power flow specific files we will use directly inside our python scripts.[^7]

Upon opening the ***ISO_NE Automation*** folder downloaded from the Sharepoint, please inspect the ***ISO_NE_Automation-main*** and verify the presence of the following. 

    dist Folder: Contains the compiled executable, necessary dependencies and the json file, the latter of which the user will be taught to adjust in the following section.

    build Folder: Contains intermediate files used during the compilation process.

    Spec File: A .spec file that describes how your script was compiled.

    Json file: This contains the variables and the files,paths, integers, strings for each of those variables.


Once you have read and understood each of the adjustable json variables, please read the following section which will direct to the necessary edits to the json file located within the ***dist*** folder. 

[^7]:https://en.wikipedia.org/wiki/JSON

#### **3. T&I Analytics JSON file**
The T&I Analytics team created a .json file named

        ISO_NE_AUT_PATHS.json
 
 This file is the external data file that will contain information needed to drive the analysis.It is written in json format, that the T&I user will write their own file paths and adjustable parameters to. These two types are essential as they provide to the tool the power specific data essential to run the study as well as the information that will determine the scope of the study, e.g. every monitored element in Massachusetts or just those in Northeastern Massachusetts. Below you will see a description of each json variable to help conceptualize the importance of each.

***NOTE**: All strings must be in quotations. This incluides folder/file paths, file names, and other miscellaneous (e.g. subsystems)


***"tara_executable"***:,
    
- path to your tara.exe mentioned above (must be in quotations and include "tara.exe")
- string

***"auxiliary_files_folder_path"***:,

- path to the folder containing the sub ,mon, con files
- string

***"Pre_Project_Parent_Folder_Path"***:

- path to the folder you have created *a priori*
- string


***"STEP_1_Script_Template_Name.txt"***:"ISO_NE_AUT_STEP_1_Template_Best.txt",

- this is the veriable containing the script template we will write to, do not worry about this one as it is contained in the folder you will download
- string

***"STEP_1_Output_Script_Name(.txt)"***:"dccont_new_script.txt",
- this is the name of the script we will create from the script template stated above. Do not worry about this as it will come with the pre-project parent folder. 
- string 

***"DC_CA_File_Name(.csv)"***:"DCCONT.csv",

- This is the name of the DC Contingency Analysis that will be created by the script above, do not worry about this. 
- string with .csv file extension.

***"DFAX_CUTOFF_Relevant_Flowgates"***:,

- Minimum DFAX for mon/con pairs generated from the DC Contingency Analysis of the Base Case. Choosing .03 and above would find all those that may be responsibility of the study unit per ISO-NE procedure, but choosing lower allows user to cast a wider net of stressed cases from which a new DC CA can be run to establish most limiting flowgates that have dfax of .03 and above. 
    *Lower DFAX likely preferable
- integer/float

***"Loading_Cutoff_Relevant_Flowgates"***:78,

- Minimum loading to apply to the DC Contingency Analysis to cast net of mon/con pairs. T&I could come up with good rule of thumb for loading minimum, but ideally you try all (longer comp time).
- integer/float

***"DFAX_CUTOFF_Flow_Reversal_Relevant_Flowgates"***:,

- negative dfax threshold to try to reverse flow, making the study unit impact from negative impact to positive impact, e.g. -0.03.
- string
-integer/float
***"Loading_Cutoff_Flow_Reversal_Relevant_Flowgates"***:,
- Maximum Loading to apply for the negative dfax case, increasing the maximum casts a wider net while flowgates with loadings closer to 0 are more likely to be loaded higher in the reverse direction. 
- string
-integer/float

***"STEP_2_Script_Template_Name(.txt)"***:"ISO_NE_AUT_STEP_2_Template.txt",

- The name of the STEP 2 script template that generates dfax (gen reports) for each flowgate generated from the dc contingency analysis in step 1, it will come with the download of the pre-project folder so no need to worry about this one. 
- string with.txt file extension

***"Base Case"***:"2027-28_EPE_pp10DEL_C0_v2 (3).raw",

- The name of the base case you are applying for this analysis. This would be likely the FCA case provided by the NYISO with the appropriate 
- string
-string with .raw extension

***"Subsystem_File_Name"***:,

- The name of the sub file located within the aux files folder.*Do not include the path. 
- string with .sub file extension

***"Mon_File_Name"***:,

- The name of the mon file located within the aux files folder,e.g. "2027-28_FCA_Qual_OverlappingImpact_Mon.mon".
- string with .mon file extension

***"Con_File_Name"***:,

- The name of the con file located within the aux files folder. *Do not include the path, e.g. "2027-28_FCA_Qual_OverlappingImpact_CTGs.con"
- string with .con file extension

***"Study_Unit_Bus_Number"***:,
- The bus number of the substation the study unit is interconnecting to, according to the ISO-NE FCA case, e.g. 113987
-This information can be easily extracted from running the FCA file in TARA Viewer or TARA studio and locating the substation.
- integer, must be present in the .raw file. 

***"Study_Unit_Load_Zone_Name"***:,

- The load zone the project is intending on applying to be a capacity resource in, e.g. "NEMABOS_Load"
- string
- *Please check-out the designated sub file to see what the different potential reference subsystems are

***"STRESSING_GENS_SUB"***:"ISO_NE_GENs",

- The subsystem we use to stress the case. For ISO-NE, this will always be the ISO_NE_Gens subsystem. 
- string
- please check-out the subsytems to see what sending subsystems can be used,
i.e. what subsystems containing some generators. 

***"STRESSING_REF_SUB"***:"NEMABOS_Load",

- The subsystem we are using as the reference for the ISO_NE_Gens. T&I used to the relevant load zone in previous analyses, but ISO-NE notified us that the ISO_NE_Load subsystem is the appropriate reference. 
- string

***"DFAX_CUTOFF_STRESS_CASE"***:0.03,

- don't worry about this one.
- float

***"MINIMUM_LOADING_STRESS_CASE"***:40,

- T&I will determine the best minimum flowgate loading to stress the case. Considering ISO-NE initial dispatch is arbitrary, maybe best to stress all with dfax> desired dfax cutoff.
- integer/float

***"DFAX_CUTOFF_FLOW_REVERSAL"***:-0.03,

- maximum dfax flowgate to check for flow reversal.
- float

***"MAXIMUM_LOADING_FLOW_REVERSAL"***:,

-  T&I will determine the best minimum flowgate loading to stress the case. Considering ISO-NE initial dispatch is arbitrary, maybe best to stress all with dfax < desired dfax cutoff. 
- integer/float

***"POST_PROJECT_PARENT_FOLDER_PATH"***:,

- Create the path for the post project parent folder, but do not include the post project folder (don't create one either). This is just the path where you want you post project results to be. 
- string 

***"PRE_PROJECT_LOADINGS_CSV_FILE_PATH"***:,
- path to which you would like to write the file containing all the stressed case loadings, i.e. Relevant Flowgates file. 
- string 

***"MINIMUM_LOADING_PRE_PROJECT_LOADING_CSV_FILE"***: 75,

- The minimum loading you would like to apply to all flowgate loadings for each stressed case, listed in the relevant flowgates file. E.g. if you project is 10 MW at a dfax of 1 and you can dispatch again a project with a negative dfax of 1, the maximum loading increase on the line is 20 MW and if the N-1 MVA is 100, at 75 percent pre-project loading the maximum loading post-project is 95%.

- T&I will come up with a good rule of thumb here. Don't worry about this.
- integer

***"DCCONT_SCRIPT_PATH"***:"C:\\Appl\\Python39\\ISO_NE_Automation\\Scripts\\Python Files\\Py Files\\
ISO-NE\\ISO_NE_AUT_Parent_2\\ISO_NE_AUT_STEP_4_Template.txt",

- The path, including the script, we will use to generate dccont reports for each stressed case which we will then loop through to create the relevant flowgates file. Don't worry about this. 
-string

***"STUDY_UNIT_CRIS_LEVEL"***:125,

- The MW level you are studying the project at in the capacity study. This would be the amount, de-rated by capacity factor, you wish to receieve Capacity interconnection rights for. 
-integer/float


***"STUDY_UNIT_INCH_FILE"***:,

- Write the path to which you would like write the inch file containing the gens dispatched fort each flowgate. Preferably keep this file inside the parent folder.
-string


***"Tara_DLL_Path"***:,

- Path to the tara.dll you will need to run the code and comes with the pyhPowerGEM Zip distribution you installed using the .whl file. 
- string, must contain the .exe extension

***"POST_PROJECT_DISPATCH_GENS"***:,

- Subsystem you will use to dispatch against the study unit in the post project case,e.g. "ISO_NE_GENs".
- string, must contain the .exe extension


***"POST_PROJECT_DISPATCH_REFERENCE"***:,

- Load zone into which we want capacity interconnection rights. Changes based on the study,e.g. "NEMABOS_Load".
- string, must contain the reference subsystem

**BASE_OVERLOAD_PEN_SCRD"**:10000

 **"CON_OVERLOAD_PEN_SCRD"**:1000
 
 **"GEN_REDISPATCH_PEN_SCRD":0.01

 **"CL_LIST"**: list in a brackets of all bus names for the cluster.

 **"CL_INCH_FILE"**: The path of the inch file that adds the cluster generators at 0 MW injection. 
## Running the Analysis with the master .py File
Go to your command prompt and ensure that you have navigated to the correct file path within the command prompt. Once yo8u have verified that the file path ends in the folder where your python files are stored, please execute the following, 

    python ISO_NE_AUT_STEP_5_STUDY_UNIT_b.py

This should begin running the analysis.
## Running the Analysis with Pyy executable

Now that we have configured Python and the pyPowerGEM package, ensured we have correct folders and files, and populated the .json file with the files and file paths necessary to run the analysis, we can proceed to running the analysis. 

If you are entirely sure you have correctly followed the steps above, open your command prompt and type the following.

    cd ISO_NE_AUT_STEP_5_STUDY_UNIT_b

and once this returns, type

    cd dist

and once this return, enter the name of the executable file. 

    ISO_NE_AUT_STEP_5_STUDY_UNIT_b.py

## Appendix I 

Please review the visual below, which provides a high level control flow

### Control Flow Diagram

![Alt text](images/ISO-NE%20Automation.png)
