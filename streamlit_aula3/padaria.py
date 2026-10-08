import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Padaria Pão",
    page_icon="🥐",
    layout="wide"
)


def criar_dataframe_padaria():
    return pd.DataFrame({
        "Produto": [
            "Pão francês", "Pão de queijo", "Pão integral",
            "Pão de forma", "Croissant", "Sonho",
            "Bolo de chocolate", "Bolo de cenoura", "Broa de milho",
            "Rosquinha", "Cookie", "Empada",
            "Coxinha", "Sanduíche natural", "Café",
            "Cappuccino", "Chocolate quente", "Suco de laranja"
        ],
        "Categoria": [
            "Pães", "Pães", "Pães",
            "Pães", "Pães", "Doces",
            "Bolos", "Bolos", "Bolos",
            "Doces", "Doces", "Salgados",
            "Salgados", "Salgados", "Bebidas",
            "Bebidas", "Bebidas", "Bebidas"
        ],
        "Preço": [
            0.80, 3.50, 8.00,
            9.50, 7.00, 6.00,
            8.00, 7.50, 5.00,
            2.50, 4.50, 6.00,
            5.50, 10.00, 4.00,
            7.00, 6.50, 8.00
        ],
        "Estoque": [
            250, 120, 35,
            40, 60, 45,
            30, 30, 50,
            80, 70, 50,
            90, 25, 100,
            60, 50, 40
        ]
    })


def calcular_preco(preco_unitario, quantidade):
    # Calcula em centavos para evitar imprecisões com dinheiro.
    preco_centavos = round(float(preco_unitario) * 100)
    return preco_centavos * int(quantidade) / 100


def formatar_moeda(valor):
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


df = criar_dataframe_padaria()

with st.sidebar:
    st.title("🥐 Padaria Pão")
    st.caption("Fresquinho todos os dias")
    st.divider()

    nome = st.text_input("Qual é seu nome?", placeholder="Digite aqui")

    st.subheader("Filtrar produtos")

    busca = st.text_input(
        "Buscar por nome",
        placeholder="Ex.: pão de queijo"
    )

    categorias = st.multiselect(
        "Categorias",
        options=df["Categoria"].unique(),
        placeholder="Todas as categorias"
    )

    apenas_baixo_estoque = st.checkbox("Mostrar estoque abaixo de 40")

st.title("🍞 Nosso balcão")
st.caption("Escolha seus produtos e confira o valor da compra.")

if nome.strip():
    st.info(f"Bem-vindo(a), {nome.strip()}! ☕")

col1, col2, col3 = st.columns(3)

col1.metric("Produtos cadastrados", len(df))
col2.metric("Unidades em estoque", int(df["Estoque"].sum()))
col3.metric("Categorias", df["Categoria"].nunique())

st.divider()

filtrado = df[
    df["Produto"].str.contains(busca, case=False, regex=False, na=False)
].copy()

if categorias:
    filtrado = filtrado[filtrado["Categoria"].isin(categorias)]

if apenas_baixo_estoque:
    filtrado = filtrado[filtrado["Estoque"] < 40]

st.subheader("📋 Produtos disponíveis")
st.caption("Use os controles da tabela para pesquisar, ordenar e baixar.")

st.dataframe(
    filtrado,
    hide_index=True,
    use_container_width=True,
    height=400,
    column_config={
        "Produto": st.column_config.TextColumn(
            "🥖 Produto", width="large"
        ),
        "Categoria": st.column_config.TextColumn("🏷️ Categoria"),
        "Preço": st.column_config.NumberColumn(
            "Preço (R$)", format="R$ %.2f"
        ),
        "Estoque": st.column_config.ProgressColumn(
            "Estoque (unidades)",
            format="%d",
            min_value=0,
            max_value=int(df["Estoque"].max())
        )
    }
)

if filtrado.empty:
    st.warning("Nenhum produto encontrado com esses filtros.")
else:
    st.caption(f"{len(filtrado)} de {len(df)} produtos exibidos.")

st.divider()
st.subheader("🛒 Carrinho")
st.caption("Selecione os produtos e ajuste a quantidade de cada um.")

selecionados = st.multiselect(
    "Adicionar produtos",
    options=df.loc[df["Estoque"] > 0, "Produto"].tolist(),
    placeholder="Escolha os produtos do carrinho"
)

if selecionados:
    coluna_itens, coluna_pagamento = st.columns([2, 1], gap="large")
    itens_carrinho = []

    with coluna_itens:
        with st.container(border=True):
            st.markdown("### 🥖 Seus itens")

            for produto in selecionados:
                item = df.loc[df["Produto"] == produto].iloc[0]
                preco = float(item["Preço"])

                col_produto, col_quantidade = st.columns([2, 1])

                with col_produto:
                    st.markdown(f"**{produto}**")
                    st.caption(f"{formatar_moeda(preco)} por unidade")

                with col_quantidade:
                    quantidade = st.number_input(
                        "Quantidade",
                        min_value=1,
                        max_value=int(item["Estoque"]),
                        value=1,
                        step=1,
                        key=f"quantidade_{produto}"
                    )

                subtotal = calcular_preco(preco, quantidade)

                itens_carrinho.append({
                    "Produto": produto,
                    "Quantidade": quantidade,
                    "Preço unitário": preco,
                    "Subtotal": subtotal
                })

                st.caption(f"Subtotal: {formatar_moeda(subtotal)}")
                st.divider()

        st.markdown("#### Resumo dos itens")

        st.dataframe(
            pd.DataFrame(itens_carrinho),
            hide_index=True,
            use_container_width=True,
            column_config={
                "Preço unitário": st.column_config.NumberColumn(
                    "Preço unitário", format="R$ %.2f"
                ),
                "Subtotal": st.column_config.NumberColumn(
                    "Subtotal", format="R$ %.2f"
                )
            }
        )

    # Soma os subtotais em centavos.
    total = sum(
        round(item["Subtotal"] * 100)
        for item in itens_carrinho
    ) / 100

    quantidade_total = sum(
        item["Quantidade"] for item in itens_carrinho
    )

    with coluna_pagamento:
        with st.container(border=True):
            st.markdown("### 💳 Pagamento")
            st.metric("Total da compra", formatar_moeda(total))
            st.caption(
                f"{len(itens_carrinho)} produtos · "
                f"{quantidade_total} unidades"
            )

            st.divider()

            valor_pago = st.number_input(
                "Valor pago (R$)",
                min_value=0.0,
                value=0.0,
                step=1.0,
                format="%.2f"
            )

            diferenca_centavos = (
                round(valor_pago * 100) - round(total * 100)
            )

            if diferenca_centavos >= 0:
                troco = diferenca_centavos / 100
                st.metric("Troco a receber", formatar_moeda(troco))

                if troco == 0:
                    st.success("Valor exato! Sem troco.")
                else:
                    st.success("Valor suficiente para pagar a compra.")
            else:
                falta = abs(diferenca_centavos) / 100
                st.warning(f"Faltam {formatar_moeda(falta)} para pagar.")

else:
    st.info("Selecione um produto para começar a calcular.")

st.divider()
st.caption("🥐 Padaria Pão · Feito com carinho, servido fresquinho.")