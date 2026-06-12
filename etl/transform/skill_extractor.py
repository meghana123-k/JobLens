# skill_extractor.py
import re
import unicodedata
from typing import Dict, List, Set, Tuple, Iterable, Optional

try:
    # Optional fuzzy matcher for typos and variants (e.g., "Kubernets" -> "Kubernetes")
    from rapidfuzz import fuzz, process  # type: ignore

    HAS_RAPIDFUZZ = True
except Exception:
    HAS_RAPIDFUZZ = False

try:
    # Optional NER backfill for tools/technologies not yet in dictionary
    import spacy  # type: ignore

    HAS_SPACY = True
except Exception:
    HAS_SPACY = False


def normalize_text(s: str) -> str:
    """
    Lowercase, strip diacritics, collapse whitespace, remove control chars.
    Keep punctuation as we rely on regex word boundaries; we'll also create
    a punctuation-light variant for phrase matching.
    """
    if not s:
        return ""
    s = s.lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\s+", " ", s)
    s = s.strip()
    return s


def strip_punct_keep_dots(s: str) -> str:
    """
    Remove most punctuation, but keep dots in tokens like 'node.js', 'react.js'.
    Also keep plus in 'c++', hash in 'c#', hyphen inside words.
    """
    # Allow dot, plus, hash, hyphen
    return re.sub(r"[^\w\.\+\#\- ]+", " ", s)


