# Flight Routes System

This is a **Flight Routes System** built using **Python 3.12** and  **Django** . It implements a directed graph structure with positional routing to manage airport connections, allowing efficient route management and pathfinding. Each airport can connect to other airports via left or right positioned routes, enabling structured navigation through the flight network.

---

## Features

* **Positional Route Structure** : Airports organized with left/right route positioning for directional navigation
* **Route Management** : Create and manage flight routes with duration tracking
* **Nth Node Search** : Find the Nth left or right node from any starting airport
* **Longest Route Detection** : Identify routes with maximum flight duration
* **Shortest Path Algorithm** : BFS-based pathfinding to find the shortest path (by total duration) between any two airports

---

## Prerequisites

* Python 3.12
* Git
* Virtual environment tool (`venv` or `virtualenv`)

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/AbdulRahimanKS/FlightRoutesSystem.git
cd FlightRoutesSystem
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / Mac:**

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Django development server

```bash
python manage.py runserver
```

---

## Accessing the Application

* **Main Application:**

  ```
  http://127.0.0.1:8000/
  ```
* **Admin Panel:**

  ```
  http://127.0.0.1:8000/admin/
  ```

---

## Credentials

Since the database is pushed, you can use superadmin credentials:

* **Superadmin:** noviindus / SuperAdmin123

---

## Application Pages

### 1. Home Page

* Displays real-time statistics:
  * Total airports in the system
  * Total routes created
* Shows the longest route with details (from airport → to airport, duration)
* Quick access cards to all major features

### 2. Add Airport

Form to create new airports in the system

Fields:

* **Airport Code** : Unique identifier (e.g., "COK", "HYD")
* **Airport Name** : Full name (e.g., "Cochin International")

### 3. Add Airport Route

* Form to create new flight routes
* Fields:
  * **From Airport** : Select source airport
  * **To Airport** : Select destination airport
  * **Position** : Choose left or right (binary tree positioning)
  * **Duration** : Enter flight time in minutes
  * **Parent** : Optional self-referencing field for hierarchical route structure

### 4. Find Nth Node

* Search form with three inputs:
  * **Starting Airport** : Choose origin point
  * **Direction** : Select left or right
  * **N (Steps)** : Number of hops to traverse
* Shows complete traversal path with durations
* Example: Starting from JFK, go left 2 times → LAX → SFO
* Handles cases where path doesn't exist

### 5. Shortest Path Between Airports

* Form to find optimal route between two airports
