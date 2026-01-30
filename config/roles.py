from typing import Dict, List

ROLE_SKILLS: Dict[str, List[str]] = {
    "Python Developer": ["python", "django", "rest", "sql", "git", "api", "oop", "pytest"],
    "Data Scientist": ["python", "machine learning", "sql", "statistics", "pandas", "numpy", "nlp", "deep learning"],
    "Web Developer": ["html", "css", "javascript", "react", "node", "git", "api", "sql"],
    "DevOps Engineer": ["docker", "kubernetes", "cloud", "git", "ci/cd", "terraform", "linux"],
    "ML Engineer": ["python", "deep learning", "mlops", "pytorch", "tensorflow", "docker", "cloud"],
}

DIFFICULTY_SETTINGS = {
    "Beginner": {"depth": 1, "complexity": 1, "time_limit": 60},
    "Intermediate": {"depth": 2, "complexity": 2, "time_limit": 90},
    "Advanced": {"depth": 3, "complexity": 3, "time_limit": 120},
}

SKILL_KEYWORDS: List[str] = list({
    "python", "java", "sql", "statistics", "pandas", "numpy", "scikit-learn", "matplotlib", "seaborn",
    "machine learning", "deep learning", "nlp", "computer vision", "pytorch", "tensorflow",
    "django", "flask", "fastapi", "rest", "api", "oop", "pytest",
    "html", "css", "javascript", "react", "node", "express", "angular", "vue",
    "docker", "kubernetes", "git", "github", "gitlab", "ci/cd", "terraform", "linux", "cloud", "aws", "gcp", "azure",
    "communication", "teamwork", "leadership", "problem solving", "agile", "scrum",
})
