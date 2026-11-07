#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gerador da Bíblia visual de engenharia de software.

Este arquivo é o único documento das funções que montam o PDF ilustrado.
Cada função pública abaixo descreve o que faz, os argumentos e o retorno.
O resultado final é o HTML autocontido impresso em A4.
"""

from __future__ import annotations

import html
from pathlib import Path


def escapar(texto: str) -> str:
    """Converte caracteres especiais de HTML para entidades seguras.

    Argumentos:
        texto: texto puro que pode conter ``<``, ``>`` e ``&``,
            inclusive código-fonte e comandos de terminal.

    Retorno:
        A mesma sequência com os caracteres reservados do HTML
        substituídos, pronta para entrar em um nó de texto ou em um
        bloco ``<pre>`` sem que o navegador interprete o código como markup.
    """
    return html.escape(texto, quote=True)


def codigo(texto: str, arquivo: str) -> str:
    """Monta um bloco de código com barra de arquivo, no estilo do manual visual.

    Argumentos:
        texto: código ou comando exatamente como deve aparecer para o leitor.
            Quebras de linha são preservadas. O texto é escapado.
        arquivo: rótulo da barra superior, por exemplo ``Limite.java`` ou
            ``EXPLAIN ANALYZE``. Não é um caminho aberto em disco.

    Retorno:
        HTML do bloco: barra escura com o nome do arquivo e um ``<pre>``
        com o código escapado. Não devolve o PDF; só o fragmento da página.
    """
    return (
        '<div class="snippet"><div class="snippet-bar">'
        f'<span class="dots"><i></i><i></i><i></i></span>{escapar(arquivo)}</div>'
        f"<pre>{escapar(texto).rstrip()}</pre></div>"
    )


def aprender(itens: list[str]) -> str:
    """Monta o quadro «O que você vai aprender» do canto superior.

    Argumentos:
        itens: frases curtas, uma por competência da página. A lista vazia
            produz um quadro sem linhas, o que não deve ocorrer nas páginas
            finais.

    Retorno:
        HTML do quadro com uma marca de confirmação por item. O texto de
        cada item é escapado.
    """
    linhas = "".join(f"<li><span class='tick'></span><span>{escapar(i)}</span></li>" for i in itens)
    return (
        "<aside class='learn'><h2>O QUE VOCÊ VAI APRENDER</h2>"
        f"<ul>{linhas}</ul></aside>"
    )


def card(numero: str, titulo: str, apoio: str, corpo: str, tom: str = "") -> str:
    """Monta um cartão numerado de uma seção da página.

    Argumentos:
        numero: algarismo ou rótulo curto exibido no círculo, como ``1``.
        titulo: título em caixa alta visual, já na forma que o leitor vê.
        apoio: frase de apoio logo abaixo do título. Pode ser vazia.
        corpo: HTML interno já montado (parágrafos, código, lista). Quem chama
            é responsável por escapar apenas o texto solto; este argumento
            não é escapado de novo, para permitir markup intencional.
        tom: classe extra. ``bad`` pinta o cartão de alerta e ``good`` pinta
            o cartão de caminho recomendado. Vazio mantém o cartão neutro.

    Retorno:
        HTML do ``<article>`` do cartão, pronto para entrar numa grade.
    """
    extra = f" {tom}" if tom else ""
    apoio_html = f"<em>{escapar(apoio)}</em>" if apoio else ""
    return (
        f"<article class='card{extra}'><div class='sh'><span class='num'>{escapar(numero)}</span>"
        f"<div><b>{escapar(titulo)}</b>{apoio_html}</div></div>{corpo}</article>"
    )


def grade(colunas: str, *cartoes: str) -> str:
    """Coloca cartões lado a lado numa linha da página.

    Argumentos:
        colunas: valor CSS de ``grid-template-columns``. Use ``1fr 1fr`` para
            dois cartões iguais ou ``1fr`` para um cartão de largura inteira.
        cartoes: um ou mais HTML de cartão, na ordem da esquerda para a direita.

    Retorno:
        Um ``div`` com a classe ``linha`` contendo os cartões. A altura mínima
        da linha é a do CSS compartilhado, para a página A4 ficar preenchida.
    """
    return f"<div class='linha' style='grid-template-columns:{colunas}'>{''.join(cartoes)}</div>"


def tabela(titulo: str, dica: str, cabecalhos: list[str], linhas: list[list[str]]) -> str:
    """Monta a tabela de soluções rápidas no pé técnico da página.

    Argumentos:
        titulo: nome da tabela, por exemplo ``QUAL ESPERA USAR``.
        dica: frase curta à direita do título. Pode ser vazia.
        cabecalhos: títulos das colunas, na ordem.
        linhas: cada item é uma linha; cada célula é texto puro e será escapada.
            O número de células deve acompanhar o número de cabeçalhos.

    Retorno:
        HTML da tabela com cabeçalho azul. Não calcula larguras de coluna;
        o CSS divide o espaço igualmente, com a primeira coluna um pouco mais estreita
        quando há três colunas.
    """
    ths = "".join(f"<th>{escapar(h)}</th>" for h in cabecalhos)
    corpo = []
    for linha in linhas:
        tds = "".join(f"<td>{escapar(c)}</td>" for c in linha)
        corpo.append(f"<tr>{tds}</tr>")
    return (
        "<div class='sol'><div class='sol-h'><b>"
        + escapar(titulo)
        + "</b><span class='hint'>"
        + escapar(dica)
        + "</span></div><table><thead><tr>"
        + ths
        + "</tr></thead><tbody>"
        + "".join(corpo)
        + "</tbody></table></div>"
    )


def checklist(titulo: str, itens: list[str]) -> str:
    """Monta a faixa verde de verificação no fim da página.

    Argumentos:
        titulo: rótulo da faixa, como ``CHECKLIST ANTES DO PR``.
        itens: até quatro frases. Cada uma vira uma coluna. Mais de quatro
            ainda são emitidas, e o CSS pode apertá-las.

    Retorno:
        HTML da faixa. Texto escapado. Não valida o conteúdo dos itens.
    """
    cols = "".join(
        f"<article><span class='tick'></span><span>{escapar(i)}</span></article>" for i in itens
    )
    return (
        f"<div class='check'><h3><span class='tick'></span> {escapar(titulo)}</h3>"
        f"<div class='check-row'>{cols}</div></div>"
    )


def pagina(
    capitulo: str,
    titulo_html: str,
    subtitulo: str,
    itens_aprender: list[str],
    *blocos: str,
) -> str:
    """Monta uma página A4 completa do manual.

    Argumentos:
        capitulo: selo do topo, por exemplo ``MÓDULO 1 · 03``.
        titulo_html: título já com ``<br>`` onde a quebra é desejada.
            Não é escapado, porque a quebra faz parte do desenho.
            Não inclua texto vindo de fora sem escapar antes.
        subtitulo: uma ou duas frases sob o título. É escapada.
        itens_aprender: lista passada a ``aprender``.
        blocos: HTML do miolo, na ordem. Os três últimos são, sempre,
            a tabela, o checklist e o texto do rodapé (``@@PAGINA@@``
            ou ``12 / 29``). Tudo o que vem antes desses três é o miolo
            (uma ou mais grades de cartões).

    Retorno:
        Uma ``<section class="page">`` pronta para impressão. A união de
        todas as páginas, mais o CSS, forma o documento.
    """
    if len(blocos) < 3:
        raise ValueError("pagina exige miolo, tabela, checklist e rodapé")
    numero = blocos[-1]
    bloco_check = blocos[-2]
    bloco_tabela = blocos[-3]
    miolo = "".join(blocos[:-3])
    return f"""<section class="page">
  <div class="top">
    <div>
      <div class="kicker">{escapar(capitulo)}</div>
      <h1>{titulo_html}</h1>
      <p class="sub">{escapar(subtitulo)}</p>
    </div>
    {aprender(itens_aprender)}
  </div>
  <div class="corpo">{miolo}{bloco_tabela}{bloco_check}</div>
  <div class="foot"><span>Bíblia visual de engenharia, arquitetura e qualidade</span><span>{escapar(numero)}</span></div>
