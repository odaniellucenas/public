# -*- coding: utf-8 -*-

"""
Dividends web scrapping from the fundamentus website.
https://www.fundamentus.com.br/
"""


import requests
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

ticker = "bbse3"  # Write here the ticker's code.
url = "https://www.fundamentus.com.br/proventos.php?tipo=2&papel=" + ticker

# Creating an empty dataframe.
df = pd.DataFrame(columns=["DATA ANÚNCIO",
                           "VALOR",
                           "TIPO PROVENTO",
                           "DATA PAGAMENTO",
                           "QTD AÇÕES"])

# Getting the web page content in text format.
'''
The User-Agent request header contains a characteristic string that allows
the network protocol peers to identify the application type, operating system,
software vendor or software version of the requesting software user agent.
Validating User-Agent header on server side is a common operation so be sure
to use valid browser’s User-Agent string
to avoid getting blocked.
Font: https://go-colly.org/articles/scraping_related_http_headers/
Font: https://stackoverflow.com/questions/68259148/getting-404-error-for-certain-stocks-and-pages-on-yahoo-finance-python
'''
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" +
                  "AppleWebKit/537.36 (KHTML, like Gecko)" +
                  "Chrome/71.0.3578.98 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;" +
              "q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",  # Do not track request header.
    "Connection": "close"
}
soup = BeautifulSoup(
    requests.get(url, headers=headers, timeout=5).text,
    "html.parser")

# Looking for the web table.
# In HTML, a table is represented by the tag <table>.
webtable = soup.find("table")

# Getting all table rows.
# In HTML, a row table is represented by the tag <tr>.
for webtable_row in webtable.tbody.find_all("tr"):
    # Getting all table columns.
    # In HTML, a column table is represented by the tag <td>.
    webtable_column = webtable_row.find_all("td")
    # if webtable_columns != []:
    if webtable_column:
        data_anuncio = webtable_column[0].text.strip(" ")
        valor = webtable_column[1].text.strip(" ")
        tipo_provento = webtable_column[2].text.strip(" ")
        data_pagamento = webtable_column[3].text.strip(" ")
        quantidade_acoes = webtable_column[4].text.strip(" ")
        df = pd.concat(
            [df, pd.DataFrame.from_records([{"DATA ANÚNCIO": data_anuncio,
                                             "VALOR": valor,
                                             "TIPO PROVENTO": tipo_provento,
                                             "DATA PAGAMENTO": data_pagamento,
                                             "QTD AÇÕES": quantidade_acoes
                                             }]
                                           )], ignore_index=True)

# -*- Working on dataframe -*-
df = df[df["DATA PAGAMENTO"] != "-"]  # Removing rows without payment date.

# Announcement date to date format.
df["DATA ANÚNCIO"] = pd.to_datetime(df["DATA ANÚNCIO"],
                                    format="%d/%m/%Y",
                                    errors="ignore")

# Payment date to date format.
df["DATA PAGAMENTO"] = pd.to_datetime(df["DATA PAGAMENTO"],
                                      format="%d/%m/%Y",
                                      errors="coerce")

df = df.astype({"QTD AÇÕES": int})  # Payment per number of shares.

# Value to decimal format.
df["VALOR"] = [x.replace(",", ".") for x in df["VALOR"]]
df = df.astype({"VALOR": float})
df["VALOR"] = df["VALOR"]/df["QTD AÇÕES"]

# Dividend type using upper case style.
df["TIPO PROVENTO"] = df["TIPO PROVENTO"].str.upper()

df["TICKER"] = str.upper(ticker)  # Including the ticker on the dataframe.

# Reorder dataframe.
df = df[["TICKER", "DATA ANÚNCIO", "DATA PAGAMENTO", "VALOR", "TIPO PROVENTO"]]

# -*- Graphics -*-
# Dividends paied per ticker.
plt.title("PROVENTOS RECEBIDOS POR " + str.upper(ticker))
plt.plot(df["DATA PAGAMENTO"], df["VALOR"], label=str.upper(ticker))
plt.ylabel("VALOR (R$)")
plt.xlabel("ANO")
# plt.legend()
plt.show()

# Dividends paied per year per ticker.
df_anual = df.set_index('DATA PAGAMENTO')
dividendos = (df_anual['VALOR']).resample('Y').sum()
plt.plot(dividendos.index.year[:-1], dividendos[:-1], label=str.upper(ticker))
plt.title("PROVENTOS ANUAIS RECEBIDOS POR " + str.upper(ticker))
plt.ylabel("VALOR (R$)")
plt.xlabel("ANO")
# plt.legend()
plt.show()

# Exporting as CSV.
df.to_csv("C:/Users/danie/Desktop/PROVENTOS " + str.upper(ticker) + ".csv",
          index=False,
          sep=";",
          encoding="UTF-8")

# Removing the unused variables.
del (data_anuncio, data_pagamento, valor, tipo_provento, ticker, headers, url,
     webtable, webtable_column, df_anual, dividendos)
