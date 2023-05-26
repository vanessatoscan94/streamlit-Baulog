import streamlit as st

import preprocessing
import simulation
import analytics

# Main Streamlit app
def main():
    st.title("Baustellenlogistik MVP")

    # Allow the user to upload a file
    uploaded_file = st.file_uploader("Upload a file", type=["xlsx"])

    # Perform analysis if a file is uploaded
    if uploaded_file is not None:
        st.text("Start Simulation!")
        data = preprocessing.run(uploaded_file)
        simulation.run(data)
        st.text("Simulation complete!")


if __name__ == "__main__":
    main()
