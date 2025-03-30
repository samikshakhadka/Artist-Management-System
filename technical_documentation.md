# Artist Management System - Technical Documentation

## 1. System Architecture Overview

The Artist Management System implements a comprehensive web application for managing artists and their song collections using a custom-built architecture rather than relying on established frameworks. This approach provides a detailed view into web application internals while maintaining complete control over the request handling pipeline.

### 1.1 Application Bootstrap Process

The system initialization follows a carefully orchestrated sequence:

1. **Entry Point**: `run.py` serves as the application's entry point, handling command-line arguments and bootstrapping the environment. It performs critical setup tasks including creating directory structures, locating server modules, and managing file paths before starting the server.

2. **Server Initialization**: Once bootstrapped, `run.py` calls the `run_server()` function in `server.py`, which initializes the HTTP server on port 8000 and begins listening for connections.

3. **Route Registration**: During initialization, `controller_init.py` dynamically registers all route handlers from the controller modules, connecting URL patterns to their respective handling functions.

4. **Static Resource Setup**: The system prepares client-side assets, creating the necessary directory structure for CSS, JavaScript, and other static files.

This initialization process demonstrates a modular approach to application startup, where each component has clearly defined responsibilities. The system also implements a clever wrapper mechanism in `_temp_run_server.py` that handles Python module import paths, making the application more resilient to different deployment configurations.

### 1.2 Custom HTTP Server Architecture

At the core of the system is a custom HTTP server built on Python's native `http.server` module. This server is implemented in `server.py` and features:

1. **Extended Request Handler**: The system extends `SimpleHTTPRequestHandler` to support additional HTTP methods (GET, POST, PUT, DELETE) and implement custom routing.

2. **Request Context Creation**: For each incoming request, the server creates a rich request object containing parsed URL components, query parameters, cookies, and request body data.

3. **Dynamic Route Matching**: The server matches request paths against registered route patterns, including support for capturing URL parameters.

4. **Custom Response Generation**: After route handler execution, the server transforms the handler's return value into an HTTP response with appropriate status codes, headers, and body content.

This custom server implementation provides full visibility into the HTTP request-response cycle while maintaining a clean separation between routing logic and request handling.

### 1.3 Role-Based Access Control System

The application implements a sophisticated Role-Based Access Control (RBAC) system that enforces different permissions based on user roles:

- **Super Admin**: Has complete access to all system functions, including user management
- **Artist Manager**: Can manage artists and their information, including CSV import/export
- **Artist**: Can view their own profile and manage their songs

This RBAC system is implemented through:

1. **Role Storage**: User roles are stored in the database using the ENUM constraint
2. **Session Integration**: User roles are included in session data for quick access
3. **Decorator-Based Enforcement**: Route handlers use decorators to enforce role requirements
4. **UI Adaptation**: The frontend dynamically adjusts its interface based on user roles

Through this comprehensive approach, the system maintains consistent access control across both server-side operations and client-side interfaces.

## 2. Component Interaction and Data Flow

### 2.1 Complete Request-Response Cycle

The system's components interact through a well-defined request-response cycle:

1. **Client Request**: Browser sends an HTTP request to the server (port 8000)
2. **Server Parsing**: `RequestHandler` in `server.py` parses the request URL, method, headers, and body
3. **Session Validation**: `auth_handler.py` validates the session cookie and retrieves user information
4. **Route Matching**: The server matches the request path against registered routes
5. **Permission Checking**: The `requires_role` decorator verifies the user has necessary permissions
6. **Handler Execution**: The matched controller function executes, often calling model methods
7. **Database Operations**: Model methods execute SQL queries against the MySQL database
8. **Response Formation**: The handler returns a structured response object
9. **Response Transmission**: Server converts the response object to HTTP response format
10. **Client Processing**: Browser processes the response and updates the UI

This flow illustrates how all components work together to process user requests and maintain system integrity. For example, when a user loads the artists list:

1. Browser sends `GET /api/artists?page=1&per_page=10`
2. Server parses the request and validates the session
3. Route matching finds the `get_artists` function in `artist_controller.py`
4. Permission checking verifies the user has access (all roles can view artists)
5. Handler calls `Artist.get_all()` from `artist_model.py` with pagination parameters
6. Model executes a SQL query to fetch artists with LIMIT and OFFSET
7. Query results are returned through the model to the controller
8. Controller formats the response with pagination metadata
9. Server sends HTTP response with JSON data
10. Browser renders the artist list and pagination controls

### 2.2 Authentication and Session Flow

The authentication system demonstrates sophisticated session management:

1. **Login Process**:
   - User submits credentials via the login form
   - `auth_handler.py` verifies credentials against the database
   - Upon successful verification, a new session is created with a UUID
   - Session ID is returned as a cookie and user details are sent in the response
   - Frontend stores user information in localStorage for UI personalization

2. **Session Validation**:
   - Each subsequent request includes the session cookie
   - `auth_handler.py` validates the session ID and checks expiration
   - User information is attached to the request object for use by controllers
   - If the session is invalid or expired, an unauthorized error is returned

3. **Logout Process**:
   - User clicks logout button
   - Frontend calls the logout API endpoint
   - Server invalidates the session and clears the session cookie
   - Browser redirects to the login page

This stateful authentication approach provides security while maintaining good user experience through persistent sessions.

### 2.3 Data Modification Workflows

The system implements complete CRUD workflows for all entities. For example, the artist creation process:

1. **Form Preparation**:
   - User clicks "Add Artist" button
   - Frontend displays a modal form for artist details
   - JavaScript validates required fields before submission

2. **Data Submission**:
   - Frontend collects form data and sends POST request to `/api/artists`
   - Request includes authentication cookie and JSON payload

3. **Server Processing**:
   - Server validates the session and checks user role (must be artist_manager)
   - Controller validates input data for required fields and formats
   - Controller calls `Artist.create()` method from the model
   - Model constructs and executes an INSERT SQL query with parameterized values
   - Database assigns an ID and timestamps to the new record

4. **Response Handling**:
   - Server returns success response with new artist ID
   - Frontend displays success message and refreshes the artist list
   - Modal form is closed

Similar workflows exist for update, delete, and specialized operations like CSV import/export, each following the same pattern of frontend preparation, data submission, server processing, and response handling.

## 3. Database Design and Data Layer

### 3.1 Schema Design Philosophy

The database schema is designed around three core entities (Users, Artists, Music) with clear relationships:

1. **Users Table**: Stores user accounts with role designations
   - Primary identifier: `id` (auto-increment integer)
   - Authentication fields: `email` (unique), `password` (bcrypt hash)
   - Personal information: name, contact details, demographics
   - Access control: `role` ENUM with three possible values
   - Audit information: creation and update timestamps

2. **Artists Table**: Stores artist information
   - Primary identifier: `id` (auto-increment integer)
   - Profile information: name, demographics, address
   - Career details: first release year, number of albums
   - Audit information: creation and update timestamps

3. **Music Table**: Stores songs associated with artists
   - Primary identifier: `id` (auto-increment integer)
   - Relationship: `artist_id` foreign key with CASCADE delete
   - Song details: title, album name, genre (as ENUM)
   - Audit information: creation and update timestamps

The schema exemplifies several relational database design principles:
- **Referential Integrity**: Foreign key constraints ensure data consistency
- **Data Normalization**: Tables are organized to reduce redundancy
- **Domain Constraints**: ENUM types restrict values to valid options
- **Cascading Operations**: When artists are deleted, their songs are automatically removed

### 3.2 Raw SQL Query Approach

As per requirements, the system uses raw SQL queries instead of an ORM. This approach is implemented through a unified query execution function that:

1. Establishes a database connection for each query
2. Creates a cursor with dictionary result mode
3. Executes parameterized queries to prevent SQL injection
4. Handles different result types (single row, multiple rows, insert ID)
5. Manages transaction commits and rollbacks
6. Properly closes resources even during exceptions

The system employs several SQL techniques:
- **Parameterized Queries**: All user input is bound through parameters
- **Dynamic Query Construction**: Building queries based on provided fields
- **Pagination**: Using LIMIT and OFFSET for efficient data retrieval
- **Transactions**: Ensuring data integrity through atomic operations
- **Error Handling**: Catching and logging database exceptions

