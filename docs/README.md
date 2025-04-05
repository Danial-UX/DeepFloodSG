# Design Documentation

## Software Architecture Diagram

![Software Architecture Diagram](/docs/software-architecture/software-architecture.png)

<!--- #### Frontend

#### Backend -->

## Use Case Diagram

![Use Case Diagram](/docs/use-case-diagrams/use-case-diagram.png)

## Sequence Diagrams

### Sensor
The devices (sensors) will send the information over to the data ingest processor which will then store it within the database.

![Sensor Activity Sequence Diagram](/docs/sequence-diagram/sensor/sensor-sequence-diagram.png)

<!-- ### Data Comparison
![Data Comparison Sequence Diagram](/docs/sequence-diagram/.png) -->

### Alert Management

Upon one of the trigger conditions being hit as detected and stored in the database, an alert will be sent to the frontend of the user.

![Alert Management Sequence Diagram](/docs/sequence-diagram/alert-management/alert-management-sequence-diagram.png)

### User Authentication

#### User Creation

Creates a new user that will be granted access rights to the system. 

![User Creation Sequence Diagram](/docs/sequence-diagram/user-auth/user-creation-sequence-diagram.png)

#### User Login

Allows an existing user to access the system and its functionalities.

![User Creation Sequence Diagram](/docs/sequence-diagram/user-auth/user-login.png)

#### User Logout

Allows a logged in user to logout of the system after they are done with their session. 

![User Creation Sequence Diagram](/docs/sequence-diagram/user-auth/user-logout.png)

### Data Exploration

#### Data Exploration View Feature

Displays all the existing data visualisation of the project.

![Data Exploration View Sequence Diagram](/docs/sequence-diagram/data-exploration/data-exploration-view-data-sequence-diagram.png)

#### Data Exploration Filter Feature

Filters out the data according to the filter conditions and displays them accordingly. 

![Data Exploration View Sequence Diagram](/docs/sequence-diagram/data-exploration/data-exploration-filter-sequence-diagram.png)

## Activity Diagrams

### Sensor Activity

After it takes the measurements, the sensor will send the data to the backend for processing. 

![Sensor Activity Activity Diagram](/docs/activity-diagrams/sensor-activity/sensor-activity-diagram.png)

### Alert Management

After hitting the trigger condition, the sensor will send an alert notification to the frontend.

![Alert Management Activity Diagram](/docs/activity-diagrams/alert-management/alert-management-activity-diagram.png)

### User Authentication

Both existing and new users can be authenticated through the same flow.

![User Authentication Activity Diagram](/docs/activity-diagrams/user-auth/user-authentication-activity-diagram.png)

### Data Exploration

The user is able to interact with the data visualisations, filtering and viewing all the existing information. 

![Data Exploration Activity Diagram](/docs/activity-diagrams/data-exploration/data-exploration-activity-diagram.png)

## Entity Relationship Diagram

![Entity Relationship Diagram](/docs/entity-relationship-diagram/entity-relationship-diagram.png)

<!-- ## Wireframes -->
