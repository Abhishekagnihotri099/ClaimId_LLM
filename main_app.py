import streamlit as st
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os
import pandas as pd
from agent_text_summarization import get_comments_summary  
import sys
import json
import re
from agent_line_items_from_documents import check_line_items_from_documents
from agent_notes_similarity_search import check_notes_incident_description
from agent_generate_flowchart_llm import generate_flowchart 
from agent_chatbot import chatbot_response

st.title("Loss Not Covered Per Policy")



def check_column_values(df, columns):
    if df.empty:
        return False
    return not df[columns].isnull().values.any()


def check_loss_details(claim_number, incidents, claims, vehicles, output):
    # Identify loss details
    columns_to_check = {
    'incidents': ['LossDesc'],
    'claims': ['LossDate', 'LossCause', 'LossLocationID'],
    'vehicles': ['Vin', 'Make', 'Model', 'Year', 'ID']
    }

    incidents_column_status = check_column_values(incidents[incidents['ClaimNumber'] == claim_number], columns_to_check['incidents'])
    claims_column_status = check_column_values(claims[claims['ClaimNumber'] == claim_number], columns_to_check['claims'])
    vehicles_column_status = check_column_values(vehicles[vehicles['ClaimNumber'] == claim_number], columns_to_check['vehicles'])
    # st.write(incidents_column_status, claims_column_status, vehicles_column_status)



    if incidents_column_status and claims_column_status and vehicles_column_status:
        comment = "Loss Details Available for given Claim Number"
        # st.warning(comment)
        output['comments'] += comment + " "
        return True
    else:
        comment = "Loss Details Missing for given Claim Number"
        # st.error(comment)
        output['comments'] += comment + " "
        return False
    
def check_policy_details(claim_number, policies, contacts, output):

    columns_to_check = {
        'policies' : ['PolicyNumber', 'PolicySource', 'EffectiveDate', 'ExpirationDate', 'CancellationDate'],
        'contacts' : ['FirstName', 'LastName']
    }

    policies_column_status = check_column_values(policies[policies['ClaimNumber'] == claim_number], columns_to_check['policies'])
    contacts_column_status = check_column_values(contacts[contacts['ClaimNumber'] == claim_number], columns_to_check['contacts'])
    # st.write(policies_column_status, contacts_column_status)

    if policies_column_status and contacts_column_status:
        comment = "Policy Details Available for given Claim Number"
        # st.warning(comment)
        output['comments'] += comment + " "
        return True
    else:
        comment = "Policy Details Missing for given Claim Number"
        # st.error(comment)
        output['comments'] += comment + " "
        return False
    
def check_claim_summary_details(claim_number, incidents, output):
     
    columns_to_check = {
    'incidents': ['LossDesc']
    }

    incidents_column_status = check_column_values(incidents[incidents['ClaimNumber'] == claim_number], columns_to_check['incidents'])

    if incidents_column_status:
        comment = "Claim Summary Details Available for given Claim Number"
        # st.warning(comment)
        output['comments'] += comment + " "
        return True
    else:
        comment = "Claim Summary Details Missing for given Claim Number"
        # st.error(comment)
        output['comments'] += comment + " "
        return False

