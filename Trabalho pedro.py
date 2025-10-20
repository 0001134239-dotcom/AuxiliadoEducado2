import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

st.title("Monitoramento da empresa ORDEP")
st.markdown('---')
st.sidebar.header("📁 Base de Dados")

uploaded_file = st.sidebar.file_uploader("Carregar planilha CSV", type="csv")

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=[
        "Data", "Máquina", "Função", "Turno",
        "Peças Boas", "Peças Ruins", "Total Produzido"
    ])
if uploaded_file is not None:
    st.session_state.df = pd.read_csv(uploaded_file, parse_dates=["Data"])
    st.sidebar.success("Arquivo carregado com sucesso.")
st.session_state.df["Eficiência (%)"] = st.session_state.df.get(
    "Eficiência (%)",
    (st.session_state.df["Peças Boas"] / st.session_state.df["Total Produzido"].replace(0, 1)) * 100
)


st.sidebar.markdown("---")
aba1, aba2, aba3 = st.tabs(["Início", "Produção", "Monitoramento"])

with aba1:
    st.title("Central de produção")

with aba2:
    st.subheader("Registro de Produção Diária")
    st.write("Insira abaixo as informações referentes à produção do turno.")

    with st.form("form_producao"):
        col1, col2, col3 = st.columns(3)
        with col1:
            data = st.date_input("Data", value=datetime.today())
        with col2:
            turno = st.selectbox("Turno", ["Manhã", "Tarde", "Noite"])
        with col3:
            maq = st.text_input("Máquina:")

        funcao = st.selectbox("Função:", ["Recolher peças boas", "Recolher peças ruins"])
        total = st.number_input("Total produzido no dia:", min_value=0)

        col4, col5 = st.columns(2)
        with col4:
            boas = st.number_input("Peças boas:", min_value=0)
        with col5:
            ruins = st.number_input("Peças defeituosas:", min_value=0)

        enviar = st.form_submit_button("Registrar Produção")

    if enviar:
        if boas + ruins != total:
            st.error("A soma de peças boas e ruins deve ser igual ao total produzido.")
        else:
            nova_linha = {
                "Data": pd.to_datetime(data),
                "Máquina": maq,
                "Função": funcao,
                "Turno": turno,
                "Peças Boas": boas,
                "Peças Ruins": ruins,
                "Total Produzido": total
            }
            st.session_state.df.loc[len(st.session_state.df)] = nova_linha

            st.session_state.df["Eficiência (%)"] = (
                st.session_state.df["Peças Boas"] / st.session_state.df["Total Produzido"].replace(0, 1)
            ) * 100

            st.success("Registro adicionado com sucesso!")

with aba3:
    st.subheader("Análises de Produção")

    if st.session_state.df.empty:
        st.info("Nenhum dado disponível. Adicione produções ou carregue um arquivo CSV.")
    else:
        df = st.session_state.df

        st.markdown("#### Resumo Geral")
        col1, col2, col3 = st.columns(3)
        col1.metric("Eficiência Média", f"{df['Eficiência (%)'].mean():.1f}%")
        col2.metric("Total Produzido", int(df["Total Produzido"].sum()))
        col3.metric("Peças com Defeito", int(df["Peças Ruins"].sum()))
        st.markdown('---')

        st.markdown("#### Registros Recentes")
        st.dataframe(df.tail(10), use_container_width=True, height=250)

        st.markdown("#### Alertas Automáticos")
        cond = (df["Eficiência (%)"] < 90) | (df["Total Produzido"] < 80)
        alertas = df.loc[cond]

        if alertas.empty:
            st.success("Nenhum alerta encontrado")
        else:
            st.error('Alerta de baixa produtividade')
            st.dataframe(alertas, use_container_width=True)
        st.markdown('---')

        st.markdown("Gráficos")
   
        prod = df.groupby("Data")[["Peças Boas", "Peças Ruins"]].sum()
        fig1, ax1 = plt.subplots(figsize=(10,4))
        prod.plot(kind='bar', stacked=True, ax=ax1, color=['#3A86FF','#FF595E'])
        ax1.set_title("Produção total por dia")
        ax1.set_ylabel("Quantidade de peças")
        ax1.set_xlabel("Data")
        plt.xticks(rotation=45)
        st.pyplot(fig1)

        efic = df.groupby("Data")["Eficiência (%)"].mean()
        fig2, ax2 = plt.subplots(figsize=(10,4))
        ax2.plot(efic.index, efic.values, marker='o', color="#FFB703")
        ax2.set_title("Eficiência média por dia (%)")
        ax2.set_ylabel("Eficiência (%)")
        ax2.set_xlabel("Data")
        ax2.set_ylim(0,100)
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig2)

        st.markdown('---')
        st.markdown("#### Exportar Planilha")
        nome_csv = st.text_input("Nome do arquivo:", value="planilha.csv")
        if st.button("Salvar como CSV"):
            df.to_csv(nome_csv, index=False)
            st.success(f"Arquivo '{nome_csv}' salvo com sucesso.")
