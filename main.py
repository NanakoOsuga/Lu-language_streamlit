import streamlit as st
from janome.tokenizer import Tokenizer
from google.oauth2 import service_account
from google.cloud import translate_v2 as translate
import alkana


# sectetsのAPIキーを変数に格納
type = st.secrets["SERVICE_ACCOUNT_INFO"]["type"]
project_id = st.secrets["SERVICE_ACCOUNT_INFO"]["project_id"]
private_key_id = st.secrets["SERVICE_ACCOUNT_INFO"]["private_key_id"]
private_key = st.secrets["SERVICE_ACCOUNT_INFO"]["private_key"]
client_email = st.secrets["SERVICE_ACCOUNT_INFO"]["client_email"]
client_id = st.secrets["SERVICE_ACCOUNT_INFO"]["client_id"]
auth_uri = st.secrets["SERVICE_ACCOUNT_INFO"]["auth_uri"]
token_uri = st.secrets["SERVICE_ACCOUNT_INFO"]["token_uri"]
auth_provider_x509_cert_url = st.secrets["SERVICE_ACCOUNT_INFO"]["auth_provider_x509_cert_url"]
client_x509_cert_url = st.secrets["SERVICE_ACCOUNT_INFO"]["client_x509_cert_url"]
universe_domain = st.secrets["SERVICE_ACCOUNT_INFO"]["universe_domain"]


## textから名詞を抽出する関数
def get_nouns(text):
    t = Tokenizer()
    tokens = t.tokenize(text)
    nouns = [token.surface for token in tokens if token.part_of_speech.split(',')[0] == '名詞']
    return nouns


# APIキーを設定
@st.cache_resource
def get_translate_client():
    service_account_info = {
        "type": st.secrets["SERVICE_ACCOUNT_INFO"]["type"],
        "project_id": st.secrets["SERVICE_ACCOUNT_INFO"]["project_id"],
        "private_key_id": st.secrets["SERVICE_ACCOUNT_INFO"]["private_key_id"],
        "private_key": st.secrets["SERVICE_ACCOUNT_INFO"]["private_key"],
        "client_email": st.secrets["SERVICE_ACCOUNT_INFO"]["client_email"],
        "client_id": st.secrets["SERVICE_ACCOUNT_INFO"]["client_id"],
        "auth_uri": st.secrets["SERVICE_ACCOUNT_INFO"]["auth_uri"],
        "token_uri": st.secrets["SERVICE_ACCOUNT_INFO"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["SERVICE_ACCOUNT_INFO"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["SERVICE_ACCOUNT_INFO"]["client_x509_cert_url"],
        "universe_domain": st.secrets["SERVICE_ACCOUNT_INFO"]["universe_domain"]
    }
    
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    return translate.Client(credentials=credentials)


## nounsを英語に翻訳する関数
def translated_nouns(nouns):
  translated_nouns = []
  translate_client = get_translate_client()

  for noun in nouns:
      result = translate_client.translate(noun, target_language='en')
      translated_nouns.append(result['translatedText'])

  return translated_nouns


## translated_nounsをカタカナにする関数
def get_kana_words(word_list):
    kana_results = []
    
    for word in word_list:
        kana_word = alkana.get_kana(word)
        kana_results.append(kana_word)
    
    return kana_results



## ↑の一連の流れをまとめた関数
def process_text(text):
    # 抽出した名詞を取得
    nouns = get_nouns(text)

    # 名詞を英語に翻訳
    translated = translated_nouns(nouns)

    # 翻訳した英語をカタカナに変換
    kana_words = get_kana_words(translated)

    return kana_words


# textの単語を抽出してリスト化する関数
def get_words(text):
    t = Tokenizer()
    tokens = t.tokenize(text)
    words = [token.surface for token in tokens]
    return words


# 単語リストと名詞リストを辞書型に変換する関数
def get_translated_word_dict(text):
    word_list = get_words(text) # 単語リスト
    noun_list = get_nouns(text) # 名詞リスト

    translated_word_dict = {} # 辞書型
    for word in word_list: # 単語リスト全体に対して処理
        if word in noun_list: # 名詞が含まれている場合
            translated_word = translated_nouns([word]) # 名詞を英語に翻訳
            if translated_word[0] is not None: # 翻訳結果がNoneでない場合
                kana_word = get_kana_words(translated_word) # カタカナに変換
                if kana_word[0] is not None: # カタカナに変換結果がNoneでない場合
                    translated_word_dict[word] = kana_word[0] # 辞書型に変換

    return translated_word_dict


# inputされたテキストを最終的に変換する関数
def replace_words_with_translation(text):
    translated_word_dict = get_translated_word_dict(text) # 辞書型
    word_list = get_words(text) # 単語リスト

    result = []
    for word in word_list:
        if word in translated_word_dict: # 単語が名詞かどうかを確認
            result.append(translated_word_dict[word]) # 単語が名詞なら、カタカナ表記をresultに追加
        else:
            result.append(word) # 単語が名詞でなければ、そのままresultに追加

    result = ' '.join(result) # 半角スペース区切り
    result = result.replace(' ', '') # 半角スペース削除

    return result