def main():
    output = {'comments': '', 'final_output': ''}
    claim_number = st.text_input("Enter the claim number")
    if claim_number:
        # Load data
        claims = pd.read_csv('claims.csv')
        policies = pd.read_csv('policies.csv')
        contacts = pd.read_csv('contacts.csv')
        vehicles = pd.read_csv('vehicles.csv')
        incidents = pd.read_csv('incidents.csv')
        exposures = pd.read_csv('exposures.csv')
        transactions = pd.read_csv('transactions.csv')
        notes = pd.read_csv('notes.csv')
        coverages = pd.read_csv('coverages.csv')
        history = pd.read_csv('history.csv')
        activities = pd.read_csv('activities.csv')

        # Check Mandatory Data Availability
        is_loss_details_available = check_loss_details(claim_number, incidents, claims, vehicles, output)
        is_policy_details_available = check_policy_details(claim_number, policies, contacts, output)
        is_claim_summary_details_available = check_claim_summary_details(claim_number, incidents, output)

        if not(is_loss_details_available and is_policy_details_available and is_claim_summary_details_available):
            comment = "**Data Check - Mandatory Data Missing for given Claim Number**"
            # st.error(comment)
            output['comments'] += comment + " "
            st.success("**FINAL OUTPUT - MANUAL REVIEW**")
            output['final_output'] = "MANUAL REVIEW"
            summary = get_comments_summary(output)
            st.success(summary)
            return output
        else:
            comment = "**Data Check - Mandatory Data Available for given Claim Number**"
            # st.success(comment)  
            output['comments'] += comment + " "         


            # Check 1 - Is policy type nominated driver policy?
            if (policies[policies['ClaimNumber'] == claim_number]['Type'] == "Nominated").any():
                comment = "**Check 1 - Yes policy type is nominated driver policy**"
                # st.success(comment)
                output['comments'] += comment + " "
                # If True - Check 2 - Check if the driver is listed as nominated driver?
                if (policies[policies['ClaimNumber'] == claim_number]['Driver'] == "Nominated").any():
                    comment = "**Check 2 - Yes the driver is listed as nominated driver**"
                    # st.success(comment)
                    output['comments'] += comment + " "
                    
                    st.success("**FINAL OUTPUT - MET (Loss and coverage consistent with policy)**")
                    output['final_output'] = "MET (Loss and coverage consistent with policy)"
                    summary = get_comments_summary(output)
                    st.success(summary)
                    return output
                else:
                    comment = "**Check 2 - Driver is not a nominated driver**"
                    # st.error(comment)
                    output['comments'] += comment + " "

                    st.success("**FINAL OUTPUT - NOT MET (Driver is not a nominated driver)**")
                    output['final_output'] = "NOT MET (Driver is not a nominated driver)"
                    summary = get_comments_summary(output)
                    st.success(summary)
                    return output

            else:
                comment = "**Check 1 - Policy type is not nominated driver policy**"
                # st.error(comment)
                output['comments'] += comment + " "

                note_body = claims.loc[claims['ClaimNumber'] == claim_number, 'Notes'].iloc[0]

                    # Call the function to check incident
                response = check_notes_incident_description(note_body)
                  # Simulating a string response

                # Convert string back to dictionary
                # st.write(response)
                # st.write(repr(response))
                response_cleaned = re.sub(r'^\s*json\s*', '', response)  # Remove 'json' and leading whitespace

                # Step 2: Remove any remaining newlines or spaces
                response_cleaned = response_cleaned.strip()

                # Step 3: Remove all internal newlines within the JSON structure, ensuring it's formatted correctly
                response = re.sub(r'\s+', ' ', response_cleaned) 
                
                # response = json.loads(response)
                # if 'true' in response:
                #     st.write('yes')
                
                # Check 3 - Underwriter question completed by?
                if 'false' in response:
                    comment = f"**Check 3 - Incident details not verified - {claims.loc[claims['ClaimNumber'] == claim_number, 'Notes'].iloc[0]}**"
                    # st.success(comment)
                    output['comments'] += comment + " "

                    st.success("**FINAL OUTPUT - NOT MET (Incident details not verified)**")
                    output['final_output'] = "NOT MET (Incident details not verified)"
                    summary = get_comments_summary(output)
                    st.success(summary)
                    return output
                else:
                    comment = f"**Check 3 - Incident details verified - {note_body}**"
                    # st.success(comment)
                    output['comments'] += comment + " "
                    
                    # Check 4 - Is loss location/vehicle active on policy?
                    if (policies[policies['ClaimNumber'] == claim_number]['Vehicle'] == "Active").any():
                        comment = "**Check 4 - Yes loss location/vehicle active on policy**"
                        # st.success(comment)
                        output['comments'] += comment + " "
                        
                        st.success("**FINAL OUTPUT - MET (Loss and coverage consistent with policy)**")
                        output['final_output'] = "MET (Loss and coverage consistent with policy)"
                        summary = get_comments_summary(output)
                        st.success(summary)
                        return output
                    else:
                        comment = "**Check 4 - Loss location/vehicle not active on policy**"
                        output['comments'] += comment + " "

                        # Check 5 - Check if correct exposure has been set up?
                        if (exposures[exposures['ClaimNumber'] == claim_number]['Exposure'] == "Correct").any():
                            comment = "**Check 5 - Correct exposure has been set up**"
                            # st.success(comment)
                            output['comments'] += comment + " "

                            st.success ("**FINAL OUTPUT - MET (Loss and coverage consistent with policy)**")
                            output['final_output'] = "MET (Loss and coverage consistent with policy)"
                            summary = get_comments_summary(output)
                            st.success(summary)
                            return output
                        else:
                            comment = "**Check 5 - Correct exposure has not been set up**"
                            # st.error(comment)
                            output['comments'] += comment + " "

                            # Check 6 - Check if claim has been assigned for Assessment?
                            if (claims[claims['ClaimNumber'] == claim_number]['Assessment'] == "NO").any():
                                comment = "**Check 6 - Claim has not been assigned for Assessment**"
                                # st.success(comment)
                                output['comments'] += comment + " "

                                st.success("**FINAL OUTPUT - NOT MET (Claim is not assigned for further assessment)**")
                                output['final_output'] = "NOT MET (Claim is not assigned for further assessment"
                                summary = get_comments_summary(output)
                                st.success(summary)
                                return output
                            else:
                                comment = "**Check 6 - Claim has been assigned for Assessment**"
                                # st.error(comment)
                                output['comments'] += comment + " "

                                # Check 7 - Check if loss cause as per PDS?
                                if (claims[claims['ClaimNumber'] == claim_number]['LossCause_asper_PDS'] == "YES").any():
                                    comment = "**Check 7 - Loss cause as per PDS**"
                                    # st.success(comment)
                                    output['comments'] += comment + " "

                                    st.success("**FINAL OUTPUT - MET (Loss and coverage consistent with policy)**")
                                    output['final_output'] = "MET (Loss and coverage consistent with policy)"
                                    summary = get_comments_summary(output)
                                    st.success(summary)
                                    return output
                                else:
                                    comment = "**Check 7 - Loss cause not as per PDS**"
                                    # st.error(comment)
                                    output['comments'] += comment + " "

                                    # Check 8 - Check if repaired/ replaced items listed in invoice is as per pds?
                                    items_as_per_pds, items_not_as_per_pds = check_line_items_from_documents(claim_number)
                                    if len(items_not_as_per_pds) == 0:
                                        comment = f"**Check 8 - {items_as_per_pds} is as per PDS**"
                                        # st.success(comment)
                                        output['comments'] += comment + " "

                                        st.success("**FINAL OUTPUT - MET (Loss and coverage consistent with policy)**")
                                        output['final_output'] = "MET (Loss and coverage consistent with policy)"
                                        summary = get_comments_summary(output)
                                        st.success(summary)

                                        return output
                                    else:
                                        comment = f"**Check 8 - {items_not_as_per_pds} is not as per PDS**"
                                        # st.error(comment)
                                        output['comments'] += comment + " "

                                        # Check 9 - Payment created agaist the repairs/replacement is justified in notes ?
                                        if (transactions[transactions['ClaimNumber'] == claim_number]['PaymentJustifiedInNotes'] == "YES").any():
                                            comment = "**Check 9 - Payment created against the repairs/replacement is justified in notes**"
                                            # st.success(comment)
                                            output['comments'] += comment + " "

                                            st.success("**FINAL OUTPUT - MET (Loss and coverage consistent with policy)**")
                                            output['final_output'] = "MET (Loss and coverage consistent with policy)"
                                            summary = get_comments_summary(output)
                                            st.success(summary)
                                            return output
                                        else:
                                            comment = "**Check 9 - Payment created against the repairs/replacement is not justified in notes**"
                                            # st.error(comment)
                                            output['comments'] += comment + " "

                                            st.success("**FINAL OUTPUT - NOT MET (Cause of loss/ event or damage is excluded on the notes)**")
                                            output['final_output'] = "NOT MET (Cause of loss/ event or damage is excluded on the notes)"
                                            summary = get_comments_summary(output)
                                            st.success(summary)
                                            return output

                

                

                

if __name__ == "__main__":
    # main()
    output = main()
    if output:
        chatbot_response(output)
    # generate_flowchart(output)
    

