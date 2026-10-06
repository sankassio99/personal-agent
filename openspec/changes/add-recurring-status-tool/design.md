# Design

## Context

O comando de recorrentes já cria um agente configurado para a aba `Recorrentes`, mas suas ferramentas atuais não fornecem uma operação determinística para atualizar apenas o status de uma linha. Veja `proposal.md` para a motivação e `specs/recurring-status-update/spec.md` para o comportamento.

## Goals / Non-Goals

**Goals:**

- Expor uma ferramenta específica para localizar uma recorrente por nome e atualizar somente a célula da coluna E.
- Garantir que os únicos valores gravados sejam os valores canônicos `Pago` e `Pendente`.
- Disponibilizar a ferramenta exclusivamente no fluxo de recorrentes e orientar o agente a utilizá-la para pedidos de atualização.
- Cobrir os caminhos de sucesso, status inválido, ausência com contas disponíveis e ambiguidade em testes sem acesso à API real.

**Non-Goals:**

- Alterar valores, descrição, categoria ou periodicidade da recorrente.
- Criar ou excluir recorrentes.
- Inferir qual registro atualizar quando a busca não resultar em uma única correspondência.

## Decisions

### Criar uma ferramenta dedicada de leitura, correspondência e atualização

A ferramenta receberá o nome da recorrente, o status solicitado e o contexto de planilha/usuário já adotado pelas ferramentas existentes. Ela lerá as linhas da aba de recorrentes, comparará nomes normalizados na coluna A e, quando houver uma correspondência única, atualizará exclusivamente a célula da coluna E daquela linha.

Usar uma ferramenta explícita evita que o modelo monte intervalos e índices de linha por conta própria. A alternativa de expor somente as operações genéricas do provedor de planilhas deixa a atualização vulnerável a alterações na linha ou coluna errada.

### Validar e normalizar antes de chamar a planilha

A ferramenta normalizará espaços, caixa e as formas `pago`/`paga` para `Pago`, e `pendente` para `Pendente`, rejeitando qualquer outro valor antes da operação de escrita.

Essa validação protege a integridade da coluna E e produz mensagens consistentes. Aceitar texto arbitrário transferiria a validação ao modelo e permitiria valores incompatíveis na planilha.

### Usar correspondência de nome normalizada, exigir unicidade e sugerir opções

A busca normalizará espaços e caixa dos nomes, permitindo o uso natural do comando sem depender da capitalização da planilha. A atualização ocorrerá apenas quando a correspondência for única. Quando não houver correspondência, a ferramenta retornará os nomes não vazios da coluna A como opções disponíveis; nomes ambíguos continuarão a exigir uma identificação mais específica.

Selecionar a primeira correspondência seria mais simples, mas poderia modificar uma recorrente diferente da pretendida. Fazer uma correção aproximada automática também evitaria uma interação adicional, mas poderia atualizar a conta errada; a lista de opções mantém a decisão com o usuário.

### Registrar a ferramenta e a instrução no agente de recorrentes

A nova ferramenta será adicionada à composição de ferramentas do agente e a instrução do fluxo de recorrentes exigirá seu uso para pedidos de alteração de status. O agente continuará encaminhando pedidos que não sejam de status pelos comportamentos existentes.

Acoplar a ferramenta à construção genérica de todos os agentes ampliaria desnecessariamente o acesso de outros fluxos à aba de recorrentes.

## Risks / Trade-offs

- [A planilha pode ter linhas de cabeçalho ou vazias] → A leitura ignorará linhas sem nome e calculará o número de linha preservando a posição original.
- [Nomes visualmente semelhantes podem gerar mais de uma correspondência] → A ferramenta recusará a atualização ambígua e pedirá um nome mais específico.
- [Falha de autenticação ou API do Google] → A ferramenta propagará um erro contextualizado, mantendo a mensagem de falha visível ao usuário e sem reportar sucesso.
- [O modelo pode tentar outra ferramenta para uma solicitação de status] → A instrução do agente priorizará explicitamente a ferramenta dedicada, e testes verificarão que ela está registrada no fluxo.

## Migration Plan

1. Implantar a nova ferramenta, seu registro no agente de recorrentes e os testes correspondentes.
2. Reiniciar o processo da aplicação para carregar a configuração atualizada.
3. Validar com um comando de atualização de status em uma planilha autorizada.
4. Em caso de regressão, reverter a alteração de código; a ferramenta não exige migração de estrutura da planilha.