### 3.3 Model Implementation Strategy

The data access layer is implemented through model classes with static methods that follow a repository pattern:

1. **User Model**: Handles user authentication, profile management, and role-based operations
2. **Artist Model**: Manages artist data, including CSV import/export functionality
3. **Music Model**: Handles song information and artist relationships

Each model provides methods for standard CRUD operations plus specialized functions:
- **Get by ID**: Retrieving single records by primary key
- **Get All**: Listing records with pagination
- **Create**: Inserting new records with validation
- **Update**: Modifying existing records with partial data
- **Delete**: Removing records (with cascading effects where appropriate)
- **Count**: Getting total record counts for pagination
- **Search**: Finding records by specific criteria

This approach provides a clean abstraction over raw SQL while maintaining complete control over query execution.

## 4. Authentication and Security

### 4.1 Password Security Implementation

The system implements robust password security through bcrypt hashing:

1. **Password Hashing**: When users register or passwords are changed, the plaintext password is:
   - Encoded to UTF-8 bytes
   - Hashed using bcrypt with automatically generated salt
   - Decoded back to string for storage
   
2. **Password Verification**: During login, the submitted password is:
   - Encoded to UTF-8 bytes
   - Compared to the stored hash using bcrypt's constant-time comparison
   - Resulting in a boolean verification result

This approach protects against several security threats:
- **Password Breaches**: Even if the database is compromised, passwords remain secured
- **Rainbow Table Attacks**: Unique salts prevent precomputed hash attacks
- **Timing Attacks**: Constant-time comparison prevents leaking information through timing differences
- **Future Proofing**: Bcrypt's work factor can be adjusted as computing power increases

### 4.2 Session Management System

The system uses a custom session management implementation:

1. **Session Creation**: Upon successful authentication, a new session is created with:
   - Universally unique identifier (UUID) as session ID
   - User ID and role for authorization checks
   - Creation timestamp and expiration time
   - Active status flag

2. **Session Storage**: Sessions are stored in an in-memory dictionary:
   - Session ID as key
   - Session object with user details as value
   - Expiration time for automatic cleanup

3. **Session Validation**: Each request with a session cookie undergoes:
   - Existence check in the session store
   - Expiration time verification
   - Active status confirmation
   - Automatic invalidation of expired sessions

4. **Session Destruction**: When a user logs out:
   - Session is marked as inactive
   - Session is removed from the session store
   - Session cookie is cleared from the client

While this implementation uses in-memory storage (suitable for development), the design could easily be extended to use a persistent store like Redis for production use.

### 4.3 Decorator-Based Authorization

The system implements RBAC through Python decorators:

1. **Role Requirement Definition**: Each route handler is decorated with required roles:
   ```python
   @route('/api/users', methods=['GET'])
   @requires_role(['super_admin'])
   def get_users(request):
       # Only super_admin can access this endpoint
   ```

2. **Role Verification Process**:
   - Extract session ID from request cookies
   - Validate session existence and expiration
   - Check if user's role is in the allowed roles list
   - Return 401 (Unauthorized) or 403 (Forbidden) for failed checks
   - Attach user information to request for successful verification

3. **Resource Ownership**: For some operations, additional checks verify resource ownership:
   - Artist can only modify their own songs
   - Prevents unauthorized access even within the same role

This approach centralizes authorization logic while keeping route handlers focused on business logic.

## 5. Frontend Architecture

### 5.1 JavaScript Module Organization

The frontend JavaScript is organized into functional modules:

1. **auth.js**: Authentication operations (login, logout, session checks)
2. **api.js**: API client for server communication
3. **user.js**: User management functionality
4. **artists.js**: Artist management functionality
5. **music.js**: Song management functionality
6. **common.js**: Shared utility functions
7. **main.js**: Application initialization and global state management
8. **setup.js**: Modal and UI component setup

This organization separates concerns and improves maintainability by grouping related functionality.

### 5.2 UI Component Management

The frontend implements a component-based approach without frameworks:

