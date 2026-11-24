from datetime import date
import io
import os
import textwrap

import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Reporte SMG1", page_icon="📄", layout="wide")

# --- Menu Lateral (Botões para mudar de página) ---
with st.sidebar:
    st.markdown("### Navegação")
    col_btn1, col_btn2 = st.columns(2)

    if "pagina_atual" not in st.session_state:
        st.session_state.pagina_atual = "Reporte"

    with col_btn1:
        if st.button("📝 Reporte", use_container_width=True):
            st.session_state.pagina_atual = "Reporte"
    with col_btn2:
        if st.button("📊 OOT", use_container_width=True):
            st.session_state.pagina_atual = "OOT"

    st.divider()
    st.caption(f"Página ativa: **{st.session_state.pagina_atual}**")


# ==============================================================================
# PÁGINA 1: REPORTE
# ==============================================================================
if st.session_state.pagina_atual == "Reporte":
    caminho_logo = "mercado livre.jfif"

    if os.path.exists(caminho_logo):
        st.image(caminho_logo, width=200)

    st.title("📄 Reporte SMG1")

    if "reportes" not in st.session_state:
        st.session_state.reportes = []

    def gerar_imagem_relatorio(reportes):
        """Gera uma imagem PNG no tamanho mínimo de folha A4 (1240x1754 px - 150 DPI)
        com o logo do Mercado Livre no cabeçalho."""
        largura = 1240
        altura_minima_a4 = 1754
        altura_cabecalho = 150
        margem = 45

        try:
            fonte_titulo = ImageFont.truetype("arialbd.ttf", 34)
            fonte_subtitulo = ImageFont.truetype("arial.ttf", 20)
            fonte_negrito = ImageFont.truetype("arialbd.ttf", 24)
            fonte_texto = ImageFont.truetype("arial.ttf", 22)
        except OSError:
            fonte_titulo = ImageFont.load_default()
            fonte_subtitulo = ImageFont.load_default()
            fonte_negrito = ImageFont.load_default()
            fonte_texto = ImageFont.load_default()

        cartoes_preparados = []
        altura_conteudo = altura_cabecalho + margem

        for item in reportes:
            linhas_texto = textwrap.wrap(item["Passagem de Turno"], width=66)
            if not linhas_texto:
                linhas_texto = ["Sem observações."]

            altura_texto = 90 + (len(linhas_texto) * 30)
            altura_card = max(270, altura_texto + 35)

            cartoes_preparados.append((item, linhas_texto, altura_card))
            altura_conteudo += altura_card + 25

        altura_total = max(altura_minima_a4, altura_conteudo + margem)

        img = Image.new("RGB", (largura, altura_total), color=(248, 249, 250))
        draw = ImageDraw.Draw(img)

        draw.rectangle([(0, 0), (largura, 125)], fill=(255, 230, 0))
        draw.rectangle([(0, 120), (largura, 125)], fill=(30, 58, 138))

        x_titulo = margem
        if os.path.exists(caminho_logo):
            try:
                logo = Image.open(caminho_logo).convert("RGB")
                logo.thumbnail((170, 95))
                y_logo = (120 - logo.height) // 2
                img.paste(logo, (margem, y_logo))
                x_titulo = margem + logo.width + 30
            except Exception:
                pass

        draw.text(
            (x_titulo, 28),
            "REPORTE DE MONITORAMENTO - SMG1",
            fill=(15, 23, 42),
            font=fonte_titulo,
        )
        draw.text(
            (x_titulo, 74),
            f"Total de registros: {len(reportes)}  |  Emitido em: {date.today().strftime('%d/%m/%Y')}",
            fill=(51, 65, 85),
            font=fonte_subtitulo,
        )

        y_atual = altura_cabecalho

        for idx, (item, linhas_texto, altura_card) in enumerate(
            cartoes_preparados, start=1
        ):
            draw.rounded_rectangle(
                [(margem, y_atual), (largura - margem, y_atual + altura_card)],
                radius=12,
                fill=(255, 255, 255),
                outline=(203, 213, 225),
                width=2,
            )

            x_foto = margem + 20
            y_foto = y_atual + 20
            tam_foto = 230

            if item["Imagem"] is not None:
                foto = Image.open(io.BytesIO(item["Imagem"])).convert("RGB")
                foto.thumbnail((tam_foto, tam_foto))
                offset_x = x_foto + (tam_foto - foto.width) // 2
                offset_y = y_foto + (tam_foto - foto.height) // 2
                img.paste(foto, (offset_x, offset_y))
            else:
                draw.rectangle(
                    [(x_foto, y_foto), (x_foto + tam_foto, y_foto + tam_foto)],
                    fill=(241, 245, 249),
                    outline=(203, 213, 225),
                    width=2,
                )
                draw.text(
                    (x_foto + 68, y_foto + 102),
                    "Sem foto",
                    fill=(100, 116, 139),
                    font=fonte_texto,
                )

            x_texto = x_foto + tam_foto + 35
            draw.text(
                (x_texto, y_atual + 24),
                f"#{idx} | Data: {item['Data']} - {item['Turno']} ({item['Tipo de Reporte']})",
                fill=(30, 58, 138),
                font=fonte_negrito,
            )

            draw.line(
                [(x_texto, y_atual + 62), (largura - margem - 25, y_atual + 62)],
                fill=(226, 232, 240),
                width=2,
            )

            y_linha = y_atual + 78
            for linha in linhas_texto:
                draw.text(
                    (x_texto, y_linha),
                    linha,
                    fill=(30, 41, 59),
                    font=fonte_texto,
                )
                y_linha += 30

            y_atual += altura_card + 25

        buffer = io.BytesIO()
        img.save(buffer, format="PNG", dpi=(150, 150))
        return buffer.getvalue()

    with st.form("form_reporte", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            data_reporte = st.date_input(
                "Data do Reporte *",
                value=date.today(),
                format="DD/MM/YYYY",
            )
            tipo_reporte = st.selectbox(
                "Tipo de Reporte *",
                ["Comunicação de Acidentes", "Passagem de Turno", "OOT", "Outros"],
            )
        with col2:
            turno = st.selectbox(
                "Turno *",
                ["1º Turno (Manhã)", "2º Turno (Tarde)", "3º Turno (Noite)"],
            )

        passagem_turno = st.text_area(
            "Reporte Detalhado *",
            placeholder="Descreva as ocorrências, status da operação e pendências para o próximo turno...",
            height=140,
        )

        imagem = st.file_uploader(
            "Evidência / Imagem (opcional)",
            type=["png", "jpg", "jpeg", "webp", "jfif"],
        )

        salvar = st.form_submit_button("Registrar Reporte")

    if salvar:
        if passagem_turno.strip():
            dados_imagem = imagem.getvalue() if imagem is not None else None

            st.session_state.reportes.append({
                "Data": data_reporte.strftime("%d/%m/%Y"),
                "Turno": turno,
                "Tipo de Reporte": tipo_reporte,
                "Passagem de Turno": passagem_turno.strip(),
                "Imagem": dados_imagem,
            })
            st.success("Reporte registrado com sucesso!")
        else:
            st.warning(
                "Preencha o campo de Passagem de Turno antes de registrar."
            )

    st.divider()
    st.subheader(f"Reportes Registrados ({len(st.session_state.reportes)})")

    if st.session_state.reportes:
        imagem_relatorio = gerar_imagem_relatorio(st.session_state.reportes)
        st.download_button(
            label="📥 Baixar Reporte em Imagem A4 (PNG)",
            data=imagem_relatorio,
            file_name=f"reporte_smg1_{date.today().strftime('%d_%m_%Y')}.png",
            mime="image/png",
            use_container_width=True,
        )

        dados_tabela = [
            {k: v for k, v in item.items() if k != "Imagem"}
            for item in st.session_state.reportes
        ]
        st.dataframe(dados_tabela, use_container_width=True)

        st.write("### Detalhes e Evidências")
        for idx, item in enumerate(st.session_state.reportes, start=1):
            col1, col2 = st.columns([1, 3])
            with col1:
                if item["Imagem"] is not None:
                    st.image(item["Imagem"], use_container_width=True)
                else:
                    st.info("Sem imagem anexada")
            with col2:
                st.write(
                    f"**#{idx} — {item['Data']} | {item['Turno']} ({item['Tipo de Reporte']})**"
                )
                st.write(item["Passagem de Turno"])
            st.divider()
    else:
        st.info("Nenhum reporte registrado ainda.")


# ==============================================================================
# PÁGINA 2: OOT (Report de Expedição Diário)
# ==============================================================================
elif st.session_state.pagina_atual == "OOT":
    st.title("📊 Report de Expedição Diário — OOT")
    st.caption("Meta OOT = 90% | Resultados ≥ 90% em Verde e < 90% em Vermelho")

    def gerar_reporte_oot_jpg(
        total_pacotes,
        total_rotas,
        media_oot,
        df_ciclos_resumo,
        fig_oot,
        fig_rotas,
    ):
        """Gera uma imagem JPG de alta resolução reunindo resumo, tabela por ciclo e os dois gráficos."""
        largura = 2000
        margem = 50
        larg_util = largura - 2 * margem
        altura_cabecalho = 135
        altura_resumo = 130

        linhas_tab = len(df_ciclos_resumo) + 1
        altura_linha_tab = 44
        altura_tabela = 50 + linhas_tab * altura_linha_tab

        altura_graf_oot = 620 if fig_oot is not None else 0
        altura_graf_rotas = 580

        altura_total = (
            margem
            + altura_cabecalho
            + 25
            + altura_resumo
            + 25
            + altura_tabela
            + 30
            + (altura_graf_oot + 30 if fig_oot is not None else 0)
            + altura_graf_rotas
            + margem
        )

        try:
            fonte_titulo = ImageFont.truetype("arialbd.ttf", 36)
            fonte_sub = ImageFont.truetype("arial.ttf", 22)
            fonte_kpi_tit = ImageFont.truetype("arialbd.ttf", 19)
            fonte_kpi_val = ImageFont.truetype("arialbd.ttf", 32)
            fonte_tab_hdr = ImageFont.truetype("arialbd.ttf", 20)
            fonte_tab_cel = ImageFont.truetype("arial.ttf", 20)
            fonte_tab_bold = ImageFont.truetype("arialbd.ttf", 20)
        except OSError:
            fonte_titulo = ImageFont.load_default()
            fonte_sub = ImageFont.load_default()
            fonte_kpi_tit = ImageFont.load_default()
            fonte_kpi_val = ImageFont.load_default()
            fonte_tab_hdr = ImageFont.load_default()
            fonte_tab_cel = ImageFont.load_default()
            fonte_tab_bold = ImageFont.load_default()

        canvas = Image.new("RGB", (largura, altura_total),
                           color=(248, 249, 250))
        draw = ImageDraw.Draw(canvas)

        # 1. Cabeçalho
        y = margem
        draw.rectangle(
            [(margem, y), (largura - margem, y + altura_cabecalho)],
            fill=(255, 230, 0),
        )
        draw.rectangle(
            [(margem, y + altura_cabecalho - 8),
             (largura - margem, y + altura_cabecalho)],
            fill=(30, 58, 138),
        )
        draw.text(
            (margem + 30, y + 24),
            "REPORT DE EXPEDIÇÃO DIÁRIO — OOT (SMG1)",
            fill=(15, 23, 42),
            font=fonte_titulo,
        )
        draw.text(
            (margem + 30, y + 74),
            f"Emitido em: {date.today().strftime('%d/%m/%Y')}  |  Meta OOT: 90,0%",
            fill=(51, 65, 85),
            font=fonte_sub,
        )

        # 2. Cards de resumo
        y += altura_cabecalho + 25
        cards = [
            ("TOTAL DE PACOTES", f"{total_pacotes:,}".replace(",", ".")),
            ("TOTAL DE ROTAS", f"{total_rotas} ROTAS"),
            ("MÉDIA GERAL OOT", f"{media_oot:.1f}%"),
        ]
        espaco_card = 25
        larg_card = (larg_util - 2 * espaco_card) // 3
        for i, (tit, val) in enumerate(cards):
            x0 = margem + i * (larg_card + espaco_card)
            x1 = x0 + larg_card
            draw.rounded_rectangle(
                [(x0, y), (x1, y + altura_resumo)],
                radius=12,
                fill=(255, 255, 255),
                outline=(203, 213, 225),
                width=2,
            )
            draw.text((x0 + 24, y + 20), tit,
                      fill=(100, 116, 139), font=fonte_kpi_tit)
            draw.text((x0 + 24, y + 58), val,
                      fill=(15, 23, 42), font=fonte_kpi_val)

        # 3. Tabela resumo por ciclo
        y += altura_resumo + 25
        draw.rounded_rectangle(
            [(margem, y), (largura - margem, y + altura_tabela)],
            radius=12,
            fill=(255, 255, 255),
            outline=(203, 213, 225),
            width=2,
        )
        draw.text(
            (margem + 24, y + 14),
            "RESUMO POR CICLO",
            fill=(15, 23, 42),
            font=fonte_tab_hdr,
        )

        y_tab = y + 48
        col_widths = [
            int(larg_util * 0.28),
            int(larg_util * 0.24),
            int(larg_util * 0.22),
            int(larg_util * 0.26),
        ]
        headers = ["Ciclo", "Pacotes", "Rotas", "Média OOT (Meta 90%)"]

        # Cabeçalho da tabela
        draw.rectangle(
            [(margem + 16, y_tab), (largura - margem - 16, y_tab + altura_linha_tab)],
            fill=(15, 23, 42),
        )
        x_cel = margem + 28
        for h_txt, w_col in zip(headers, col_widths):
            draw.text((x_cel, y_tab + 11), h_txt,
                      fill=(255, 255, 255), font=fonte_tab_hdr)
            x_cel += w_col

        # Linhas da tabela
        for idx_r, row in df_ciclos_resumo.iterrows():
            y_row = y_tab + (idx_r + 1) * altura_linha_tab
            bg_row = (248, 250, 252) if idx_r % 2 == 1 else (255, 255, 255)
            draw.rectangle(
                [(margem + 16, y_row), (largura -
                                        margem - 16, y_row + altura_linha_tab)],
                fill=bg_row,
            )
            draw.line(
                [(margem + 16, y_row + altura_linha_tab),
                 (largura - margem - 16, y_row + altura_linha_tab)],
                fill=(226, 232, 240),
                width=1,
            )

            pct_fmt = f"{int(row['Pacotes']):,}".replace(",", ".")
            rot_fmt = f"{int(row['Rotas'])}"
            oot_val = row["Média OOT"]

            if pd.notna(oot_val):
                oot_fmt = f"{oot_val:.1f}%"
                cor_oot = (22, 163, 74) if oot_val >= 90.0 else (220, 38, 38)
            else:
                oot_fmt = "—"
                cor_oot = (100, 116, 139)

            x_cel = margem + 28
            valores_linha = [
                (str(row["Ciclo"]), fonte_tab_bold, (15, 23, 42)),
                (pct_fmt, fonte_tab_cel, (30, 41, 59)),
                (rot_fmt, fonte_tab_cel, (30, 41, 59)),
                (oot_fmt, fonte_tab_bold, cor_oot),
            ]
            for val_txt, fnt, clr in valores_linha:
                draw.text((x_cel, y_row + 11), val_txt, fill=clr, font=fnt)
                x_cel += col_widths[valores_linha.index((val_txt, fnt, clr))]

        # 4. Gráfico 1 (OOT)
        y += altura_tabela + 30
        if fig_oot is not None:
            bytes_oot = fig_oot.to_image(
                format="png",
                width=larg_util,
                height=altura_graf_oot,
                scale=2,
            )
            img_oot = Image.open(io.BytesIO(bytes_oot)).convert("RGB")
            img_oot = img_oot.resize(
                (larg_util, altura_graf_oot), Image.Resampling.LANCZOS)
            canvas.paste(img_oot, (margem, y))
            y += altura_graf_oot + 30

        # 5. Gráfico 2 (Ciclos / Rotas / Pacotes)
        bytes_rotas = fig_rotas.to_image(
            format="png",
            width=larg_util,
            height=altura_graf_rotas,
            scale=2,
        )
        img_rotas = Image.open(io.BytesIO(bytes_rotas)).convert("RGB")
        img_rotas = img_rotas.resize(
            (larg_util, altura_graf_rotas), Image.Resampling.LANCZOS)
        canvas.paste(img_rotas, (margem, y))

        buffer = io.BytesIO()
        canvas.save(buffer, format="JPEG", quality=98, subsampling=0)
        return buffer.getvalue()

    if "oot_dados" not in st.session_state:
        st.session_state.oot_dados = {
            "CICLO CPM": {
                "Pacotes": 10898,
                "Rotas": 52,
                "Ondas": {"1ª onda": 96.2, "2ª onda": 96.2},
            },
            "CICLO AM": {
                "Pacotes": 17584,
                "Rotas": 100,
                "Ondas": {
                    "1ª onda": 92.3,
                    "2ª onda": 92.3,
                    "3ª onda": 92.3,
                    "4ª onda": 92.3,
                    "5ª onda": 84.6,
                    "6ª onda": 71.4,
                },
            },
            "CICLO PM": {
                "Pacotes": 13523,
                "Rotas": 146,
                "Ondas": {
                    "1ª onda": 97.2,
                    "2ª onda": 68.4,
                    "3ª onda": 91.7,
                    "4ª onda": 100.0,
                },
            },
            "CICLO SD": {
                "Pacotes": 1346,
                "Rotas": 33,
                "Ondas": {"1ª onda": 97.0},
            },
            "CICLO EXTRA": {
                "Pacotes": 0,
                "Rotas": 0,
                "Ondas": {},
            },
            "CICLO SDE": {
                "Pacotes": 243,
                "Rotas": 13,
                "Ondas": {"1ª onda": 92.3},
            },
        }

    with st.expander("📝 Preencher / Alterar Dados por Ciclo e Onda", expanded=True):
        for ciclo, info in st.session_state.oot_dados.items():
            st.markdown(f"### {ciclo}")
            c_pac, c_rot = st.columns(2)

            with c_pac:
                info["Pacotes"] = st.number_input(
                    "Pacotes",
                    min_value=0,
                    value=int(info["Pacotes"]),
                    step=1,
                    key=f"pac_{ciclo}",
                )
            with c_rot:
                info["Rotas"] = st.number_input(
                    "Rotas",
                    min_value=0,
                    value=int(info["Rotas"]),
                    step=1,
                    key=f"rot_{ciclo}",
                )

            st.markdown("**Performance OOT:**")
            ondas_dict = info["Ondas"]
            if ondas_dict:
                cols_ondas = st.columns(min(4, len(ondas_dict)))
                for idx_onda, (nome_onda, valor_oot) in enumerate(ondas_dict.items()):
                    with cols_ondas[idx_onda % len(cols_ondas)]:
                        ondas_dict[nome_onda] = st.number_input(
                            f"{nome_onda}:",
                            min_value=0.0,
                            max_value=100.0,
                            value=float(valor_oot),
                            step=0.1,
                            format="%.1f",
                            key=f"oot_{ciclo}_{nome_onda}",
                        )
            else:
                st.caption("Nenhuma onda configurada neste ciclo.")

            c_add, c_rem = st.columns(2)
            with c_add:
                if st.button(f"➕ Adicionar onda em {ciclo}", key=f"add_{ciclo}"):
                    prox_num = len(ondas_dict) + 1
                    novo_nome = f"{prox_num}ª onda"
                    while novo_nome in ondas_dict:
                        prox_num += 1
                        novo_nome = f"{prox_num}ª onda"
                    ondas_dict[novo_nome] = 90.0
                    st.rerun()

            with c_rem:
                if ondas_dict and st.button(
                    f"➖ Remover última onda de {ciclo}", key=f"rem_{ciclo}"
                ):
                    ultima_chave = list(ondas_dict.keys())[-1]
                    del ondas_dict[ultima_chave]
                    st.rerun()

            st.divider()

    linhas_ciclos = []
    linhas_ondas = []

    for ciclo, info in st.session_state.oot_dados.items():
        linhas_ciclos.append({
            "Ciclo": ciclo,
            "Pacotes": info["Pacotes"],
            "Rotas": info["Rotas"],
        })
        for nome_onda, valor_oot in info["Ondas"].items():
            linhas_ondas.append({
                "Ciclo": ciclo,
                "Onda": nome_onda.upper(),
                "OOT (%)": valor_oot,
            })

    df_ciclos = pd.DataFrame(linhas_ciclos)
    df_ondas = pd.DataFrame(linhas_ondas)

    medias_por_ciclo = (
        df_ondas.groupby("Ciclo")["OOT (%)"].mean().to_dict()
        if not df_ondas.empty
        else {}
    )
    df_ciclos["Média OOT"] = df_ciclos["Ciclo"].map(medias_por_ciclo)

    total_pacotes = int(df_ciclos["Pacotes"].sum())
    total_rotas = int(df_ciclos["Rotas"].sum())
    media_oot = float(df_ondas["OOT (%)"].mean()
                      ) if not df_ondas.empty else 0.0

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric(
        "📦 Total de Pacotes (Todos os Ciclos)",
        f"{total_pacotes:,}".replace(",", "."),
    )
    col_m2.metric("🚚 Total de Rotas (Todos os Ciclos)", f"{total_rotas} ROTAS")
    col_m3.metric(
        "🎯 Média Geral OOT",
        f"{media_oot:.1f}%",
        delta=f"{media_oot - 90:.1f}% vs Meta",
    )

    st.divider()

    # --- Gráfico 1: Performance OOT (%) por Onda ---
    st.subheader("1. Performance OOT (%) por Ciclo/Onda vs. Meta (90%)")

    fig_oot = None
    if not df_ondas.empty:
        df_ondas["Ciclo_Onda"] = (
            df_ondas["Ciclo"].str.replace("CICLO ", "", regex=False)
            + " - "
            + df_ondas["Onda"]
        )

        ciclos_destaque = {"CICLO CPM", "CICLO PM", "CICLO SDE"}
        labels_eixo_x = [
            f"<span style='color:#FFE200; font-weight:bold;'>{texto}</span>"
            if ciclo in ciclos_destaque
            else texto
            for ciclo, texto in zip(df_ondas["Ciclo"], df_ondas["Ciclo_Onda"])
        ]

        cores_barras = [
            "#16a34a" if val >= 90.0 else "#dc2626" for val in df_ondas["OOT (%)"]
        ]

        fig_oot = go.Figure()

        fig_oot.add_trace(
            go.Bar(
                x=df_ondas["Ciclo_Onda"],
                y=df_ondas["OOT (%)"],
                marker_color=cores_barras,
                text=[f"{val:.1f}%" for val in df_ondas["OOT (%)"]],
                textposition="outside",
                textfont=dict(size=16, color="white"),
                name="Performance OOT (%)",
            )
        )

        fig_oot.add_trace(
            go.Scatter(
                x=df_ondas["Ciclo_Onda"],
                y=[90.0] * len(df_ondas),
                mode="lines",
                line=dict(color="#38bdf8", width=3, dash="dash"),
                name="Meta OOT (90%)",
            )
        )

        fig_oot.update_layout(
            paper_bgcolor="black",
            plot_bgcolor="black",
            font=dict(color="white", size=14),
            yaxis=dict(title="Performance (%)", range=[
                       0, 118], gridcolor="#1e293b"),
            xaxis=dict(
                title="Ciclo / Onda",
                tickmode="array",
                tickvals=df_ondas["Ciclo_Onda"],
                ticktext=labels_eixo_x,
                tickangle=-25,
                tickfont=dict(size=13),
            ),
            barmode="group",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=14),
            ),
            margin=dict(b=110, t=70, l=70, r=40),
            height=480,
        )

        st.plotly_chart(fig_oot, use_container_width=True)
    else:
        st.info("Adicione pelo menos uma onda para exibir o gráfico de OOT.")

    st.divider()

    # --- Gráfico 2: Quantidade de Rotas e Pacotes por Ciclo ---
    st.subheader("2. Quantidade de Rotas e Pacotes por Ciclo")

    limite_y_rotas = max(10, float(df_ciclos["Rotas"].max()) * 1.28)

    textos_ciclos = [
        f"{int(p):,}".replace(",", ".") + f" pct | {int(r)} rotas"
        for p, r in zip(df_ciclos["Pacotes"], df_ciclos["Rotas"])
    ]

    anotacoes_meta_ciclo = []
    status_meta_texto = []

    for ciclo, rotas in zip(df_ciclos["Ciclo"], df_ciclos["Rotas"]):
        if ciclo in medias_por_ciclo:
            media_c = medias_por_ciclo[ciclo]
            bateu_meta = media_c >= 90.0
            rotulo_meta = f"{media_c:.1f}%"
            cor_meta = "#16a34a" if bateu_meta else "#dc2626"
        else:
            rotulo_meta = "—"
            cor_meta = "#cbd5e1"

        status_meta_texto.append(rotulo_meta)

        if rotas > 0:
            anotacoes_meta_ciclo.append(
                dict(
                    x=ciclo,
                    y=rotas / 2,
                    text=f"<b>{rotulo_meta}</b>",
                    showarrow=False,
                    font=dict(color=cor_meta, size=15),
                    bgcolor="rgba(15, 23, 42, 0.85)",
                    borderpad=4,
                    xref="x",
                    yref="y",
                )
            )

    fig_rotas = go.Figure(
        data=[
            go.Bar(
                x=df_ciclos["Ciclo"],
                y=df_ciclos["Rotas"],
                customdata=list(zip(df_ciclos["Pacotes"], status_meta_texto)),
                marker_color="#298466",
                text=textos_ciclos,
                textposition="outside",
                textfont=dict(size=16, color="white"),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Rotas: %{y}<br>"
                    "Pacotes: %{customdata[0]:,}<br>"
                    "Média OOT: %{customdata[1]}<extra></extra>"
                ),
                name="Rotas",
            )
        ]
    )

    fig_rotas.update_layout(
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(color="white", size=16),
        yaxis=dict(
            title="Quantidade de Rotas",
            range=[0, limite_y_rotas],
            gridcolor="#1e293b",
        ),
        xaxis=dict(title="Ciclo", tickfont=dict(size=14)),
        annotations=anotacoes_meta_ciclo,
        margin=dict(b=70, t=50, l=70, r=40),
        height=440,
    )

    st.plotly_chart(fig_rotas, use_container_width=True)

    st.divider()

    # --- Botão único para baixar tudo em JPG ---
    try:
        jpg_completo = gerar_reporte_oot_jpg(
            total_pacotes=total_pacotes,
            total_rotas=total_rotas,
            media_oot=media_oot,
            df_ciclos_resumo=df_ciclos,
            fig_oot=fig_oot,
            fig_rotas=fig_rotas,
        )
        st.download_button(
            label="📥 Baixar Reporte Completo OOT (JPG)",
            data=jpg_completo,
            file_name=f"reporte_completo_oot_{date.today().strftime('%d_%m_%Y')}.jpg",
            mime="image/jpeg",
            use_container_width=True,
        )
    except Exception:
        st.caption(
            "Para exportar o JPG completo, instale o pacote `kaleido` (`pip install kaleido`)."
        )
