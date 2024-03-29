DP 1.12.2023
- Added Query controllers for Comments
- Added tests for Comments
- Fixed a few bugs
- Document some undocumented code
- Update README.md

DP 30.11.2023
- Added tests for User Query
- Added tests for Post Controller and Query
- Added tests for Event Controller and Query
- Fixed a few bugs

DP 26.11.2023
- Added tests for User Controller

DP 23.11.2023
- Added JWT authentication middleware for query
- Added feed and customized logged user endpoints
- Added UUIDAuditBase parameters to RabbitMQ messaging for Mongo

- Removed some unused imports and dead code

DP 22.11.2023
- Added Post sharing functionality
- Added User follow functionality
- Added User and Post controllers to query for GET requests

- Refactored Post sharing

DP 21.11.2023
- Added JWT authentication middleware

- Refactored controllers to use User object from JWT payload

- Changed DTOs to no longer require user_id field
- Created Login endpoint

DP 20.11.2023
- Further refactored Mongo infrastructure

- Added "Comments" endpoints to Controller
- Added MongoDB Event handler for comments
- Added "joined" load strategy for relationships to Comments and Posts, in order to fix the issue with additional relationship query while being in SQLAlchemy async mode

- Fixed a bug where Collection class was not returning correct operartion success status

DP 16.11.2023
- Altered User model
- Refactored mongo infrastructure

DP 22.10.2023
- Initialized repository with basic boilerplate structure
