import re 
import os 
import traceback 
import requests 
import json 

from bs4 import BeautifulSoup 

def main() : 
    try : 
        print('Initializing web scraper...')
        scraper = spa_web_scraper()

        urls = [
            "https://mellowspamidrand.com/" , 
            "https://mellowspamidrand.com/about-us/" ,
            "https://mellowspamidrand.com/services/" ,
            "https://mellowspamidrand.com/contact/" ,  
        ]        

        print(f'Attempting to scrape {len(urls)} URLs')
        result = scraper.page_contents(urls)

        print("scraping process completed")

        # Verify that JSON file was created 
        if os.path.exists('extracted_data.json') :
           print('JSON file created successfully ')
           with open('extracted_data.json', 'r') as f : 
               print("Json file contents :") 
               print(f.read())

        else :
            print("WARNING: No JSON file was created")

    except Exception as e : 
        print(f"critical error during scraping : {e} ")
        # show traceback of the error 
        traceback.print_exc()

        

class spa_web_scraper : 

    def update_json_file(self, new_data, filename='extracted_data.json') : 
        try : 
            # Check the status of the file, whether file exists or not 
            # handle empty or nonexistent file 
            # if file is empty, initialize the file with a new data structure 
            if not os.path.exists(filename) or os.stat(filename).st_size == 0 : 
                existing_data = []

            else :
                # read for existing data 
                with open(filename ,'r') as file  :
                    existing_data = json.load(file) 

            # update the existing data 
            if isinstance(existing_data , list) :
                # if the json file has a list, append to it 
                existing_data.append(new_data)
            
            elif isinstance(existing_data, dict):
                # if the json file has a dictionary, update the dictionary 
                existing_data.update(new_data )
            
            # write the updated data 
            with open(filename, 'w') as file  :
                json.dump(existing_data,file , indent=4 )

            print("successfully updated JSON file")

        except FileNotFoundError : 
            print(f"error : the file {'extracted_data.json'} was not found")

        except json.JSONDecodeError : 
            print("Error : the file contains invalid json")
            # Handle the issue by writing the new data to the file
            with open (filename, 'w') as file   : 
                json.dump([new_data], file, indent=4)

        except Exception as e : 
            print(f'An error occurred : {str(e)}')

    def  page_contents(self, urls) :
        # create different data structures for the different types of scraped data you will be storing 
        # Here you will be storing the business information 
        about_data = [] 
        # here the data that will be stored will be about the services offered by the business 
        services_data = [] 
        # here the data will be stored will about the contact information of the business 
        contact_data = [] 
        
        for url in urls : 
            try : 
                # Adding debugging logs to detect where the bugs are in the system 
                print(f'Processing URL : {url}')
                response = requests.get(url , timeout=15)

                # Check the HTTP response status of the request 
                response.raise_for_status()

                # initialize scraper 
                soup = BeautifulSoup(response.text,'lxml') 

                # route data to appropriate data structure based on URL 
                if 'about-us' in url : 
                    # extract specific content in about-us page 
                    about_content = {
                        'name' : soup.find('h3').text.strip() if soup.find('h3') else 'No title' , 
                        'paragraphs' : [p.text for p in soup.find_all('p')] , 
                        'vision' : soup.find(attrs={"class" : "uvc-main-heading"}).text if soup.find(attrs={"class" : "uvc-main-heading"}) else "no vision", 
                        'vision-paragraph' : soup.find(attrs={"class" : "uvc-sub-heading"}).text  if soup.find(attrs={"class" : "uvc-sub-heading"}) else "no vision-paragraph", 
                    }

                    # store the extracted data/values in a data structure 
                    about_data.append(about_content) 

                    print(f"about data collected : {about_content}")

                elif 'services' in url : 
                    # we are going to use parent elements to scrape data 
                    #find a common parent element that contains the services 
                    services_section = soup.find('div' , class_='wpb_wrapper') 

                    print(f"services section : {services_section}")

                    if services_section:
                        print(f'Services section content :{services_section.prettify()}') # debugging info 
                        current_category = None 
                        # iterate through all the  elements in the services section 
                        for element in services_section.find_all([ 'p', 'table']) : 
                            if element.name == 'p' and element.find('strong') :
                                # update the current category 
                                current_category = element.find('strong').text.strip() 
                                print(f"Found category : {current_category}") # debugging info 

                            elif element.name == 'table' and current_category : 
                                #extract services and prices from the table 
                                services = []
                                for row in element.find_all('tr'): 
                                    service_name = row.find('td' , class_='left').text.strip() if row.find('td', class_='left') else None
                                    service_prices = row.find('td', class_='right').text.strip() if row.find('td', class_='right') else None 
                                    if service_name and service_prices :
                                        services.append({'service' :service_name, 'price': service_prices})

                                # add data to servies data 
                                services_data.append({
                                    'category' : current_category , 
                                    'services' : services 
                                })  

                                print(f'services added under {current_category} : {services}')
                                

            except requests.RequestException as e : 
                print(f'Request failed : {e}')

            except requests.ConnectionError : 
                print('Connection failed')

            except requests.Timeout : 
                print("Request timed out")

            except Exception : 
                print('Parsing failed')

            except ValueError as e  :
                print(f'Data validation failed :{e}') 

        # write the data to the JSON file 
        self.update_json_file(
            {
                "about" : about_data , 
                "services" : services_data , 
                "contact" : contact_data 
            }
        )



if __name__ == "__main__" : 
    main() 












