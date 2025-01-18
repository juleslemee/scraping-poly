from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd

# Use Selenium to get the fully rendered HTML
def get_rendered_html(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run browser in headless mode
    driver = webdriver.Chrome(options=options)  # Ensure you have ChromeDriver installed

    driver.get(url)  # Navigate to the page
    html_content = driver.page_source  # Get the fully rendered HTML
    driver.quit()  # Close the browser
    return html_content

# Fetch the rendered HTML (replace with the actual URL)
url = "https://jc.aep.polymtl.ca/entreprises-presentes/"  # Replace with the target website
html_content = get_rendered_html(url)

# Use BeautifulSoup to parse the rendered HTML
soup = BeautifulSoup(html_content, "html.parser")

# Extract the list of days
day_elements = soup.select(".rtbs_menu ul li a")
days = {elem["data-tab"]: elem.text.strip() for elem in day_elements}

data = []  # List to hold row data

# Loop through each day's tab
for data_tab, day in days.items():
    # Find the corresponding tab's table content
    tab_content = soup.select_one(data_tab)

    # Find all rows in the table for the specific day
    if tab_content:
        rows = tab_content.find_all("tr", {"class": lambda x: x and "ninja_table_row" in x})

        # Loop through each row
        for row in rows:

            # Extract company description
            description_td = row.find("td", class_="ninja_clmn_nm_description")
            title = description_td.find("p", class_="titretab").text.strip() if description_td else None
            description = description_td.find("p", class_="paratab").text.strip() if description_td else None

            # Extract bolded recruitment data specifically for internships
            programme_td = row.find("td", class_="ninja_clmn_nm_programme")
            internship_recruitment = []

            if programme_td:
                # Find all <tr> rows within this section
                rows_in_td = programme_td.find_all("tr")
                
                # Locate the "Recrutement de Stagiaires" header
                for i, tr in enumerate(rows_in_td):
                    th = tr.find("th")
                    if th and "Recrutement de Stagiaires" in th.text:
                        # The next <tr> contains the recruitment periods for internships
                        internship_row = rows_in_td[i + 1]  # Assuming it's the immediate next row
                        internship_cells = internship_row.find_all("td", class_="tabactive")
                        internship_recruitment = [td.text.strip() for td in internship_cells]
                        break  # Exit the loop once internships are processed

            # Extract engineering fields
            engineering_fields = []
            if programme_td:
                fields_paragraphs = programme_td.find_all("p", class_="no")
                engineering_fields = [field.text.strip() for field in fields_paragraphs]

            # Append to data list
            data.append({
                "Company Name": title,
                "Description": description,
                "Day": day,
                "Internship Recruitment Periods": internship_recruitment,
                "Engineering Fields": engineering_fields
            })

# Convert to a Pandas DataFrame
df = pd.DataFrame(data)

# Define the set of fields to filter
fields_to_include = {
    'Automatisation Industrielle', 'Mathématiques Appliqués', 'Physique',
    'Génie énergétique et nucléaire', 'Cyberenquête', 'Métallurgique',
    'Cyberfraude', 'Mécanique', 'Industriel', 'Cybersécurité', 'DesignFabrication', 'Aérospatial'
}

# Filter the DataFrame based on the updated fields
filtered_df = df[
    df['Engineering Fields'].apply(lambda fields: any(field in fields_to_include for field in fields)) &
    df['Internship Recruitment Periods'].apply(lambda periods: 'E25' in periods)
]

filtered_df.to_csv('mechy_companies.csv', index=False)

# Display the filtered DataFrame
#print(filtered_df)

# unique fields just for future reference:
'''
{'Électricité de bâtiment', 'Mines', 'Électrique', 'Automatisation Industrielle', 'Mathématiques Appliqués', 
'Sécurité incendie', 'Internet industriel des objets', 'Technologie Biomédicale', 'Logiciel', 'Physique', 
'Génie énergétique et nucléaire', 'Cyberenquête', 'Biomédical', 'Chimique', 'Mineral', 'Métallurgique', 
'Cyberfraude', 'Mécanique du bâtiment', 'Mécanique', 'Industriel', 'Cybersécurité', 'DesignFabrication', 
'Géologique', 'Aérospatial', 'Civil', 'Informatique'}
'''

# get extra info using AI: industries, what exactly they sell, the company values/ what is important to them
