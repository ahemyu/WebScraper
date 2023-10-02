##################################################
# sites_tested: 
# https://de.mitsubishielectric.com/fa/products/drv/servo/mr_j4/servo-amplifier/mr-j4-100b4-rj.html -> Needs click automation for language selections
# https://de.mitsubishielectric.com/fa/products/drv/servo/mr_j5/servo-amplifier/mr-j5-40g-rj.html -> Needs click automation for language selections
# https://de.mitsubishielectric.com/fa/de_en/products/drv/inv/fr_a800/fra800e/fr-a840-00126-e2-60.html
# https://de.mitsubishielectric.com/fa/products/edge/melipc/mi5000/mi5000/mi5122-vw.html
# https://de.mitsubishielectric.com/fa/products/edge/melipc/mi3000/mi3000/mi3321g-w.html
# https://de.mitsubishielectric.com/fa/products/edge/melipc/mi2000/mi2000/mi2012-w.html
#################################################
import os.path
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, WebDriverException
from typing import Generator
from decouple import config
import time
import json
import winsound


# print(os.environ.get('USERNAME'))

os.chdir("C:\\Users\\GoekcekE\\Desktop\\repo\\WebScrapper")
options = Options()
options.add_argument('--headless=new')
browser = webdriver.Chrome()
# create human actions
action = ActionChains(browser)

# Constants for JSON file names (to keep Code DRY)
ALL_PRODUCT_URLS_JSON = "All_Product_UrlsV5_with_pagination.json"
ERROR_LOG_JSON = "Error_Log.json"
SERIES_PAGE_URLS_JSON = "Series_Page_UrlsV2.json"

def read_json(filename: str) -> json.JSONDecoder:
    with open(filename, "r", encoding="utf8") as in_file:
        return json.load(in_file)

## version without directory specification
# def write_json(needed_data, mode: str, filename: str = "AAS_Manuals.json"):
    
#     # Replace '/' with '|'
#     sanitized_filename = filename.replace('/', '_')
#     print(f"Debug: Writing to {sanitized_filename}")

#     with open(sanitized_filename, mode, encoding='utf8') as outfile:
#         json.dump(needed_data, outfile, indent=2, ensure_ascii=False)


# version with directory specification 
def write_json(needed_data, mode: str, filename: str = "AAS_Manuals.json", directory: str = ""):
    # print(f"Debug: Filename type = {type(filename)}, value = {filename}")
    # print(f"Debug: Directory type = {type(directory)}, value = {directory}")

    # Replace '/' with '_'
    sanitized_filename = filename.replace('/', '_')
    
    # If a directory is specified, append it to the filename
    if directory:
        # print(f"Debug: Joining {directory} and {sanitized_filename}")
        sanitized_filename = directory + sanitized_filename
    
    # print(f"Debug: Writing to {sanitized_filename}")
    
    with open(sanitized_filename, mode, encoding='utf8') as outfile:
        json.dump(needed_data, outfile, indent=2, ensure_ascii=False)


def check_if_modal_exists() -> bool:
    """Use to closer the modal window at the beginneing of the session"""
    modal_button = check_if_element_is_visible(5, By.XPATH, "/html/body/div[2]/div[2]/div/div[1]/button")
    return modal_button


def check_if_cookies_exists() -> bool:
    """Use to accept all cookies at the beginning of the session"""
    cookies_button = check_if_element_is_visible(5, By.XPATH, "//*[@id='__next']/div[3]/div[2]/button[3]")
    return cookies_button


def if_modal_and_cookies_exists_click_close(modal_button: bool, cookies_button: bool) -> None:
    if modal_button:
        find_element_and_click("/html/body/div[2]/div[2]/div/div[1]/button")
    if cookies_button:
        find_element_and_click("//*[@id='__next']/div[3]/div[2]/button[3]")


def log_in(user_name: str, password: str):
    browser.get('https://de.mitsubishielectric.com/fa')
    time.sleep(1)
    modal = check_if_modal_exists()
    cookies = check_if_cookies_exists()
    if_modal_and_cookies_exists_click_close(modal, cookies)
    browser.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div/div/div[2]/a[2]/button').click()
    user_name_input = browser.find_element(By.ID, 'username')
    password_input = browser.find_element(By.ID, 'password')
    log_in_button = browser.find_element(By.ID, 'kc-login')
    action.move_to_element(user_name_input).perform()
    action.click().perform()
    action.send_keys(user_name).perform()
    time.sleep(1)
    action.move_to_element(password_input).perform()
    action.click().perform()
    action.send_keys(password).perform()
    time.sleep(1)
    log_in_button.click()



def grab_urls_in_main_page() -> list[str]:
    browser.get("https://de.mitsubishielectric.com/fa/de_en/products")
    modal = check_if_modal_exists()
    cookies = check_if_cookies_exists()
    if_modal_and_cookies_exists_click_close(modal, cookies)
    main = browser.find_element(By.CLASS_NAME, 'Content_main___eR2u')
    links = main.find_elements(By.CLASS_NAME, 'LinkList_iconLink__77q_o')
    link_list = [x.get_attribute("href") for x in links]
    return link_list


def grab_urls_in_series_page(main_page_urls: list = None, is_initial: bool = False, filename: str = SERIES_PAGE_URLS_JSON) -> None:
    urls = []  
    read_data = {}  

    # Check if the file with 'filename' exists and is readable, read the JSON data if it does.
    if os.path.isfile(filename) and os.access(filename, os.R_OK):
        read_data = read_json(filename)
    else:
        read_data = {"series_page_urls": []}

    # Iterate through each URL in 'main_page_urls' to scrape data
    for url in main_page_urls:
        browser.get(url)
        # If this is the initial page load, check for modals and cookies and close them if present.
        if is_initial:
            modal = check_if_modal_exists()
            cookies = check_if_cookies_exists()
            if_modal_and_cookies_exists_click_close(modal, cookies)

        main = browser.find_element(By.CLASS_NAME, 'Content_main___eR2u')

        # Find all divs that match the class name 'Grid_col-md-4__mwcj3' within the main content
        div_columns = main.find_elements(By.CLASS_NAME, 'Grid_col-md-4__mwcj3')

        # Iterate through each div to find series page URLs
        for div in div_columns:
            lower_link_container = div.find_elements(By.CLASS_NAME, 'LinklistTeaser_linkList__l9h5j')
            
            # If no link containers are found, directly grab the header link
            if len(lower_link_container) <= 0:
                header = div.find_element(By.CLASS_NAME, 'LinklistTeaserHeader_link__jhCiA')
                urls.append(header.get_attribute('href'))

            # If link containers are present, iterate through them to collect URLs
            for lower_link in lower_link_container:
                a_tag = lower_link.find_elements(By.TAG_NAME, 'a')
                for link in a_tag:
                    read_data["series_page_urls"].append(link.get_attribute("href"))

    # Write the collected series page URLs back to the JSON file
    write_json(read_data, "w", filename)


