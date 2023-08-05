#!/usr/bin/env python3
import codecs
import glob
import os
import re
import time
import traceback
import zipfile
from zipfile import ZipFile
import shutil
from read_data import *


# import tableauserverclient as TSC
import typer
from bs4 import BeautifulSoup
# from google.cloud import bigquery, storage

# from common_resources.secret_accessor import access_latest_enabled_secret_version

# TABLEAU_USER_NAME = os.getenv("TABLEAU_USER_NAME", "telia_admin")

"""
def download_workbook(user_name, password, master_workbook_name):
    tableau_auth = TSC.TableauAuth(user_name, password, "")
    server = TSC.Server("https://tableau.telia-gcp.com")
    server.auth.sign_in(tableau_auth)
    workbook_id = ""
    with server.auth.sign_in(tableau_auth):
        req_options = TSC.RequestOptions()
        req_options.filter.add(
            TSC.Filter(
                TSC.RequestOptions.Field.Name,
                TSC.RequestOptions.Operator.Equals,
                master_workbook_name,
            )
        )

        workbook_match = TSC.Pager(server.workbooks, req_options)[0]
        print(f"Workbook name:{workbook_match.name}")
        file_path = server.workbooks.download(workbook_match.id)
        print("\nDownloading the file to {0}.".format(file_path))

        # workbook = server.workbooks.get_by_id(workbook_id)
        # server.workbooks.populate_connections(workbook)

    # print information about the data connections for the workbook item
    # print("\nThe connections for {0}: ".format(workbook.name))
    # for connection in workbook.connections:
    #   print(connection.datasource_name)
    #  print(server.connection.get_by_id(connection.id).name)
    return workbook_id
"""

def unzip_workbook():
    twbx_file = glob.glob("*.twbx")
    os.rename(twbx_file[0], twbx_file[0].replace("twbx", "zip"))
    with zipfile.ZipFile(twbx_file[0].replace("twbx", "zip"), "r") as zip_ref:
        zip_ref.extractall("")


def modify_xml(countries):
    xml_file = glob.glob("*.twb")
    xml = xml_file[0]
    print(xml)
    # f = codecs.open(xml, "r", "UTF-8")
    # soup = BeautifulSoup((f.read()), "xml")
    locale = {
        "swe": "sv_SE",
        "no": "nb_NO",
        "fin": "fi_FI",
        "est": "en_GB",
        "dk": "da_DK",
    }
    df = read_customer_language('TestData/TestDataaa.csv')
    for country in countries:

        print(f"Generating xml per country: {country}")
        f = codecs.open(xml, "r", "UTF-8")
        soup = BeautifulSoup((f.read()), "xml")

        # text = soup.find_all(string=re.compile("swe"))
        # for comment in text:
        #     fixed_text = comment.replace("swe", country)
        #     comment.replace_with(fixed_text)
        if df is not None:
            new_df = df[(df.Template == 'Template1')]
            print(new_df)
        for index, row in new_df.iterrows() :
            replace_text = row['replace_text'].strip()
            target_replace_text = row [country].strip()
            print(f"replace_text - {replace_text} and target_replace_text - {target_replace_text}")
            text_overview= soup.find(string = re.compile(re.escape(replace_text)))
            if text_overview :
                fixed_text = text_overview.replace(replace_text,target_replace_text)
                text_overview.replace_with(fixed_text)
                print(f"replace_text - {replace_text} and target_replace_text - {target_replace_text}")

        # text_overview= soup.find(string = re.compile(re.escape("**OVERVIEW$$")))
        # if text_overview :
        #     fixed_text = text_overview.replace('**OVERVIEW$$','Översikt')
        #     text_overview.replace_with(fixed_text)

        # text_article= soup.find(string = re.compile(re.escape("**ARTICLES$$")))
        # if text_article :
        #     fixed_text = text_article.replace('**ARTICLES$$','Artiklar')
        #     text_article.replace_with(fixed_text)

        # text_startDate= soup.find(string = '**START DATE$$')
        # if text_startDate :
        #     fixed_text = text_startDate.replace('**START DATE$$','Start datum')
        #     text_startDate.replace_with(fixed_text)

        for elem in soup.find_all(True):
            for attr, para in elem.attrs.items():
                if "swe" in str(elem.get(attr)):
                    print(elem.get(attr))
                    elem[attr] = elem.get(attr).replace("swe", country)
                    print(elem[attr])
                    # myset.add(elem.get(attr).replace("swe", country))

        for elem in soup.find_all(True):
            for attr, para in elem.attrs.items():
                if "en_GB" in str(elem.get(attr)):
                    elem[attr] = elem.get(attr).replace("en_GB", locale.get(country))
        with open(f"test_{country}.twb", "w", encoding="UTF-8") as file:
        #with open(os.path.join('target/',f"test_{country}.twb"), "w", encoding="UTF-8") as file:
            file.write(str(soup))
        


