# Spec Delta

## Purpose

Provide spreadsheet-managed category choices so the assistant can classify incomplete expense and income entries consistently with each user's workbook.

## ADDED Requirements

### Requirement: Expense categories are retrieved from the summary worksheet
The system SHALL retrieve non-empty expense categories from `Sumário!B30:B42` in the spreadsheet mapped to the requesting Telegram user.

#### Scenario: A mapped user requests expense categories
- **WHEN** the category tool is invoked for expense classification by a mapped user
- **THEN** it returns the non-empty values from `Sumário!B30:B42` in that user's spreadsheet

#### Scenario: An unmapped user requests expense categories
- **WHEN** the category tool is invoked for expense classification without a mapped spreadsheet
- **THEN** it rejects the request without accessing a spreadsheet

### Requirement: Income categories are retrieved from the summary worksheet
The system SHALL retrieve non-empty income categories from `Sumário!B49:B53` in the spreadsheet mapped to the requesting Telegram user.

#### Scenario: A mapped user requests income categories
- **WHEN** the category tool is invoked for income classification by a mapped user
- **THEN** it returns the non-empty values from `Sumário!B49:B53` in that user's spreadsheet

### Requirement: Missing categories are inferred from available categories
The system SHALL retrieve the applicable category list before inferring a category for an expense or income entry that does not include one.

#### Scenario: An expense omits its category
- **WHEN** a user provides a new expense without a category
- **THEN** the agent retrieves the expense categories and selects an applicable available category before adding the expense

#### Scenario: An income omits its category
- **WHEN** a user provides a new income without a category
- **THEN** the agent retrieves the income categories and selects an applicable available category before adding the income

#### Scenario: A category is explicitly provided
- **WHEN** a user provides a category while adding an expense or income
- **THEN** the agent preserves that category and does not infer a replacement

#### Scenario: No applicable category can be inferred
- **WHEN** the applicable category list is empty or none of its values fit the entry
- **THEN** the agent asks the user to provide a category and does not add the entry
