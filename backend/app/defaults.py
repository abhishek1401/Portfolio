DEFAULT_DASHBOARD = {
    "user": {
        "name": "Avery Stone",
        "title": "Product Engineer",
        "location": "Austin, TX",
        "email": "avery.stone@example.com",
        "phone": "+1 555 0138",
        "availability": "Open to product engineering roles",
        "focus": "Building calm, useful software for teams",
        "bio": (
            "Avery is a full-stack product engineer who enjoys turning messy "
            "business workflows into simple, reliable tools."
        ),
        "avatarUrl": "/assets/default-avatar.svg",
        "themeColor": "#176b87",
    },
    "stats": [
        {"label": "Projects", "value": "18", "detail": "Shipped across SaaS and internal tools"},
        {"label": "Experience", "value": "7 yrs", "detail": "Backend, frontend, and data workflows"},
        {"label": "Users Served", "value": "42k", "detail": "Monthly active users across products"},
    ],
    "skills": ["Python", "React", "API Design", "Data Modeling", "UX Systems", "Automation"],
    "projects": [
        {
            "name": "Ops Command Center",
            "description": "A live operations dashboard for monitoring SLA risk and support load.",
            "status": "Live",
            "link": "https://example.com/ops-command-center",
        },
        {
            "name": "Customer Health Portal",
            "description": "A CRM-adjacent view that combines product usage, notes, and renewals.",
            "status": "Pilot",
            "link": "https://example.com/customer-health",
        },
    ],
    "timeline": [
        {
            "date": "2026",
            "title": "Lead Engineer, Platform Tools",
            "description": "Designed admin workflows, API contracts, and file-backed prototypes.",
        },
        {
            "date": "2024",
            "title": "Senior Full-Stack Engineer",
            "description": "Built React dashboards and Python services for operational teams.",
        },
    ],
    "links": [
        {"label": "Portfolio", "url": "https://example.com"},
        {"label": "LinkedIn", "url": "https://linkedin.com"},
        {"label": "GitHub", "url": "https://github.com"},
    ],
}

DEFAULT_AUTH = {
    "username": "admin",
    "passwordSalt": "local-dashboard-salt-v1",
    "passwordHash": "1f10be63346e3456d351a53645d47c09f426ef480d9a8fd96a510f54399b1ff6",
}
