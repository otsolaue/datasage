from datasage.pipeline.stages import StageType

# Each recipe is a dict with a display name and a prompt template.
# {text} is replaced with the user's input at runtime.

RECIPES: dict[StageType, list[dict]] = {
    StageType.CLEAN: [
        {
            "name": "Remove boilerplate",
            "prompt": "Remove any boilerplate, headers, footers, and navigation text from the following. Return only the meaningful content:\n\n{text}",
        },
        {
            "name": "Normalize whitespace & encoding",
            "prompt": "Fix encoding issues, collapse excessive whitespace, and normalize punctuation in the following text. Return the cleaned text only:\n\n{text}",
        },
    ],
    StageType.EXTRACT: [
        {
            "name": "Key facts",
            "prompt": "Extract the key facts from the following text as a numbered list. Be concise:\n\n{text}",
        },
        {
            "name": "Named entities",
            "prompt": "List all named entities (people, organizations, locations, dates) found in the following text. Group by type:\n\n{text}",
        },
        {
            "name": "Quotes",
            "prompt": "Extract all direct quotes from the following text, noting who said each one if available:\n\n{text}",
        },
    ],
    StageType.ANALYZE: [
        {
            "name": "Summarize",
            "prompt": "Write a concise summary of the following text in 3-5 sentences:\n\n{text}",
        },
        {
            "name": "Sentiment",
            "prompt": "Analyze the sentiment of the following text. Is it positive, negative, or neutral? Explain briefly:\n\n{text}",
        },
        {
            "name": "Themes",
            "prompt": "Identify the main themes and topics in the following text. List them with a one-sentence explanation each:\n\n{text}",
        },
    ],
}


def get_recipes(stage: StageType) -> list[dict]:
    return RECIPES.get(stage, [])


def apply_recipe(recipe: dict, text: str) -> str:
    return recipe["prompt"].replace("{text}", text)
