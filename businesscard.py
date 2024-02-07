import streamlit as st
import os
import matplotlib.pyplot as plt
import cv2
import re
import easyocr
import pandas as pd
import psycopg2

# SETTING PAGE CONFIGURATIONS
st.set_page_config(page_title="BizCardX: Extracting Business Card Data with OCR",
                   layout="wide",
                   initial_sidebar_state="auto")
st.title("BizCardX: Extracting Business Card Data with OCR")
option=["Home","Upload & Extract","Modify"]
selected_option=st.selectbox("SELECT OPTION",option)

reader = easyocr.Reader(['en']) 
mydb=psycopg2.connect(host="localhost",
                                user="postgres",
                                password="dev@0905",
                                database="biz_data",
                                port="5432"
                                )
cursor=mydb.cursor()
create_query= '''create table if not exists biz_data (Company_Name text,
                                                      Card_Holder_Name varchar(100),
                                                      Designation varchar(100),
                                                      Mobile_number text,
                                                      Email_address text,
                                                      Website_URL text,
                                                      Area varchar(50),
                                                      City varchar(50),
                                                      State varchar(50),
                                                      Pin_code text,
                                                      image BYTEA
                                                        )''' 
cursor.execute(create_query)
mydb.commit()

if selected_option == "Home":
    col1,col2=st.columns(2)
    with col1:
        st.markdown("## :blue[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")
        st.markdown("## :blue[**Overview :**] This Streamlit application allow users to upload an image of a business card and extract relevant information from it using easyOCR. ")

# Create the 'uploaded_cards' directory if it does not exist
if not os.path.exists("uploaded_cards"):
    os.makedirs("uploaded_cards")