1. **Modal Systems**: Reusable modal dialog implementation for forms
2. **Data Tables**: Dynamic table generation with sorting and pagination
3. **Form Management**: Form submission handling with validation
4. **Tab Interface**: Multi-tab navigation with content switching
5. **Role-Based UI**: Dynamic UI adjustment based on user roles

These components are implemented using vanilla JavaScript DOM manipulation, demonstrating framework-like capabilities without external dependencies.

### 5.3 API Communication Layer

The frontend implements a structured API communication layer:

1. **Base Request Function**: Centralized request handling with:
   - Method and content type specification
   - JSON serialization and parsing
   - Cookie inclusion for authentication
   - Error handling and response processing
   
2. **Domain-Specific API Methods**: Organized by entity:
   - User endpoints (CRUD operations for users)
   - Artist endpoints (CRUD plus import/export)
   - Music endpoints (CRUD plus filtering)
   - Authentication endpoints (login, logout, session validation)

3. **Special Content Handling**:
   - FormData for file uploads
   - File download processing for CSV export
   - Different content types based on response

This approach provides a clean, consistent interface for server communication throughout the application.

## 6. Advanced Implementation Techniques

### 6.1 Custom Route Decorator System

The system implements a sophisticated route decorator using Python's higher-order functions:

1. **Decorator Creation**: The `route` function returns a decorator function that:
   - Accepts a handler function as its parameter
   - Registers the handler with specified HTTP methods and path pattern
   - Returns the original handler function unchanged

2. **Path Parameter Extraction**: For paths with parameters (like `/api/users/{id}`):
   - Path templates are converted to regex patterns
   - Parameters are captured as named groups
   - Extracted parameters are added to the request object for handler use

3. **Decorator Composition**: Route decorators can be combined with role requirement decorators:
   ```python
   @route('/api/users/{id}', methods=['PUT'])
   @requires_role(['super_admin'])
   def update_user(request):
       # Handler implementation
   ```

This approach provides a clean, declarative API for route definition while handling complex parameter extraction automatically.

### 6.2 CSV Import/Export Implementation

The system provides sophisticated CSV data handling:

1. **Import Process**:
   - File upload through multipart form data
   - File content extraction and parsing
   - Row-by-row processing with validation
   - Batch insertion into database
   - Error handling and reporting

2. **Export Process**:
   - Database query to retrieve all artist records
   - Dynamic header generation from record keys
   - CSV formatting with proper escaping
   - Content-type and disposition headers for download
   - In-memory processing without temporary files

This implementation demonstrates advanced data processing capabilities without relying on external libraries.

### 6.3 Pagination Implementation

The system implements comprehensive pagination:

1. **Backend Implementation**:
   - Page and per-page parameters from query string
   - Offset calculation for SQL queries
   - Total count queries for page calculation
   - Metadata inclusion in responses

2. **Frontend Implementation**:
   - Dynamic pagination control rendering
   - Ellipsis for large page counts
   - Current page highlighting
   - Previous/next navigation
   - Page click handling

This approach provides efficient data retrieval and a user-friendly interface for navigating large datasets.

## 7. System limitations and Improvement Recommendations

### 7.1 Current Limitations

1. **In-Memory Session Storage**: The current implementation stores sessions in memory, which:
   - Doesn't persist across server restarts
   - Doesn't scale across multiple server instances
   - Has memory consumption concerns for large user bases

2. **Connection Per Query**: Each database query establishes a new connection, which:
   - Increases connection overhead
   - Limits throughput under heavy load
   - Creates potential connection exhaustion issues

3. **Limited Error Handling**: Error handling could be improved with:
   - More structured error responses
   - Better client-side error presentation
   - More detailed logging

4. **No Test Coverage**: The system lacks automated tests, which:
   - Makes regression testing manual and time-consuming
   - Reduces confidence in code changes
   - Creates potential maintenance challenges

### 7.2 Recommended Improvements

1. **Persistent Session Storage**:
   - Implement Redis-based session storage
   - Add session expiration and cleanup mechanisms
   - Implement distributed session support

2. **Database Connection Pooling**:
   - Implement connection pooling for query execution
   - Reuse connections across multiple queries
   - Add connection health checking

