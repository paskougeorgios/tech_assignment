# Write up

## Suggestions

### Proposal 1

If I had four more hours, I would focus on three important improvements to make the API more production-ready and scalable.
First, I would add proper database indexes. Indexes are critical for improving query performance, especially for frequently searched fields such as book title, author, or ISBN. Without indexes, the database performs full table scans, which becomes inefficient as the amount of data grows. Adding indexes would significantly improve response times and scalability.



### Proposal 2

I would implement authentication and authorization structure from day one. Even if the current API is simple, designing the authentication layer early is important for future extensibility and AI integration scenarios. Modern AI agents and external services often require secure API access through JWT tokens, roles, permissions, and rate limiting. Building the login structure early avoids major architectural refactoring later and ensures the API follows secure development practices from the beginning.



### Proposal 3
  
I would create an Architectural Decision Record (ADR) document. ADRs are important because they document the reasoning behind technical decisions, such as framework selection, database design, authentication strategy, or project structure. This improves maintainability, team collaboration, and onboarding for future developers. It also helps justify architectural choices and makes future changes easier to evaluate.