def grab_product_urls(pagination_state: dict, series_urls: list, url: str, i: int, is_initial: bool, filename: str = ALL_PRODUCT_URLS_JSON):
    embedded = []
    product_urls = []
    error = read_json(ERROR_LOG_JSON)
    error["Error_Log"] = []
    try:
        browser.get(url)

        if is_initial:
            modal_exists = check_if_modal_exists()
            cookies_exists = check_if_cookies_exists()
            if_modal_and_cookies_exists_click_close(modal_exists, cookies_exists)

        pagination_state["product_list_visible"] = check_if_element_is_visible(
            120,
            By.CLASS_NAME,
            "ProductList_content__aeHQs"
        )

        pagination_state["product_links_visible"] = check_if_element_is_visible(
            5,
            By.CLASS_NAME,
            "ProductList_item__7P_Di"
        )
        pagination_state["pagination_visible"] = check_if_element_is_visible(
            5,
            By.CLASS_NAME,
            'Pagination_page__UPea8'
        )

        # if product link goes one step deeper to get to product page
        if not pagination_state["product_list_visible"]:
            grid_col_3 = check_if_element_is_visible(
                5,
                By.XPATH,
                "//div[contains(@class, 'Content_main___eR2u')]/div[contains(@class, 'Grid_row__14f8y')]/div[contains(@class, 'Grid_col-md-3__qW9oL')]")
            grid_col_4 = check_if_element_is_visible(
                5,
                By.XPATH,
                "//div[contains(@class, 'Content_main___eR2u')]/div[contains(@class, 'Grid_row__14f8y')]/div[contains(@class, 'Grid_col-md-4__mwcj3')]")
            if grid_col_3:
                main = browser.find_element(By.CLASS_NAME, 'Content_main___eR2u')
                div_columns = main.find_elements(By.CLASS_NAME, 'Grid_col-md-3__qW9oL')
                for div in div_columns:
                    lower_link_container = div.find_elements(By.CLASS_NAME, 'LinklistTeaser_linkList__l9h5j')
                    if len(lower_link_container) <= 0:
                        header = div.find_element(By.CLASS_NAME, 'LinklistTeaserHeader_link__jhCiA')
                        print("appending_upperlink from css grid 3")
                        series_urls.append(header.get_attribute('href'))
                        write_json(series_urls, "w", SERIES_PAGE_URLS_JSON)

                    for lower_link in lower_link_container:
                        a_tag = lower_link.find_elements(By.TAG_NAME, 'a')
                        for link in a_tag:
                            print("appending lowerLinks from css grid 3")
                            series_urls.append(link.get_attribute("href"))
                            write_json(series_urls, "w", SERIES_PAGE_URLS_JSON)

            elif grid_col_4:
                main = browser.find_element(By.CLASS_NAME, 'Content_main___eR2u')
                div_columns = main.find_elements(By.CLASS_NAME, 'Grid_col-md-4__mwcj3')
                for div in div_columns:
                    lower_link_container = div.find_elements(By.CLASS_NAME, 'LinklistTeaser_linkList__l9h5j')
                    if len(lower_link_container) <= 0:
                        header = div.find_element(By.CLASS_NAME, 'LinklistTeaserHeader_link__jhCiA')
                        print("appending upper links from css grid 4")
                        embedded.append(header.get_attribute('href'))

                    for lower_link in lower_link_container:
                        a_tag = lower_link.find_elements(By.TAG_NAME, 'a')
                        for link in a_tag:
                            print("appending lowerLinks from css grid 4")
                            embedded.append(link.get_attribute("href"))

            else:
                while pagination_state["retry"] < 4:
                    browser.refresh()
                    pagination_state["retry"] += 1
                    pagination_state["product_list_visible"] = check_if_element_is_visible(
                        30,
                        By.CLASS_NAME,
                        "ProductList_content__aeHQs"
                    )
                    if pagination_state["product_list_visible"]:
                        pagination_state["retry"] = 0
                        break

        if pagination_state["pagination_visible"]:
            try:
                main = browser.find_element(By.CLASS_NAME, 'Content_main___eR2u')
                div_with_link = main.find_elements(By.CLASS_NAME, "ProductList_item__7P_Di")
                contains_more_than3 = check_if_element_is_visible(5, By.XPATH,
                                                                  '//li[contains(@class,  "Pagination_page__UPea8")][4]')
                if contains_more_than3:
                    pages = int(
                        main.find_element(By.XPATH, '//li[contains(@class, "Pagination_page__UPea8")][4]').text)
                    pagination_state["page_length"] = pages
                else:
                    pages = len(main.find_elements(By.XPATH, '//li[contains(@class, "Pagination_page__UPea8")]'))
                    pagination_state["page_length"] = pages
                while pagination_state["current_page"] < pages:
                    pagination_state["link_length_per_page"] = len(div_with_link)

                    print(pagination_state)
                    time.sleep(3)
                    main = browser.find_element(By.CLASS_NAME, 'Content_main___eR2u')
                    div_with_link = main.find_elements(By.CLASS_NAME, "ProductList_item__7P_Di")
                    next_page = main.find_element(By.CLASS_NAME, "Pagination_next__KWtNc")
                    if pagination_state["error"]:
                        browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                        time.sleep(5)
                        browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                        time.sleep(5)
                        action.move_to_element(next_page).perform()
                        time.sleep(3)
                        action.click(next_page).perform()
                        pagination_state["product_list_visible"] = False
                        pagination_state["product_links_visible"] = False
                        pagination_state["pagination_visible"] = False

                    elif all([pagination_state["product_list_visible"], pagination_state["product_links_visible"],
                              pagination_state["pagination_visible"]]) and not pagination_state["error"]:
                        pagination_state["total_link_length"] += pagination_state["link_length_per_page"]
                        for link in div_with_link:
                            href = link.find_element(By.CLASS_NAME, 'ImageTextTeaser_titleLink__sdGg6') \
                                .get_attribute("href")
                            product_urls.append(href)
                            if os.path.exists(
                                    filename):  # change to product_urls in production
                                data = read_json(filename)
                                data["Product_Urls"].append(href)
                                write_json(data, "w", filename)
                            else:
                                write_json({"Product_Urls": product_urls}, "w",
                                           filename)

                        if pagination_state["current_page"] < pages:
                            try:
                                pagination_state["current_page"] += 1

                                browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                                time.sleep(5)
                                browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                                time.sleep(5)
                                action.move_to_element(next_page).perform()
                                time.sleep(3)
                                action.click(next_page).perform()
                                pagination_state["product_list_visible"] = False
                                pagination_state["product_links_visible"] = False
                                pagination_state["pagination_visible"] = False
                            except (WebDriverException, Exception) as e:
                                print(e)
                                pagination_state["error"] = True
                                error["Error_Log"].append({
                                    "Error": f"{e}",
                                    "Series_url_index": i,
                                    "Series_url": url,
                                    "Time": f"{datetime.datetime.now()}"
                                })
                                write_json(error, "w", ERROR_LOG_JSON)
                        else:
                            pagination_state["current_page"] += 1

                    elif not pagination_state["product_list_visible"]:
                        while not pagination_state["product_list_visible"]:
                            pagination_state["product_list_visible"] = check_if_element_is_visible(
                                5,
                                By.CLASS_NAME,
                                "ProductList_content__aeHQs"
                            )

                            pagination_state["product_links_visible"] = check_if_element_is_visible(
                                5,
                                By.CLASS_NAME,
                                "ImageTextTeaser_titleLink__sdGg6"
                            )

                            pagination_state["pagination_visible"] = check_if_element_is_visible(
                                5,
                                By.CLASS_NAME,
                                'Pagination_page__UPea8'
                            )

            except (WebDriverException, Exception) as e:
                print(e)
                error["Error_Log"].append({
                    "Error": f"{e}",
                    "Series_url_index": i,
                    "Series_url": url,
                    "Time": f"{datetime.datetime.now()}"
                })
                write_json(error, "w", ERROR_LOG_JSON)
        elif not pagination_state["pagination_visible"]:
            main = browser.find_element(By.CLASS_NAME, 'Content_main___eR2u')
            div_with_link = main.find_elements(By.CLASS_NAME, "ProductList_item__7P_Di")
            for link in div_with_link:
                href = link.find_element(By.CLASS_NAME, 'ImageTextTeaser_titleLink__sdGg6') \
                    .get_attribute("href")
                product_urls.append(href)
                if os.path.exists(filename):  # change to product_urls in production
                    data = read_json(filename)
                    data["Product_Urls"].append(href)
                    write_json(data, "w", filename)
                else:
                    write_json({"Product_Urls": product_urls}, "w",
                               filename)

    except (WebDriverException, Exception) as e:
        print(e)
        error["Error_Log"].append({
            "Error": f"{e}",
            "Series_url_index": i,
            "Series_url": url,
            "Time": f"{datetime.datetime.now()}"
        })
        write_json(error, "w", ERROR_LOG_JSON)