3. **Enhanced Security**:
   - Add CSRF protection for form submissions
   - Implement rate limiting for authentication attempts
   - Add secure headers (CSP, HSTS, etc.)

4. **Code Organization**:
   - Consider a more structured package organization
   - Implement a configuration system for environment-specific settings
   - Add comprehensive logging throughout the application

5. **Testing Infrastructure**:
   - Implement unit testing for model and controller logic
   - Add integration tests for API endpoints
   - Create fixtures for test data management

These improvements would address the current limitations while maintaining the custom architecture approach.

## 9. Workflow Diagrams

### 9.1 Server Startup Process

The Artist Management System follows a structured startup workflow that begins with the execution of `run.py` and culminates in a fully operational web server. The following diagram illustrates this process:

```
┌───────────┐     ┌───────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│           │     │                   │     │                     │     │                     │
│  run.py   │────►│ setup_client_files│────►│ Find server.py     │────►│ Create _temp_run    │
│ execution │     │ (Creates dirs)    │     │ location           │     │ _server.py wrapper  │
│           │     │                   │     │                     │     │                     │
└───────────┘     └───────────────────┘     └─────────────────────┘     └──────────┬──────────┘
                                                                                    │
                                                                                    │
                                                                                    ▼
┌───────────────────┐     ┌───────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│                   │     │                   │     │                     │     │                     │
│ HTTP Server       │◄────┤ register_all      │◄────┤ Initialize server   │◄────┤ Execute _temp_run   │
│ Listening (8000)  │     │ _routes()         │     │ components          │     │ _server.py          │
│                   │     │                   │     │                     │     │                     │
└───────────────────┘     └───────────────────┘     └─────────────────────┘     └─────────────────────┘
```

The server startup process involves the following steps:

1. **Run.py Execution**: 
   - The user executes `run.py` from the command line
   - Command-line arguments are parsed
   - The system identifies the `run project` command

2. **Client Files Setup**:
   - `setup_client_files()` creates the necessary directory structure
   - Static directories for CSS, JavaScript, and assets are created
   - HTML templates are copied to the client directory

3. **Server Module Location**:
   - The system searches for `server.py` in multiple possible locations
   - Once found, its path is recorded for the next step

4. **Wrapper Creation**:
   - A temporary wrapper script (`_temp_run_server.py`) is created
   - This wrapper handles Python import paths and module discovery
   - It provides a consistent execution environment regardless of directory structure

5. **Wrapper Execution**:
   - The Python interpreter executes the wrapper script
   - The wrapper adds appropriate directories to the Python path
   - It imports the server module and locates the `run_server()` function

6. **Server Initialization**:
   - The server creates necessary directories if they don't exist
   - Database connections are tested
   - The route registration process begins through `controller_init.py`

7. **Route Registration**:
   - `register_all_routes()` is called to register all controllers
   - Each controller registers its routes with the routing system
   - Route patterns are compiled to regex where necessary

8. **Server Listening**:
   - An HTTP server instance is created on port 8000
   - The server begins listening for incoming connections
   - A confirmation message is printed to the console

This multi-stage bootstrap process ensures the application starts correctly across different environments and maintains proper module import paths.

### 9.2 Request-Response Cycle

The following diagram illustrates the complete request-response cycle from client request to rendered response:

```
┌─────────┐         ┌───────────────┐         ┌────────────────┐         ┌────────────────┐
│         │ HTTP    │               │ Find    │                │ Execute │                │
│ Browser │────────►│ server.py     │────────►│ Route Matching │────────►│ Auth Decorator │
│         │ Request │ RequestHandler│ Handler │                │         │                │
└─────────┘         └───────────────┘         └────────────────┘         └────────┬───────┘
     ▲                                                                             │
     │                                                                             │
     │                                                                             ▼
     │                                                                     ┌────────────────┐
     │                                                                     │                │
     │                                                                     │ Controller     │
     │                                                                     │ Function       │
     │                                                                     │                │
     │                                                                     └────────┬───────┘
     │                                                                              │
     │                                                                              │
     │                                                                              ▼
┌─────────┐         ┌───────────────┐         ┌────────────────┐         ┌────────────────┐
│         │ HTTP    │               │ Format  │                │ Return  │                │
│ Browser │◄────────┤ server.py     │◄────────┤ Response       │◄────────┤ Model Methods  │
│         │ Response│ RequestHandler│ Response│ Processing     │ Data    │ DB Queries     │
└─────────┘         └───────────────┘         └────────────────┘         └────────────────┘
```

