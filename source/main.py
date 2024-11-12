import requests
import random
import time
import csv
import bs4

FILENAME: str = "pricecharting_scraped_data.csv"
WEB_BASE_URL: str = "https://www.pricecharting.com"

# Some random user agents found in the site https://user-agents.net/
USER_AGENTS: list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    "TuneIn Radio Pro/30.1.0; iPhone12,1; iOS/18.0.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36",
    "radio.de 5.8.12 (iPad; iPhone OS 18.1; de_DE)",
    "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.0 Safari/537.36 CrKey/1.56.500000 DeviceType/SmartSpeaker [ip:93.66.124.203]"
]

def write_csv(csv_data: dict, filename: str) -> None:
    """
    Writes the dataset CSV with the given data and filename.
    :param csv_data: (dict) The dataset to write into a CSV.
    :param filename: (str) The filename (path) of the CSV to write.
    :return: It has no return.
    """
    try:
        csv_columns: list = ["Category", "Subcategory", "2ndSubcategory", "Name", "1stColumnPrice", "2ndColumnPrice", "3rdColumnPrice"]

        with open(file=filename, mode="w", newline="", encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(csv_columns)

            for csv_key in csv_data:
                for sub_cat in csv_data[csv_key]["subcategories"]:
                    if "subcategories" in csv_data[csv_key]["subcategories"][sub_cat]:
                        for sub_sub_cat in csv_data[csv_key]["subcategories"][sub_cat]["subcategories"]:
                            csv_writer.writerows(csv_data[csv_key]["subcategories"][sub_cat]["subcategories"][sub_sub_cat]["site_data"])
                    else:
                        csv_writer.writerows(csv_data[csv_key]["subcategories"][sub_cat]["site_data"])
    except Exception as e:
        print(e)

def get_headers() -> dict:
    """
    It returns a random user-agent for the headers.
    :return: (dict) The dict with a random user agent to use in the request.
    """
    try:
        user_agent = random.choice(USER_AGENTS)
        return {"User-Agent": user_agent}
    except Exception as e:
        print(e)

def get_delay() -> None:
    """
    It performs a random delay in the execution.
    :return: It has no return.
    """
    try:
        delay = random.uniform(a=1, b=3)
        time.sleep(delay)
    except Exception as e:
        print(e)

def get_site(url: str) -> str:
    """
    Gets the HTML of the given url.
    :param url: (str) The url to get its HTML.
    :return: (str) The HTML of the site.
    """
    try:
        # Make a request to the site
        site_response: requests.models.Response = requests.get(url=url, headers=get_headers())

        # Check if an error happened
        # If an error happened, then some of the exceptions will be printed and None will be returned
        site_response.raise_for_status()

        # Set a random delay so, the requests are not fully consecutive
        get_delay()

        # If everything is okay, the return the site html
        return site_response.text
    except requests.HTTPError as e:
        print("HTTP error with url:", url, "\n", e)
    except requests.ConnectionError as e:
        print("Connection error with url", url, "\n", e)
    except Exception as e:
        print("Error with url", url, "\n", e)
    return ""

def get_data(csv_data: dict) -> None:
    """
    Gets the data of all the products in PriceCharting and saves it into a dict.
    :param csv_data: (dict) The dictionary to fill with the data of all the products in PriceCharting.
    :return: It has no return.
    """
    try:
        # Base site
        base_site_html: str = get_site(WEB_BASE_URL)

        # Base site handling
        if base_site_html:
            beauty_soup_obj: bs4.BeautifulSoup = bs4.BeautifulSoup(markup=base_site_html, features="html.parser")
            h2_elements: bs4.element.ResultSet = beauty_soup_obj.find_all(name="h2", class_="more-browse")

            for h2_el in h2_elements:
                a_elements: bs4.element.ResultSet = h2_el.find_all(name="a")

                if a_elements:
                    category_names: list = [a.get_text(strip=True) for a in a_elements]
                    category_urls: list = [a_el["href"] for a_el in a_elements]

                    for cat_name, cat_url in zip(category_names, category_urls):
                        if cat_url.startswith("/"):
                            cat_url: str = WEB_BASE_URL + cat_url

                        csv_data[cat_name]: dict = {"site_url": cat_url, "subcategories": {}}

        # Categories handling
        for csv_key in csv_data:
            category_site_html: str = get_site(csv_data[csv_key]["site_url"])

            if category_site_html:
                beauty_soup_obj: bs4.BeautifulSoup = bs4.BeautifulSoup(markup=category_site_html, features="html.parser")
                home_box_all: bs4.element.ResultSet = beauty_soup_obj.find_all(name="div", class_="home-box all")

                if home_box_all:
                    a_elements: bs4.element.ResultSet = home_box_all[0].select(selector="ul li a")

                    for a_el in a_elements:
                        sub_cat_url: str = a_el["href"]
                        if sub_cat_url.startswith("/"):
                            sub_cat_url: str = WEB_BASE_URL + sub_cat_url

                        csv_data[csv_key]["subcategories"][a_el.get_text(strip=True)]: dict = {"site_url": sub_cat_url, "site_data": []}
                else:
                    h2_elements: bs4.element.ResultSet = beauty_soup_obj.find_all(name="h2", class_="more-browse")

                    for h2_el in h2_elements:
                        a_elements: bs4.element.ResultSet = h2_el.find_all(name="a")

                        if a_elements:
                            category_names: list = [a.get_text(strip=True) for a in a_elements]
                            category_urls: list = [a_el["href"] for a_el in a_elements]

                            for cat_name, cat_url in zip(category_names, category_urls):
                                if csv_data[csv_key]["site_url"].endswith("/"):
                                    cat_url: str = csv_data[csv_key]["site_url"] + cat_url[1:]
                                else:
                                    cat_url: str = WEB_BASE_URL + cat_url

                                csv_data[csv_key]["subcategories"][cat_name]: dict = {"site_url": cat_url, "subcategories": {}}

        # Sub-categories handling
        for csv_key in csv_data:
            for sub_cat in csv_data[csv_key]["subcategories"]:
                if "subcategories" in csv_data[csv_key]["subcategories"][sub_cat]:
                    sub_category_site_html: str = get_site(csv_data[csv_key]["subcategories"][sub_cat]["site_url"])

                    if sub_category_site_html:
                        beauty_soup_obj: bs4.BeautifulSoup = bs4.BeautifulSoup(markup=sub_category_site_html, features="html.parser")
                        home_box_all: bs4.element.ResultSet = beauty_soup_obj.find_all(name="div", class_="home-box all")

                        if home_box_all:
                            a_elements: bs4.element.ResultSet = home_box_all[0].select(selector="ul li a")

                            for a_el in a_elements:
                                sub_cat_url: str = a_el["href"]

                                if csv_data[csv_key]["site_url"].endswith("/"):
                                    sub_cat_url: str = csv_data[csv_key]["site_url"] + sub_cat_url[1:]
                                else:
                                    sub_cat_url: str = WEB_BASE_URL + sub_cat_url

                                csv_data[csv_key]["subcategories"][sub_cat]["subcategories"][a_el.get_text(strip=True)]: dict = {"site_url": sub_cat_url, "site_data": []}

        # Products handling
        for csv_key in csv_data:
            for sub_cat in csv_data[csv_key]["subcategories"]:
                if "subcategories" in csv_data[csv_key]["subcategories"][sub_cat]:
                   for sub_sub_cat in csv_data[csv_key]["subcategories"][sub_cat]["subcategories"]:
                       print("Processing " + csv_key + " - " + sub_cat + " - " + sub_sub_cat)
                       products_site_html: str = get_site(csv_data[csv_key]["subcategories"][sub_cat]["subcategories"][sub_sub_cat]["site_url"])

                       if products_site_html:
                           beauty_soup_obj: bs4.BeautifulSoup = bs4.BeautifulSoup(markup=products_site_html, features="html.parser")
                           product_rows: bs4.element.ResultSet = beauty_soup_obj.select(selector='tr[id^="product-"]')

                           for row in product_rows:
                                td_elements: bs4.element.ResultSet = row.find_all(name="td")

                                product_name: str = td_elements[1].get_text(strip=True)
                                product_1st_price: str = td_elements[2].get_text(strip=True)
                                product_2nd_price: str = td_elements[3].get_text(strip=True)
                                product_3rd_price: str = td_elements[4].get_text(strip=True)

                                product_csv_row: list = [csv_key, sub_cat, sub_sub_cat, product_name, product_1st_price, product_2nd_price, product_3rd_price]
                                csv_data[csv_key]["subcategories"][sub_cat]["subcategories"][sub_sub_cat]["site_data"].append(product_csv_row)
                else:
                    print("Processing " + csv_key + " - " + sub_cat)
                    products_site_html: str = get_site(csv_data[csv_key]["subcategories"][sub_cat]["site_url"])

                    if products_site_html:
                        beauty_soup_obj: bs4.BeautifulSoup = bs4.BeautifulSoup(markup=products_site_html, features="html.parser")
                        product_rows: bs4.element.ResultSet = beauty_soup_obj.select(selector='tr[id^="product-"]')

                        for row in product_rows:
                            td_elements: bs4.element.ResultSet = row.find_all(name="td")

                            product_name: str = td_elements[1].get_text(strip=True)
                            product_1st_price: str = td_elements[2].get_text(strip=True)
                            product_2nd_price: str = td_elements[3].get_text(strip=True)
                            product_3rd_price: str = td_elements[4].get_text(strip=True)

                            product_csv_row: list = [csv_key, sub_cat, "", product_name, product_1st_price, product_2nd_price, product_3rd_price]
                            csv_data[csv_key]["subcategories"][sub_cat]["site_data"].append(product_csv_row)
    except Exception as e:
        print(e)

def main() -> None:
    """
    Main method, executes everything and measures the time used.
    :return: It has no return.
    """
    st: float = time.time()

    # Perform everything
    csv_data: dict = {}
    get_data(csv_data=csv_data)
    write_csv(csv_data=csv_data, filename=FILENAME)

    print("Time used:", time.time() - st)

if __name__ == "__main__":
    main()