def pagination_hof(
        product_url_list: list = None,
        series_urls: list = None,
        get_document_links: bool = False,
        get_product_links: bool = False,
        is_initial: bool = False,
        filename: bool = ALL_PRODUCT_URLS_JSON
):
    pagination_state: dict[str, str | int | bool] = {
        "Get_product_links": get_product_links,
        "Get_document_links": get_document_links,
        "Main_content_page_visible": False,
        "product_list_visible": False,
        "product_links_visible": False,
        "pagination_visible": False,
        "Next_pagination_button_isDisplayed": False,
        "Current_URL": None,
        "current_page": 0,
        "page_length": 0,
        "link_length_per_page": 0,
        "total_link_length": 0,
        "retry": 0,
        "error": False
    }

    # for testing purposes
    urls = ["https://de.mitsubishielectric.com/fa/de_en/products/cnt/plc/plcr/base_unit"]

    if pagination_state["Get_product_links"]:
        for i, url in enumerate(series_urls):
            pagination_state["Current_URL"] = url
            grab_product_urls(pagination_state, series_urls, url, i, is_initial=is_initial, filename=filename)
    elif pagination_state["Get_document_links"]:
        for i, url in enumerate(product_url_list):
            # TODO Modify below function to fit this HOF
            parse_product_page()
            pass


def check_if_element_is_visible(seconds: int, by_type: object, locator: str) -> bool:
    """Check if a html element is visible and returns a bool"""
    wait = WebDriverWait(browser, seconds)
    try:
        wait.until(
            EC.presence_of_element_located((by_type, locator)))
        return True
    except TimeoutException:
        return False


def find_element_and_click(locator) -> None:
    """Finds a web element to be clicked"""
    button = browser.find_element(By.XPATH, locator)
    button.click()