The request-response flow follows these steps:

1. **Client Request Initiation**:
   - User interacts with the UI (clicks a button, submits a form)
   - Browser sends an HTTP request to the server (GET, POST, PUT, DELETE)
   - Request includes headers, cookies, and potentially a request body

2. **Server Request Handling**:
   - `RequestHandler.do_GET/POST/PUT/DELETE` receives the request
   - `handle_request()` parses URL components and creates a request object
   - Request body is parsed based on Content-Type (JSON or form data)
   - Session cookie is extracted and validated

3. **Route Matching**:
   - `find_route_handler()` matches the request URL against registered routes
   - For parametrized routes, regex patterns extract path parameters
   - If no matching route is found, a 404 response is returned

4. **Authentication Middleware**:
   - The `requires_role` decorator checks session validity
   - If session is invalid, a 401 Unauthorized response is returned
   - If user lacks required role, a 403 Forbidden response is returned
   - User information is attached to the request object

5. **Controller Function Execution**:
   - The matched controller function executes with the request object
   - Request parameters and body are validated
   - Business logic is applied to the request data

6. **Model Interaction**:
   - Controller calls appropriate model methods
   - Model constructs and executes SQL queries
   - Database results are returned to the controller
   - Data transformations are applied if necessary

7. **Response Processing**:
   - Controller formats the data into a response object
   - Response includes status code, headers, and body content
   - Additional metadata (like pagination) may be included

8. **Response Transmission**:
   - `send_response_from_result()` converts the response object to HTTP
   - Headers and cookies are set as needed
   - Response body is serialized (typically to JSON)
   - Response is sent back to the client

9. **Client Processing**:
   - Browser receives and processes the HTTP response
   - JavaScript code handles the response based on status and content
   - UI is updated to reflect the new state
   - Success/error messages are displayed as appropriate

The entire cycle demonstrates clean separation of concerns, with each component handling its specific responsibilities while passing data to the next component in the chain.

### 9.3 Authentication Flow

The authentication process follows a specific workflow that establishes and maintains user sessions:

```
┌─────────┐         ┌───────────────┐         ┌────────────────┐         ┌────────────────┐
│         │ Login   │               │ Call    │                │ Query   │                │
│ Browser │────────►│ /api/login    │────────►│ auth_handler   │────────►│ User.          │
│         │ Request │ endpoint      │ login() │ login()        │         │ authenticate() │
└─────────┘         └───────────────┘         └────────────────┘         └────────┬───────┘
     ▲                                                                             │
     │                                                                             │
     │                                                                             ▼
     │                                                                     ┌────────────────┐
     │                                                                     │                │
     │                                                                     │ Bcrypt password│
     │                                                                     │ verification   │
     │                                                                     │                │
     │                                                                     └────────┬───────┘
     │                                                                              │
     │                                                                              │
     │                                                                              ▼
┌─────────┐         ┌───────────────┐         ┌────────────────┐         ┌────────────────┐
│         │ Session │               │ Create  │                │ Return  │                │
│ Browser │◄────────┤ Set session   │◄────────┤ Generate UUID  │◄────────┤ Store session  │
│         │ Cookie  │ cookie        │ Session │ session ID     │ Success │ in memory      │
└─────────┘         └───────────────┘         └────────────────┘         └────────────────┘
```

The authentication flow proceeds as follows:

1. **Login Request**:
   - User enters email and password in the login form
   - Form submission triggers a POST request to `/api/login`
   - Request includes credentials in JSON format

2. **Credential Verification**:
   - Server routes the request to the login handler
   - `auth_handler.login()` is called with credentials
   - `User.authenticate()` queries the database for the user
   - Bcrypt compares submitted password with stored hash

