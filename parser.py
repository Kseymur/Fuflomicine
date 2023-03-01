from bs4 import BeautifulSoup
import requests as req
import pandas as pd
import re


cat_list = []
product_list = []
data = {}
main_url = 'https://apteka.ru'
for_iter_pages = '?page='
stop_product = ''
stop_descript_prod = ''
wrong_prod = ''


def get_category(cat_list, url):
  #получаем список с категориями  
  catalog_html = req.get(url='https://app.scrapingbee.com/api/v1/',
      params={
          'api_key': 'API_KEY',
          'url': url,
          'render_js': 'false'
      })
  print(catalog_html.status_code)
  catalog = BeautifulSoup(catalog_html.text, 'html.parser')
  category = BeautifulSoup(str(catalog.find_all('div', class_="ViewCatalogRoot__subcat")))
  for a in category.find_all('a', href=True):
    cat_list.append(a['href'])  
  return cat_list


def get_exact_cat(url):
  #получаем soup-объект каждой отдельной категории
  exact_cat_html = req.get(url='https://app.scrapingbee.com/api/v1/',
      params={
          'api_key': 'API_KEY',
          'url': url,
          'render_js': 'false'
      })
  exact_cat = BeautifulSoup(exact_cat_html.text, 'html.parser')
  return exact_cat


def get_pages(exact_cat):
  #получаем количество страниц в категории
  page_list = []
  page_exact_cat = BeautifulSoup(str(exact_cat.find_all('div',class_="Paginator-wrapper")))
  for a in page_exact_cat.find_all('a'):
    page_list.append(a['href'])
  numbers = []
  for el in page_list:
    num = re.findall('[0-9]+', el)
    numbers.extend(num)
  max_page_num = max(list(map(int,numbers)))
  return max_page_num


def get_products(for_iter_pages, max_page_num, url, stop_product, product_list):
  #получаем список продуктов в категории
  for n in range(1,max_page_num+1):
    new_url = url+for_iter_pages+str(n)
    page_cat_html = req.get(url='https://app.scrapingbee.com/api/v1/',
      params={
          'api_key': 'API_KEY',
          'url': new_url,
          'render_js': 'false'
      })
    if page_cat_html.status_code != 200:
      stop_product = new_url
      break
    else:
      page_cat = BeautifulSoup(page_cat_html.text, 'html.parser')
      for a in page_cat.find_all('a', class_="catalog-card__link"):
        product_list.append(a['href'])

  return product_list


def get_description(main_url, product_list, stop_descript_prod, data, wrong_prod):
  #расширяем словарь описаниями лекарств
  for prod in product_list:
    prod_html = req.get(url='https://app.scrapingbee.com/api/v1/',
      params={
          'api_key': 'API_KEY',
          'url': main_url+prod,
          'render_js': 'false'
      })
    print(prod_html.status_code)
    if prod_html.status_code != 200:
      stop_descript_prod = prod
      break
    else:
      product = BeautifulSoup(prod_html.text, 'html.parser')
      wrong_prod = product
      name = product.find_all('meta', itemprop="name")[3]['content'] #find('h1').text
      print(name)
      prod_desription = BeautifulSoup(str(product.find_all('div', 'ProductDescription-content')))
      only_description = BeautifulSoup(str(prod_desription.find_all('dd')))
      clear_description = only_description.get_text()
      if name not in data.keys():
        data[name] = clear_description


cat_list = get_category(cat_list,'https://apteka.ru/sym/leka/') #получили список категорий
for cat in cat_list: #парсим по категориям
  exact_cat = get_exact_cat(main_url+cat)
  max_page = get_pages(exact_cat)
  prod_list = get_products(for_iter_pages, max_page, main_url+cat, stop_product, product_list)
  get_description(main_url, prod_list, stop_descript_prod, data, wrong_prod)


df = pd.DataFrame.from_dict(data, orient = 'index')
df.to_csv("data.csv")