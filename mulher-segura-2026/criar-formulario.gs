/**
 * Execute criarPreInscricaoMulherSegura UMA vez em https://script.google.com/
 * na conta institucional autorizada. Não compartilhe URL de edição nem planilha.
 */
function criarPreInscricaoMulherSegura() {
  const props = PropertiesService.getScriptProperties();
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const old = props.getProperty('FORM_ID');
    if (old) { const existing=FormApp.openById(old); Logger.log('URL de resposta: '+existing.getPublishedUrl()); Logger.log('URL de edição (restrito): '+existing.getEditUrl()); return; }
    const form = FormApp.create('Operação Mulher Segura 2026 | Pré-inscrição DAI/CBMMG');
    form.setAcceptingResponses(false);
    form.setDescription('Palestra: 25/11/2026, das 9h às 11h, Google Meet. Dra. Isabel Araújo Rodrigues, OAB/MG. Público: efetivo masculino elegível da DAI. Dados utilizados exclusivamente para organização e controle institucional. A pré-inscrição não substitui a presença. Não inclua relatos pessoais ou dados de terceiros.');
    form.setCollectEmail(false).setPublishingSummary(false).setAllowResponseEdits(false).setShowLinkToRespondAgain(false).setConfirmationMessage('Pré-inscrição registrada. Acompanhe as orientações da coordenação pelos canais institucionais. Este registro não substitui o controle de presença.');
    form.addTextItem().setTitle('Nome completo').setRequired(true).setValidation(FormApp.createTextValidation().requireTextMatchesPattern('.*\\S+\\s+\\S+.*').setHelpText('Informe nome e sobrenome.').build());
    form.addTextItem().setTitle('Número BM').setHelpText('Informe seu número BM com dígito verificador, se aplicável. Ex.: 123.456-7.').setRequired(true).setValidation(FormApp.createTextValidation().requireTextMatchesPattern('^(?:[0-9]{6,8}|[0-9]{3}\\.[0-9]{3}-[0-9]|[0-9]{6}-[0-9])$').setHelpText('Use apenas dígitos ou o formato 123.456-7.').build());
    form.addListItem().setTitle('Posto/graduação').setChoiceValues(['Coronel BM','Tenente-Coronel BM','Major BM','Capitão BM','1º Tenente BM','2º Tenente BM','Aspirante a Oficial BM','Subtenente BM','1º Sargento BM','2º Sargento BM','3º Sargento BM','Cabo BM','Soldado BM – 1ª classe','Soldado BM – 2ª classe']).setRequired(true);
    form.addListItem().setTitle('Órgão externo ou seção/divisão de lotação').setChoiceValues(['DAI – Diretoria','DAI – Subdiretoria','DAI – DAI/1','DAI/2 – Coordenação de Órgãos Externos','DAI – Outra seção/divisão interna','AFAS','ALMG','CEDEC','CTPM','Fundação SALVAR','GMG','Intendência CAMG','MPMG','OGE','SEE','SEJUSP','SEMAD','SENASP','SES','TJMG','TJMMG']).setRequired(true);
    form.addTextItem().setTitle('Se selecionou outra seção/divisão interna, especifique').setRequired(false);
    const sheet=SpreadsheetApp.create('Respostas restritas | Pré-inscrição Operação Mulher Segura 2026');
    form.setDestination(FormApp.DestinationType.SPREADSHEET,sheet.getId());
    props.setProperty('FORM_ID',form.getId());
    Logger.log('URL de resposta: '+form.getPublishedUrl());
    Logger.log('URL de edição (restrito): '+form.getEditUrl());
    Logger.log('Planilha (restrita): '+sheet.getUrl());
    Logger.log('Antes de abrir: confira acesso institucional e permissões; publique o formulário e habilite respostas. Teste com dados fictícios e remova a resposta de teste do formulário e da planilha. Depois informe o URL de resposta ao responsável pela página.');
  } finally {lock.releaseLock();}
}
