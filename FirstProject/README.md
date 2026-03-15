<h1 align="center">🤖 Robot Emergency Battery – A* Search</h1>

## 📌 Description
This project implements an **Artificial Intelligence search algorithm** to solve a planning problem where a maintenance robot must retrieve an **Emergency Battery** located above the Energy Room of an abandoned space station.

The robot cannot reach the battery directly. To obtain it, it must:

- Move a **metal box** across the room  
- Place it **under the battery**  
- **Climb onto the box**  
- **Grab the battery**

The solution is computed using the **A\* (A-Star) informed search algorithm**, which finds an efficient sequence of actions by combining path cost and heuristic estimation.

---

## 🚀 Features
- **State Space Representation** for robot position, box position, and battery status  
- **Action Simulation** including movement, pushing the box, climbing, and grabbing the battery  
- **A\* Search Implementation** for optimal path finding  
- **Heuristic Function** that estimates the remaining cost to reach the goal  
- **Step-by-step solution output**

---

## ⚙️ State Model

Each state is represented as:

Where:

- `PosRobot` → Robot position  
- `PosCaja` → Box position  
- `EncimaCaja` → Whether the robot is on the box  
- `TieneBateria` → Whether the robot has obtained the battery  

Goal state:
- estado(,,_,si)


---

## 🧠 Algorithm

The project uses the **A\*** search algorithm:
- f(n) = g(n) + h(n)

- `g(n)` → accumulated path cost  
- `h(n)` → heuristic estimate of remaining cost  

The heuristic considers:

- Distance between the **box and the battery**
- Distance between the **robot and the box**
- Whether the robot is already **standing on the box**

---

## 🎯 Purpose
This project demonstrates fundamental **Artificial Intelligence concepts**, including **state modeling, heuristic design, and informed search algorithms**, through a practical planning problem.

---

👨‍💻 Developed for the **Introduction to Artificial Intelligence** course.