class SkillExtractor:
    """
    Dictionary-first skill extractor with:
    - Phrase-first exact matching using compiled regex (with word/sep boundaries)
    - Safe alias expansion for variants (e.g., react.js/reactjs/react)
    - Optional fuzzy matching (rapidfuzz) and spaCy NER backfill

    Usage:
      extractor = SkillExtractor(enable_fuzzy=False, enable_ner=False)
      skills = extractor.extract_skills(text)

      # For Arbeitnow jobs
      skills = extractor.extract_job_skills(job_dict)
    """

    def __init__(
        self,
        enable_fuzzy: bool = False,
        fuzzy_threshold: int = 90,  # 0..100; 90 is strict and avoids false positives
        enable_ner: bool = False,
    ):
        self.enable_fuzzy = enable_fuzzy and HAS_RAPIDFUZZ
        self.fuzzy_threshold = fuzzy_threshold
        self.enable_ner = enable_ner and HAS_SPACY
        self._nlp = spacy.load("en_core_web_sm") if self.enable_ner else None

        # Centralized, normalized skill dictionary:
        # Each entry has a canonical name and a list of aliases/keywords to match.
        # Keep canonical names Title Case and concise.
        self.SKILL_ONTOLOGY: Dict[str, Dict[str, Iterable[str]]] = (
            self._build_skill_ontology()
        )

        # Flatten aliases -> canonical, preferring longer phrases in match order
        self.alias_to_canonical: Dict[str, str] = {}
        for canonical, meta in self.SKILL_ONTOLOGY.items():
            self.alias_to_canonical[normalize_text(canonical)] = canonical
            for a in meta.get("aliases", []):
                self.alias_to_canonical[normalize_text(a)] = canonical

        # For regex phrase-first matching, precompile sorted by alias length desc
        self._compiled_patterns: List[Tuple[re.Pattern, str]] = self._compile_patterns(
            self.alias_to_canonical
        )

        # For fuzzy fallback list
        self._all_aliases: List[str] = list(self.alias_to_canonical.keys())

    def _build_skill_ontology(self) -> Dict[str, Dict[str, Iterable[str]]]:
        """
        A curated, extensible skill ontology with rich aliases.
        You can add business/role skills too (e.g., Finance, HR) if needed.

        Note:
        - Prefer canonical short names (e.g., 'Google Cloud' over 'Google Cloud Platform').
        - Put long/explicit phrases in aliases so phrase-first matching hits them.
        """
        return {
            # Programming Languages
            "Python": {"aliases": ["python", "py"]},
            "Java": {"aliases": ["java"]},
            "JavaScript": {"aliases": ["javascript", "js", "ecmascript"]},
            "TypeScript": {"aliases": ["typescript", "ts"]},
            "C": {"aliases": ["c language", "lang c"]},
            "C++": {"aliases": ["c++", "cpp"]},
            "C#": {"aliases": ["c#", "c sharp", "c-sharp"]},
            "Go": {"aliases": ["go", "golang"]},
            "Rust": {"aliases": ["rust"]},
            "PHP": {"aliases": ["php"]},
            "Ruby": {"aliases": ["ruby"]},
            "Scala": {"aliases": ["scala"]},
            "Kotlin": {"aliases": ["kotlin"]},
            "Swift": {"aliases": ["swift"]},
            "R": {"aliases": ["r language", "lang r"]},
            "Perl": {"aliases": ["perl"]},
            # Frontend
            "React": {"aliases": ["react", "reactjs", "react.js"]},
            "Angular": {"aliases": ["angular", "angularjs", "angular.js"]},
            "Vue.js": {"aliases": ["vue", "vuejs", "vue.js"]},
            "Next.js": {"aliases": ["nextjs", "next.js"]},
            "Nuxt.js": {"aliases": ["nuxt", "nuxtjs", "nuxt.js"]},
            "HTML": {"aliases": ["html", "html5"]},
            "CSS": {"aliases": ["css", "css3"]},
            "SASS": {"aliases": ["sass", "scss"]},
            "Tailwind CSS": {"aliases": ["tailwind", "tailwindcss", "tailwind css"]},
            "Bootstrap": {"aliases": ["bootstrap", "twbs"]},
            # Backend / Frameworks
            "Django": {"aliases": ["django"]},
            "Flask": {"aliases": ["flask"]},
            "FastAPI": {"aliases": ["fastapi"]},
            "Spring": {"aliases": ["spring framework", "spring"]},
            "Spring Boot": {"aliases": ["spring boot"]},
            "Node.js": {"aliases": ["node", "nodejs", "node.js"]},
            "Express.js": {"aliases": ["express", "expressjs", "express.js"]},
            "Laravel": {"aliases": ["laravel"]},
            ".NET": {"aliases": [".net", "dotnet", ".net core", "asp.net", "asp net"]},
            "Ruby on Rails": {"aliases": ["rails", "ruby on rails"]},
            "GraphQL": {"aliases": ["graphql", "graph ql"]},
            # Databases
            "SQL": {"aliases": ["sql"]},
            "MySQL": {"aliases": ["mysql"]},
            "PostgreSQL": {"aliases": ["postgresql", "postgres", "postgre sql"]},
            "MongoDB": {"aliases": ["mongodb", "mongo db"]},
            "Redis": {"aliases": ["redis"]},
            "Oracle": {"aliases": ["oracle", "oracle db", "oracle database"]},
            "SQLite": {"aliases": ["sqlite", "sqlite3"]},
            "Cassandra": {"aliases": ["cassandra", "apache cassandra"]},
            "DynamoDB": {"aliases": ["dynamodb", "amazon dynamodb", "aws dynamodb"]},
            "Elasticsearch": {"aliases": ["elasticsearch", "elastic search"]},
            "Snowflake": {"aliases": ["snowflake"]},
            "BigQuery": {"aliases": ["bigquery", "google bigquery"]},
            "Redshift": {"aliases": ["redshift", "amazon redshift", "aws redshift"]},
            # Cloud
            "AWS": {"aliases": ["aws", "amazon web services"]},
            "Azure": {"aliases": ["azure", "microsoft azure"]},
            "Google Cloud": {
                "aliases": [
                    "gcp",
                    "google cloud platform",
                    "google cloud",
                    "google cloud plaform",
                ]
            },
            # DevOps / Infra
            "Docker": {"aliases": ["docker"]},
            "Kubernetes": {"aliases": ["kubernetes", "k8s"]},
            "Jenkins": {"aliases": ["jenkins"]},
            "GitHub Actions": {"aliases": ["github actions", "gh actions"]},
            "GitHub": {"aliases": ["github"]},
            "GitLab": {"aliases": ["gitlab"]},
            "Git": {"aliases": ["git"]},
            "Terraform": {"aliases": ["terraform", "tf"]},
            "Ansible": {"aliases": ["ansible"]},
            "Pulumi": {"aliases": ["pulumi"]},
            "Linux": {"aliases": ["linux"]},
            "Bash": {
                "aliases": ["bash", "bash scripting", "shell scripting", "sh", "zsh"]
            },
            "Nginx": {"aliases": ["nginx"]},
            "Apache HTTP": {"aliases": ["apache", "apache httpd", "httpd"]},
            "Prometheus": {"aliases": ["prometheus"]},
            "Grafana": {"aliases": ["grafana"]},
            "Datadog": {"aliases": ["datadog"]},
            "New Relic": {"aliases": ["new relic"]},
            "Sentry": {"aliases": ["sentry"]},
            # Data Engineering
            "Pandas": {"aliases": ["pandas"]},
            "NumPy": {"aliases": ["numpy", "num py"]},
            "Apache Spark": {"aliases": ["spark", "apache spark", "pyspark"]},
            "Hadoop": {"aliases": ["hadoop"]},
            "Airflow": {"aliases": ["airflow", "apache airflow"]},
            "Kafka": {"aliases": ["kafka", "apache kafka"]},
            "ETL": {"aliases": ["etl", "elt"]},
            "Data Warehouse": {
                "aliases": ["data warehouse", "data warehousing", "dwh"]
            },
            "dbt": {"aliases": ["dbt", "data build tool"]},
            "Apache Beam": {"aliases": ["beam", "apache beam"]},
            # AI / ML
            "Machine Learning": {"aliases": ["machine learning", "ml"]},
            "Deep Learning": {"aliases": ["deep learning", "dl"]},
            "TensorFlow": {"aliases": ["tensorflow", "tf"]},
            "PyTorch": {"aliases": ["pytorch", "torch"]},
            "Scikit-Learn": {"aliases": ["scikit-learn", "sklearn", "scikit learn"]},
            "NLP": {"aliases": ["nlp", "natural language processing"]},
            "LLM": {
                "aliases": ["llm", "large language model", "large language models"]
            },
            "Generative AI": {"aliases": ["generative ai", "genai", "gen ai"]},
            "OpenAI": {"aliases": ["openai", "openai api", "openai apis", "open ai"]},
            "Hugging Face": {
                "aliases": ["huggingface", "hugging face", "transformers"]
            },
            "LangChain": {"aliases": ["langchain"]},
            "Ray": {"aliases": ["ray", "ray tune", "ray serve"]},
            # Testing / QA
            "PyTest": {"aliases": ["pytest", "py test"]},
            "JUnit": {"aliases": ["junit", "j unit"]},
            "Selenium": {"aliases": ["selenium", "selenium webdriver", "webdriver"]},
            "Cypress": {"aliases": ["cypress"]},
            "Playwright": {"aliases": ["playwright"]},
            # BI / Analytics / Tools
            "Tableau": {"aliases": ["tableau"]},
            "Power BI": {"aliases": ["power bi", "pbi"]},
            "Looker": {"aliases": ["looker", "looker studio", "data studio"]},
            "Jira": {"aliases": ["jira"]},
            "Confluence": {"aliases": ["confluence"]},
            # Mobile
            "Android": {"aliases": ["android", "kotlin android"]},
            "iOS": {"aliases": ["ios", "swift ios", "objective-c", "objective c"]},
            "React Native": {"aliases": ["react native"]},
            "Flutter": {"aliases": ["flutter", "dart flutter", "dart"]},
            # Other frequently appearing skills/keywords
            "Microservices": {
                "aliases": ["microservices", "micro-service", "micro services"]
            },
            "REST": {"aliases": ["rest", "restful", "rest api", "restful api"]},
            "gRPC": {"aliases": ["grpc"]},
            "CI/CD": {
                "aliases": [
                    "ci/cd",
                    "cicd",
                    "continuous integration",
                    "continuous delivery",
                    "continuous deployment",
                ]
            },
            "TDD": {
                "aliases": ["tdd", "test driven development", "test-driven development"]
            },
            "OOP": {
                "aliases": [
                    "oop",
                    "object oriented programming",
                    "object-oriented programming",
                ]
            },
            "Design Patterns": {"aliases": ["design patterns"]},
            "Security": {
                "aliases": ["security", "appsec", "application security", "owasp"]
            },
            # Roles/Soft skills (optional — enable if you want them counted as "skills")
            # "Project Management": {"aliases": ["project management", "pm"]},
            # "Agile": {"aliases": ["agile", "scrum", "kanban"]},
        }

    def _compile_patterns(
        self, alias_to_canonical: Dict[str, str]
    ) -> List[Tuple[re.Pattern, str]]:
        """
        Compile regex patterns for each alias with careful boundaries:
        - Prefer phrase-first by sorting aliases by length (desc)
        - Accept separators like spaces, hyphens, slashes, dots inside phrases
        - Use case-insensitive matching
        """
        items = sorted(
            alias_to_canonical.items(), key=lambda kv: len(kv[0]), reverse=True
        )
        compiled = []
        for alias_norm, canonical in items:
            if not alias_norm:
                continue
            # Turn alias into a pattern that tolerates separators between tokens
            # Example: "google cloud platform" -> r'\bgoogle[\s\-/\.]*cloud[\s\-/\.]*platform\b'
            tokens = re.split(r"[ \-/_\.]+", alias_norm)
            tokens = [re.escape(t) for t in tokens if t]
            if not tokens:
                continue
            inner = r"[\s\-/\.]*".join(tokens)
            # Boundaries: start boundary (^|[^A-Za-z0-9+#.]) and end boundary
            # to avoid matching inside larger tokens, while allowing C++, C#, Node.js
            pattern = rf"(?<![A-Za-z0-9\+\#\.]){inner}(?![A-Za-z0-9\+\#\.])"
            try:
                compiled.append((re.compile(pattern, flags=re.IGNORECASE), canonical))
            except re.error:
                # Fallback to a simpler word-boundary pattern if needed
                simple = r"\b" + re.escape(alias_norm) + r"\b"
                compiled.append((re.compile(simple, flags=re.IGNORECASE), canonical))
        return compiled

    def extract_skills(self, text: str) -> List[str]:
        """
        Extract normalized skills from free text using phrase-first exact matching.
        Optionally apply fuzzy and/or NER backfill if enabled in constructor.
        """
        if not text:
            return []

        # Two normalized variants: one raw-lower/diacritics-stripped, one punctuation-light
        norm = normalize_text(text)
        norm_loose = strip_punct_keep_dots(norm)

        found: Set[str] = set()

        # Exact phrase-first matches
        for pat, canonical in self._compiled_patterns:
            if pat.search(norm) or pat.search(norm_loose):
                found.add(canonical)

        # Optional: Fuzzy catch for minor typos, against aliases not already matched
        if self.enable_fuzzy and self._all_aliases:
            hay = norm_loose
            # Heuristic: scan tokens and short n-grams up to length 4 for fuzzy comparison
            tokens = hay.split()
            grams = set()
            for n in range(1, 5):
                for i in range(len(tokens) - n + 1):
                    grams.add(" ".join(tokens[i : i + n]))
            # Compare grams to alias list
            # Use process.extract to get top candidates, add those above threshold
            for gram in grams:
                matches = process.extract(
                    gram, self._all_aliases, scorer=fuzz.token_set_ratio, limit=2
                )
                for alias, score, _ in matches:
                    if score >= self.fuzzy_threshold:
                        canonical = self.alias_to_canonical.get(alias)
                        if canonical:
                            found.add(canonical)

        # Optional: NER backfill — capture ORG/PRODUCT/WORK_OF_ART that are known tools if present
        if self.enable_ner and self._nlp:
            doc = self._nlp(text)
            ner_terms = {
                normalize_text(ent.text)
                for ent in doc.ents
                if ent.label_ in {"ORG", "PRODUCT", "WORK_OF_ART"}
            }
            for term in ner_terms:
                if term in self.alias_to_canonical:
                    found.add(self.alias_to_canonical[term])

        return sorted(found)

    def extract_job_skills(self, job: Dict) -> List[str]:
        """
        Extract from Arbeitnow job dict:
        - tags (exact match via aliases)
        - title
        - description
        """
        found: Set[str] = set()

        # Tags — map each tag through normalization and alias table
        for tag in job.get("tags", []) or []:
            tnorm = normalize_text(str(tag))
            if tnorm in self.alias_to_canonical:
                found.add(self.alias_to_canonical[tnorm])
            else:
                # Try a simple word-boundary search using compiled patterns
                for pat, canonical in self._compiled_patterns:
                    if pat.fullmatch(tnorm) or pat.search(tnorm):
                        found.add(canonical)

        # Title and description
        found.update(self.extract_skills(job.get("title", "") or ""))
        found.update(self.extract_skills(job.get("description", "") or ""))

        return sorted(found)


