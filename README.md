# Software Requirements Specification for Library Management System

File Version: V1.1
Update Time: 2025.07.15

### 1. Introduction

  #### 1.1 Purpose
  
  The purpose of this document is to clearly and accurately define the various requirements of the Library Management System, including functional requirements, performance requirements, and constraints to be followed during the design process.
  It will serve as the core basis for the system development team to carry out their work, ensuring that the developed system can accurately meet the actual needs of library administrators and borrowers in daily operations, and improve the efficiency and quality of library management work.
  
  #### 1.2 Scope
  
  This Library Management System mainly focuses on the core business processes of library management, specifically covering:
  Book lending, returning, and stocking operations.
  User registration and login functions.
  Recording key information (e.g., lending time, borrower, corresponding book number).
  The system will create an intuitive and user-friendly GUI interface to:
  Enable administrators to efficiently manage book information and query lending records.
  Allow borrowers to self-service query books, handle lending/returning procedures.
  This system is a stand-alone software, suitable for local management scenarios of small libraries or personal bookrooms.
  
  #### 1.3 Definitions, Acronyms, and Abbreviations
  Book Information: Detailed data describing a book, including: book number (unique ID), title, author, ISBN, publisher, publication date, collection location, book classification, unit price, quantity, etc. The book number (unique ID) distinguishes physical copies of the same ISBN.
  Borrower: A user of the system, divided into two types: administrator and ordinary borrower.
  Lending Record: A record tracking book lending details: lending time, due return time, actual return time, borrower, corresponding book number, etc.

### 2. Overall Description

#### 2.1 Product Prospect
With the development of small libraries and personal bookrooms, traditional manual recording or simple spreadsheet management is inefficient (e.g., slow to query book status, track lending records).
This Library Management System, as a Python-based stand-alone GUI software, aims to:
Solve the cumbersome problems of manual management via localized, efficient operations.
Achieve digital management of book information and lending records.
Improve convenience and accuracy in library management.

#### 2.2 Product Functions
The system provides the following core capabilities:

##### 2.2.1 User Management
Supports user registration and login.
Implements permission management to distinguish roles:
Administrator: Full access (book management, user management, all lending record queries).
Ordinary Borrower: Limited access (book query, lending/returning, personal lending record queries).

##### 2.2.2 Book Management
Stocking: Administrators add new books (with unique book numbers) and fill in details (title, author, ISBN, etc.). The system enforces unique book number checks to avoid duplicates.
Query: Users search books by multiple conditions (book number, title, author, ISBN, etc.). Results display basic info + current status (e.g., “available,” “lent out,” “in stock”).
Modification: Administrators update book info (e.g., collection location, price). Changes require confirmation and sync to storage in real time.
Deletion: Administrators remove books no longer in the collection. The system prompts for confirmation (deletion is irreversible, but lending records are retained).

##### 2.2.3 Lending Management
Lending: Borrowers select available books (via unique book numbers) to initiate lending. The system records: borrower info, lending time, book number, and calculates due return time (e.g., default 30-day period). Updates book status to “lent out.”
Returning: Borrowers return books, triggering: actual return time recording, status update to “in stock.” If overdue, the system calculates overdue days and fines (per preset rules).
Renewal: Borrowers renew non-overdue books (e.g., max 1 renewal, extending the due return time by 15 days). Updates are saved to storage.

##### 2.2.4 Lending Record Query
Administrator: Queries all system lending records, with filters (book number, title, ISBN, borrower name, time range, return status). Results exportable as CSV for analysis.
Borrower: Views personal lending records (returned/unreturned). Unreturned books display due return times.

##### 2.2.5 Overdue Reminder
The system monitors lending status in real time. On software launch, it scans lending records and flags overdue books (displayed with red markers in interfaces). Info includes: borrower, book name, number, overdue days.
Administrators can send manual reminders (via in-system messages, visible to borrowers on next login).

#### 2.3 User Characteristics
Administrator: Manages book info (stocking, modification, deletion), user management, and all lending record queries. Requires basic Windows operations; understanding of library management processes.
Ordinary Borrower: Performs book query, lending/returning, and personal lending record queries. Requires basic computer skills; ability to follow GUI prompts.

#### 2.4 Operating Environment
This is a Python-based stand-alone GUI software with the following requirements:

##### 2.4.1 Hardware Environment
Windows personal computer (recommended):
CPU: i3 or above
Memory: 4GB or above
Hard disk: 10GB+ available space

##### 2.4.2 Software Environment
Operating System: Windows 10 or later.
Python Environment: Python 3.8 or later (installed).
Dependent Libraries: GUI frameworks (e.g., Tkinter, PyQt — depends on development).

##### 2.4.3 Operation Mode
Users launch the GUI locally (no network required).
All data is stored in local text files.

### 3. Specific Requirements

