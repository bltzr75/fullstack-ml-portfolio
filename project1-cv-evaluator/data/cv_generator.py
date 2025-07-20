"""CV generation utilities (incorporating persona and resume builder logic)"""

import random
from typing import Dict, List, Any
from datetime import datetime


class CVGenerator:
    """Generate synthetic CVs for training"""
    
    def __init__(self):
        self.skill_pools = self._initialize_skill_pools()
        self.education_institutions = self._initialize_education()
        self.company_pools = self._initialize_companies()
        
    def generate_cv(self, domain: str, experience_level: str, quality_tier: str) -> Dict[str, Any]:
        """Generate a complete CV based on parameters"""
        
        persona = self._generate_persona(domain, experience_level, quality_tier)
        cv_text = self._generate_cv_text(persona)
        
        return {
            'cv_text': cv_text,
            'persona': persona,
            'metadata': {
                'domain': domain,
                'experience_level': experience_level,
                'quality_tier': quality_tier,
                'generated_at': datetime.now().isoformat()
            }
        }
    
    def _generate_persona(self, domain: str, experience_level: str, quality_tier: str) -> Dict[str, Any]:
        """Generate persona for CV"""
        
        return {
            'name': self._generate_name(),
            'title': self._generate_title(domain, experience_level),
            'contact': self._generate_contact(),
            'skills': self._generate_skills(domain, experience_level, quality_tier),
            'experience': self._generate_experience(domain, experience_level, quality_tier),
            'education': self._generate_education(quality_tier),
            'domain': domain,
            'experience_level': experience_level,
            'quality_tier': quality_tier
        }
    
    def _generate_cv_text(self, persona: Dict[str, Any]) -> str:
        """Convert persona to CV text"""
        
        cv_parts = []
        
        # Header
        cv_parts.append(f"Name: {persona['name']}")
        cv_parts.append(f"Title: {persona['title']}")
        cv_parts.append(f"Email: {persona['contact']['email']}")
        cv_parts.append(f"Phone: {persona['contact']['phone']}")
        cv_parts.append(f"Location: {persona['contact']['location']}")
        
        # Professional Summary
        cv_parts.append("\nPROFESSIONAL SUMMARY")
        cv_parts.append("=" * 50)
        cv_parts.append(self._generate_summary(persona))
        
        # Skills
        cv_parts.append("\nTECHNICAL SKILLS")
        cv_parts.append("=" * 50)
        for category, skills in persona['skills'].items():
            cv_parts.append(f"{category}: {skills}")
        
        # Experience
        cv_parts.append("\nPROFESSIONAL EXPERIENCE")
        cv_parts.append("=" * 50)
        for exp in persona['experience']:
            cv_parts.append(f"{exp['title']} | {exp['company']}")
            cv_parts.append(f"Duration: {exp['period']}")
            for achievement in exp['achievements']:
                cv_parts.append(f"• {achievement}")
            cv_parts.append("")
        
        # Education
        cv_parts.append("EDUCATION")
        cv_parts.append("=" * 50)
        for edu in persona['education']:
            cv_parts.append(f"{edu['degree']} - {edu['institution']} ({edu['year']})")
        
        return '\n'.join(cv_parts)
    
    def _generate_name(self) -> str:
        """Generate random name"""
        first_names = ['Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Avery']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller']
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def _generate_title(self, domain: str, experience_level: str) -> str:
        """Generate job title"""
        titles = {
            'data_science': {
                'entry': 'Data Analyst',
                'mid': 'Data Scientist',
                'senior': 'Senior Data Scientist',
                'executive': 'Head of Data Science'
            },
            'software_engineering': {
                'entry': 'Software Engineer',
                'mid': 'Senior Software Engineer',
                'senior': 'Principal Engineer',
                'executive': 'VP of Engineering'
            }
        }
        
        return titles.get(domain, titles['data_science'])[experience_level]
    
    def _generate_contact(self) -> Dict[str, str]:
        """Generate contact information"""
        return {
            'email': f"contact@{random.choice(['gmail', 'outlook', 'yahoo'])}.com",
            'phone': f"+1{random.randint(2000000000, 9999999999)}",
            'location': random.choice(['San Francisco, CA', 'New York, NY', 'Seattle, WA'])
        }
    
    def _generate_skills(self, domain: str, experience_level: str, quality_tier: str) -> Dict[str, str]:
        """Generate skills based on parameters"""
        domain_skills = self.skill_pools.get(domain, self.skill_pools['data_science'])
        
        # Number of skills based on quality
        skill_counts = {
            'excellent': random.randint(6, 8),
            'good': random.randint(4, 6),
            'average': random.randint(3, 5),
            'below_average': random.randint(2, 4)
        }
        
        skills = {}
        num_categories = skill_counts.get(quality_tier, 4)
        
        for category in list(domain_skills.keys())[:num_categories]:
            category_skills = domain_skills[category]
            selected = random.sample(category_skills, min(5, len(category_skills)))
            skills[category] = ', '.join(selected)
        
        return skills
    
    def _generate_experience(self, domain: str, experience_level: str, quality_tier: str) -> List[Dict[str, Any]]:
        """Generate work experience"""
        companies = self.company_pools[quality_tier]
        
        num_positions = {
            'entry': 1,
            'mid': 2,
            'senior': 3,
            'executive': 4
        }[experience_level]
        
        experience = []
        current_year = datetime.now().year
        
        for i in range(num_positions):
            years_ago = i * 3
            experience.append({
                'title': self._generate_title(domain, experience_level),
                'company': random.choice(companies),
                'period': f"{current_year - years_ago - 2} - {current_year - years_ago}",
                'achievements': self._generate_achievements(domain, quality_tier)
            })
        
        return experience
    
    def _generate_achievements(self, domain: str, quality_tier: str) -> List[str]:
        """Generate achievements based on quality"""
        achievement_templates = {
            'excellent': [
                "Led team of {num} developers delivering {impact}",
                "Improved {metric} by {percent}% through {method}",
                "Architected {system} handling {scale} requests/day"
            ],
            'good': [
                "Developed {feature} improving {metric}",
                "Collaborated with team to deliver {project}",
                "Implemented {technology} for {purpose}"
            ],
            'average': [
                "Worked on {project} using {technology}",
                "Participated in {activity}",
                "Assisted with {task}"
            ]
        }
        
        templates = achievement_templates.get(quality_tier, achievement_templates['average'])
        return [self._fill_template(t) for t in random.sample(templates, min(3, len(templates)))]
    
    def _fill_template(self, template: str) -> str:
        """Fill achievement template with random values"""
        replacements = {
            '{num}': str(random.randint(3, 10)),
            '{impact}': random.choice(['key features', 'critical systems', 'new products']),
            '{metric}': random.choice(['performance', 'efficiency', 'user satisfaction']),
            '{percent}': str(random.randint(20, 80)),
            '{method}': random.choice(['optimization', 'refactoring', 'new architecture']),
            '{system}': random.choice(['microservices', 'data pipeline', 'API platform']),
            '{scale}': f"{random.randint(1, 10)}M",
            '{feature}': random.choice(['recommendation engine', 'analytics dashboard', 'API']),
            '{project}': random.choice(['platform migration', 'new feature launch', 'system upgrade']),
            '{technology}': random.choice(['Python', 'React', 'Docker', 'Kubernetes']),
            '{purpose}': random.choice(['scalability', 'performance', 'user experience']),
            '{activity}': random.choice(['code reviews', 'sprint planning', 'technical discussions']),
            '{task}': random.choice(['bug fixes', 'documentation', 'testing'])
        }
        
        result = template
        for key, value in replacements.items():
            result = result.replace(key, value)
        return result
    
    def _generate_education(self, quality_tier: str) -> List[Dict[str, str]]:
        """Generate education background"""
        institutions = self.education_institutions[quality_tier]
        
        return [{
            'degree': random.choice(['Bachelor of Science', 'Master of Science']),
            'institution': random.choice(institutions),
            'year': str(random.randint(2015, 2023))
        }]
    
    def _generate_summary(self, persona: Dict[str, Any]) -> str:
        """Generate professional summary"""
        templates = {
            'excellent': "Highly accomplished {title} with proven track record of delivering exceptional results",
            'good': "Experienced {title} skilled in modern technologies and best practices",
            'average': "Dedicated {title} with solid foundation in {domain}"
        }
        
        template = templates.get(persona['quality_tier'], templates['average'])
        return template.format(
            title=persona['title'],
            domain=persona['domain'].replace('_', ' ')
        )
    
    def _initialize_skill_pools(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize skill pools by domain"""
        return {
            'data_science': {
                'Programming': ['Python', 'R', 'SQL', 'Scala', 'Java'],
                'ML/AI': ['Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch'],
                'Data Tools': ['Pandas', 'NumPy', 'Jupyter', 'Apache Spark'],
                'Cloud': ['AWS', 'GCP', 'Azure', 'Docker', 'Kubernetes']
            },
            'software_engineering': {
                'Languages': ['Python', 'JavaScript', 'Java', 'Go', 'TypeScript'],
                'Frontend': ['React', 'Vue.js', 'Angular', 'HTML5', 'CSS3'],
                'Backend': ['Node.js', 'Django', 'Flask', 'Spring Boot'],
                'DevOps': ['Docker', 'Kubernetes', 'Jenkins', 'GitLab CI']
            }
        }
    
    def _initialize_education(self) -> Dict[str, List[str]]:
        """Initialize education institutions by quality"""
        return {
            'excellent': ['MIT', 'Stanford University', 'Harvard University', 'UC Berkeley'],
            'good': ['University of Washington', 'Georgia Tech', 'University of Michigan'],
            'average': ['State University', 'Regional College', 'Community College'],
            'below_average': ['Online University', 'Technical Institute']
        }
    
    def _initialize_companies(self) -> Dict[str, List[str]]:
        """Initialize company pools by quality"""
        return {
            'excellent': ['Google', 'Apple', 'Microsoft', 'Amazon', 'Meta'],
            'good': ['IBM', 'Oracle', 'Salesforce', 'Adobe', 'Cisco'],
            'average': ['TechCorp', 'DataFlow Inc', 'Innovation Labs'],
            'below_average': ['Local Tech Company', 'StartupTech']
        }