if selected_option == "Upload & Extract" :
    st.markdown("### Upload a Business Card")
    uploaded_card = st.file_uploader("upload here",label_visibility="collapsed",type=["png","jpeg","jpg"])
    
    if uploaded_card is not None:

        def save_card(uploaded_card):
            with open(os.path.join("uploaded_cards", uploaded_card.name), "wb") as f:
                f.write(uploaded_card.getbuffer())
        save_card(uploaded_card)
        
        def image_preview(image, res):
            for (bbox, text, prob) in res:
                # unpack the bounding box
                (tl, tr, br, bl) = bbox
                tl = (int(tl[0]), int(tl[1]))
                tr = (int(tr[0]), int(tr[1]))
                br = (int(br[0]), int(br[1]))
                bl = (int(bl[0]), int(bl[1]))
                cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                cv2.putText(image, text, (tl[0], tl[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            plt.rcParams['figure.figsize'] = (15, 15)
            plt.axis('off')
            plt.imshow(image)
            # DISPLAYING THE UPLOADED CARD
        col1, col2 = st.columns(2, gap="large")
        with col1:
                st.markdown("#     ")
                st.markdown("#     ")
                st.markdown("### You have uploaded the card")
                st.image(uploaded_card)
        # DISPLAYING THE CARD WITH HIGHLIGHTS
        with col2:
                st.markdown("#     ")
                st.markdown("#     ")
        with st.spinner("Processing image Please wait ..."):
                st.set_option('deprecation.showPyplotGlobalUse', False)
                saved_img = os.getcwd() + "\\" + "uploaded_cards" + "\\" + uploaded_card.name
                image = cv2.imread(saved_img)
                res = reader.readtext(saved_img)
                st.markdown("### Image Processed and Data Extracted")
                st.pyplot(image_preview(image, res))
        #easy OCR
        saved_img = os.getcwd()+ "\\" + "uploaded_cards"+ "\\"+ uploaded_card.name
        result = reader.readtext(saved_img,detail = 0,paragraph=False)

        def binary_img(file_path):
            with open(file_path, 'rb') as file:
                binaryData = file.read()
            return binaryData

        data = {"Company_Name": [],
                "Card_Holder_Name": [],
                "Designation": [],
                "Mobile_number": [],
                "Email_address": [],
                "Website_URL": [],
                "Area": [],
                "City": [],
                "State": [],
                "Pin_code": [],
                "image": binary_img(saved_img)
                }
        
        def get_data(res):
            for ind, i in enumerate(res):
                if "www " in i.lower() or "www." in i.lower():  # Website with 'www'
                    data["Website_URL"].append(i)
                elif "WWW" in i:  # In case the website is in the next elements of the 'res' list
                    Website_URL = res[ind + 1] + "." + res[ind + 2]
                    data["Website_URL"].append(Website_URL)
                elif '@' in i:
                    data["Email_address"].append(i)
                # To get MOBILE NUMBER
                elif "-" in i:
                    data["Mobile_number"].append(i)
                    if len(data["Mobile_number"]) == 2:
                        data["Mobile_number"] = " & ".join(data["Mobile_number"])
                # To get COMPANY NAME
                elif ind == len(res) - 1:
                    data["Company_Name"].append(i)
                # To get Card Holder Name
                elif ind == 0:
                    data["Card_Holder_Name"].append(i)
                #To get designation
                elif ind == 1:
                    data["Designation"].append(i)

                #To get area
                if re.findall('^[0-9].+, [a-zA-Z]',i):
                    data["Area"].append(i.split(',')[0])
                elif re.findall('[0-9] [a-zA-z]+',i):
                    data["Area"].append(i)
                #To get city name
                match1 = re.findall('.+St , ([a-zA-Z]+).+',i)
                match2 = re.findall('.+St,,([a-zA-Z]+).+',i)
                match3 = re.findall('^[E].*',i)
                if match1:
                    data["City"].append(match1[0])
                elif match2:
                    data["City"].append(match2[0])
                elif match3:
                    data["City"].append(match3[0])

                #To get state name
                state_match = re.findall('[a-zA-Z]{9} +[0-9]', i)
                if state_match:
                    data["State"].append(i[:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);', i):
                    data["State"].append(i.split()[-1])
                if len(data["State"]) == 2:
                    data["State"].pop(0)

                #To get Pincode
                if len(i) >= 6 and i.isdigit():
                    data["Pin_code"].append(i)
                elif re.findall('[a-zA-Z]{9} +[0-9]', i):
                    data["Pin_code"].append(i[10:])
        get_data(result)

        #Creating a dataframe and storing in DB
        def create_df(data):
            df = pd.DataFrame(data)
            return df
        df = create_df(data)
        st.success("### Data Extracted ")
        st.write(df)

        if st.button("Upload to Database"):
            
            for index,row in df.iterrows():
                insert_query=''' insert into biz_data (Company_Name,
                                                        Card_Holder_Name,
                                                        Designation,
                                                        Mobile_number,
                                                        Email_address,
                                                        Website_URL,
                                                        Area,
                                                        City,
                                                        State,
                                                        Pin_code,
                                                        image)
                                                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                                                    
                values=(row['Company_Name'],
                        row['Card_Holder_Name'],
                        row['Designation'],
                        row['Mobile_number'],
                        row['Email_address'],
                        row['Website_URL'],
                        row['Area'],
                        row['City'],
                        row['State'],
                        row['Pin_code'],
                        row['image']
                        )
                cursor.execute(insert_query,values)
                mydb.commit()
            st.success("#### Uploaded to database successfully!")

# MODIFY MENU
if selected_option == "Modify":
    col1,col2,col3 = st.columns([3,3,2])
    col2.markdown("## Alter or Delete the data here")
    column1,column2 = st.columns(2,gap="large")
    try :
        with column1:
            cursor.execute("Select Card_Holder_Name FROM biz_data")
            result = cursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
        selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))
        st.markdown("#### Update or modify any data below")
        cursor.execute(
                "select Company_Name,Card_Holder_Name,Designation,Mobile_number,Email_address,Website_URL,Area,City,State,Pin_code from biz_data WHERE Card_Holder_Name=%s",
                (selected_card,))
        result = cursor.fetchone()
        # DISPLAYING ALL THE INFORMATIONS
        Company_Name = st.text_input("Company_Name", result[0])
        Card_Holder_Name = st.text_input("Card_Holder_Name", result[1])
        Designation = st.text_input("Designation", result[2])
        Mobile_number = st.text_input("Mobile_number", result[3])
        Email_address = st.text_input("Email_address", result[4])
        Website_URL = st.text_input("Website_URL", result[5])
        Area = st.text_input("Area", result[6])
        City = st.text_input("City", result[7])
        State = st.text_input("State", result[8])
        Pin_code = st.text_input("Pin_Code", result[9])

        if st.button("Commit changes to DB"):
            # Update the information for the selected business card in the database
            cursor.execute("""UPDATE biz_data SET Company_Name=%s,Card_Holder_Name= %s,Designation=%s,Mobile_number=%s,Email_address=%s,Website_URL=%s,Area=%s,City=%s,State=%s,Pin_code=%s
                                        WHERE Card_Holder_Name=%s""", (
            Company_Name,Card_Holder_Name,Designation,Mobile_number,Email_address,Website_URL,Area,City,State,Pin_code,
            selected_card))
            mydb.commit()
            st.success("Information updated in database successfully.")

        with column2:
            cursor.execute("SELECT Card_Holder_Name FROM biz_data")
            result = cursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to Delete", list(business_cards.keys()))
            st.write(f"### You have selected :green[**{selected_card}'s**] card to delete")
            st.write("#### Proceed to delete this card?")

            if st.button("Yes Delete Business Card"):
                cursor.execute(f"DELETE FROM cbiz_data WHERE Card_Holder_Name='{selected_card}'")
                mydb.commit()
                st.success("Business card information deleted from database.")
    except:
        st.warning("There is no data available in the database")

    if st.button("View updated data"):
        cursor.execute(
            "select Company_Name,Card_Holder_Name,Designation,Mobile_number,Email_address,Website_URL,Area,City,State,Pin_code from biz_data")
        updated_df = pd.DataFrame(cursor.fetchall(),
                                  columns=["Company_Name", "Card_Holder_Name", "Designation", "Mobile_Number", "Email",
                                           "Website", "Area", "City", "State", "Pin_Code"])
        st.write(updated_df)


    
        