3. **Session Creation**:
   - Upon successful authentication, `create_session()` is called
   - A new Session object is created with a UUID session ID
   - Session includes user ID, role, and expiration time
   - Session is stored in the in-memory sessions dictionary

4. **Response Formation**:
   - Session ID is included in a Set-Cookie header
   - User information (excluding password) is returned in response
   - Success status and message are included

5. **Client-Side Processing**:
   - Browser stores the session cookie
   - JavaScript stores user details in localStorage
   - UI redirects to the dashboard page
   - UI elements adapt based on user role

This authentication flow establishes a secure session that is validated on subsequent requests, maintaining user state across interactions with the application.

### 9.4 Role-Based Data Access Flow

The following diagram illustrates how role-based access control affects data operations:

```
┌─────────────┐         ┌───────────────┐         ┌────────────────┐         ┌────────────────┐
│             │ Request │               │ Validate│                │ Check   │                │
│ User Action │────────►│ API Endpoint  │────────►│ Session        │────────►│ Role           │
│             │         │               │         │ Validation     │         │ Requirements   │
└─────────────┘         └───────────────┘         └────────────────┘         └────────┬───────┘
                                                                                      │
                                                                                      │
                                                                                      ▼
┌─────────────┐         ┌───────────────┐         ┌────────────────┐         ┌────────────────┐
│             │         │               │ Based   │                │ If      │                │
│ Super Admin │◄────────┤ Full Access   │◄────────┤ Role-Based     │◄────────┤ Authorized     │
│ View        │         │ to All Data   │ on Role │ Permission     │         │ Continue       │
└─────────────┘         └───────────────┘         └────────────────┘         └────────────────┘
                                                          │
                                                          │
                                                          ▼
                                                  ┌────────────────┐
                                                  │                │
                                                  │ Artist Manager │
                                                  │ Limited Access │
                                                  │                │
                                                  └────────────────┘
                                                          │
                                                          │
                                                          ▼
                                                  ┌────────────────┐
                                                  │                │
                                                  │ Artist         │
                                                  │ Own Data Only  │
                                                  │                │
                                                  └────────────────┘
```

The role-based data access flow demonstrates how different user roles experience different levels of access:

1. **Initial Request Processing**:
   - User action triggers an API request
   - Session validation confirms user identity
   - Role check determines access level

2. **Super Admin Access**:
   - Super admins have complete access to all data
   - Can manage users, artists, and view all music
   - Full CRUD access to user records
   - Can view but not modify artist and music records

3. **Artist Manager Access**:
   - Limited to artist management
   - Cannot access user management functions
   - Full CRUD access to artist records
   - Can view but not modify music records
   - Can import/export artist data via CSV

4. **Artist Access**:
   - Most restricted access level
   - Can view artist listing
   - Can view song listing for all artists
   - Can only modify their own songs
   - Cannot access user or artist management

This hierarchical access control ensures that users can only perform operations appropriate to their role within the system, maintaining data security and operational boundaries.

## 10. Conclusion

The Artist Management System demonstrates a comprehensive approach to web application development using custom components rather than established frameworks. By implementing the HTTP server, routing system, authentication, and data access layer from scratch, the system provides valuable insights into web application internals.

Key technical achievements include:
- Custom HTTP server with advanced routing capabilities
- Session-based authentication with role-based access control
- Raw SQL query execution with a repository-like abstraction
- Complete CRUD operations with proper validation and error handling
- CSV import/export functionality for bulk data operations
- Role-based UI adaptation for different user types

The workflow diagrams illustrate how these components interact to create a cohesive system, from server startup to request processing and access control. This architecture offers educational value by exposing the underlying mechanisms of web applications while maintaining a clean separation of concerns and modular organization.

The system successfully implements the required features:
1. A relational database structure with User, Artist, and Song tables
2. Raw SQL queries for all database operations (no ORM)
3. A login/registration system with session management
4. Role-based access control for all operations
5. Complete CRUD functionality for all entities
6. CSV import/export capabilities for artists
7. A responsive, role-adaptive user interface

This documentation serves as both a technical reference and an educational resource for understanding the implementation details of a full-featured web application built from first principles.