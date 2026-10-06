# Spec Delta

## Purpose

Permitir que usuários atualizem com segurança o status de pagamento de despesas recorrentes por comandos em linguagem natural.

## ADDED Requirements

### Requirement: Update recurring payment status

O sistema SHALL permitir que o agente atualize o status de uma despesa recorrente identificada pelo nome na coluna A, gravando `Pago` ou `Pendente` na coluna E da respectiva linha da planilha de recorrentes.

#### Scenario: Mark a recurring expense as paid

- **WHEN** o usuário solicita que o status da recorrente “digi internet” seja atualizado para “paga”
- **THEN** o sistema SHALL localizar a recorrente correspondente e gravar `Pago` na coluna E da sua linha.

#### Scenario: Mark a recurring expense as pending

- **WHEN** o usuário solicita que o status de uma recorrente seja atualizado para “pendente”
- **THEN** o sistema SHALL gravar `Pendente` na coluna E da linha correspondente.

### Requirement: Normalize accepted status requests

O sistema SHALL aceitar valores de status sem diferenciação entre maiúsculas e minúsculas e SHALL normalizar as formas portuguesas de pago, incluindo `paga`, para `Pago`; solicitações de pendente SHALL ser normalizadas para `Pendente`.

#### Scenario: Normalize feminine paid status

- **WHEN** o usuário informa o status “paga”
- **THEN** o sistema SHALL persistir o valor canônico `Pago`.

#### Scenario: Reject an unsupported status

- **WHEN** o usuário solicita um status diferente de pago ou pendente
- **THEN** o sistema SHALL informar que os únicos status aceitos são `Pago` e `Pendente` sem alterar a planilha.

### Requirement: Report update outcome

O sistema SHALL informar ao usuário se a atualização foi concluída, se não encontrou uma recorrente correspondente ou se encontrou mais de uma correspondência ambígua, sem modificar linhas que não tenham sido identificadas de forma única. Quando não encontrar uma recorrente, o sistema SHALL incluir na resposta os nomes não vazios das contas recorrentes disponíveis na coluna A.

#### Scenario: Recurring expense is not found

- **WHEN** o usuário solicita a atualização de uma recorrente inexistente
- **THEN** o sistema SHALL informar que a recorrente não foi encontrada, listar as contas recorrentes disponíveis e não SHALL alterar a planilha.

#### Scenario: Recurring expense match is ambiguous

- **WHEN** mais de uma recorrente corresponder ao nome informado pelo usuário
- **THEN** o sistema SHALL solicitar uma identificação mais específica e não SHALL alterar a planilha.
