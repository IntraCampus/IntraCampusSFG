# IntraCampusSFG
IntraCampus is a role-based web and mobile application that helps educational institutions manage core campus services efficiently. It offers a centralized interface to handle room bookings, class schedules, maintenance requests, and announcements. Access to each service is determined by user roles such as students, staff, and administrator. 

Vision Goals:
• Eliminate paper-based processes (e.g., manual room booking forms, maintenance logbooks).
• Provide real-time access to schedules and resources via web/mobile apps.
• Automate workflows (e.g., approval chains, maintenance dispatches).
• Scale sustainably to support future campus expansions or new features.
• Foster collaboration between stakeholders (students, faculty, admins, maintenance).

    Functional Requirements
1. User Authentication & Authorization
• Role-based access control (Student, Staff, Admin)
2. Room Booking
• Create, edit, and cancel room reservations
• Conflict handling and availability checks
3. Class Scheduling
• View personal or class-wide schedules
• Staff can add or modify class entries
4. Maintenance Requests
• Submit issues
• Track status updates by staff/maintenance team
5. Announcements
• Create, edit, and delete announcements (staff/admin)
• Auto-display for relevant roles

   Non-Functional Requirements
1. Performance
• Scalable backend using Django and SQL Lite (Django built-in)
2. Availability
• 99.5% uptime for hosted environments
3. Security
• Built-in authentication framework (django.contrib.auth.)
• Encrypted passwords
• Role-based access control (RBAC)
4. Usability
• Web version using Python (Responsive)
    Technical Requirements
Software Stack
• Frontend: HTML 5, CSS 3
• Backend: Django (Python), Django REST Framework
• Database: SQLite
• Authentication: Built-in authentication framework (django.contrib.auth.)
• DevOps: GitHub Actions
• Monitoring/Logging: Prometheus
