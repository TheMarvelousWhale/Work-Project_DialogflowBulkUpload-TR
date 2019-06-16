# DialogflowBulkUpload

This is the automation files for creating a specific type of intents (one parent with two children intents) for the NTU Dialogflow Chatbot.

Most files are boilerplate files and ceaned info files from the University staff, while the main workhorse is big.py.
Do note that the intents are custom payloads for Kommunicate. 

Please do note that in the Lyon-Template folder there are two files that deserve a bit more attention: agent.js and package.json. Please do use the newest version for these two files otherwise the behaviours of the bot will be suspicious as well. 

## HOW TO USE THE CODE 

create a new folder and dump ALL the json file and the py file inside
extract the zip and put the Lyon - Template folder in the newly created folder
the QnVarTemplate excel use 00 as placeholder for the Tutorial Room number
The main file with 4 columns - qn, ns,lhs, lhn in that order (I was lazy so I hardcoded the index, for fear that someone will misspell the col name). Within each column the info must follow the same format for regex to read properly (even if it doesn't, python will complain so no worries. Debugging this is easy)

### Now Open Big.py

Make sure that the files from line 40-66 are named correctly (if it doesn't then again, FileNotFound Error from Python)
Make sure the 7 libraries are in your system

And hit RUN. Hopefully the following will happen:

1. Shutil lib creates a copy of "Lyona Template" folder
2. Pandas read the two excel files into its Dataframes for processing
3. Json read the 4 json into python format
4. Python goes down the row of the main DF (from TR.xlsx), generate the to-be-json parent and parent_usersays (which makes use of the other excel file to generate different training phrases), then generate the two children in a similar fashion. It does so by taking the relevant info out from Pandas DF using Regex,make a deepcopy of the json, then slot these infos in the correct positions in the json copy. (modularized into the 4 functions written near the top of big.py). 
5. Export the python thing into json and put the json directly into the "Lyona Template - Copy" folder.
6. Zip the folder up into file called "New Intents.zip" and delete the folder

7. Now you need to pray that everything works correctly and upload this zip into the Dialogflow agent. 
