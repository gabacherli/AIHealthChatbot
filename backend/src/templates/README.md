# Templates Directory

This directory contains template files used throughout the AI Health Chatbot application. Templates are organized by type and purpose to improve maintainability and separation of concerns.

## Directory Structure

```
templates/
├── prompts/                    # AI prompt templates
│   ├── patient_assistant_pt.md # Portuguese patient assistant prompt
│   ├── patient_assistant_en.md # English patient assistant prompt
│   ├── professional_assistant_pt.md # Portuguese professional prompt
│   ├── professional_assistant_en.md # English professional prompt
│   ├── patient_no_context.md   # English patient prompt without context
│   ├── patient_no_context_pt.md # Portuguese patient prompt without context
│   ├── professional_no_context.md # English professional prompt without context
│   └── professional_no_context_pt.md # Portuguese professional prompt without context
└── README.md                   # This file
```

## Prompt Templates

### Patient Assistant Templates

- **patient_assistant_pt.md**: Comprehensive Portuguese medical assistant prompt for patients with detailed clinical evidence requirements, reference formatting, and chronic disease focus
- **patient_assistant_en.md**: English version of the patient assistant prompt (simplified)

### Professional Assistant Templates

- **professional_assistant_pt.md**: Portuguese template for healthcare professionals with clinical insights and evidence-based information
- **professional_assistant_en.md**: English template for healthcare professionals with clinical insights and evidence-based information

### No-Context Templates

- **patient_no_context.md**: English general health information prompt for patients without specific medical context
- **patient_no_context_pt.md**: Portuguese general health information prompt for patients without specific medical context
- **professional_no_context.md**: English professional prompt for general medical queries
- **professional_no_context_pt.md**: Portuguese professional prompt for general medical queries

## Default Language

**All template loading methods default to Portuguese ("pt").** This reflects the primary target audience of the AI Health Chatbot. English templates are available by explicitly specifying `language="en"`.

## Template Variables

Templates may contain placeholder variables that are replaced at runtime:

- `{context_type}`: Type of medical records context ("patient" or "your")
- `{patient_note}`: Additional notes for professional queries

## Usage

Templates are loaded using the `TemplateLoader` service:

```python
from src.services.template_loader import template_loader

# All methods default to Portuguese ("pt")

# Load patient prompt (defaults to Portuguese)
patient_prompt = template_loader.get_patient_prompt()

# Load patient prompt in English (explicit)
patient_prompt_en = template_loader.get_patient_prompt(language="en")

# Load professional prompt with context (defaults to Portuguese)
professional_prompt = template_loader.get_professional_prompt(context_type="patient")

# Load professional prompt with context in English (explicit)
professional_prompt_en = template_loader.get_professional_prompt(context_type="patient", language="en")

# Load no-context prompt for patient (defaults to Portuguese)
no_context_prompt = template_loader.get_no_context_prompt("patient", is_professional_query=False)

# Load no-context prompt for patient in English (explicit)
no_context_prompt_en = template_loader.get_no_context_prompt("patient", is_professional_query=False, language="en")
```

## Benefits of Template Organization

1. **Maintainability**: Easy to edit prompts without touching application code
2. **Version Control**: Better tracking of prompt changes in git
3. **Separation of Concerns**: Content separated from business logic
4. **Internationalization**: Easy to add new language versions
5. **Caching**: Templates are cached for performance
6. **Fallback Support**: Graceful degradation if templates fail to load

## Adding New Templates

1. Create a new `.md` file in the appropriate subdirectory
2. Add loading methods to `TemplateLoader` if needed
3. Update this README with the new template information
4. Test the template loading in your application

## Template Format

Templates should be written in Markdown format with:
- Clear section headers using `##`
- Proper formatting for readability
- Placeholder variables in `{variable_name}` format
- UTF-8 encoding for international characters
