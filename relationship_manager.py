import streamlit as st
import pandas as pd

# Relationship Manager Class
class RelationshipManager:
    def __init__(self):
        self.relationships = []

    def create_relationship(self, table1_name, column1, table2_name, column2, cardinality, active=True, cross_filter_direction="both"):
        relationship = {
            "table1_name": table1_name,
            "column1": column1,
            "table2_name": table2_name,
            "column2": column2,
            "cardinality": cardinality,
            "active": active,
            "cross_filter_direction": cross_filter_direction,
        }
        self.relationships.append(relationship)

    def apply_filter(self, tables, source_table_name, target_table_name, source_column, target_column):
        if source_table_name not in tables or target_table_name not in tables:
            return None
        source_table = tables[source_table_name]
        target_table = tables[target_table_name]

        # Filter based on the relationships
        merged_table = pd.merge(
            source_table,
            target_table,
            left_on=source_column,
            right_on=target_column,
            how="inner"
        )
        return merged_table


# Sample DataFrames
dsoutcome_history_final = pd.DataFrame({
    "CLAIM ID": [101, 102, 103],
    "Outcome": ["Approved", "Denied", "Pending"]
})

claims = pd.DataFrame({
    "CLAIM ID": [101, 102, 104],
    "ClaimAmount": [1000, 2000, 1500]
})

# Create tables dictionary
tables = {
    "DsoutcomeHistoryFinal": dsoutcome_history_final,
    "Claims": claims
}

# Initialize Relationship Manager
rm = RelationshipManager()

# Streamlit Interface
st.title("Dynamic Relationship Manager")

# Input to define the relationship
st.sidebar.header("Define Relationship")
table1_name = st.sidebar.selectbox("Select Table 1", options=list(tables.keys()))
column1 = st.sidebar.selectbox("Select Column in Table 1", options=tables[table1_name].columns)

table2_name = st.sidebar.selectbox("Select Table 2", options=list(tables.keys()))
column2 = st.sidebar.selectbox("Select Column in Table 2", options=tables[table2_name].columns)

cardinality = st.sidebar.selectbox("Select Cardinality", options=["Many to One", "One to Many", "One to One", "Many to Many"])
active = st.sidebar.checkbox("Make Relationship Active", value=True)
cross_filter_direction = st.sidebar.selectbox("Select Cross-Filter Direction", options=["Both", "Single"])

if st.sidebar.button("Create Relationship"):
    rm.create_relationship(table1_name, column1, table2_name, column2, cardinality, active, cross_filter_direction)
    st.sidebar.success(f"Relationship created between {table1_name}.{column1} and {table2_name}.{column2}.")

# Display relationships
st.header("Defined Relationships")
if rm.relationships:
    st.table(pd.DataFrame(rm.relationships))
else:
    st.write("No relationships defined yet.")

# Apply filter based on user input
st.header("Filter Application")
if st.button("Apply Filter"):
    if rm.relationships:
        relationship = rm.relationships[-1]  # Apply the latest relationship
        filtered_table = rm.apply_filter(
            tables,
            relationship["table1_name"],
            relationship["table2_name"],
            relationship["column1"],
            relationship["column2"]
        )
        if filtered_table is not None:
            st.write("Filtered Table:")
            st.dataframe(filtered_table)
        else:
            st.error("One of the tables is missing. Cannot apply filter.")
    else:
        st.warning("No relationships to apply.")