def zip_twbx():
    zip_workbooks = glob.glob("test_*")
    images = glob.glob("Image/*")
    for wb in zip_workbooks:
        wb_zip = wb.replace("twb", "zip")
        print(wb_zip)
        zip_file_path = os.path.join('target/', wb_zip)
        with ZipFile(zip_file_path,'w') as zipObj:
       # zipObj = ZipFile(wb_zip, "w")
            for image in images:
                zipObj.write(image)
        # zipObj.write('Data/Extracts/federated_1n961c2076uwam1cw8yvw0.hyper',os.path.join('Data/Extracts/federated_1n961c2076uwam1cw8yvw0.hyper'))
            # Add multiple files to the zip
            add_folder_to_zip(zipObj,'Data/','Data/')
            zipObj.write(wb)
            # close the Zip File
            zipObj.close()
        os.rename(zip_file_path, zip_file_path.replace("zip", "twbx"))

def add_folder_to_zip(zip_archive, folder_path, folder_name_in_zip):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            zip_archive.write(file_path, os.path.join(folder_name_in_zip, os.path.relpath(file_path, folder_path)))


"""
def publish_workbook(
    user_name,
    password,
    name_dashboard,
    tabs,
    export,
    tableau_id_project,
    country,
    wb,
):
    countries_dict = {
        "SWE": "Sweden",
        "NO": "Norway",
        "FIN": "Finland",
        "EST": "Estonia",
        "DK": "Denmark",
    }
    tableau_auth = TSC.TableauAuth(user_name, password, "")
    server = TSC.Server("https://tableau.telia-gcp.com")
    server.auth.sign_in(tableau_auth)
    with server.auth.sign_in(tableau_auth):
        # create a workbook item
        replace = f"{name_dashboard} {countries_dict[country]}"
        tabs_bool = tabs

        if export:
            replace = f"{name_dashboard} {countries_dict[country]} - Data Export"
        wb_item = TSC.WorkbookItem(
            name=wb.replace(wb, replace),
            project_id=tableau_id_project,
            show_tabs=tabs_bool,
        )
        # call the publish method with the workbook item
        wb_item = server.workbooks.publish(wb_item, wb, "Overwrite")

"""
"""
def translate_manu(file, table, LANGUAGE, query_labels={}):
    project_id = "telia-ddi-no-prod"
    query_labels["country"] = LANGUAGE.lower()
    query_labels["function"] = "translate_manu"
    # client = bigquery.Client(
    #     project=project_id,
    #     default_query_job_config=bigquery.QueryJobConfig(
    #         connection_properties=[
    #             bigquery.query.ConnectionProperty(
    #                 key="query_label",
    #                 value=",".join([":".join([k, v]) for k, v in query_labels.items()]),
    #             ),
    #         ],
    #     ),
    # )
    sql = f"SELECT * FROM `telia-ddi-delivery.translations_standard_products.{table}` "

    df_replacements = client.query(sql, project=project_id).to_dataframe()

    LANGUAGE = LANGUAGE
    src_file = file

    # Clean up the DF a bit, reading from XLS means empty strings are NaN and sometimes we
    # get an UTF-8 BOM in the beginning of strings, so get rid of that
    df_replacements.fillna("", inplace=True)
    df_replacements = df_replacements[["ENG", LANGUAGE]]
    f = codecs.open(src_file, "r", "UTF-8")
    soup = BeautifulSoup((f.read()), "xml")
    # tags = ["caption", "formula", "value"]
    mydict = dict(zip(df_replacements.ENG, df_replacements[LANGUAGE]))
    new_mydict = {}
    for k in sorted(mydict, key=len, reverse=True):
        new_mydict[k] = mydict[k]
    print(len(new_mydict))
    for k, v in new_mydict.items():
        k = f"**{k}**"
        text = soup.find_all(string=re.compile(str(k).replace("*", "\*")))
        for comment in text:
            if not v:
                fixed_text = comment.replace(k, f"{k} - MISSING ")
                comment.replace_with(fixed_text)
            else:
                fixed_text = comment.replace(k, f"{v}")
                comment.replace_with(fixed_text)

    for k, v in new_mydict.items():
        k = f"**{k}**"
        for elem in soup.find_all(True):
            for attr, para in elem.attrs.items():
                if k in str(elem.get(attr)):
                    # print(str(elem.get(attr)))
                    # print(v)
                    if not v:
                        elem[attr] = elem.get(attr).replace(k, f"{k} - MISSING ")
                    else:
                        elem[attr] = elem.get(attr).replace(k, f"{v}")
    with open(src_file, "w", encoding="UTF-8") as file:
        file.write(str(soup))
"""
"""
def find_tableau_project(tableau_folder, user_name, password):
    tableau_auth = TSC.TableauAuth(user_name, password, "")
    server = TSC.Server("https://tableau.telia-gcp.com")
    server.auth.sign_in(tableau_auth)
    with server.auth.sign_in(tableau_auth):
        found = [
            proj for proj in TSC.Pager(server.projects) if tableau_folder == proj.name
        ]
        print(found[0].id)
        return found[0].id


def download_pictures(project="telia-ddi-delivery", bucket_gcp="hyperfiles-pictures"):
    print("Download csv data from bucket:")
    storage_client = storage.Client(project)
    bucket = storage_client.get_bucket(bucket_gcp)

    storage_client1 = storage.Client(project)
    bucket1 = storage_client1.get_bucket(bucket_gcp)

    for file in storage_client.list_blobs(bucket):
        destination_file_name = f"Image/{file.name}"
        blob = bucket1.blob(file.name)
        blob.download_to_filename(destination_file_name)

"""
def workbook_creation(
    master_workbook_name,
    name_dashboard,
    export,
    tabs,
    countries,
    tableau_folder,
    translate_sheet_table,
    run,
    email,
):
    # Secret version has been added to telia-ddi-utils secret manager manually
    # user_name = TABLEAU_USER_NAME
    # password = access_latest_enabled_secret_version(
    #     project_id="telia-ddi-utils",
    #     secret_id=f"tableau_{TABLEAU_USER_NAME}_password",
    # )
    print(master_workbook_name)
    print(name_dashboard)
    print(export)
    print(tabs)
    print(countries)
    print(tableau_folder)
    print(translate_sheet_table)
    print(email)
    try:
        if run:
            # tableau_id_project = find_tableau_project(
            #     tableau_folder, user_name, password
            # )
            # download_workbook(user_name, password, master_workbook_name)
            shutil.copy('source_template/BMW media insights.twbx','BMW media insights.twbx')
            unzip_workbook()
            time.sleep(4)
            # download_pictures()
            # time.sleep(8)
            countries_list = countries.split(",")
            modify_xml(countries_list)
            xmls = glob.glob("test_*")
            for xml_file in xmls:
                country = xml_file[xml_file.find("_") + 1 :]
                country = country[: country.find(".")]
                country = country.upper()
                print(country)

                # translate_manu(xml_file, translate_sheet_table, country)
            zip_twbx()
            time.sleep(2)
            # xmls = glob.glob("test_*.twbx")
            # for xml_file in xmls:
            #     country = xml_file[xml_file.find("_") + 1 :]
            #     country = country[: country.find(".")]
            #     country = country.upper()
            #     print(country)
            #     publish_workbook(
            #         user_name,
            #         password,
            #         name_dashboard,
            #         tabs,
            #         export,
            #         tableau_id_project,
            #         country,
            #         xml_file,
            #     )
            delete_files = ["*.twb","*.zip","Data","Image"]
            for files_ext in delete_files:
                if '.' in files_ext :
                    files = glob.glob(files_ext)
                    for f in files:
                        os.remove(f)
                else :
                    shutil.rmtree(files_ext)
    except Exception:
        trace = str(traceback.format_exc())
        print(trace)

        pass


