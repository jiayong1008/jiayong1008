import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


print("Please insert your Microsoft credentials")
email = input("Email: ")
password = input("Password: ")

print("\nPlease fill up necessary information below.")
recipient = input("Recipient: ").upper()
message = input("Message:\n")
while True:
    try:
        repeat = int(input("Number of times to repeat [1-100]: "))
        if (repeat in range(100)):
            break
    except:
        pass

# You need to install chrome's webdriver first, then include the full path as a string argument oin webdriver.Chrome
driver = webdriver.Chrome('C:/full/path/to/your/chromedriver.exe')
driver.get("https://teams.microsoft.com/")
time.sleep(1)

# Enter Email
emailField = driver.find_element_by_xpath('//*[@id="i0116"]')
emailField.click()
emailField.send_keys(email)
driver.find_element_by_xpath('//*[@id="idSIButton9"]').click()
time.sleep(2.5)

# Enter Password
passField = driver.find_element_by_xpath('//*[@id="i0118"]')
passField.click()
passField.send_keys(password)
driver.find_element_by_xpath('//*[@id="idSIButton9"]').click()
time.sleep(1.2)

# Stay Signed In
driver.find_element_by_xpath('//*[@id="idSIButton9"]').click()

try:
    tryAgain = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="page-content-wrapper"]/div[1]/div/div[1]/div[2]/button')))
    tryAgain.click()
except:
    pass

chatButton = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app-bar-86fcd49b-61a2-4701-b771-54728cd291fb"]')))
chatButton.click()
time.sleep(0.5)

# click dismiss notification button
driver.find_element_by_xpath('//*[@id="toast-container"]/div/div/div[2]/div/button[2]').click()

found = False
recipients = driver.find_elements_by_class_name('cle-item')
for person in recipients:
    if (recipient == person.get_attribute('data-tid').strip('chat-list-entry-with-').upper()):
        found = True
        print(f"{recipient} found")
        person.click()
        chatMessage = driver.find_element_by_xpath('//*[@id="cke_1_contents"]/div')
        sendButton = driver.find_element_by_xpath('//*[@id="send-message-button"]')
        for i in range(repeat):
            chatMessage.click()
            chatMessage.send_keys(message)
            sendButton.click()
        break
    
if (not found):
    print(f"{recipient} not found in current chat list")
# driver.find_element_by_xpath('//*[@id="toast-container"]/div/div/div[2]/div/button[2]').click()

