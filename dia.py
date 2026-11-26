from datetime import date
import io
import os

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

    def _carregar_fontes_reporte():
        candidatos_bold = [
            "arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ]
        candidatos_regular = [
            "arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]

        fonte_b = next((p for p in candidatos_bold if os.path.exists(p)), None)
        fonte_r = next(
            (p for p in candidatos_regular if os.path.exists(p)), None
        )

        if fonte_b and fonte_r:
            return (
                ImageFont.truetype(fonte_b, 34),
                ImageFont.truetype(fonte_r, 21),
                ImageFont.truetype(fonte_b, 24),
                ImageFont.truetype(fonte_r, 23),
            )
        padrao = ImageFont.load_default()
        return (padrao, padrao, padrao, padrao)

    def _quebrar_texto_por_largura(draw, texto, fonte, largura_max):
        """Quebra o texto considerando parágrafos e largura real em pixels."""
        linhas_finais = []
        for paragrafo in texto.splitlines() or [""]:
            palavras = paragrafo.split()
            if not palavras:
                linhas_finais.append("")
                continue

            linha_atual = palavras[0]
            for palavra in palavras[1:]:
                teste = f"{linha_atual} {palavra}"
                bbox = draw.textbbox((0, 0), teste, font=fonte)
                if (bbox[2] - bbox[0]) <= largura_max:
                    linha_atual = teste
                else:
                    linhas_finais.append(linha_atual)
                    linha_atual = palavra
            linhas_finais.append(linha_atual)

        return linhas_finais or ["Sem observações."]

    def gerar_imagem_relatorio(reportes, formato="PNG"):
        """Gera imagem em PNG ou JPG de alta nitidez, ajustando a altura ao conteúdo."""
        largura = 1400
        altura_minima = 1754 if formato.upper() == "PNG" else 600
        altura_cabecalho = 150
        margem = 45
        larg_card = largura - 2 * margem

        fonte_titulo, fonte_subtitulo, fonte_negrito, fonte_texto = (
            _carregar_fontes_reporte()
        )

        img_med = Image.new("RGB", (largura, 200), color=(255, 255, 255))
        draw_med = ImageDraw.Draw(img_med)

        tam_foto_base = 260
        larg_area_texto = larg_card - (20 + tam_foto_base + 35 + 25)
        altura_linha = 32

        cartoes_preparados = []
        altura_conteudo = altura_cabecalho + margem

        for item in reportes:
            linhas_texto = _quebrar_texto_por_largura(
                draw_med,
                item["Passagem de Turno"],
                fonte_texto,
                larg_area_texto,
            )

            altura_foto_real = tam_foto_base
            foto_redimensionada = None
            if item["Imagem"] is not None:
                try:
                    foto_orig = Image.open(
                        io.BytesIO(item["Imagem"])
                    ).convert("RGB")
                    escala_w = tam_foto_base / max(1, foto_orig.width)
                    novo_w = max(1, int(foto_orig.width * escala_w))
                    novo_h = max(1, int(foto_orig.height * escala_w))
                    if novo_h > 420:
                        escala_h = 420 / novo_h
                        novo_w = max(1, int(novo_w * escala_h))
                        novo_h = max(1, int(novo_h * escala_h))
                    foto_redimensionada = foto_orig.resize(
                        (novo_w, novo_h), Image.Resampling.LANCZOS
                    )
                    altura_foto_real = max(200, novo_h)
                except Exception:
                    foto_redimensionada = None

            altura_bloco_texto = 85 + len(linhas_texto) * altura_linha
            altura_card = max(
                250, altura_foto_real + 40, altura_bloco_texto + 30
            )

            cartoes_preparados.append((
                item,
                linhas_texto,
                foto_redimensionada,
                altura_foto_real,
                altura_card,
            ))
            altura_conteudo += altura_card + 25

        altura_total = max(altura_minima, altura_conteudo + margem)

        img = Image.new("RGB", (largura, altura_total), color=(248, 249, 250))
        draw = ImageDraw.Draw(img)

        draw.rectangle([(0, 0), (largura, 125)], fill=(255, 230, 0))
        draw.rectangle([(0, 120), (largura, 125)], fill=(30, 58, 138))

        x_titulo = margem
        if os.path.exists(caminho_logo):
            try:
                logo = Image.open(caminho_logo).convert("RGB")
                logo.thumbnail((180, 96), Image.Resampling.LANCZOS)
                y_logo = (120 - logo.height) // 2
                img.paste(logo, (margem, y_logo))
                x_titulo = margem + logo.width + 30
            except Exception:
                pass

        draw.text(
            (x_titulo, 26),
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

        for idx, (
            item,
            linhas_texto,
            foto_redimensionada,
            altura_foto_real,
            altura_card,
        ) in enumerate(cartoes_preparados, start=1):
            draw.rounded_rectangle(
                [(margem, y_atual), (largura - margem, y_atual + altura_card)],
                radius=12,
                fill=(255, 255, 255),
                outline=(203, 213, 225),
                width=2,
            )

            x_foto = margem + 20
            y_foto = y_atual + 20

            if foto_redimensionada is not None:
                offset_x = (
                    x_foto + (tam_foto_base - foto_redimensionada.width) // 2
                )
                offset_y = (
                    y_foto + (altura_foto_real - foto_redimensionada.height) // 2
                )
                img.paste(foto_redimensionada, (offset_x, offset_y))
            else:
                draw.rectangle(
                    [
                        (x_foto, y_foto),
                        (x_foto + tam_foto_base, y_foto + 220),
                    ],
                    fill=(241, 245, 249),
                    outline=(203, 213, 225),
                    width=2,
                )
                draw.text(
                    (x_foto + 85, y_foto + 98),
                    "Sem foto",
                    fill=(100, 116, 139),
                    font=fonte_texto,
                )

            x_texto = x_foto + tam_foto_base + 35
            draw.text(
                (x_texto, y_atual + 22),
                f"#{idx} | Data: {item['Data']} - {item['Turno']} ({item['Tipo de Reporte']})",
                fill=(30, 58, 138),
                font=fonte_negrito,
            )

            draw.line(
                [(x_texto, y_atual + 60), (largura - margem - 25, y_atual + 60)],
                fill=(226, 232, 240),
                width=2,
            )

            y_linha = y_atual + 76
            for linha in linhas_texto:
                draw.text(
                    (x_texto, y_linha),
                    linha,
                    fill=(30, 41, 59),
                    font=fonte_texto,
                )
                y_linha += altura_linha

            y_atual += altura_card + 25

        buffer = io.BytesIO()
        if formato.upper() == "JPG" or formato.upper() == "JPEG":
            img.save(buffer, format="JPEG", quality=98, subsampling=0)
        else:
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
                [
                    "Comunicação de Acidentes",
                    "Passagem de Turno",
                    "OOT",
                    "Outros",
                ],
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
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            imagem_relatorio_jpg = gerar_imagem_relatorio(
                st.session_state.reportes, formato="JPG"
            )
            st.download_button(
                label="📥 Baixar Reporte em JPG (Alta Nitidez)",
                data=imagem_relatorio_jpg,
                file_name=f"reporte_smg1_{date.today().strftime('%d_%m_%Y')}.jpg",
                mime="image/jpeg",
                use_container_width=True,
            )
        with col_dl2:
            imagem_relatorio_png = gerar_imagem_relatorio(
                st.session_state.reportes, formato="PNG"
            )
            st.download_button(
                label="📥 Baixar Reporte em PNG A4",
                data=imagem_relatorio_png,
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

    def _carregar_fontes_oot():
        """Carrega fontes TrueType ampliadas para facilitar leitura em telas grandes."""
        candidatos_bold = [
            "arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ]
        candidatos_regular = [
            "arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]

        caminho_b = next(
            (p for p in candidatos_bold if os.path.exists(p)), None
        )
        caminho_r = next(
            (p for p in candidatos_regular if os.path.exists(p)), None
        )

        if caminho_b and caminho_r:
            return {
                "titulo": ImageFont.truetype(caminho_b, 42),
                "sub": ImageFont.truetype(caminho_r, 25),
                "kpi_tit": ImageFont.truetype(caminho_b, 22),
                "kpi_val": ImageFont.truetype(caminho_b, 38),
                "graf_tit": ImageFont.truetype(caminho_b, 30),
                "tab_hdr": ImageFont.truetype(caminho_b, 23),
                "tab_cel": ImageFont.truetype(caminho_r, 23),
                "tab_bold": ImageFont.truetype(caminho_b, 23),
                "bar_lbl": ImageFont.truetype(caminho_b, 24),
                "axis_lbl": ImageFont.truetype(caminho_b, 21),
                "y_lbl": ImageFont.truetype(caminho_r, 20),
            }

        padrao = ImageFont.load_default()
        return {
            "titulo": padrao,
            "sub": padrao,
            "kpi_tit": padrao,
            "kpi_val": padrao,
            "graf_tit": padrao,
            "tab_hdr": padrao,
            "tab_cel": padrao,
            "tab_bold": padrao,
            "bar_lbl": padrao,
            "axis_lbl": padrao,
            "y_lbl": padrao,
        }

    def _texto_centralizado(
        draw, cx, y, texto, fonte, fill, bg_color=None, pad_x=7, pad_y=4
    ):
        """Desenha texto centralizado em cx com largura real medida via textbbox."""
        bbox = draw.textbbox((0, 0), texto, font=fonte)
        larg_txt = bbox[2] - bbox[0]
        alt_txt = bbox[3] - bbox[1]
        x = int(cx - larg_txt / 2)

        if bg_color is not None:
            draw.rounded_rectangle(
                [
                    (x - pad_x, y - pad_y),
                    (x + larg_txt + pad_x, y + alt_txt + pad_y),
                ],
                radius=6,
                fill=bg_color,
            )

        draw.text((x, y), texto, fill=fill, font=fonte)
        return larg_txt, alt_txt

    def _desenhar_grafico_oot_pil(df_ondas_plot, largura, altura, fontes):
        """Desenha gráfico 1 (OOT por Ciclo/Onda vs. Meta 90%) com fontes ampliadas."""
        img = Image.new("RGB", (largura, altura), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        draw.text(
            (36, 22),
            "1. PERFORMANCE OOT (%) POR CICLO/ONDA VS. META (90%)",
            fill=(255, 255, 255),
            font=fontes["graf_tit"],
        )

        # Legenda superior direita com fonte ampliada
        y_leg = 28
        draw.rectangle(
            [(largura - 440, y_leg + 4), (largura - 412, y_leg + 24)],
            fill=(22, 163, 74),
        )
        draw.text(
            (largura - 402, y_leg),
            "≥ 90%",
            fill=(255, 255, 255),
            font=fontes["axis_lbl"],
        )
        draw.rectangle(
            [(largura - 315, y_leg + 4), (largura - 287, y_leg + 24)],
            fill=(220, 38, 38),
        )
        draw.text(
            (largura - 277, y_leg),
            "< 90%",
            fill=(255, 255, 255),
            font=fontes["axis_lbl"],
        )
        draw.line(
            [(largura - 185, y_leg + 14), (largura - 150, y_leg + 14)],
            fill=(56, 189, 248),
            width=4,
        )
        draw.text(
            (largura - 140, y_leg),
            "Meta 90%",
            fill=(56, 189, 248),
            font=fontes["axis_lbl"],
        )

        x_esq, x_dir = 110, largura - 45
        y_topo, y_base = 102, altura - 130
        alt_area = y_base - y_topo
        larg_area = x_dir - x_esq
        teto_y = 122.0

        for tick_val in [0, 25, 50, 75, 100]:
            ty = y_base - int((tick_val / teto_y) * alt_area)
            draw.line(
                [(x_esq, ty), (x_dir, ty)], fill=(30, 41, 59), width=1
            )
            draw.text(
                (28, ty - 12),
                f"{tick_val}%",
                fill=(148, 163, 184),
                font=fontes["y_lbl"],
            )

        draw.line(
            [(x_esq, y_topo), (x_esq, y_base)], fill=(100, 116, 139), width=2
        )
        draw.line(
            [(x_esq, y_base), (x_dir, y_base)], fill=(100, 116, 139), width=2
        )

        y_meta = y_base - int((90.0 / teto_y) * alt_area)
        for sx in range(x_esq, x_dir - 12, 24):
            draw.line(
                [(sx, y_meta), (sx + 12, y_meta)],
                fill=(56, 189, 248),
                width=4,
            )

        n = len(df_ondas_plot)
        if n == 0:
            return img

        passo = larg_area / n
        larg_barra = max(28, min(96, int(passo * 0.56)))
        ciclos_destaque = {"CICLO CPM", "CICLO PM", "CICLO SDE"}

        for i, (_, row) in enumerate(df_ondas_plot.iterrows()):
            val = float(row["OOT (%)"])
            ciclo = str(row["Ciclo"])
            rotulo = str(row["Ciclo_Onda"])

            cx = int(x_esq + (i + 0.5) * passo)
            x0 = cx - larg_barra // 2
            x1 = cx + larg_barra // 2
            h_barra = max(2, int((min(val, teto_y) / teto_y) * alt_area))
            y0 = y_base - h_barra

            cor_barra = (22, 163, 74) if val >= 90.0 else (220, 38, 38)
            draw.rectangle([(x0, y0), (x1, y_base)], fill=cor_barra)

            _texto_centralizado(
                draw,
                cx,
                max(66, y0 - 34),
                f"{val:.1f}%",
                fontes["bar_lbl"],
                (255, 255, 255),
            )

            cor_lbl = (
                (255, 226, 0) if ciclo in ciclos_destaque else (226, 232, 240)
            )
            y_lbl_x = y_base + 14 if (n <= 10 or i % 2 == 0) else y_base + 48
            _texto_centralizado(
                draw,
                cx,
                y_lbl_x,
                rotulo,
                fontes["axis_lbl"],
                cor_lbl,
            )

        return img

    def _desenhar_grafico_rotas_pil(
        df_ciclos_plot, medias_map, largura, altura, fontes
    ):
        """Desenha gráfico 2 (Rotas e Pacotes por Ciclo) com fontes ampliadas."""
        img = Image.new("RGB", (largura, altura), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        draw.text(
            (36, 22),
            "2. QUANTIDADE DE ROTAS E PACOTES POR CICLO",
            fill=(255, 255, 255),
            font=fontes["graf_tit"],
        )

        x_esq, x_dir = 110, largura - 45
        y_topo, y_base = 102, altura - 80
        alt_area = y_base - y_topo
        larg_area = x_dir - x_esq

        max_rotas = max(10.0, float(df_ciclos_plot["Rotas"].max()) * 1.32)

        for idx_g in range(5):
            frac = idx_g / 4.0
            ty = y_base - int(frac * alt_area)
            val_tick = int(round(frac * max_rotas))
            draw.line(
                [(x_esq, ty), (x_dir, ty)], fill=(30, 41, 59), width=1
            )
            draw.text(
                (28, ty - 12),
                f"{val_tick}",
                fill=(148, 163, 184),
                font=fontes["y_lbl"],
            )

        draw.line(
            [(x_esq, y_topo), (x_esq, y_base)], fill=(100, 116, 139), width=2
        )
        draw.line(
            [(x_esq, y_base), (x_dir, y_base)], fill=(100, 116, 139), width=2
        )

        n = len(df_ciclos_plot)
        if n == 0:
            return img

        passo = larg_area / n
        larg_barra = max(68, min(220, int(passo * 0.56)))

        for i, (_, row) in enumerate(df_ciclos_plot.iterrows()):
            ciclo = str(row["Ciclo"])
            pacotes = int(row["Pacotes"])
            rotas = int(row["Rotas"])

            cx = int(x_esq + (i + 0.5) * passo)
            x0 = cx - larg_barra // 2
            x1 = cx + larg_barra // 2
            h_barra = max(2, int((rotas / max_rotas) * alt_area))
            y0 = y_base - h_barra

            draw.rectangle([(x0, y0), (x1, y_base)], fill=(41, 132, 102))

            txt_topo = (
                f"{pacotes:,}".replace(",", ".") + f" pct | {rotas} rotas"
            )
            _texto_centralizado(
                draw,
                cx,
                max(66, y0 - 34),
                txt_topo,
                fontes["bar_lbl"],
                (255, 255, 255),
            )

            if ciclo in medias_map and pd.notna(medias_map[ciclo]) and rotas > 0:
                media_c = float(medias_map[ciclo])
                cor_meta = (
                    (34, 197, 94) if media_c >= 90.0 else (248, 113, 113)
                )
                y_mid = max(y0 + 10, min(y_base - 38, (y0 + y_base) // 2 - 14))
                _texto_centralizado(
                    draw,
                    cx,
                    y_mid,
                    f"{media_c:.1f}%",
                    fontes["bar_lbl"],
                    cor_meta,
                    bg_color=(15, 23, 42),
                    pad_x=9,
                    pad_y=5,
                )

            _texto_centralizado(
                draw,
                cx,
                y_base + 18,
                ciclo,
                fontes["axis_lbl"],
                (226, 232, 240),
            )

        return img

    def gerar_reporte_oot_jpg(
        total_pacotes,
        total_rotas,
        media_oot,
        df_ciclos_resumo,
        df_ondas_resumo,
        medias_map,
        fig_oot,
        fig_rotas,
    ):
        """Gera uma imagem JPG nítida com fontes ampliadas para telas grandes."""
        largura = 2000
        margem = 50
        larg_util = largura - 2 * margem
        altura_cabecalho = 145
        altura_resumo = 140

        qtd_ciclos = max(1, len(df_ciclos_resumo))
        altura_linha_tab = 50
        altura_tabela = 64 + (qtd_ciclos + 1) * altura_linha_tab

        altura_graf_oot = 740 if not df_ondas_resumo.empty else 0
        altura_graf_rotas = 650

        altura_total = (
            margem
            + altura_cabecalho
            + 25
            + altura_resumo
            + 25
            + altura_tabela
            + (30 + altura_graf_oot if not df_ondas_resumo.empty else 0)
            + 30
            + altura_graf_rotas
            + margem
        )

        fontes = _carregar_fontes_oot()
        canvas = Image.new(
            "RGB", (largura, altura_total), color=(248, 249, 250)
        )
        draw = ImageDraw.Draw(canvas)

        # 1. Cabeçalho
        y = margem
        draw.rectangle(
            [(margem, y), (largura - margem, y + altura_cabecalho)],
            fill=(255, 230, 0),
        )
        draw.rectangle(
            [
                (margem, y + altura_cabecalho - 8),
                (largura - margem, y + altura_cabecalho),
            ],
            fill=(30, 58, 138),
        )
        draw.text(
            (margem + 30, y + 24),
            "REPORT DE EXPEDIÇÃO DIÁRIO — OOT (SMG1)",
            fill=(15, 23, 42),
            font=fontes["titulo"],
        )
        draw.text(
            (margem + 30, y + 80),
            f"Emitido em: {date.today().strftime('%d/%m/%Y')}  |  Meta OOT: 90,0%",
            fill=(51, 65, 85),
            font=fontes["sub"],
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
            draw.text(
                (x0 + 24, y + 20),
                tit,
                fill=(100, 116, 139),
                font=fontes["kpi_tit"],
            )
            draw.text(
                (x0 + 24, y + 60),
                val,
                fill=(15, 23, 42),
                font=fontes["kpi_val"],
            )

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
            font=fontes["tab_hdr"],
        )

        y_tab = y + 52
        col_widths = [
            int(larg_util * 0.28),
            int(larg_util * 0.24),
            int(larg_util * 0.22),
            int(larg_util * 0.26),
        ]
        headers = ["Ciclo", "Pacotes", "Rotas", "Média OOT (Meta 90%)"]

        draw.rectangle(
            [
                (margem + 16, y_tab),
                (largura - margem - 16, y_tab + altura_linha_tab),
            ],
            fill=(15, 23, 42),
        )
        x_cel = margem + 28
        for h_txt, w_col in zip(headers, col_widths):
            draw.text(
                (x_cel, y_tab + 13),
                h_txt,
                fill=(255, 255, 255),
                font=fontes["tab_hdr"],
            )
            x_cel += w_col

        for idx_r, (_, row) in enumerate(df_ciclos_resumo.iterrows()):
            y_row = y_tab + (idx_r + 1) * altura_linha_tab
            bg_row = (248, 250, 252) if idx_r % 2 == 1 else (255, 255, 255)
            draw.rectangle(
                [
                    (margem + 16, y_row),
                    (largura - margem - 16, y_row + altura_linha_tab),
                ],
                fill=bg_row,
            )
            draw.line(
                [
                    (margem + 16, y_row + altura_linha_tab),
                    (largura - margem - 16, y_row + altura_linha_tab),
                ],
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
                (str(row["Ciclo"]), fontes["tab_bold"], (15, 23, 42)),
                (pct_fmt, fontes["tab_cel"], (30, 41, 59)),
                (rot_fmt, fontes["tab_cel"], (30, 41, 59)),
                (oot_fmt, fontes["tab_bold"], cor_oot),
            ]
            for idx_col, (val_txt, fnt, clr) in enumerate(valores_linha):
                draw.text((x_cel, y_row + 13), val_txt, fill=clr, font=fnt)
                x_cel += col_widths[idx_col]

        # 4. Gráfico 1 (OOT)
        y += altura_tabela + 30
        if not df_ondas_resumo.empty and fig_oot is not None:
            img_oot = _desenhar_grafico_oot_pil(
                df_ondas_resumo, larg_util, altura_graf_oot, fontes
            )
            canvas.paste(img_oot, (margem, y))
            y += altura_graf_oot + 30

        # 5. Gráfico 2 (Ciclos / Rotas / Pacotes)
        img_rotas = _desenhar_grafico_rotas_pil(
            df_ciclos_resumo, medias_map, larg_util, altura_graf_rotas, fontes
        )
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
    media_oot = float(df_ondas["OOT (%)"].mean()) if not df_ondas.empty else 0.0

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
            yaxis=dict(title="Performance (%)", range=[0, 118], gridcolor="#1e293b"),
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
        df_ondas["Ciclo_Onda"] = []
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
    jpg_completo = gerar_reporte_oot_jpg(
        total_pacotes=total_pacotes,
        total_rotas=total_rotas,
        media_oot=media_oot,
        df_ciclos_resumo=df_ciclos,
        df_ondas_resumo=df_ondas,
        medias_map=medias_por_ciclo,
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