def get_product_series_and_name() -> dict:
    """
    Grabs the product name and series name and product type from the technical information tab
    and returns the basic data structure needed to append the document information. 
    """

    browser.implicitly_wait(3)  # wait for table elements to load in
    product_type_exists = check_if_element_is_visible(20, By.XPATH,
                                                      '//*[@id="__next"]/div[3]/div[1]/div[2]/div[2]/div/div[1]/div/div[2]/table/tr[2]/td')

    series_name_exists = check_if_element_is_visible(20, By.XPATH,
                                                     '//*[@id="__next"]/div[3]/div[1]/div[2]/div[2]/div/div[1]/div/div[2]/table/tr[1]/td')
    product_name_exists = check_if_element_is_visible(20, By.XPATH, '//*[@id="__next"]/div[3]/div[1]/div[2]/h1')

    checks = {
        "product_type_exists": product_type_exists,
        "series_name_exists": series_name_exists,
        "product_name_exists": product_name_exists
    }

    match checks:
        case {"product_type_exists": True, "series_name_exists": True, "product_name_exists": True}:
            product_type = browser.find_element(By.XPATH,
                                                '//*[@id="__next"]/div[3]/div[1]/div[2]/div[2]/div/div[1]/div/div[2]/table/tr[2]/td')
            series_name = browser.find_element(By.XPATH,
                                               '//*[@id="__next"]/div[3]/div[1]/div[2]/div[2]/div/div[1]/div/div[2]/table/tr[1]/td')
            product_name = browser.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div[1]/div[2]/h1')
            return {
                "series_name": series_name.text,
                "product_type": product_type.text,
                "product_name": product_name.text,
                "documents": []
            }
        case {"product_type_exists": False, "series_name_exists": True, "product_name_exists": True}:
            series_name = browser.find_element(By.XPATH,
                                               '//*[@id="__next"]/div[3]/div[1]/div[2]/div[2]/div/div[1]/div/div[2]/table/tr[1]/td')
            product_name = browser.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div[1]/div[2]/h1')
            return {
                "series_name": series_name.text,
                "product_name": product_name.text,
                "documents": []
            }
        case {"product_type_exists": True, "series_name_exists": False, "product_name_exists": True}:
            product_type = browser.find_element(By.XPATH,
                                                '//*[@id="__next"]/div[3]/div[1]/div[2]/div[2]/div/div[1]/div/div[2]/table/tr[2]/td')
            product_name = browser.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div[1]/div[2]/h1')
            return {
                "product_type": product_type.text,
                "product_name": product_name.text,
                "documents": []
            }
        case {"product_type_exists": False, "series_name_exists": False, "product_name_exists": True}:
            product_name = browser.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div[1]/div[2]/h1')
            return {
                "product_name": product_name.text,
                "documents": []
            }


def is_manual(data: dict, content_string: list, link: str = None) -> None:
    """Checks data of type Manual"""
    if "Manual" in content_string:
        note = content_string[6] if len(content_string) > 6 else ''
        try:
           
            data['documents'].append(
                {
                    "doc_name": content_string[0],
                    "doc_language": content_string[2].split(" ")[0],
                    "doc_type": content_string[5],
                    "doc_size": content_string[4],
                    "doc_year": content_string[2].split(' ')[1].replace("(", '').replace(")", '').split("/")[1],
                    "doc_version": content_string[2].split(' ')[1].replace("(", '').replace(")", '').split("/")[0],
                    "doc_extension": content_string[3],
                    "doc_link": link
                }
            )
        except IndexError as e:
            print(f"Data structure not correct there was an {e}. Creating new data structure")
            try:
                data['documents'].append(
                    {
                        "doc_name": content_string[0],
                        "doc_language": content_string[2],
                        "doc_type": content_string[5],
                        "doc_size": content_string[4],
                        "doc_extension": content_string[3],
                        "doc_link": link,
                        "note": note
                    }
                )
            except IndexError as e:
                print(f"Data structure not correct there was an {e}. Creating new data structure")
                data['documents'].append(
                    {
                        "doc_name": content_string[0],
                        "doc_language": content_string[2].split(" ")[0],
                        "doc_type": content_string[5],
                        "doc_size": content_string[4],
                        "doc_year": content_string[2].split(' ')[1].replace("(", '').replace(")", '').split("/")[1],
                        "doc_extension": content_string[3],
                        "doc_link": link,
                        "note": note
                    }
                )
        if "Handbücher" in content_string:
            print("From Handbucher")
            try:
                data['documents'].append(
                    {
                        "doc_name": content_string[0],
                        "doc_language": content_string[2].split(" ")[0],
                        "doc_type": content_string[5],
                        "doc_size": content_string[4],
                        "doc_year": content_string[2].split(' ')[1].replace("(", '').replace(")", '').split("/")[1],
                        "doc_extension": content_string[3],
                        "doc_link": link,
                        "note": note
                    }
                )
            except IndexError as e:
                print(f"Data structure not correct there was an {e}. Creating new data structure")
                data['documents'].append(
                    {
                        "doc_name": content_string[0],
                        "doc_language": content_string[2].split(" ")[0],
                        "doc_type": content_string[5],
                        "doc_size": content_string[4],
                        "doc_year": content_string[2].split(' ')[1].replace("(", '').replace(")", '').split("/")[1],
                        "doc_extension": content_string[3],
                        "doc_link": link,
                        "note": note
                    }
                )


def is_firmware(data: dict, content_string: list, link: str = None) -> None:
    """Checks data of Firmware"""
    if "Firmware" in content_string:
        note = content_string[5] if len(content_string) > 5 else ''

        data['documents'].append(
            {
                "doc_name": content_string[0],
                "doc_type": content_string[4],
                "doc_size": content_string[3],
                "doc_extension": content_string[2],
                "doc_link": link,
                "note": note
            }
        )


def is_cad_files(data: dict, content_string: list, link: str = None) -> None:
    """Checks data of type Manual"""
    if "CAD Files" in content_string:
        note = content_string[5] if len(content_string) > 5 else ''
        data['documents'].append(
            {
                "doc_name": content_string[0],
                "doc_type": content_string[4],
                "doc_size": content_string[3],
                "doc_extension": content_string[2],
                "doc_link": link,
                "note": note
            }
        )

    if "CAD-Dateien" in content_string:
        data['documents'].append(
            {
                "doc_name": content_string[0],
                "doc_type": content_string[4],
                "doc_size": content_string[3],
                "doc_extension": content_string[2],
                "doc_link": link,
                "note": note
            }
        )


