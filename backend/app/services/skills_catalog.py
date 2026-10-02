"""
Modular skill catalog.

Add new skills here — the analyzer picks them up automatically.
Each skill can have aliases for better matching.
"""

from dataclasses import dataclass, field


@dataclass
class SkillDefinition:
    name: str
    aliases: list[str] = field(default_factory=list)
    category: str = "general"  # programming, framework, database, cloud, ai, testing, tools
    priority: int = 1  # higher = more relevant for "strong" skill ranking


# Keep this list easy to extend for portfolio demos and interview explanations
SKILL_CATALOG: list[SkillDefinition] = [
    # Languages
    SkillDefinition("Python", ["python3", "py"], "programming", 5),
    SkillDefinition("Java", ["core java", "jdk"], "programming", 4),
    SkillDefinition("JavaScript", ["js", "ecmascript"], "programming", 5),
    SkillDefinition("TypeScript", ["ts"], "programming", 4),
    SkillDefinition("SQL", ["structured query language"], "database", 5),
    SkillDefinition("HTML", ["html5"], "programming", 2),
    SkillDefinition("CSS", ["css3"], "programming", 2),
    SkillDefinition("C++", ["cpp", "c plus plus"], "programming", 3),
    SkillDefinition("C#", ["csharp", "c sharp"], "programming", 3),
    SkillDefinition("Go", ["golang"], "programming", 3),
    SkillDefinition("R", [], "programming", 2),

    # Frameworks / libraries
    SkillDefinition("React", ["reactjs", "react.js"], "framework", 5),
    SkillDefinition("Next.js", ["nextjs"], "framework", 3),
    SkillDefinition("Node.js", ["nodejs", "node"], "framework", 4),
    SkillDefinition("FastAPI", ["fast api"], "framework", 5),
    SkillDefinition("Django", [], "framework", 4),
    SkillDefinition("Flask", [], "framework", 4),
    SkillDefinition("Express", ["express.js", "expressjs"], "framework", 3),
    SkillDefinition("Spring Boot", ["springboot", "spring"], "framework", 3),
    SkillDefinition("Vue.js", ["vue", "vuejs"], "framework", 2),
    SkillDefinition("Angular", [], "framework", 2),
    SkillDefinition("Tailwind CSS", ["tailwind", "tailwindcss"], "framework", 2),

    # Databases
    SkillDefinition("MongoDB", ["mongo"], "database", 4),
    SkillDefinition("PostgreSQL", ["postgres", "psql"], "database", 4),
    SkillDefinition("MySQL", [], "database", 3),
    SkillDefinition("SQLite", [], "database", 3),
    SkillDefinition("Redis", [], "database", 2),
    SkillDefinition("Firebase", [], "database", 2),

    # AI / ML / GenAI
    SkillDefinition("Machine Learning", ["ml", "scikit-learn", "sklearn"], "ai", 5),
    SkillDefinition("Artificial Intelligence", ["ai"], "ai", 4),
    SkillDefinition("Generative AI", ["genai", "gen ai"], "ai", 5),
    SkillDefinition("NLP", ["natural language processing"], "ai", 5),
    SkillDefinition("Deep Learning", ["neural networks", "cnn", "rnn"], "ai", 4),
    SkillDefinition("LLM APIs", ["openai", "gpt", "langchain", "llm"], "ai", 5),
    SkillDefinition("TensorFlow", ["tf"], "ai", 3),
    SkillDefinition("PyTorch", [], "ai", 3),
    SkillDefinition("Pandas", [], "ai", 3),
    SkillDefinition("NumPy", ["numpy"], "ai", 3),
    SkillDefinition("Computer Vision", ["opencv", "cv"], "ai", 2),

    # Cloud / DevOps
    SkillDefinition("AWS", ["amazon web services"], "cloud", 4),
    SkillDefinition("Azure", ["microsoft azure"], "cloud", 3),
    SkillDefinition("Google Cloud", ["gcp", "google cloud platform"], "cloud", 3),
    SkillDefinition("Docker", ["containerization"], "cloud", 5),
    SkillDefinition("Kubernetes", ["k8s"], "cloud", 3),
    SkillDefinition("CI/CD", ["continuous integration", "github actions", "jenkins"], "cloud", 3),
    SkillDefinition("Linux", ["ubuntu", "unix"], "cloud", 2),

    # Tools / VCS
    SkillDefinition("Git", [], "tools", 5),
    SkillDefinition("GitHub", [], "tools", 4),
    SkillDefinition("REST APIs", ["rest api", "restful", "api development"], "tools", 4),
    SkillDefinition("GraphQL", [], "tools", 2),
    SkillDefinition("Postman", [], "tools", 3),
    SkillDefinition("Jira", [], "tools", 2),

    # Testing
    SkillDefinition("Selenium", [], "testing", 4),
    SkillDefinition("API Testing", ["rest assured", "api test"], "testing", 4),
    SkillDefinition("Manual Testing", ["qa", "quality assurance"], "testing", 3),
    SkillDefinition("Pytest", ["unit testing", "py.test"], "testing", 3),
    SkillDefinition("Jest", [], "testing", 2),
    SkillDefinition("Cypress", [], "testing", 2),
]


# Role-oriented recommended skill bundles (used when JD is absent)
ROLE_RECOMMENDATIONS = {
    "ai_ml": ["FastAPI", "Docker", "AWS", "NLP", "LLM APIs", "Generative AI", "PostgreSQL"],
    "fullstack": ["TypeScript", "Docker", "PostgreSQL", "REST APIs", "CI/CD", "AWS"],
    "backend": ["FastAPI", "Docker", "PostgreSQL", "Redis", "AWS", "CI/CD"],
    "qa": ["Selenium", "API Testing", "Postman", "Pytest", "CI/CD", "SQL"],
    "default": ["FastAPI", "Docker", "AWS", "NLP", "LLM APIs", "PostgreSQL", "CI/CD"],
}


def build_skill_lookup() -> dict[str, SkillDefinition]:
    """Map lowercase alias/name -> SkillDefinition for fast detection."""
    lookup: dict[str, SkillDefinition] = {}
    for skill in SKILL_CATALOG:
        lookup[skill.name.lower()] = skill
        for alias in skill.aliases:
            lookup[alias.lower()] = skill
    return lookup


SKILL_LOOKUP = build_skill_lookup()
