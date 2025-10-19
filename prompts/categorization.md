Categorize this news article into one of four categories and detect if it's clickbait.

**Article Information:**
- **Title:** {title}
- **Source:** {source}
- **Summary:** {summary}

**Your Task:**
1. Categorize the article into ONE of these categories:
   - **Must Know**: Critical news everyone should know about (major events, protests, natural disasters, political developments, cultural moments, celebrity deaths that matter socially)
   - **Sports Context**: Sports news with context for non-fans - include "why people care" and what's significant (championships, playoffs, major upsets, retirements)
   - **Tech & Tools**: Technology news, productivity tools, AI developments, coding tools, developer resources, industry trends
   - **Fun Stuff**: Entertainment, humor, interesting stories, cultural phenomena, diversions

2. Determine if this is clickbait:
   - Sensationalized headlines with vague promises ("You won't believe...")
   - Misleading or deceptive titles
   - Native advertising disguised as news
   - Low-quality content designed solely for clicks

3. Provide a confidence score (0.0 to 1.0) for your categorization

4. Briefly explain your reasoning (1-2 sentences)

**Important Guidelines:**
- Avoid echo chambers: Ensure balanced representation across political perspectives
- Filter out: Celebrity gossip (unless culturally significant), sports statistics (focus on context), promotional content
- Prioritize: Factual reporting over opinion pieces, original reporting over aggregation
- For sports: Focus on "why this matters" not play-by-play details

**Response Format:**
Respond ONLY with valid JSON in this exact format:
```json
{{
  "category": "Must Know",
  "is_clickbait": false,
  "confidence": 0.95,
  "reasoning": "Major political development with widespread social impact"
}}
```

The category field MUST be exactly one of: "Must Know", "Sports Context", "Tech & Tools", or "Fun Stuff"
