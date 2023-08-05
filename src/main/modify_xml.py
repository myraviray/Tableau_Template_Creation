def modify_xml_test(file_pattern, project, name_suffix, country, module, query_labels={}):
    query_labels["country"] = country
    query_labels["module"] = module
    query_labels["function"] = "modify_xml"
    print("Replace XML elements in template workbook")
    xml_file = glob.glob(file_pattern)
    xml = xml_file[0]
    f = codecs.open(xml, "r", "UTF-8")
    soup = BeautifulSoup((f.read()), "xml")

    # --- Replace XML tag contents
    # Change language/locale of the workbook to English
    # Note: CIFM is the only report that would need to have its locale changed
    # That is a TODO when the script starts working with CIFM
    wb_tag = soup.find("workbook")
    wb_tag["locale"] = "en_GB"

    # Corner case for Crowd Insights for Retail
    if "retails" in module or "retails_wifi" in module:
        # A. update minimum store chain selection in dropdown lists
        print(f"Module is '{module}', performing additional operations...")
        print("Querying for additional data...\n")
        project_id = "telia-ddi-delivery"
        client = bigquery.Client(
            project=project_id,
            default_query_job_config=bigquery.QueryJobConfig(
                connection_properties=[
                    bigquery.query.ConnectionProperty(
                        key="query_label",
                        value=",".join(
                            [":".join([k, v]) for k, v in query_labels.items()]
                        ),
                    ),
                ],
            ),
        )

        customer = name_suffix[name_suffix.find("_") + 1 :]
        customer_lower_case = customer.lower()
        sql = f"""
        SELECT MIN(CONCAT(chain,', ',REPLACE(store_name, ',', '' ))) AS min_name
        FROM `{project_id}.data_components_all_v1.general_store_location_all`
        WHERE
            customer='{customer}'
            AND country='{country}'
        """
        print(sql)
        df_replacements = client.query(sql).to_dataframe()
        print(
            f"\nAcquired replacement value for **minstorechain**: {df_replacements['min_name'].iloc[0]}"
        )

        print(
            f"Replacing value of **minstorechain** with {df_replacements['min_name'].iloc[0]}"
        )
        minstorechain_tags = soup.find_all(member=re.compile("\*\*minstorechain\*\*"))
        for tag in minstorechain_tags:
            # Warning: the member attribute value had trailing and ending &quot;
            # replace() is used to preserve Tableau field's string type within XML (?)
            tag["member"] = tag["member"].replace(
                "**minstorechain**", df_replacements["min_name"].iloc[0]
            )

        # B. Update URL for a button that leads to Export dashboard (created manually by Industry squad on customer demand)
        # The 'url' attribute has **countrycustomer** mark left by Tableau developer
        button_tags = soup.find_all(
            name="zone",
            attrs={
                "param": "Image/data download.png",
                "url": re.compile("\*\*countrycustomer\*\*"),
            },
        )
        export_url = f"{TABLEAU_SERVER_URL}/#/views/CrowdInsightsforRetail-Export{COUNTRY_NAME_DICT.get(country)}{customer_lower_case}/DailyAreaVisits"

        print(f"Updating URLs for Export dashboard to {export_url}")
        for tag in button_tags:
            tag["url"] = export_url

    print("Replace datasource instances")
    # The code fragment below covers the following XML tags:
    # Datasource reference(?):
    #   <datasources>
    #       <datasource caption='VALUE_TO_BE_CHECKED' ... ... .../>
    #   </datasources>

    # Datasource definition:
    #   <datasources>
    #       <datasource caption='VALUE_TO_BE_CHECKED' ... ... ...>
    #           <repository-location derived-from='VALUE_TO_BE_CHECKED' id='VALUE_TO_BE_CHECKED' ... />
    #           <connection ... ... dbname='VALUE_TO_BE_CHECKED' ... />
    #   </datasources>

    # Old versions of code were also adjusting XML tag strings at:
    #
    #   <attribute datatype='string' name='datasource'>STR_TO_BE_CHECKED</attribute>
    #
    # but it doesn't seem to be affecting the workbook publishing
    datasource_param = WORKBOOK_DATASOURCE_MAPPING.get(module)

    datasource_tags = soup.find_all(name="datasource", attrs={"caption": True})
    for ds_tag in datasource_tags:
        # Strip "caption" tail from substrings like ' | Project : HYPER-CVI-GENERIC '
        trimmed_caption = re.sub(r"( \| .*)", "", ds_tag["caption"])
        ds_tag["caption"] = trimmed_caption

        # Change project suffix in captions
        # Split between full-scoped and custom-scoped Data Sources
        # unless it's one of the static Data Sources
        if any(x in ds_tag["caption"] for x in datasource_param["static"]):
            continue
        elif any(x in ds_tag["caption"] for x in datasource_param["country_scoped"]):
            # Special case when need to change suffix by country code only rather than by full project name
            # TODO: combine both conditions into one?
            if "telia_scalable_500_1000_text" in ds_tag["caption"]:
                ds_tag["caption"] = ds_tag["caption"].replace("swe", country)
            else:
                ds_tag["caption"] = ds_tag["caption"].replace(
                    "telia-ddi-swe-prod", f"{project}"
                )
        elif any(x in ds_tag["caption"] for x in datasource_param["custom_scoped"]):
            ds_tag["caption"] = ds_tag["caption"].replace(
                "telia-ddi-swe-prod", f"{project}_{name_suffix}"
            )
        else:
            continue

        # Change repository location and connection
        # Caption from parent tag needs to lose spaces to get into 'repository-location' and 'connection'
        # Currently this needs to be done for telia_scalable_500_1000_text
        caption_payload = (
            ds_tag["caption"].replace(" ", "")
            if "telia_scalable_500_1000_text" in ds_tag["caption"]
            else ds_tag["caption"]
        )
        repo_loc_tag = ds_tag.find("repository-location")
        if repo_loc_tag is not None:
            repo_loc_tag["id"] = caption_payload
            repo_loc_tag[
                "derived-from"
            ] = f"{TABLEAU_SERVER_URL}/datasources/{caption_payload}"

        conn_tag = ds_tag.find("connection")
        if conn_tag is not None:
            conn_tag["dbname"] = caption_payload
            conn_tag["server-ds-friendly-name"] = caption_payload

    output_file_name = f"{module}_{project}_{name_suffix}.twb"
    with open(output_file_name, "w", encoding="UTF-8") as file:
        file.write(str(soup))

    return output_file_name