</section>"""


def p(*textos: str) -> str:
    """Agrupa parágrafos de texto puro num bloco ``.body``.

    Argumentos:
        textos: cada argumento vira um ``<p>``. O texto é escapado.

    Retorno:
        HTML do bloco de parágrafos.
    """
    return "<div class='body'>" + "".join(f"<p>{escapar(t)}</p>" for t in textos) + "</div>"


def bullets(itens: list[str]) -> str:
    """Lista simples com marca de confirmação.

    Argumentos:
        itens: frases. Cada uma é escapada.

    Retorno:
        HTML de uma ``ul.clean``.
    """
    lis = "".join(f"<li><span class='tick'></span><span>{escapar(i)}</span></li>" for i in itens)
    return f"<ul class='clean'>{lis}</ul>"


ESTILO = r"""
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { font-family: Inter, "Noto Sans", sans-serif; color: #0f172a; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 210mm; height: 297mm; overflow: hidden; position: relative; background: #f4f7fb; padding: 8mm 7mm 5.5mm; display: flex; flex-direction: column; gap: 2.3mm; break-after: page; page-break-after: always; }
.page:last-child { break-after: auto; page-break-after: auto; }
.page::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3.2mm; background: linear-gradient(90deg, #1d4ed8, #0ea5e9); }
.top { display: grid; grid-template-columns: 1.4fr 0.9fr; gap: 3mm; }
.kicker { display: inline-flex; background: #1d4ed8; color: #fff; font-size: 8px; font-weight: 800; letter-spacing: 0.12em; padding: 3px 8px; border-radius: 999px; margin-bottom: 1.4mm; }
h1 { margin: 0; font-size: 24px; line-height: 0.94; letter-spacing: -0.03em; font-weight: 800; color: #0b3f91; text-transform: uppercase; }
.sub { margin: 1.4mm 0 0; font-size: 10px; line-height: 1.35; color: #334155; }
.learn { background: #fff; border: 1.5px solid #bfdbfe; border-radius: 10px; padding: 2.2mm 2.8mm; }
.learn h2 { margin: 0 0 1.4mm; font-size: 9px; letter-spacing: 0.08em; color: #1d4ed8; }
.learn ul, ul.clean { margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 1.1mm; }
.learn li, ul.clean li { display: flex; gap: 5px; align-items: flex-start; font-size: 9px; line-height: 1.28; }
.tick { width: 12px; height: 12px; border-radius: 50%; background: #059669; display: inline-flex; align-items: center; justify-content: center; flex: none; margin-top: 1px; }
.tick::after { content: ""; width: 5px; height: 3px; border-left: 1.5px solid #fff; border-bottom: 1.5px solid #fff; transform: rotate(-45deg) translate(0.5px, -0.5px); }
.corpo { flex: 1; min-height: 0; display: flex; flex-direction: column; gap: 2.2mm; }
.linha { display: grid; gap: 2.2mm; min-height: 0; }
.card { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 2.2mm 2.6mm; display: flex; flex-direction: column; gap: 1.4mm; }
.card.bad { background: #fff5f5; border-color: #fecdd3; }
.card.good { background: #f0fdf4; border-color: #bbf7d0; }
.sh { display: flex; gap: 2mm; align-items: flex-start; }
.num { width: 18px; height: 18px; border-radius: 50%; background: #1d4ed8; color: #fff; font-size: 10px; font-weight: 800; display: inline-flex; align-items: center; justify-content: center; flex: none; }
.sh b { display: block; font-size: 10px; letter-spacing: 0.02em; color: #0f2744; line-height: 1.15; text-transform: uppercase; }
.sh em { display: block; margin-top: 1px; font-style: normal; font-size: 8px; color: #64748b; line-height: 1.25; }
.body p { margin: 0 0 1.1mm; font-size: 9px; line-height: 1.35; color: #1e293b; }
.body p:last-child { margin: 0; }
.snippet { border-radius: 8px; overflow: hidden; border: 1px solid #1e293b; }
.snippet-bar { background: #111827; color: #cbd5e1; font-size: 8px; display: flex; align-items: center; gap: 6px; padding: 3px 8px; font-family: "JetBrains Mono", ui-monospace, monospace; }
.dots { display: inline-flex; gap: 3px; }
.dots i { width: 6px; height: 6px; border-radius: 50%; display: block; }
.dots i:nth-child(1) { background: #fb7185; } .dots i:nth-child(2) { background: #fbbf24; } .dots i:nth-child(3) { background: #34d399; }
pre { margin: 0; background: #0b1220; color: #e2e8f0; padding: 5px 7px 6px; font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 7.5px; line-height: 1.38; white-space: pre-wrap; }
.sol { border: 1px solid #dbeafe; border-radius: 10px; overflow: hidden; background: #fff; }
.sol-h { display: flex; align-items: center; gap: 2mm; padding: 1.4mm 2.2mm; background: #eff6ff; }
.sol-h b { font-size: 9px; letter-spacing: 0.04em; color: #1e3a8a; }
.sol-h .hint { margin-left: auto; font-size: 8px; color: #64748b; }
table { width: 100%; border-collapse: collapse; font-size: 8px; }
th { text-align: left; background: #1d4ed8; color: #fff; font-weight: 700; padding: 3px 6px; }
td { padding: 3px 6px; border-bottom: 1px solid #e2e8f0; vertical-align: top; line-height: 1.3; background: #fff; }
tr:nth-child(even) td { background: #f8fafc; }
.check { background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 10px; padding: 1.6mm 2.2mm; }
.check h3 { margin: 0 0 1.2mm; font-size: 9px; letter-spacing: 0.06em; color: #065f46; display: flex; align-items: center; gap: 6px; }
.check-row { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 1.5mm; }
.check-row article { display: flex; gap: 4px; align-items: flex-start; font-size: 8px; line-height: 1.25; color: #064e3b; }
.foot { display: flex; justify-content: space-between; font-size: 7.5px; color: #94a3b8; }
.cover-k { font-size: 10px; font-weight: 800; letter-spacing: 0.16em; color: #1d4ed8; }
.mods { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2.2mm; }
.mod { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 2.4mm; border-top: 3.5px solid #1d4ed8; }
.mod b { display: block; font-size: 8px; letter-spacing: 0.08em; color: #1d4ed8; }
.mod h3 { margin: 0.6mm 0; font-size: 12px; color: #0f2744; }
.mod p { margin: 0; font-size: 8.2px; line-height: 1.3; color: #334155; }
"""


def documento(paginas: list[str]) -> str:
    """Junta o CSS e as páginas num HTML autocontido para impressão A4.

    Argumentos:
        paginas: lista ordenada de seções já montadas por ``pagina`` ou pela
            capa. A primeira página é a capa. A ordem é a ordem de leitura.

    Retorno:
        Documento HTML completo, com ``lang="pt-BR"``, sem dependência de
        arquivo externo. O Chrome headless imprime esse texto em PDF.
    """
    miolo = "\n".join(paginas)
    return (
        "<!DOCTYPE html><html lang='pt-BR'><head><meta charset='utf-8'>"
        "<title>Bíblia visual de engenharia de software</title><style>"
        + ESTILO
        + "</style></head><body>"
        + miolo
        + "</body></html>"
    )


def gravar(destino: Path, paginas: list[str]) -> Path:
    """Grava o HTML da bíblia no caminho pedido.

    Argumentos:
        destino: caminho do arquivo ``.html``. A pasta pai precisa existir.
        paginas: páginas na ordem de leitura, no formato devolvido por ``pagina``.

    Retorno:
        O mesmo caminho ``destino``, depois da escrita em UTF-8.
        Não gera o PDF; a impressão fica a cargo do Chrome.
    """
    destino.write_text(documento(paginas), encoding="utf-8")
    return destino


def gerar(destino: Path | None = None) -> Path:
    """Gera o HTML completo da bíblia visual.

    Argumentos:
        destino: arquivo de saída. Quando é ``None``, grava
            ``biblia-engenharia-software.html`` ao lado deste script.

    Retorno:
        Caminho do HTML gravado. A função importa as páginas só na hora
        de executar, para o módulo de layout não depender do conteúdo
        durante a importação.
    """
    from biblia_paginas import construir_paginas

    saida = destino or Path(__file__).with_name("biblia-engenharia-software.html")
    return gravar(saida, construir_paginas())


if __name__ == "__main__":
    print(gerar())
