import requests, json, time, os
from datetime import datetime
import pandas as pd

#Assign or create a file directory for JSON files
courses_filepath = "CourseStatusReport.csv"

# Open csv files listing course information, retrieved from https://wildfly-prd.iit.edu/coursestatusreport/
d = pd.read_csv(courses_filepath, dtype=str)
d.set_index("CRN", inplace=True, drop=True)
d["Primary ID"] = None
d["email"] = None

# API key
api_key = "YOUR API KEY HERE"


def GetEmail(api_key, index, row):
    raw_name = row["Primary Instructor"]

    try:
        #NEED TO BUILD IN THE POSSIBILITY OF FACULTY WITH SPACES IN THEIR NAMES
        first_name, last_name = raw_name.split(", ")
        first_name = first_name.replace(" ","%2B")
        first_name = first_name.replace("'","")
        print(first_name)
        last_name = last_name.replace(" ","%2B")
        last_name = last_name.replace("'","")
        print(last_name)

        # Make an API call to search for the instructor name and retrieve a Primary ID.
        apicall = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/users?{format}&apikey={api_key}&q=ALL~{first_name}%2b{last_name}'
        format = "format=json"
        call_elements = {"format": format,
                         "api_key": api_key,
                         "first_name": first_name,
                         "last_name": last_name}
        print(apicall.format(**call_elements))
        response = requests.get(apicall.format(**call_elements))
        instr_response = response.json()
        print(instr_response)

        if instr_response["total_record_count"] > 1:
            for i in instr_response["user"]:
                primary_id = i["primary_id"]
                inst_apicall = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/users/{primary_id}?{format}&apikey={api_key}'
                inst_call_elements = {"format": format,
                                      "api_key": api_key,
                                      "primary_id": primary_id}
                is_empl_response = requests.get(inst_apicall.format(**inst_call_elements))
                user_group = is_empl_response.json()["user_group"]["desc"]

                if user_group == "Academic Employees":
                    id = primary_id

        else:
            id = instr_response["user"][0]["primary_id"]

        print(id)
        email_call = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/users/{id}?{format}&apikey={api_key}'
        format = "format=json"
        email_call_elements = {"id": id,
                         "format": format,
                         "api_key": api_key}
        email_response = requests.get(email_call.format(**email_call_elements))
        print(email_response)
        email_dict = email_response.json()
        print(email_dict)
        email = email_dict["contact_info"]["email"][0]["email_address"]

    except:
        print("No User Found")
        id = "NOT FOUND"
        email = "NOT FOUND"

    return id, email

instr_list = []

for index, row in d.iterrows():
    department = row["Department"]
    instructor = row["Primary Instructor"]
    unique_instructor = [department, instructor]

    if unique_instructor not in instr_list:
        print(unique_instructor)
        instr_list.append(unique_instructor)
        
        instr_details = GetEmail(api_key, index, row)
        print(instr_details)
        instructor_id = instr_details[0]
        instructor_email = instr_details[1]
        d.loc[index, 'Primary ID'] = instructor_id
        d.loc[index, 'email'] = instructor_email
        d.to_csv(courses_filepath)

    else:
        pass

