#import required libraries
import datetime
import requests
import sys
reload(sys)
sys.setdefaultencoding("utf8")
import warnings
import app_dict
 
warnings.filterwarnings("ignore")
global verbose
debug=True
 
#Initialize the metadata array, which will be updated as data is collected
meta_array=[]
data={"instance":{"metadata":meta_array}}
#Define list of customOptions that wont be populated as Tags
filtered_tags=["ServerNamePart2"]
#Obtain current date in the format DD-MMM-YYY , and associate it to Creation Date metadata
####meta_array.append({"name": "Creation Date","value":datetime.datetime.today().strftime("%d-%b-%Y")})
cd="<%=container.dateCreated%>"
months=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
c_date=cd.split()[0].split("-")
meta_array.append({"name": "Creation Date","value": c_date[2]+"-"+months[int(c_date[1])-1]+"-"+ c_date[0]})
 
 
#Transform underscore of customOptions labels into spaces and promote them to tags
cmString="<%=server.customOptions%>"
customOptions={}
for m_entry in cmString.lstrip("[").rstrip("]").split(","):
   e=m_entry.split(":")
   n_label=e[0].replace("_"," ").strip()
   customOptions[n_label]=e[1].strip()
   #Add to the metadata only the tags that are not filtered
   if n_label not in filtered_tags:
      meta_array.append({"name":n_label,"value": customOptions[n_label]})
#######
#Use the app_dict imported dictionary to pull the Application criticality and App Name
try:
  current_APPID=str("<%=customOptions.Application_ID %>")
  app_details=app_dict.appIDs[current_APPID]
  meta_array.append({"name": "AppCriticality","value": app_details["Application criticality"]})
  meta_array.append({"name": "Application","value": app_details["Name"]})
except: print("error pulling app details")
#######
#Obtain the OS code (Linux|Windows) from the vm itself, and add it to the OS metadata
OS_long="<%=server.osTypeCode%>".capitalize()
if OS_long.upper().startswith("WIN"):
	OS="Windows"
else:
    OS="Linux"
meta_array.append({"name":"OS" ,"value": OS})
 
# Obtain the Hostname from the server name and add it to metadata 
Hostname="<%=server.hostname%>"
meta_array.append({"name":"Hostname" ,"value": Hostname.split(".")[0].upper()})
 
cloudType=str("<%=zone.cloudTypeCode%>")
########## Begin AWS Only ############################
if cloudType.upper().startswith("AMAZON"):
#Set instance name back to the Hostname and not AWS Name
    Hostname="<%=server.hostname%>"
    data={"instance":{"displayName":Hostname.split(".")[0].upper(),"metadata":meta_array}}
########## END AWS Only ############################
group_name="<%=group.name%>"
location=group_name.split(" - ")[2].replace(" /","/").replace("/ ","/")
 
meta_array.append({"name":"Location" ,"value": location})
#print("metadata"+str(data))
#print("id: "+"<%=instance.id%>")
header={"Authorization": "Bearer "+"<%=cypher.read("secret/ecsautomation")%>"}
if debug:
  print (str(header))
  print(str(data))
url="https://azcmp.astrazeneca.net/api/instances/"+"<%=instance.id%>"
api_call=requests.put(url, headers=header, verify=False,json=data)
print(str(api_call.json))
print("Status:"+str(api_call.status_code)+",reason:"+str(api_call.reason ))
