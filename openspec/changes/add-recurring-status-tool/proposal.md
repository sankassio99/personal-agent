# Proposal

## Why

O comando de recorrentes não consegue alterar o estado de pagamento de uma despesa recorrente na planilha. Isso obriga o usuário a editar a planilha manualmente e impede que comandos como `/recorrente atualiza o status da digi internet para paga` sejam executados de forma confiável.

## What Changes

- Adicionar uma ferramenta especializada para localizar uma despesa recorrente pelo nome e atualizar sua situação na coluna E da planilha.
- Restringir os valores persistidos de situação a `Pago` e `Pendente`.
- Orientar o agente de recorrentes a usar a ferramenta quando o usuário solicitar atualização de status, incluindo variações naturais como “paga”.
- Retornar ao usuário um resultado claro para atualização concluída, status inválido e, quando a recorrente não for encontrada, as contas recorrentes disponíveis.

## Capabilities

### New Capabilities

- `recurring-status-update`: Atualiza o status `Pago` ou `Pendente` de uma despesa recorrente identificada pelo usuário na coluna E da planilha.

### Modified Capabilities

- Nenhuma.

## Impact

- Código do agente e das ferramentas de recorrentes.
- Adaptador de acesso à planilha do Google e sua lógica de localização/atualização de linhas.
- Instruções do agente, testes automatizados e documentação operacional relacionada a recorrentes.