def is_network_configuration_file(data: dict, content_string: list, link: str = None) -> None:
    if "Network Configuration Files" in content_string:
        # there are two different data structures in this category
        note = content_string[5] if len(content_string) > 5 else ''
        try:
            data['documents'].append(
                {
                    "doc_name": content_string[0],
                    "doc_type": content_string[4],
                    "doc_size": content_string[3],
                    "doc_extension": content_string[2],
                    "doc_link": link,
                    "Note": note
                }
            )
        except IndexError as e:
            print(f"Data structure not correct there was an {e}. Creating new data structure")
            data['documents'].append(
                {
                    "doc_name": content_string[0],
                    "doc_type": content_string[4],
                    "doc_size": content_string[3],
                    "doc_extension": content_string[2],
                    "doc_link": link,
                }
            )
        if "Netzwerkkonfigurations-Dateien" in content_string:
            # there are two different data structures in this category
            try:
                data['documents'].append(
                    {
                        "doc_name": content_string[0],
                        "doc_type": content_string[4],
                        "doc_size": content_string[3],
                        "doc_extension": content_string[2],
                        "doc_link": link,
                        "Note": note
                    }
                )
            except IndexError as e:
                print(f"Data structure not correct there was an {e}. Creating new data structure")
                data['documents'].append(
                    {
                        "doc_name": content_string[0],
                        "doc_type": content_string[4],
                        "doc_size": content_string[3],
                        "doc_extension": content_string[2],
                        "doc_link": link,
                    }
                )


def is_catalogue(data: dict, content_string: list, link: str = None) -> None:
    pass
    if "Catalogues" in content_string:
        note = content_string[6] if len(content_string) > 6 else ''
        try:
            data['documents'].append(
                {
                    "doc_language": content_string[2].split(" ")[0],
                    "doc_name": content_string[0],
                    "doc_type": content_string[5],
                    "doc_size": content_string[4],
                    "doc_extension": content_string[3],
                    "doc_link": link,
                    "note": note
                }
            )
        except IndexError as e:
            print(f"Data structure not correct there was an {e}. Creating new data structure")
            data['documents'].append(
                {
                    "doc_language": content_string[2].split(" ")[0],
                    "doc_name": content_string[0],
                    "doc_type": content_string[5],
                    "doc_size": content_string[4],
                    "doc_extension": content_string[3],
                    "doc_link": link
                }
            )


def is_certificate(data: dict, content_string: list, link: str = None) -> None:
    note = content_string[6] if len(content_string) > 6 else ''
    if 'Zertifikate' in content_string:
        
        data['documents'].append(
            {
                "doc_language": content_string[2].split(" ")[0],
                "doc_name": content_string[0],
                "doc_type": content_string[5],
                "doc_size": content_string[4],
                "doc_extension": content_string[3],
                "doc_link": link,
                "note": note,
                "doc_year": content_string[2].split(' ')[1].replace("(", '').replace(")", '').split("/")[0]
            }
        )

    if 'Certificates' in content_string:
        # there are two different data structures in this category
        try:
            if release_year := content_string[2].split(' ')[1]:
                data['documents'].append(
                    {
                        "doc_name": content_string[0],
                        "doc_release_year": release_year.replace("(", '').replace(")", '').split("/")[0],
                        "doc_language": content_string[2].split(" ")[0],
                        "doc_type": content_string[5],
                        "doc_size": content_string[4],
                        "doc_extension": content_string[3],
                        "doc_link": link,
                        "note": note
                    }
                )
        except IndexError as e:
            print(f"Data structure not correct there was an {e}. Creating new data structure")

            data['documents'].append(
                {
                    "doc_name": content_string[0],
                    "doc_language": content_string[2].split(" ")[0],
                    "doc_type": content_string[5],
                    "doc_size": content_string[4],
                    "doc_extension": content_string[3],
                    "doc_link": link,
                    "note": note
                }
            )


def is_software(data: dict, content_string: list, link: str = None) -> None:
    if 'Software' in content_string:
        note = content_string[6] if len(content_string) > 6 else ''
        data['documents'].append(
            {
                "doc_name": content_string[0],
                "doc_language": content_string[2].split(" ")[0],
                "doc_type": content_string[5],
                "doc_size": content_string[4],
                "doc_year": content_string[2].split(' ')[1].replace("(", '').replace(")", '').split("/")[1],
                "doc_version": content_string[2].split(' ')[1].replace("(", '').replace(")", '').split("/")[0],
                "doc_extension": content_string[3],
                "doc_link": link,
                "note": note
            }
        )


def is_program_axamples_and_or_function_blocks(data: dict, content_string: list, link: str = None) -> None:
    if 'Program Examples / Function Blocks' in content_string:
        note = content_string[5] if len(content_string) > 6 else ''
        data['documents'].append(
            {
                "doc_name": content_string[0],
                "doc_type": content_string[4],
                "doc_size": content_string[3],
                "doc_extension": content_string[2],
                "doc_link": link,
                "note": note
            }
        )


