def generate_prompt(book, chapter):
    return f"""
TASK: Research everything relevant to {book} chapter {chapter} and produce a structured, blog‑ready summary.

GOALS:
- Provide a clear, engaging summary of {book} {chapter}.
- Include study‑guide insights: structure, symbolism, Old Testament connections, cultural context, theological themes, and literary design.
- Add fun or humorous stories, teaching anecdotes, or memorable illustrations commonly used when explaining {book} {chapter}.
- Add historical facts, linguistic notes, cultural background, and scholarly observations.
- Include all sources used, even if general (commentaries, dictionaries, encyclopedias, sermons, academic papers, etc.).
- Write everything in a tone suitable for a blog post: engaging, clear, accurate, and easy to read.

OUTPUT STRUCTURE:
1. Chapter Overview — A concise but rich summary of {book} {chapter}.
2. Key Events / Structure — Break down the major movements of the chapter.
3. Study‑Guide Insights — Themes, literary design, Old Testament echoes, theological meaning.
4. Historical & Cultural Background — Customs, geography, lineage, political context, etc.
5. Fun Stories & Illustrations — Clean, humorous anecdotes teachers use when explaining this chapter.
6. Interesting Facts — Linguistic notes, symbolism, numerology, unique features of the chapter.
7. Application Ideas — How modern readers apply {book} {chapter}.
8. Sources Used — List every resource referenced.

STYLE REQUIREMENTS:
- Write clearly and engagingly.
- Avoid doctrinal bias; present multiple viewpoints when relevant.
- No filler; every section should add value.
- Make it easy for me to adapt into a blog post.

ADDITIONAL INSTRUCTIONS:
- If quoting Scripture, quote only 1–2 verses maximum and keep them short.
- Summaries must be original, not copied.
- Humor should be clean and respectful.
- Facts must be accurate and sourced.

FINAL DELIVERABLE:
A fully structured, polished, blog‑ready research document on {book} chapter {chapter} containing summaries, study‑guide insights, fun stories, facts, and a complete list of sources.
"""

# --- Run the generator ---
book = input("Enter the book name (e.g., Matthew): ")
chapter = input("Enter the chapter number (e.g., 1): ")

print(generate_prompt(book, chapter))