#### 3.1 Functional Requirements

##### 3.1.1 User Registration and Login
Registration: Users fill in required info (username, password, contact details, ID number) via a registration interface. The system validates:
Unique username.
Valid format for contact details/ID number.
Login: Registered users enter username + password. The system authenticates and redirects to role-specific interfaces (administrator/borrower).
Permission Management: Strict role-based access (full access for administrators; limited access for borrowers).

##### 3.1.2 Book Management
Stocking: Administrators input detailed book info (unique ID, title, author, etc.). The system enforces:
Unique book number checks.
Support for multiple copies of the same ISBN (via unique book numbers).
Query: Multi-condition search (book number, title, author, ISBN, etc.). Results display as a list (basic info + status).
Modification: Administrators update book info (e.g., collection location, price). Changes require confirmation and sync to storage.
Deletion: Administrators remove books (with confirmation prompt). Lending records are retained.

##### 3.1.3 Lending Management
Lending: Borrowers select available books (via unique numbers). The system records:
Borrower info, lending time, book number.
Calculates due return time (e.g., 30 days).
Updates book status to “lent out.”
Returning: Borrowers return books, triggering:
Actual return time recording.
Status update to “in stock.”
Overdue calculation (days + fines, if applicable).
Renewal: Borrowers renew non-overdue books (e.g., 1 renewal max, +15 days to due return time). Updates saved to storage.

##### 3.1.4 Lending Record Query
Administrator: Queries all records with filters (book number, title, ISBN, borrower name, time range, return status). Export to CSV.
Borrower: Views personal records (returned/unreturned). Unreturned books show due return times.

##### 3.1.5 Overdue Reminder
Real-time monitoring: On software launch, scans records and flags overdue books (red markers in interfaces). Info includes: borrower, book name, number, overdue days.
Manual reminders: Administrators send in-system messages (visible to borrowers on next login).

#### 3.2 Performance Requirements
Response Time: All user operations (login, query, lending, returning, info modification) must complete within 2 seconds (optimize text file read/write efficiency).
Concurrent Access: Single-user operation (no multi-user concurrency needed). Ensure no data corruption/loss during frequent text file operations (e.g., batch stocking, large queries).
Data Storage:
Text files support:
≥50,000 book info records (with unique IDs).
≥500,000 lending records.
Optimize performance for growing data (e.g., split lending records by month).
Data Backup:
Automatic backup: Daily first launch backs up all data files to a user-specified local path (e.g., D:\Library Management System Backup\YYYYMMDD).
Manual backup: User-triggered backups.
Backup files (e.g., books_202507151030.json) support data recovery (overwrite damaged files).

#### 3.3 Design Constraints

##### 3.3.1 Interface
Stand-alone software: No network interfaces. Local file import/export (JSON, CSV) supported for batch data operations (e.g., bulk book info import, statistical data export).

##### 3.3.2 Data Storage

###### Formats:
Book info: JSON (e.g., books.json), array of records (all fields: book number, title, author, etc.).
User info: JSON (e.g., users.json), stores registration info (username, encrypted password, permission type).
Lending records: CSV (e.g., borrow_records.csv), fields include: borrower, book number, lending time, due return time, actual return time.
Path Configuration: Storage paths configurable in software settings (default: data folder in installation directory). Ensure read/write access and use file locks to prevent concurrent write conflicts.

##### 3.3.3 Security
Passwords: Stored encrypted (e.g., MD5).
Sensitive Data: Encrypt ID numbers, contact details (symmetric encryption) — decrypted on read.
Startup Password: Optional to prevent unauthorized access.

##### 3.3.4 Compatibility
OS: Windows 10 or later.
GUI: Adaptive to screen resolutions (e.g., 1366×768, 1920×1080) without layout issues.
Python: Runs on Windows with Python 3.8 or later.

### 4. Appendix

#### 4.1 Glossary
ISBN: International Standard Book Number: A unique identifier for publications. Different copies share the same ISBN.
Book Number (Unique ID): A system/admin-assigned identifier for physical book copies (ensures operation accuracy for the same ISBN).
Stand-alone GUI Software: Runs on a single computer, interacts via GUI, no network required, data stored locally.
Text File Storage: Uses JSON/CSV for data storage (no database dependency). Suitable for small stand-alone applications (simple, easy to back up).

#### 4.2 Analysis Models

##### 4.2.1 Data Flow Diagram
Describes data flow/logic:
Book info: stocking → lending/returning.
User info: registration → login.
Lending records: generation → updates (text file read/write).

##### 4.2.2 Entity Relationship Diagram
Key relationships:
Books (unique ID) ↔ Lending Records: One-to-many (multiple loans per book).
Borrowers (unique username) ↔ Lending Records: One-to-many (multiple loans per borrower).
ISBN ↔ Books: One-to-many (multiple copies per ISBN).
