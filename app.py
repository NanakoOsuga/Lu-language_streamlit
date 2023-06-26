import streamlit as st
from janome.tokenizer import Tokenizer
from google.cloud import translate_v2 as translate
import alkana
from main import replace_words_with_translation

st.title('ルー語変換アプリ')

# User input
text = st.text_input('テキストを入力してください')

if text:
    result = replace_words_with_translation(text)
    st.write(result)

# pip install googletrans
# pip install google-cloud-translate
# pip install --upgrade google-cloud-translate
# pip install protobuf==3.20.0
# set GOOGLE_APPLICATION_CREDENTIALS="PATH"
# export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
# pip install -U alkana
# pip install janome