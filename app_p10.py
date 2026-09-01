import streamlit as st
from PIL import Image
from google import genai
import os

st.set_page_config(
    page_title="Intelligent Receipt Analyzer",
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 Intelligent Receipt Analyzer")

st.write(
    "Upload or take a photo of a receipt and get a complete explanation "
    "of items, prices, tax, discount and total."
)

api_key = ("AQ.Ab8RN6LRCfiIhOfHXazqIYPnQCZ6EV-9s1jo437IQFJrJXJc-A")

if not api_key:
    st.error("GEMINI_API_KEY is not set.")
    st.info("Set your Gemini API key in PowerShell and restart the app.")
    st.stop()

client = genai.Client(api_key=api_key)

st.subheader("📷 Upload Receipt")

uploaded_file = st.file_uploader(
    "Choose a receipt image",
    type=["jpg", "jpeg", "png"]
)

camera_file = st.camera_input("Or take a picture")

image_file = camera_file if camera_file else uploaded_file

if image_file is not None:

    image = Image.open(image_file)

    st.subheader("🖼️ Uploaded Image")
    st.image(image, width="stretch")

    if st.button(
        "🔍 Analyze Receipt",
        type="primary",
        width="stretch"
    ):

        prompt = """
Analyze this receipt image carefully.

Extract ONLY information that is clearly visible.

RECEIPT DETAILS

Store:
Address:
Date:
Time:
Receipt Number:

ITEMS

For every item provide:
Item name:
Quantity:
Unit price:
Line total:

FINANCIAL SUMMARY

Subtotal:
Discount:
CGST:
SGST:
IGST:
Other tax:
Grand total:

PAYMENT METHOD:

CALCULATION CHECK

Check whether:

Item totals + taxes - discounts = final total.

If the calculation does not match, explain the difference.

TAX EXPLANATION

Explain the taxes shown on the receipt in simple language.

PRICE EXPLANATION

Explain the price of each item, quantity, item total,
subtotal, discount, tax and final amount.

OTHER INFORMATION

Mention any other important information visible.

IMPORTANT:
Do not guess.
If something cannot be read, write "Not visible".
"""

        with st.spinner("🔍 Analyzing the receipt..."):

            try:

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[prompt, image]
                )

                st.success("✅ Analysis completed!")

                st.subheader("📊 Complete Receipt Analysis")

                st.markdown(response.text)

            except Exception as e:

                st.error("Something went wrong while analyzing the image.")

                st.code(str(e))

else:

    st.info("📤 Upload a receipt image or take a photo to begin.")