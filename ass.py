Absolutely, Abhishek! Let me simplify the **formula and documentation** so it’s **easy to understand**, even for someone new to the project. I’ll write it in plain language, step by step.

---

## **📘 Document Percentage Statistics - Easy Version**

### **Purpose**

Calculate how many documents fall into different performance ranges based on their `percentage` score.

---

### **Formula / Logic**

1. **Count total documents** in the table.

2. **Classify each document** based on its `percentage`:

| Category   | Condition                |
| ---------- | ------------------------ |
| **> 81%**  | `percentage > 81`        |
| **71–80%** | `71 <= percentage <= 80` |
| **50–70%** | `50 <= percentage <= 70` |
| **< 50%**  | `percentage < 50`        |

3. **Count how many documents** are in each category.

4. **Calculate percentage share** of each category:

[
\text{Category Percentage} = \frac{\text{Count in Category}}{\text{Total Documents}} \times 100
]

---

### **Example**

Suppose the table has **5 documents** with percentages:

```
[85, 77, 62, 48, 91]
```

* **> 81%** → 85, 91 → 2 documents → 40%
* **71–80%** → 77 → 1 document → 20%
* **50–70%** → 62 → 1 document → 20%
* **< 50%** → 48 → 1 document → 20%

**Output:**

```json
{
  "total_documents": 5,
  "greater_than_81": 2,
  "range_71_to_80": 1,
  "range_50_to_70": 1,
  "less_than_50": 1,
  "summary_percentage": {
    ">81%": 40.0,
    "71–80%": 20.0,
    "50–70%": 20.0,
    "<50%": 20.0
  }
}
```

---

### **Step-by-step**

1. Count total documents.
2. Check each document’s percentage.
3. Increase the count of the corresponding category.
4. Calculate the category percentage using the formula:

[
\text{Percentage} = \frac{\text{Number of documents in category}}{\text{Total documents}} \times 100
]

---

### **Benefits**

* Quickly see which documents are performing well or poorly.
* Easy to decide which documents need review.
* Helps monitor overall data quality.

---

If you want, I can **also write a one-line “formula diagram”** showing the ranges visually. It’s very easy to include in docs or presentations.

Do you want me to do that?
