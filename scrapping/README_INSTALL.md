🧭 Installer Google Chrome version 124 sur Ubuntu pour Selenium

Ce guide explique comment installer **Google Chrome version 124.0.6367.78** sur Ubuntu, avec le **ChromeDriver correspondant**, pour faire tourner vos scripts Selenium sans erreur de compatibilité.

---

📌 Pourquoi ?

Selenium nécessite que la version de `ChromeDriver` corresponde exactement à la version de Google Chrome installée sur votre système. Une incompatibilité produit cette erreur :

```
SessionNotCreatedException: This version of ChromeDriver only supports Chrome version XXX
```

---

✅ Étapes d'installation

1. Désinstaller toute version actuelle de Chrome

```bash
sudo apt remove --purge google-chrome-stable
sudo rm -rf /opt/google/chrome
```

---

2. Télécharger Google Chrome version 124 (version exacte)

```bash
wget https://mirror.cs.uchicago.edu/google-chrome/pool/main/g/google-chrome-stable/google-chrome-stable_124.0.6367.91-1_amd64.deb
```

---

3. Installer cette version

```bash
sudo apt install ./google-chrome-stable_124.0.6367.78-1_amd64.deb
```

🔍 Vérification :
```bash
google-chrome --version
# Résultat attendu : Google Chrome 124.0.6367.78
```

---

4. Télécharger le ChromeDriver correspondant

```bash
wget https://storage.googleapis.com/chrome-for-testing-public/124.0.6367.78/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip
mkdir -p ~/chromedriver
mv chromedriver-linux64/chromedriver ~/chromedriver/
chmod +x ~/chromedriver/chromedriver
```

🔍 Vérification :
```bash
~/chromedriver/chromedriver --version
# Résultat attendu : ChromeDriver 124.0.6367.78
```

---

5. Ajouter ChromeDriver au PATH (optionnel mais recommandé)

Ajoutez cette ligne à la fin de votre fichier `~/.bashrc` ou `~/.zshrc` :

```bash
export PATH="$HOME/chromedriver:$PATH"
```

Rechargez le terminal :

```bash
source ~/.bashrc  # ou source ~/.zshrc selon votre shell
```

---

🐍 Installer les dépendances Python

```bash
pip install selenium requests beautifulsoup4
```

---

🧪 Exemple de script Selenium compatible

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")  # Facultatif

service = Service(executable_path="/home/votre_utilisateur/chromedriver/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.google.com")
print(driver.title)
driver.quit()
```

---

🛠 Dépannage

- Erreur : `session not created`
  → Vérifiez que `chrome` et `chromedriver` sont de **la même version exacte**.
- Erreur : `chromedriver not found`
  → Vérifiez qu’il est dans le bon dossier et exécutable : `chmod +x`.

---

📎 Liens utiles

- 📥 ChromeDriver Archive: https://googlechromelabs.github.io/chrome-for-testing/
- 📦 Chrome .deb archive: https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/

---

🏁 Résultat

Une fois tous les éléments en place, vous pouvez exécuter vos scripts Selenium sans erreurs de version, en toute stabilité ✅
