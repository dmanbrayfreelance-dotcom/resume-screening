"""
25 Benchmark Industry Job Descriptions Seeder
Populates standard multi-discipline job profiles into the database (MongoDB Atlas or Fallback Store)
covering AI/ML, Software Engineering, Data Science, Cloud/DevOps, Cybersecurity, and Product/QA.
"""

from typing import Any, Dict, List

BENCHMARK_25_JDS: List[Dict[str, Any]] = [
    # ── AI / ML Domain (1-5) ──
    {
        "job_id": "job-bench-001",
        "title": "Senior AI / ML Research Engineer",
        "department": "AI Research & Labs",
        "location": "San Francisco, CA / Remote",
        "employment_type": "Full-time",
        "experience_years_min": 4.0,
        "education_level": "Master's or Ph.D. in Computer Science, AI, or equivalent",
        "description": "Lead research and development of multimodal deep learning models, Whisper speech-to-text integration, and transformer architectures.",
        "responsibilities": [
            "Design and fine-tune multimodal LLMs and ASR speech processing pipelines",
            "Optimize inference latency using TensorRT, ONNX Runtime, and quantization",
            "Collaborate with product teams to evaluate candidate speech prosody and claim credibility",
        ],
        "required_skills": ["Python", "PyTorch", "Whisper", "Transformers", "FastAPI", "NLP"],
        "preferred_skills": ["Docker", "Kubernetes", "CUDA", "TensorRT", "Hugging Face"],
        "scoring_weights": {
            "skill_match": 0.40,
            "experience_match": 0.25,
            "multimodal_presentation": 0.15,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
    {
        "job_id": "job-bench-002",
        "title": "Lead Multimodal Deep Learning Architect",
        "department": "Core Intelligence",
        "location": "New York, NY / Hybrid",
        "employment_type": "Full-time",
        "experience_years_min": 6.0,
        "education_level": "Master's Degree in Machine Learning or related field",
        "description": "Architect high-throughput cross-modal neural networks fusing vision, audio acoustics, and text representations.",
        "responsibilities": [
            "Architect multimodal fusion representations bridging acoustic prosody and semantic text",
            "Establish algorithmic fairness and debiasing benchmarks across screening runs",
            "Mentor junior ML engineers and publish internal reproducible model architectures",
        ],
        "required_skills": ["Python", "PyTorch", "Deep Learning", "Computer Vision", "NLP", "System Design"],
        "preferred_skills": ["OpenCV", "Whisper", "C++", "Triton Server", "MLOps"],
        "scoring_weights": {
            "skill_match": 0.35,
            "experience_match": 0.30,
            "multimodal_presentation": 0.15,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
    {
        "job_id": "job-bench-003",
        "title": "NLP & Conversational AI Engineer",
        "department": "Language Technologies",
        "location": "Seattle, WA / Remote",
        "employment_type": "Full-time",
        "experience_years_min": 3.0,
        "education_level": "Bachelor's or Master's in CS / Linguistics",
        "description": "Develop domain-adapted BERT sentiment models and RAG knowledge retrieval for talent intelligence workflows.",
        "responsibilities": [
            "Fine-tune multilingual BERT models for sentiment polarity and vocal confidence analysis",
            "Build semantic taxonomy matching algorithms mapping resume achievements to job competencies",
            "Implement vector retrieval pipelines with Pinecone and FAISS",
        ],
        "required_skills": ["Python", "NLP", "BERT", "Transformers", "FastAPI", "Vector Embeddings"],
        "preferred_skills": ["LangChain", "LlamaIndex", "MongoDB", "Scikit-Learn"],
        "scoring_weights": {
            "skill_match": 0.35,
            "experience_match": 0.25,
            "multimodal_presentation": 0.15,
            "sentiment_engagement": 0.15,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
    {
        "job_id": "job-bench-004",
        "title": "Computer Vision Systems Engineer",
        "department": "Vision & Sensory AI",
        "location": "Austin, TX / Hybrid",
        "employment_type": "Full-time",
        "experience_years_min": 3.5,
        "education_level": "Bachelor's in Computer Engineering / CS",
        "description": "Build real-time video frame processing pipelines for non-verbal engagement and head-pose telemetry.",
        "responsibilities": [
            "Develop face tracking, movement stability, and eye-contact estimation routines",
            "Deploy low-latency video chunking and frame sampling microservices",
            "Benchmark vision metrics against demographic fairness standards",
        ],
        "required_skills": ["Python", "OpenCV", "Computer Vision", "PyTorch", "C++"],
        "preferred_skills": ["FFmpeg", "MediaPipe", "CUDA", "Docker", "REST APIs"],
        "scoring_weights": {
            "skill_match": 0.35,
            "experience_match": 0.25,
            "multimodal_presentation": 0.20,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
    {
        "job_id": "job-bench-005",
        "title": "MLOps & Foundation Model Deployer",
        "department": "AI Platform Engineering",
        "location": "Remote / San Francisco",
        "employment_type": "Full-time",
        "experience_years_min": 4.0,
        "education_level": "Bachelor's Degree in Software Engineering or CS",
        "description": "Construct scalable CI/CD pipelines, model monitoring, and automated retraining loops for screening AI.",
        "responsibilities": [
            "Package Whisper, sentence-transformers, and BERT pipelines into containerized microservices",
            "Manage Prometheus/Grafana latency, memory, and model drift telemetry",
            "Maintain high availability of inference APIs on AWS and Kubernetes",
        ],
        "required_skills": ["Python", "Docker", "Kubernetes", "MLOps", "CI/CD", "FastAPI"],
        "preferred_skills": ["AWS", "Prometheus", "Terraform", "GitLab CI", "ONNX Runtime"],
        "scoring_weights": {
            "skill_match": 0.40,
            "experience_match": 0.30,
            "multimodal_presentation": 0.10,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },

    # ── Full-Stack & Software Engineering (6-10) ──
    {
        "job_id": "job-bench-006",
        "title": "Senior Full-Stack AI Developer",
        "department": "Talent Intelligence Studio",
        "location": "Remote / Hybrid",
        "employment_type": "Full-time",
        "experience_years_min": 4.0,
        "education_level": "Bachelor's in Computer Science or Equivalent",
        "description": "Engineer interactive screening interfaces, candidate scorecards, and high-performance FastAPI backends.",
        "responsibilities": [
            "Build reactive React/TypeScript dashboards with Recharts data visualizers",
            "Implement multipart file upload pipelines handling large MP4 video resumes and PDFs",
            "Optimize MongoDB queries and client-side caching for instant candidate drawer loads",
        ],
        "required_skills": ["React", "TypeScript", "Python", "FastAPI", "MongoDB", "Tailwind CSS"],
        "preferred_skills": ["Docker", "Node.js", "REST APIs", "Whisper", "Vite"],
        "scoring_weights": {
            "skill_match": 0.45,
            "experience_match": 0.25,
            "multimodal_presentation": 0.10,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
    {
        "job_id": "job-bench-007",
        "title": "Lead Backend Python / FastAPI Architect",
        "department": "Platform Services",
        "location": "Chicago, IL / Hybrid",
        "employment_type": "Full-time",
        "experience_years_min": 5.0,
        "education_level": "Bachelor's or Master's in Computer Science",
        "description": "Architect asynchronous distributed backend services handling heavy NLP computation and database persistence.",
        "responsibilities": [
            "Design clean architecture async REST APIs with Pydantic v2 validation",
            "Implement resilient MongoDB Atlas connection pooling with automatic local JSON fallback",
            "Enforce strict algorithmic fairness and non-adverse action API compliance",
        ],
        "required_skills": ["Python", "FastAPI", "MongoDB", "PostgreSQL", "Docker", "System Design"],
        "preferred_skills": ["Redis", "RabbitMQ", "Pytest", "CI/CD", "AWS"],
        "scoring_weights": {
            "skill_match": 0.40,
            "experience_match": 0.30,
            "multimodal_presentation": 0.10,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
    {
        "job_id": "job-bench-008",
        "title": "Frontend React / TypeScript UI Specialist",
        "department": "Design & Frontend Engineering",
        "location": "Remote / New York",
        "employment_type": "Full-time",
        "experience_years_min": 3.0,
        "education_level": "Bachelor's in Design, CS, or Web Engineering",
        "description": "Craft glassmorphic, accessible, and high-performance talent screening and rubric adjustment web applications.",
        "responsibilities": [
            "Develop smooth animations, sliders, and radar charts for multi-factor candidate ranking",
            "Implement WCAG 2.1 accessibility and responsive mobile layouts with Tailwind CSS",
            "Integrate dynamic client API state with optimistic UI updates and error boundaries",
        ],
        "required_skills": ["React", "TypeScript", "Tailwind CSS", "HTML5", "CSS3", "JavaScript"],
        "preferred_skills": ["Vite", "Next.js", "Redux", "REST APIs", "GraphQL"],
        "scoring_weights": {
            "skill_match": 0.40,
            "experience_match": 0.25,
            "multimodal_presentation": 0.15,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
    {
        "job_id": "job-bench-009",
        "title": "Distributed Systems Core Engineer",
        "department": "Infrastructure & Core Platform",
        "location": "Boston, MA / Remote",
        "employment_type": "Full-time",
        "experience_years_min": 4.5,
        "education_level": "Bachelor's in CS / Distributed Systems",
        "description": "Engineer low-latency worker queues, parallel multimodal batch scoring, and distributed event logs.",
        "responsibilities": [
            "Build message broker pipelines for asynchronous media processing and model batching",
            "Optimize concurrency and memory overhead when loading dense embedding models",
            "Ensure sub-second leaderboard re-ranking across thousands of candidate profiles",
        ],
        "required_skills": ["Go", "Python", "Distributed Systems", "Kafka", "Docker", "Linux"],
        "preferred_skills": ["Kubernetes", "gRPC", "Redis", "PostgreSQL", "C++"],
        "scoring_weights": {
            "skill_match": 0.35,
            "experience_match": 0.35,
            "multimodal_presentation": 0.10,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
    {
        "job_id": "job-bench-010",
        "title": "Mobile Application Engineer (React Native / iOS)",
        "department": "Mobile Products",
        "location": "Los Angeles, CA / Hybrid",
        "employment_type": "Full-time",
        "experience_years_min": 3.0,
        "education_level": "Bachelor's Degree in Software Engineering",
        "description": "Build cross-platform mobile video interview recording and candidate screening apps.",
        "responsibilities": [
            "Implement high-fidelity native camera and microphone capture for mobile video interviews",
            "Integrate on-device audio compression and resilient chunked network uploads",
            "Ensure smooth recruiter review workflows on iOS and Android devices",
        ],
        "required_skills": ["React", "JavaScript", "TypeScript", "REST APIs", "HTML5"],
        "preferred_skills": ["Swift", "Kotlin", "Docker", "FastAPI", "Tailwind CSS"],
        "scoring_weights": {
            "skill_match": 0.40,
            "experience_match": 0.25,
            "multimodal_presentation": 0.15,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },

    # ── Data Science & Big Data (11-14) ──
    {
        "job_id": "job-bench-011",
        "title": "Principal Data Scientist",
        "department": "Advanced Analytics",
        "location": "Remote / Seattle",
        "employment_type": "Full-time",
        "experience_years_min": 6.0,
        "education_level": "Ph.D. or Master's in Statistics, Data Science, or CS",
        "description": "Formulate predictive hiring fit models, calibration drift metrics, and four-fifths adverse impact statistical audits.",
        "responsibilities": [
            "Audit candidate score spreads, variance distributions, and demographic proxy neutralizations",
            "Develop explainable hybrid score synthesis balancing skill overlap and speaking confidence",
            "Publish quarterly algorithmic fairness and statistical compliance audit reports",
        ],
        "required_skills": ["Python", "Data Science", "Machine Learning", "Pandas", "NumPy", "Scikit-Learn"],
        "preferred_skills": ["NLP", "PyTorch", "R", "SQL", "Deep Learning"],
        "scoring_weights": {
            "skill_match": 0.35,
            "experience_match": 0.30,
            "multimodal_presentation": 0.15,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
    {
        "job_id": "job-bench-012",
        "title": "Big Data & Real-Time Streaming Engineer",
        "department": "Data Platform",
        "location": "Atlanta, GA / Hybrid",
        "employment_type": "Full-time",
        "experience_years_min": 4.0,
        "education_level": "Bachelor's in CS / Information Systems",
        "description": "Construct high-volume event ingestion pipelines processing resumes, transcripts, and telemetry data.",
        "responsibilities": [
            "Build ETL/ELT pipelines ingesting unstructured multimodal evaluation records into data lakes",
            "Implement real-time analytics aggregation for candidate search indexing",
            "Maintain database partitioning and query efficiency across millions of evaluations",
        ],
        "required_skills": ["Python", "SQL", "ETL", "Kafka", "Data Pipelines", "MongoDB"],
        "preferred_skills": ["PostgreSQL", "Snowflake", "BigQuery", "Docker", "AWS"],
        "scoring_weights": {
            "skill_match": 0.40,
            "experience_match": 0.30,
            "multimodal_presentation": 0.10,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
    {
        "job_id": "job-bench-013",
        "title": "Business Intelligence & Analytics Lead",
        "department": "Talent Operations",
        "location": "Denver, CO / Remote",
        "employment_type": "Full-time",
        "experience_years_min": 3.5,
        "education_level": "Bachelor's in Business Analytics, Statistics, or CS",
        "description": "Create executive reporting dashboards visualizing candidate pipeline throughput, skill gap distributions, and recruiter decision times.",
        "responsibilities": [
            "Build automated CSV/JSON reporting feeds for HR leadership and enterprise ATS integrations",
            "Analyze threshold sensitivity impact on candidate pool selection volumes",
            "Partner with recruiting leads to optimize scoring rubric weights for key departments",
        ],
        "required_skills": ["SQL", "Python", "Data Pipelines", "REST APIs", "Pandas"],
        "preferred_skills": ["FastAPI", "MongoDB", "PostgreSQL", "React", "Docker"],
        "scoring_weights": {
            "skill_match": 0.35,
            "experience_match": 0.25,
            "multimodal_presentation": 0.20,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
    {
        "job_id": "job-bench-014",
        "title": "Data Infrastructure Platform Architect",
        "department": "Enterprise Cloud Data",
        "location": "Remote / San Jose, CA",
        "employment_type": "Full-time",
        "experience_years_min": 5.0,
        "education_level": "Bachelor's or Master's in Computer Engineering",
        "description": "Design secure cloud storage, vector database indexes, and database encryption architectures.",
        "responsibilities": [
            "Architect TLS-secured MongoDB Atlas clusters with automatic disaster recovery failover",
            "Design vector database indexing strategies (Pinecone, ChromaDB) for instant semantic candidate retrieval",
            "Enforce GDPR and California privacy scrubbers on stored candidate PII",
        ],
        "required_skills": ["MongoDB", "PostgreSQL", "System Design", "AWS", "Python", "Docker"],
        "preferred_skills": ["Kubernetes", "Redis", "Terraform", "CI/CD", "Vector Embeddings"],
        "scoring_weights": {
            "skill_match": 0.40,
            "experience_match": 0.30,
            "multimodal_presentation": 0.10,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },

    # ── Cloud, DevOps & SRE (15-17) ──
    {
        "job_id": "job-bench-015",
        "title": "Senior DevOps & Infrastructure Engineer",
        "department": "Cloud Platform Operations",
        "location": "Remote / Dallas, TX",
        "employment_type": "Full-time",
        "experience_years_min": 4.0,
        "education_level": "Bachelor's in Computer Science or IT",
        "description": "Deploy, scale, and maintain multi-cloud production clusters running multimodal screening microservices.",
        "responsibilities": [
            "Automate infrastructure provisioning using Terraform and GitHub Actions CI/CD",
            "Maintain containerized deployments of FastAPI, Whisper workers, and React frontends on Render/AWS",
            "Implement zero-downtime rolling updates and health check monitors",
        ],
        "required_skills": ["Docker", "Kubernetes", "CI/CD", "AWS", "Linux", "Terraform"],
        "preferred_skills": ["Python", "FastAPI", "Prometheus", "Nginx", "GitHub Actions"],
        "scoring_weights": {
            "skill_match": 0.45,
            "experience_match": 0.25,
            "multimodal_presentation": 0.10,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
    {
        "job_id": "job-bench-016",
        "title": "Site Reliability Engineer (SRE - Kubernetes)",
        "department": "Platform Reliability",
        "location": "Salt Lake City, UT / Hybrid",
        "employment_type": "Full-time",
        "experience_years_min": 3.5,
        "education_level": "Bachelor's in CS / Systems Administration",
        "description": "Ensure 99.99% service availability, manage autoscaling for heavy GPU/CPU inference, and optimize latency.",
        "responsibilities": [
            "Configure Kubernetes horizontal pod autoscalers (HPA) responding to spikes in candidate video uploads",
            "Establish Service Level Objectives (SLOs) and automated rollback triggers",
            "Optimize container images to reduce build times and memory footprints",
        ],
        "required_skills": ["Kubernetes", "Docker", "Linux", "Prometheus", "CI/CD", "Python"],
        "preferred_skills": ["Grafana", "AWS", "GCP", "Bash", "Terraform"],
        "scoring_weights": {
            "skill_match": 0.40,
            "experience_match": 0.30,
            "multimodal_presentation": 0.10,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
    {
        "job_id": "job-bench-017",
        "title": "Cloud Solutions Architect (AWS / GCP Multi-Cloud)",
        "department": "Enterprise Architecture",
        "location": "Remote / Washington, D.C.",
        "employment_type": "Full-time",
        "experience_years_min": 6.0,
        "education_level": "Bachelor's or Master's in Computer Engineering",
        "description": "Design resilient multi-cloud architectures accommodating high-throughput enterprise hiring deployments.",
        "responsibilities": [
            "Architect hybrid cloud topologies connecting on-premise ATS with cloud AI screening microservices",
            "Design cost-efficient serverless and spot instance architectures for batch resume parsing",
            "Enforce security perimeters, IAM roles, and secret management across AWS and GCP",
        ],
        "required_skills": ["AWS", "GCP", "System Design", "Docker", "Kubernetes", "Terraform"],
        "preferred_skills": ["Python", "Microservices", "CI/CD", "Linux", "PostgreSQL"],
        "scoring_weights": {
            "skill_match": 0.35,
            "experience_match": 0.35,
            "multimodal_presentation": 0.10,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },

    # ── Cybersecurity & Governance (18-20) ──
    {
        "job_id": "job-bench-018",
        "title": "Cloud Security & DevSecOps Engineer",
        "department": "Information Security",
        "location": "Remote / Boston, MA",
        "employment_type": "Full-time",
        "experience_years_min": 3.5,
        "education_level": "Bachelor's in Cybersecurity, CS, or IT Security",
        "description": "Safeguard candidate media uploads, sanitize PII, and secure container images across build cycles.",
        "responsibilities": [
            "Integrate automated vulnerability scanning (SAST/DAST) into CI/CD deployment pipelines",
            "Implement end-to-end encryption for candidate video interview storage and Whisper transcripts",
            "Audit PII anonymization algorithms to ensure zero demographic data leakage",
        ],
        "required_skills": ["CI/CD", "Docker", "Linux", "AWS", "Python", "Kubernetes"],
        "preferred_skills": ["Terraform", "PostgreSQL", "MongoDB", "REST APIs", "GitHub Actions"],
        "scoring_weights": {
            "skill_match": 0.40,
            "experience_match": 0.25,
            "multimodal_presentation": 0.15,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
    {
        "job_id": "job-bench-019",
        "title": "Cyber Threat Intelligence & SOC Analyst",
        "department": "Security Operations Center",
        "location": "Phoenix, AZ / Hybrid",
        "employment_type": "Full-time",
        "experience_years_min": 2.5,
        "education_level": "Bachelor's in Cybersecurity or Information Assurance",
        "description": "Monitor system endpoints, inspect unusual upload anomalies, and defend platform infrastructure.",
        "responsibilities": [
            "Investigate anomalous file submissions and prevent malicious script injection via resume uploads",
            "Monitor authentication logs, rate limits, and cross-origin resource requests",
            "Conduct quarterly incident response drills and penetration testing audits",
        ],
        "required_skills": ["Linux", "Python", "REST APIs", "SQL", "Bash"],
        "preferred_skills": ["Docker", "AWS", "Prometheus", "CI/CD", "FastAPI"],
        "scoring_weights": {
            "skill_match": 0.35,
            "experience_match": 0.25,
            "multimodal_presentation": 0.15,
            "sentiment_engagement": 0.15,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
    {
        "job_id": "job-bench-020",
        "title": "Application Security Specialist & Pentester",
        "department": "Security Engineering",
        "location": "San Diego, CA / Remote",
        "employment_type": "Full-time",
        "experience_years_min": 4.0,
        "education_level": "Bachelor's in Computer Science or InfoSec",
        "description": "Conduct deep application penetration testing, API vulnerability assessments, and secure code audits.",
        "responsibilities": [
            "Perform rigorous penetration tests against FastAPI REST endpoints and React client assets",
            "Audit file parsing libraries (PyMuPDF, python-docx, moviepy) against buffer overflow exploits",
            "Design secure API key authentication and role-based access controls for recruiter teams",
        ],
        "required_skills": ["Python", "FastAPI", "Linux", "REST APIs", "Docker", "System Design"],
        "preferred_skills": ["React", "JavaScript", "AWS", "PostgreSQL", "C++"],
        "scoring_weights": {
            "skill_match": 0.40,
            "experience_match": 0.30,
            "multimodal_presentation": 0.10,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },

    # ── Product, QA & Specialized Roles (21-25) ──
    {
        "job_id": "job-bench-021",
        "title": "Principal Technical Product Manager (AI Platforms)",
        "department": "Product Management",
        "location": "Remote / San Francisco",
        "employment_type": "Full-time",
        "experience_years_min": 5.0,
        "education_level": "Bachelor's or Master's in CS, Business, or Engineering",
        "description": "Define product strategy for talent intelligence studios, explainable AI scorecards, and recruiter workflows.",
        "responsibilities": [
            "Define functional requirements for cross-modal claim verification and skill-gap explainability",
            "Gather feedback from talent acquisition leads to optimize hiring calibration metrics",
            "Oversee roadmap execution across frontend, ML research, and backend engineering squads",
        ],
        "required_skills": ["System Design", "Agile", "Scrum", "REST APIs", "Data Science"],
        "preferred_skills": ["Python", "React", "Machine Learning", "FastAPI", "MongoDB"],
        "scoring_weights": {
            "skill_match": 0.30,
            "experience_match": 0.30,
            "multimodal_presentation": 0.20,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
    {
        "job_id": "job-bench-022",
        "title": "QA Automation Lead & SDET Engineer",
        "department": "Quality Engineering",
        "location": "Minneapolis, MN / Remote",
        "employment_type": "Full-time",
        "experience_years_min": 3.5,
        "education_level": "Bachelor's in Software Engineering / CS",
        "description": "Develop automated end-to-end integration tests validating resume parsing, multimodal scoring, and API reliability.",
        "responsibilities": [
            "Design Pytest test suites covering edge cases in PDF/DOCX ingestion and Whisper transcription fallback",
            "Build automated regression checks for leaderboard sorting and fairness calibration math",
            "Establish continuous testing gates in GitHub Actions prior to staging deployments",
        ],
        "required_skills": ["Python", "FastAPI", "Docker", "CI/CD", "REST APIs", "Linux"],
        "preferred_skills": ["React", "TypeScript", "MongoDB", "PostgreSQL", "PyTorch"],
        "scoring_weights": {
            "skill_match": 0.40,
            "experience_match": 0.25,
            "multimodal_presentation": 0.15,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
    {
        "job_id": "job-bench-023",
        "title": "Database Administrator (MongoDB & PostgreSQL)",
        "department": "Database Operations",
        "location": "Columbus, OH / Remote",
        "employment_type": "Full-time",
        "experience_years_min": 4.0,
        "education_level": "Bachelor's in Information Technology or CS",
        "description": "Maintain enterprise database performance, index optimization, backup policies, and multi-region replication.",
        "responsibilities": [
            "Tune compound indexes on candidates and evaluation collections for sub-10ms query execution",
            "Manage automated backup snapshots and point-in-time recovery on MongoDB Atlas and PostgreSQL",
            "Design schema migration strategies accommodating evolving scoring models",
        ],
        "required_skills": ["MongoDB", "PostgreSQL", "SQL", "Linux", "Docker"],
        "preferred_skills": ["Redis", "AWS", "Python", "System Design", "Terraform"],
        "scoring_weights": {
            "skill_match": 0.45,
            "experience_match": 0.25,
            "multimodal_presentation": 0.10,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
    {
        "job_id": "job-bench-024",
        "title": "Generative AI Application Engineer",
        "department": "Next-Gen AI Applications",
        "location": "Remote / Seattle, WA",
        "employment_type": "Full-time",
        "experience_years_min": 3.0,
        "education_level": "Bachelor's in Computer Science or AI",
        "description": "Construct autonomous interview question generators, resume claim cross-examiners, and RAG agents.",
        "responsibilities": [
            "Develop intelligent candidate interview probing agents using LangChain and transformer embeddings",
            "Fine-tune prompt chains generating structured recruiter executive summaries",
            "Implement guardrails preventing hallucinated skill matching or biased candidate ratings",
        ],
        "required_skills": ["Python", "Generative AI", "NLP", "FastAPI", "Transformers", "Prompt Engineering"],
        "preferred_skills": ["PyTorch", "LangChain", "Vector Embeddings", "Docker", "React"],
        "scoring_weights": {
            "skill_match": 0.35,
            "experience_match": 0.25,
            "multimodal_presentation": 0.15,
            "sentiment_engagement": 0.15,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
    {
        "job_id": "job-bench-025",
        "title": "Embedded Systems & Edge AI Engineer",
        "department": "Edge Computing",
        "location": "Portland, OR / Hybrid",
        "employment_type": "Full-time",
        "experience_years_min": 3.5,
        "education_level": "Bachelor's in Electrical Engineering or Computer Engineering",
        "description": "Port speech and vision neural models to edge hardware with strict latency and memory constraints.",
        "responsibilities": [
            "Quantize Whisper and acoustic models for on-device integer inference via ONNX Runtime",
            "Optimize memory usage and thermals on edge appliances running real-time speech evaluation",
            "Develop C++/Python bindings for high-throughput sensor telemetry ingestion",
        ],
        "required_skills": ["C++", "Python", "Linux", "Deep Learning", "Computer Vision"],
        "preferred_skills": ["CUDA", "ONNX Runtime", "PyTorch", "Docker", "FFmpeg"],
        "scoring_weights": {
            "skill_match": 0.40,
            "experience_match": 0.30,
            "multimodal_presentation": 0.10,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.10,
        },
        "status": "open",
    },
]


async def seed_benchmark_jobs(db: Any) -> int:
    """
    Seeds the 25 benchmark Job Descriptions into the 'jobs' collection if it is currently empty.
    Returns the count of seeded jobs.
    """
    import logging
    from datetime import datetime, timezone
    from backend.app.core.database import COLLECTION_JOBS

    logger = logging.getLogger("app.data.seed_25_jds")
    jobs_col = db[COLLECTION_JOBS]

    # Check existing count
    count = await jobs_col.count_documents({})
    if count >= len(BENCHMARK_25_JDS):
        logger.info(f"Jobs collection already contains {count} profiles. Skipping seed.")
        return 0

    now_iso = datetime.now(timezone.utc).isoformat()
    seeded = 0

    for job in BENCHMARK_25_JDS:
        existing = await jobs_col.find_one({"job_id": job["job_id"]})
        if not existing:
            doc = dict(job)
            doc["created_at"] = now_iso
            doc["updated_at"] = now_iso
            await jobs_col.insert_one(doc)
            seeded += 1

    logger.info(f"Successfully seeded {seeded} benchmark Job Descriptions.")
    return seeded


if __name__ == "__main__":
    import asyncio
    import json
    from pathlib import Path

    # Save as JSON fixture as well
    out_file = Path(__file__).parent / "benchmark_25_jds.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(BENCHMARK_25_JDS, f, indent=2)
    print(f"Generated {len(BENCHMARK_25_JDS)} benchmark JDs in {out_file}")