def get_doc_text(url, data: dict, web_element: list = None) -> dict:
    """
    Function will grab an array of strings which will need to be sliced to get te appropriate data and appended to the basic data structure
    -----------------------------------------------
    EX:
    [
    'MELIPC MI5000 Series Safety Guidelines\\n22.03.2023\\nEnglish (B/2019)\\nPDF\\n403.9 KiB\\nManual\\nSafety precautions for using the MELIPC MI5122-VW',
    'MELIPC MI5000 Series Programming Manual (VXWorks)\\n22.03.2023\\nEnglish (B/2019)\\nPDF\\n1.3 MiB\\nManual\\nFunctions required for programming MELIPC MI5122-VW',
    'MELIPC MI5000 Series Programming Manual (Windows)\\n22.03.2023\\nEnglish (B/2019)\\nPDF\\n673.7 KiB\\nManual\\nFunctions required for programming MELIPC MI5122-VW',
    "MELIPC MI5000 Series User's Manual (Application)\\n22.03.2023\\nEnglish (E/2019)\\nPDF\\n5.4 MiB\\nManual\\nFunctions and parameter settings of the MELIPC MI5122-VW",
    "MELIPC MI5000 Series User's Manual (Startup)\\n22.03.2023\\nEnglish (D/2019)\\nPDF\\n14.1 MiB\\nManual\\nSystem configuration, specifications, installation, wiring, maintenance, inspection, and troubleshooting of the MELIPC MI5122-VW",
    'UK Declaration of Conformity MELIPC MI5000\\n22.03.2023\\nEnglish (0/2021)\\nPDF\\n204.5 KiB\\nCertificates\\nUK Declaration of Conformity LVD/EMC/RoHS EN 61131-2:2007 EN IEC 63000:2018',
    'EC Declaration MELIPC MI5000\\n22.03.2023\\nEnglish (B/2021)\\nPDF\\n62.9 KiB\\nCertificates\\nEC Declaration of Conformity EMC/LVD/RoHS; CE certificates',
    'MELIPC Catalogue\\n22.03.2023\\nEnglish\\nPDF\\n13.0 MiB\\nCatalogues\\nIndustrial Coumputer MEILIPC Series MELIPC Product overview, Real-time Data Analyzer software, EdgeCross Software'
    ]

    """
    text = [x.text for x in web_element[:]]

    for i in range(len(text)):
        content_string = text[i].split("\n")
        # basic data structure
        try:
            data['documents'].append(
                {
                    "doc_name": content_string[0],
                    "doc_language": content_string[2].split(" ")[0],
                    "doc_type": content_string[5],
                    "doc_size": content_string[4],
                    "doc_year": content_string[2].split(' ')[1].replace("(", '').replace(")", '').split("/")[1],
                    "doc_version": content_string[2].split(' ')[1].replace("(", '').replace(")", '').split("/")[0],
                    "doc_extension": content_string[3],
                    "doc_link": None,
                    "note": content_string[6] if len(content_string) > 6 else ''
                }
            )

        # if an index error exists, use the following data structure below to match the proper data
        except IndexError as e:
            error_log = read_json(ERROR_LOG_JSON)
            print(f"Data structure not correct there was an {e}. Creating new data structure")
            content_string = text[i].split("\n")
            print(content_string)
            try:
                is_manual(data, content_string)
                is_firmware(data, content_string)
                is_cad_files(data, content_string)
                is_network_configuration_file(data, content_string)
                is_catalogue(data, content_string)
                is_certificate(data, content_string)
                is_software(data, content_string)
                is_program_axamples_and_or_function_blocks(data, content_string)
            except IndexError as e:
                error_data = {
                    "Error": str(e),
                    "URL": url,
                    "ContentString": str(content_string),
                    "Time": str(datetime.datetime.now())
                }
                error_log["Error"].append(error_data)
                write_json(error_data, "w", ERROR_LOG_JSON)

    return data


def clean_data(url, data: dict) -> dict:
    """Takes all data from the pulldown menus on the AAS Website """

    targeted_div = browser.find_elements(By.CLASS_NAME, 'RelatedDocumentCategoryCollapsible_item__EI__e')

    link_div_target = browser.find_elements(By.CLASS_NAME, 'RelatedDocumentCategoryCollapsible_item__EI__e')

    link = parse_links(link_div_target)

    # get_product_series_and_name(products, product_category, series_name)
    text_data = get_doc_text(url, data, targeted_div)
    documents = combine_data(text_data, link)
    return documents


