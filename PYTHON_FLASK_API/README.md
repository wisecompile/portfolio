#### Purpose and Business Context

This project implements an internal service architecture for real-time access to inventory data from a Microsoft SQL Server. The solution is divided into two independent Flask-based services, each addressing a separate business scenario and deployed as production Windows services with full logging and process control.

#### HTTP Web Interface for Field Sales

Designed for field sales representatives who need to access stock status from their smartphones while working outside the office. The web interface is optimized for mobile browsers and requires no app installation. This approach was chosen specifically because most of the crowd are unwilling to install separate applications. Sales representatives can check SKU availability, pricing, descriptions, and up-to-date stock levels filtered by brand. The system also performs IP logging and request auditing.

#### REST API for Applications and Dealer Sites

Provides a secure REST API for third-party applications, dealer web portals, and other systems requiring current inventory data. API access is protected with API keys, with each key mapped to permitted brands for each partner. The API returns structured data in JSON format, supporting batch queries for real-time synchronization with dealer websites or apps.

#### Service Separation and Security

Both web and API services are deployed as independent Windows services, each listening on a separate internal port (port numbers are not published). Database credentials and connection strings are never present in public sources. Each service uses Waitress as a production WSGI server and logs all access events for security and diagnostics.

#### Project Relevance

The project reflects practical industry needs in inventory management and B2B system integration, enabling secure, robust, and convenient access to key business data for both field users and automated systems. The architecture demonstrates real-world skills in modular design, production deployment, and secure authentication mechanisms.

All confidential data, such as port numbers and connection strings, are excluded from the public repository and documentation.