def main():
    workbook_creation("a","dash",'exp','tabs','fin,nor','folder','tst',True,'abc@gm.com')
    #zip_twbx()
    
    """master_workbook_name = "Telia Crowd Insights - Data Export - Master Version"  # Crowd Insights for Municipalities - Sweden DEV_ID
    name_dashboard = "Telia Crowd Insisghts"
    export = False
    tabs = False
    countries = ""
    tableau_folder = "Telia Crowd Insights"
    translate_sheet_table = "generic_sheet_sync"""
"""
    query_labels = {"function": "workbooks_countries", "country": "all"}
    sql = "SELECT * FROM `telia-ddi-utils.tableau_countries_wbs.workbooks`"
    client = bigquery.Client(
        project="telia-ddi-no-prod",
        default_query_job_config=bigquery.QueryJobConfig(
            connection_properties=[
                bigquery.query.ConnectionProperty(
                    key="query_label",
                    value=",".join([":".join([k, v]) for k, v in query_labels.items()]),
                ),
            ],
        ),
    )
    workbooks_df = client.query(sql, project="telia-ddi-no-prod").to_dataframe()
    workbooks_df.apply(
        lambda row: workbook_creation(
            row["master_workbook_name"],
            row["name_dashboard"],
            row["export"],
            row["tabs"],
            row["countries"],
            row["tableau_folder"],
            row["translate_sheet_table"],
            row["run"],
            row[
                "email"
            ],  # previously used for sending emails via SendGrid, not active anymore
        ),
        axis=1,
    )
    """


if __name__ == "__main__":
    typer.run(main)