def parse_languages(data: dict):
    mapping: dict[str, int | bool] = {
        "ELEMENT_VISIBLE": False,
        "SELECTED": False,
        "SELECTION_OPTIONS_VISIBLE": False,
        "RETRY": 0,
        "CURRENT_DROPDOWN_INDEX": 0,
        "TOTAL_DROPDOWNS": 0,
        "CURRENT_LANGUAGE_INDEX": 0,
        "TOTAL_LANGUAGES_IN_DROPDOWN": 0
    }

    language_selection_box = browser.find_elements(By.CLASS_NAME, 'Select_control___0xiB')
    language_selection_box.pop(0)
    mapping["TOTAL_DROPDOWNS"] = len(language_selection_box)
    while mapping["CURRENT_DROPDOWN_INDEX"] < len(language_selection_box):

        # scroll down to element
        browser.execute_script(
            "arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'})",
            language_selection_box[mapping["CURRENT_DROPDOWN_INDEX"]]
        )
        time.sleep(.5)
        # move cursor to element
        action.move_to_element(language_selection_box[mapping["CURRENT_DROPDOWN_INDEX"]])
        time.sleep(.5)
        # click element
        action.click()
        action.perform()
        mapping["SELECTED"] = True
        time.sleep(1)

        select_items = browser.find_element(By.CLASS_NAME, 'Select_menu__lvZp5')
        file_language = select_items.find_elements(By.CLASS_NAME, "Select_option__SGKWu")

        mapping["TOTAL_LANGUAGES_IN_DROPDOWN"] = len(file_language)
        while mapping["CURRENT_LANGUAGE_INDEX"] < len(file_language):
            # for debugging
            print(mapping)
            selection_menu = check_if_element_is_visible(5, By.CLASS_NAME, "Select_menu__lvZp5")
            if selection_menu:
                mapping["ELEMENT_VISIBLE"] = True

            if mapping["CURRENT_LANGUAGE_INDEX"] == 0:
                print(f"skipping first element")
                mapping["CURRENT_LANGUAGE_INDEX"] += 1

            elif mapping["ELEMENT_VISIBLE"]:
                half = len(file_language) // 2
                selection_elements = browser.find_elements(By.CLASS_NAME, 'Select_option__SGKWu')
                print(f"moving to element at index {mapping['CURRENT_LANGUAGE_INDEX']}")
                if mapping["CURRENT_LANGUAGE_INDEX"] <= half:

                    action.move_to_element(selection_elements[mapping["CURRENT_LANGUAGE_INDEX"]]).perform()
                    time.sleep(.5)
                    action.click(selection_elements[mapping["CURRENT_LANGUAGE_INDEX"]]).perform()
                    time.sleep(.5)
                    changed_data = language_selection_box[mapping["CURRENT_DROPDOWN_INDEX"]].find_element(
                        By.XPATH,
                        f"(//div[@class='Select_root__9vxgj SearchResultItem_select__RKoKh'])"  # gets the node
                        f"[{mapping['CURRENT_DROPDOWN_INDEX'] + 1}]"  # gets the index of node + 1                         
                        f"/parent::div/parent::div/parent::div"  # gets the parent of the parent of the parent
                    )
                    time.sleep(1)
                    language_data = changed_data.text.split("\n")
                    language_doc_link = changed_data.find_element(By.TAG_NAME, "a").get_attribute("href")
                    language_data.pop(2)

                    # is_manual(data, language_data, language_doc_link)
                    # is_firmware(data, language_data, language_doc_link)
                    # is_cad_files(data, language_data, language_doc_link)
                    # is_network_configuration_file(data, language_data, language_doc_link)
                    # is_catalogue(data, language_data, language_doc_link)
                    # is_certificate(data, language_data, language_doc_link)
                    # is_software(data, language_data, language_doc_link)
                    # is_program_axamples_and_or_function_blocks(data, language_data, language_doc_link)

                    mapping["CURRENT_LANGUAGE_INDEX"] += 1
                    mapping["SELECTED"] = False
                    mapping["ELEMENT_VISIBLE"] = False
                    mapping["SELECTION_OPTIONS_VISIBLE"] = False
                    try:
                        data['documents'].append(
                            {
                                "doc_name": language_data[0],
                                "doc_language": language_data[2].split(" ")[0],
                                "doc_type": language_data[5],
                                "doc_size": language_data[4],
                                "doc_year": language_data[2].split(' ')[1].replace("(", '').replace(")", '').split("/")[
                                    1],
                                "doc_version": language_data[2].split(' ')[1].replace("(", '').replace(")", '')
                                .split("/")[0],
                                "doc_extension": language_data[3],
                                "doc_link": language_doc_link,
                                "note": language_data[6]
                            }
                        )
                    except IndexError as e:
                        print(e)
                        print(language_data)
                        data['documents'].append(
                            {
                                "doc_name": language_data[0],
                                "doc_language": language_data[2].split(" ")[0],
                                "doc_type": language_data[5],
                                "doc_size": language_data[4],
                                "doc_year": language_data[2].split(' ')[1].replace("(", '').replace(")", ''),
                                "doc_extension": language_data[3],
                                "doc_link": language_doc_link,
                                "note": language_data[6]
                            }
                        )
                else:

                    action.scroll_to_element(selection_elements[-1]).perform()
                    time.sleep(.5)
                    browser.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'})",
                        language_selection_box[mapping["CURRENT_DROPDOWN_INDEX"]]
                    )
                    time.sleep(.5)
                    action.move_to_element(selection_elements[mapping["CURRENT_LANGUAGE_INDEX"]]).perform()
                    time.sleep(.5)
                    action.click(selection_elements[mapping["CURRENT_LANGUAGE_INDEX"]]).perform()
                    changed_data = language_selection_box[mapping["CURRENT_DROPDOWN_INDEX"]].find_element(
                        By.XPATH,
                        f"(//div[@class='Select_root__9vxgj SearchResultItem_select__RKoKh'])"  # gets the node
                        f"[{mapping['CURRENT_DROPDOWN_INDEX'] + 1}]"  # gets the index of node + 1                         
                        f"/parent::div/parent::div/parent::div"  # gets the parent of the parent of the parent
                    )
                    time.sleep(1)
                    language_data = changed_data.text.split("\n")
                    language_data.pop(2)
                    language_doc_link = changed_data.find_element(By.TAG_NAME, "a").get_attribute("href")
                    mapping["SELECTED"] = False
                    mapping["ELEMENT_VISIBLE"] = False
                    mapping["SELECTION_OPTIONS_VISIBLE"] = False
                    mapping["CURRENT_LANGUAGE_INDEX"] += 1
                    try:
                        data['documents'].append(
                            {
                                "doc_name": language_data[0],
                                "doc_language": language_data[2].split(" ")[0],
                                "doc_type": language_data[5],
                                "doc_size": language_data[4],
                                "doc_year": language_data[2].split(' ')[1].replace("(", '').replace(")", '').split("/")[
                                    1],
                                "doc_version": language_data[2].split(' ')[1].replace("(", '').replace(")", '')
                                .split("/")[0],
                                "doc_extension": language_data[3],
                                "doc_link": language_doc_link,
                                "note": language_data[6]
                            }
                        )
                    except IndexError as e:
                        print(e)
                        data['documents'].append(
                            {
                                "doc_name": language_data[0],
                                "doc_language": language_data[2].split(" ")[0],
                                "doc_type": language_data[5],
                                "doc_size": language_data[4],
                                "doc_year": language_data[2].split(' ')[1].replace("(", '').replace(")", '').split("/")[
                                    1],
                                "doc_version":
                                    language_data[2].split(' ')[1].replace("(", '').replace(")", '').split("/")[
                                        0],
                                "doc_extension": language_data[3],
                                "doc_link": language_doc_link,
                                "note": language_data[6]
                            }
                        )

            elif not mapping["ELEMENT_VISIBLE"]:
                while not mapping["ELEMENT_VISIBLE"] and not mapping["SELECTION_OPTIONS_VISIBLE"]:
                    action.move_to_element(language_selection_box[mapping["CURRENT_DROPDOWN_INDEX"]]).perform()
                    time.sleep(.5)
                    action.click(language_selection_box[mapping["CURRENT_DROPDOWN_INDEX"]]).perform()
                    time.sleep(.5)
                    mapping["SELECTED"] = True
                    time.sleep(1)
                    recheck_element = check_if_element_is_visible(5, By.CLASS_NAME, 'Select_menu__lvZp5')
                    mapping["ELEMENT_VISIBLE"] = recheck_element
                    check_selection_options = check_if_element_is_visible(5, By.CLASS_NAME, 'Select_option__SGKWu')
                    mapping["SELECTION_OPTIONS_VISIBLE"] = check_selection_options
        mapping["CURRENT_DROPDOWN_INDEX"] += 1
        mapping["CURRENT_LANGUAGE_INDEX"] = 0
    return data


