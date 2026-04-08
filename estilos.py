import streamlit as st


def aplicar_estilos():
    st.markdown("""
    <style>

    html, body, [class*="css"] {
        font-family: Georgia, "Times New Roman", serif !important;
    }

    h1, h2, h3, h4, h5, h6, p, div {
        font-family: Georgia, "serif", serif !important;
        letter-spacing: 0.5px;
    }

    button {
        font-family: Georgia, "Times New Roman", serif !important;
    }

    input, textarea, select {
        font-family: Georgia, "Times New Roman", serif !important;
    }

    h1 {
    font-size: 2.5rem;
    }
    
    </style>
    """, unsafe_allow_html=True)