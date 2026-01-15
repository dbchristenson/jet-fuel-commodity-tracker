import re

import requests
import streamlit as st
from bs4 import BeautifulSoup

JETFUEL_EIA = "https://www.eia.gov/dnav/pet/hist/EER_EPJK_PF4_RGC_DPGD.htm"
DIESEL_EIA = "https://www.eia.gov/dnav/pet/hist/EER_EPD2DXL0_PF4_RGC_DPGD.htm"


def create_download_link(base_url, href):
    return base_url.split("pet/")[0] + "pet" + href.replace("..", "")


def get_download_link(url):
    response = requests.get(url)
    content = response.content

    soup = BeautifulSoup(content, "html.parser")
    xls_href = soup.find("a", href=re.compile(r"hist_xls"))

    download_link = create_download_link(url, xls_href["href"])

    return download_link


def download_data(url, filename):
    download_link = get_download_link(url)
    data_response = requests.get(download_link)

    with open(filename, "wb") as f:
        f.write(data_response.content)


if __name__ == "__main__":
    st.cache_data.clear()
    jetfuel_download_link = get_download_link(JETFUEL_EIA)
    diesel_download_link = get_download_link(DIESEL_EIA)

    download_data(JETFUEL_EIA, "data/commodity_jetfuel_prices.xlsx")
    download_data(DIESEL_EIA, "data/commodity_diesel_prices.xlsx")
