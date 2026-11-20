"""Translate native widget chrome not exposed by Streamlit's Python API."""

import streamlit as st

# Static, application-owned code. Never interpolate publication or user content.
NATIVE_PORTUGUESE = r"""
<script>
(() => {
  window.communitylabUiTranslation?.disconnect();
  const phrases = {
    'Drag and drop files here': 'Arraste e solte os arquivos aqui',
    'Drag and drop file here': 'Arraste e solte o arquivo aqui',
    'Browse files': 'Selecionar arquivos', 'Browse file': 'Selecionar arquivo',
    'Choose options': 'Selecione as opções', 'Choose an option': 'Selecione uma opção',
    'No results': 'Nenhum resultado', 'No options': 'Nenhuma opção',
    'Search': 'Pesquisar', 'Download as CSV': 'Baixar como CSV',
    'Download': 'Baixar', 'Fullscreen': 'Tela cheia', 'View fullscreen': 'Abrir em tela cheia',
    'Close fullscreen': 'Sair da tela cheia', 'Close': 'Fechar',
    'Copy to clipboard': 'Copiar para a área de transferência',
    'Copy': 'Copiar', 'Copied!': 'Copiado!', 'Clear all': 'Limpar seleção',
    'Remove file': 'Remover arquivo', 'Remove': 'Remover',
    'Show password text': 'Mostrar senha', 'Hide password text': 'Ocultar senha',
    'Open calendar': 'Abrir calendário', 'Previous month': 'Mês anterior',
    'Next month': 'Próximo mês', 'Select date': 'Selecione a data',
    'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 'April': 'Abril',
    'May': 'Maio', 'June': 'Junho', 'July': 'Julho', 'August': 'Agosto',
    'September': 'Setembro', 'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro',
    'Sun': 'Dom', 'Mon': 'Seg', 'Tue': 'Ter', 'Wed': 'Qua', 'Thu': 'Qui', 'Fri': 'Sex', 'Sat': 'Sáb',
    'Sunday': 'Domingo', 'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira',
    'Wednesday': 'Quarta-feira', 'Thursday': 'Quinta-feira', 'Friday': 'Sexta-feira', 'Saturday': 'Sábado'
  };
  const translated = value => {
    const stripped = value.trim();
    if (phrases[stripped]) return value.replace(stripped, phrases[stripped]);
    return value.replace(/^Limit (.+) per file(?:\s*[•·]\s*(.+))?$/, (_, size, types) =>
      `Limite de ${size} por arquivo${types ? ' · ' + types : ''}`);
  };
  const selectors = [
    '[data-testid="stFileUploaderDropzone"]', '[data-testid="stElementToolbar"]',
    '[data-testid="stTooltipContent"]', '[data-testid="stCodeCopyButton"]',
    '[data-baseweb="calendar"]', '[data-baseweb="select"] [aria-hidden="true"]'
  ].join(',');
  const translate = () => {
    document.documentElement.lang = 'pt-BR';
    document.querySelectorAll(selectors).forEach(root => {
      const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
      const nodes = [];
      while (walker.nextNode()) nodes.push(walker.currentNode);
      nodes.forEach(node => {
        const value = translated(node.nodeValue);
        if (value !== node.nodeValue) node.nodeValue = value;
      });
    });
    document.querySelectorAll('[data-testid="stFileUploader"] button, [data-testid="stElementToolbar"] button, [data-testid="stDateInput"] button').forEach(node => {
      ['aria-label', 'title'].forEach(attr => {
        const value = node.getAttribute(attr);
        if (value && translated(value) !== value) node.setAttribute(attr, translated(value));
      });
    });
  };
  let queued = false;
  window.communitylabUiTranslation = new MutationObserver(() => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => { queued = false; translate(); });
  });
  window.communitylabUiTranslation.observe(document.body, {subtree:true, childList:true, characterData:true});
  translate();
})();
</script>
"""


def localize_native_controls():
    st.html(NATIVE_PORTUGUESE, unsafe_allow_javascript=True)
