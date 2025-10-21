from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import re, json, time

service = Service("C:\\Users\\Pedro V\\Desktop\\chromedriver.exe")

options = webdriver.ChromeOptions()
options.binary_location = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
options.add_argument("--headless")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(service=service, options=options)
driver.get("https://fiveg.schoolking.com.br/ranking/")
time.sleep(3)

conteudo = driver.find_element(By.TAG_NAME, "body").text
driver.quit()

# Expressão regular para extrair os dados
padrao = r"\{ ([^}]+) \} ([^\d]+?) (\d+) \d+ (\d+)"
dados = []
for match in re.findall(padrao, conteudo):
    time, nome, pontos, combo = match
    dados.append({
        "nome": nome.strip(),
        "time": time.strip(),
        "pontos": int(pontos),
        "combo": int(combo)
    })

with open("ranking.json", "w", encoding="utf-8") as f:
    json.dump(dados, f, ensure_ascii=False, indent=2)

print("Ranking salvo com sucesso!")