def parse_links(links: list) -> Generator[str, None, None]:
    for a in links:
        links = a.find_elements(By.TAG_NAME, 'a')
        for link in links:
            yield link.get_attribute("href")


def combine_data(data: dict, links: Generator[str, None, None]) -> dict:
    for docs in data['documents']:
        docs["doc_link"] = next(links)
    return data


def click_to_destination():
    """Simulates a click to reveal text data from Java Script"""
    browser.implicitly_wait(3)
    download_tab = check_if_element_is_visible(20, By.XPATH, '//*[@id="__next"]/div[3]/div[1]/div[2]/div[2]/ul/li[4]/a')
    if download_tab:
        find_element_and_click('//*[@id="__next"]/div[3]/div[1]/div[2]/div[2]/ul/li[4]/a')

        # open all js clickable objects
        try:
            element = check_if_element_is_visible(20, By.XPATH,
                                                  '//*[@id="collapsible-trigger-collapsible_content__uycr6"]/span/div')
            if element:
                tabs = browser.find_elements(By.XPATH,
                                             '//*[@id="collapsible-trigger-collapsible_content__uycr6"]/span/div')
                for tab in tabs:
                    browser.execute_script("arguments[0].click();", tab)
        except (TimeoutException, ElementClickInterceptedException) as e:
            print(e)


def parse_product_page(urls: list = None, is_initial: bool = False) -> None:
    """
    Generic function to parse a product page and returns a dictionary:

    ex:

    {
        "series_name": "MELSERVO-J4",
        "product_type": "MR-J4",
        "product_name": "MR-J4-60B-RJ",
        "documents": [
            {
                'doc_extension': 'PDF',
                'doc_language': 'English',
                'doc_link': 'https://de.mitsubishielectric.com/fa/auth/login?locale=en-DE',
                'doc_name': 'Certificate of compliance (UL)',
                'doc_release_year': '2021',
                'doc_size': '2.0 MiB',
                'doc_type': 'Certificates',
                'note': 'UL Certificate of Conformity number: '
                        'UL-CA-L113619-41119-12309102-1 for MR-J5'
            }
        ]
    }
    """
    url_index = 0
    data = {
        "products": []
    }
    if is_initial:
        modal_exists = check_if_modal_exists()
        cookies_exists = check_if_cookies_exists()
        if_modal_and_cookies_exists_click_close(modal_exists, cookies_exists)

    try:
        for i, url in enumerate(urls):
            try:
                url_index = i
                browser.get(url)

                # get foundational data
                foundational_data = get_product_series_and_name()
                # click to desired result
                click_to_destination()
                # wait for data to load
                time.sleep(5)
                # grab the rest of the data
                complete_data = clean_data(url, foundational_data)
                main = browser.find_element(By.CLASS_NAME, "Content_main___eR2u")
                language_selection_box = main.find_elements(By.CLASS_NAME, 'Select_control___0xiB')
                if language_selection_box:
                    with_languages = parse_languages(complete_data)
                    data["products"].append(with_languages)
                    write_json(data["products"], "w", "All_Product_Documents_V5_with_languages_no_pagination.json")
                data["products"].append(complete_data)
                write_json(data, "w", "All_Product_Documents_V5_with_languages_no_pagination.json")
             
                #Write single data to file
                write_json(complete_data, "w", complete_data["product_name"] + ".json", "jsons/LV_Distri_Series/")
            except Exception as e:
                print(e)
                print("Failed for " + url)

    except WebDriverException:
        write_json(data, "w", "All_Product_Documents_V5_with_languages_no_pagination.json")
        write_json({"Date": f"{datetime.datetime.now()}", "Current_Url_index": url_index}, "w+", ERROR_LOG_JSON)


def run():
    pass


if __name__ == "__main__":

    #TODO::: complete Specs for Drivers and the remaining other Series

    # start_time = time.time()

    #Set these file names before running
    series_pages_urls_filename =  'Just_P_Manage_Series.json'
    product_pages_urls_filename =  'All_Prods_P_Manage_Series.json'# 'All_Lvi_Prods.json'# 'All_Robots_Prods.json'     
    """
    use below 2 functions to grab main and series urls or skip them and load directly from an existing file.
    """
    # main_page_urls = grab_urls_in_main_page()
    # grab_urls_in_series_page(main_page_urls=main_page_urls, is_initial=False, filename=series_pages_urls_filename)

    series_urls = read_json(series_pages_urls_filename)
    """
    Below use series urls to grab product urls or skip if you have product urls already in a list
    """
    pagination_hof(series_urls=series_urls["series_page_urls"], get_product_links=True, is_initial=True, filename=product_pages_urls_filename)
    """
    parse product urls to get document data. do not forget to log in 
    """

    log_in(user_name=config("NAME"), password=config("PASSWORD"))
    product_urls = read_json(product_pages_urls_filename)
    # parse_product_page(urls=product_urls["Product_Urls"], is_initial=True)
    #product_urls = {
    #    "Product_Urls" : [
    #        "https://de.mitsubishielectric.com/fa/products/drv/servo/mr_j4/servo-amplifier/mr-j4-60b-rj.html"
    #    ]
    #}
    parse_product_page(urls=product_urls["Product_Urls"], is_initial=True)
    
    #Just running it for one product
    #parse_product_page(urls=["https://de.mitsubishielectric.com/fa/de_de/products/drv/servo/mr_j5/servo-amplifier/mr-j5-100g-rj.html"], is_initial=True)

    browser.quit()
    print("Finished")
    winsound.Beep(440, 500)

    # end_time = time.time()
    # program_run_time = end_time - start_time
    # write_json(
    #     {"program_run_time": program_run_time},
    #     'a',
    #     "All_Product_Documents_V5_with_languages_no_pagination.json")
    # print(program_run_time)
