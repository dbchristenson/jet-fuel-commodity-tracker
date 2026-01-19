import os
from pathlib import Path
from random import choice

import streamlit as st


def render_header():
    # Roll for image
    if "header_image" not in st.session_state:

        # This block only runs ONCE per user session (on page load/refresh)
        headers_dir = Path("resources") / "headers"
        available_files = os.listdir(headers_dir)

        if available_files:
            # random.choice is cleaner than randint with indices
            selected_file = choice(available_files)

            print("DO A BARREL ROLL: New image selected.")
            print(f"image_location: {selected_file}")

            # Save the result to session state
            st.session_state["header_image"] = headers_dir / selected_file
        else:
            st.session_state["header_image"] = None

    # Retrieve the image from state (this happens on every rerun)
    image_url = st.session_state["header_image"]

    # Set the title and favicon that appear in the Browser's tab bar.
    st.set_page_config(
        page_title="Jet Fuel Commodity Tracker",
        page_icon=":earth_americas:",
    )

    st.header(":airplane: Jet Fuel Commodity Tracker")
    st.image(str(image_url) if image_url else None, width="stretch")