# Simple convenience functions for your existing code style:


# Backward-compatible TECH_SKILLS-like flat alias map (if you still need it):
def create_skill_dictionary() -> Dict[str, str]:
    """
    Flatter alias -> canonical map, built from the ontology above.
    Useful if you want to export or debug the alias coverage.
    """
    extractor = SkillExtractor(enable_fuzzy=False, enable_ner=False)
    return dict(extractor.alias_to_canonical)


def extract_skills(text: str) -> List[str]:
    """
    Convenience wrapper using default extractor (no fuzzy/NER by default).
    """
    return SkillExtractor(enable_fuzzy=False, enable_ner=False).extract_skills(text)


def extract_job_skills(job: Dict) -> List[str]:
    """
    Convenience wrapper for Arbeitnow job dicts.
    """
    return SkillExtractor(enable_fuzzy=False, enable_ner=False).extract_job_skills(job)


# Example local test
if __name__ == "__main__":
    description = """
    Senior Full Stack AI Engineer

    We are looking for an experienced engineer to build scalable AI-powered applications. 
    The ideal candidate should have strong experience in Python, TypeScript, React.js, Next.js, Node.js, FastAPI, and PostgreSQL.

    You will design and maintain cloud-native microservices deployed on AWS and Kubernetes, using Docker, Terraform, and GitHub Actions for CI/CD automation.

    The candidate should be comfortable working with Redis, MongoDB, Apache Spark, Airflow, and data warehouse technologies. 
    Experience building ETL pipelines and large-scale data processing systems is highly desirable.

    Knowledge of machine learning, deep learning, NLP, LLMs, OpenAI APIs, PyTorch, TensorFlow, and Scikit-Learn is preferred.

    Additional experience with Linux, Bash scripting, Git, Jira, Tableau, and Power BI will be considered a plus.

    Nice to have:
    - Go or Rust
    - Azure or Google Cloud Platform (GCP)
    - Selenium and PyTest for automated testing
    - Spring Boot based backend services

    Requirements:
    5+ years of software development experience in modern web technologies, distributed systems, cloud computing, and AI-driven products.
    """

    print(extract_skills(description))
