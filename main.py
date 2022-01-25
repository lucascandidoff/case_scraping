from selenium import webdriver
from selenium.webdriver.chrome.options import Options  
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time
from bs4 import BeautifulSoup
import pandas as pd

chrome_options = Options()

chrome_options.add_argument("--headless") # faz com que o browser não abra durante o processo
p = '/Users/lucascandido/Documents/Estudos/Web_Scraping/chromedriver' 
driver = webdriver.Chrome(executable_path=p,options=chrome_options)
driver.get('https://portal.cfm.org.br/busca-medicos/')
timeout = 5

select = Select(driver.find_element_by_id('tipoSituacao'))
select.select_by_visible_text('Ativo')
button = driver.find_element_by_xpath('//*[@id="buscaForm"]/div/div[4]/div[2]/button')
driver.execute_script("return arguments[0].click();", button)

table = {}

print('-=-==-=-=--=-=---=-=-=-=-=-=')
print('Waiting page 1...')
print('-=-==-=-=--=-=---=-=-=-=-=-=')

time.sleep(10)

for j in range(3):
    next_page = driver.find_element_by_xpath(f'//*[@id="paginacao"]/div/div/ul/li[{j+1}]')
    driver.execute_script("return arguments[0].click();", next_page)

    if j > 0: 
        print(f'Waiting page {j+1}...')
        print('-=-==-=-=--=-=---=-=-=-=-=-=')
        time.sleep(10)

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    medicos_nome = soup.find('div', attrs={'class':'busca-resultado'}).find_all('h4')
    medicos_foto = soup.find('div', attrs={'class':'busca-resultado'}).find_all('img')
    medicos_outras_inf = soup.find_all('div', attrs={'class':'col-md-4'})
    medicos_situacao = soup.find_all('div', attrs={'class':'col-md'})
    medicos_especialidade = soup.find_all('div', attrs={'class':'col-md-12'})
    medicos_endereco = soup.find_all('div', attrs={'class':'row endereco'})
    medicos_telefone = soup.find_all('div', attrs={'class':'row telefone'})

    temp = []
    for i in medicos_nome:
        temp.append(i.next)
    table['Nome'] = temp

    temp = []
    for i in medicos_outras_inf:
        if 'CRM' in i.contents[1].next:
            temp.append(i.contents[2].split()[0])
    table['CRM'] = temp

    temp = []
    for i in medicos_outras_inf:
        if 'Data de Inscrição' in i.contents[1].next:
            temp.append(i.contents[2].split()[0])
    table['Data de Inscricao'] = temp

    temp = []
    for i in medicos_situacao:
        if len(i.contents[2].strip()) > 0:
            temp.append(i.contents[2].strip())
    table['Situacao'] = temp

    temp = []
    for i in medicos_especialidade:
        if 'RQE' in i.next:
            temp.append(i.next)
        elif 'sem especialidade' in i.contents[2].next:
            temp.append(i.contents[2].next)

    table['Especialidade'] = temp

    temp = []
    for i in medicos_endereco:
        temp.append(i.next.text.split(' ', maxsplit=1)[1]);
    table['Endereco'] = temp

    temp = []
    for i in medicos_telefone:
        temp.append(i.next.text.split(' ', maxsplit=1)[1])
    table['Telefone'] = temp

    temp = []
    for i in medicos_foto:
        temp.append(i['src'])
    table['Foto'] = temp

    if j == 0: 
        df = pd.DataFrame(table)
    else:    
        df_temp = pd.DataFrame(table)
        df = df.append(df_temp, ignore_index=True, sort=False)

df['Logradouro'] = ''
df['Bairro'] = ''
df['CEP'] = ''
df['Cidade'] = ''
df['Estado'] = ''

for h in range(len(df)):
    endereco = df['Endereco'][h] 
    if '-' in endereco:
        for i in range(endereco.count('-')+1):
            if i == 0: df['Logradouro'][h] = endereco.split('-')[0].strip()
            elif i == 1: df['Bairro'][h] = endereco.split('-')[1].strip()
            elif i == 2: df['CEP'][h] = endereco.split('-')[2].strip()
            elif i == 3: 
                cidade = endereco.split('-')[3].strip()
                if '/' in cidade:
                    df['Cidade'][h] = cidade.split('/')[0].strip()
                    df['Estado'][h] = cidade.split('/')[1].strip()
                else:
                    df['Cidade'][h] = cidade.strip()
    else:
        df['Logradouro'][h] = df['Endereco'][h].strip()

df = df.drop('Endereco', axis=1)
df = df[['Nome','CRM','Data de Inscricao','Situacao','Especialidade','Logradouro','Bairro','CEP','Cidade','Estado','Telefone','Foto']]

df.to_excel('medicos.xlsx')

print('Fim')
print('-=-==-=-=--=-=---=-=-=-=-=-=')

