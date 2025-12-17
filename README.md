## 📊 Budget Control Dashboard

![Budget Control Dashboard](budget_control.png)



## Installation

1. Get the app:
   ```bash
   bench get-app https://github.com/AhmedAbokhatwa/budget-management-system.git
2. Navigate to the apps directory:
    ```bash
    mv budget-management-system/ budget
3. Install the app on your site:
    ```bash
    bench --site your-site-name install-app budget

## Overview

# Budget Management System
        A comprehensive budget management feature for ERPNext that provides monthly budget distribution and real-time budget tracking with configurable actions when limits are exceeded.

## Features

🚀 Budget Management System (BMS)
✨ Key Features:

Automatic Monthly Allocation
– Split annual budgets across months automatically.

Control Screen
– Adjust (Increase/Decrease) any month’s budget.
– Distribute monthly budgets with advanced filters (by Item, Cost Center, Expense Account).

Purchase Order Validation
– Control overspending with Stop or Warning messages before submission when PO limits are exceeded.

Powerful Reporting
– Export budget reports anytime to PDF or Excel for analysis and sharing.

Cascading Deletion (Sequential Delete)
– Maintain clean data by ensuring related records are deleted in sequence.

Budget Control Log
– Track every adjustment (increase/decrease) with a full audit trail for transparency.


### 🎯 Budget
Advanced budget control system with monthly distribution and automatic enforcement.

### 📊 Monthly Budget Distribution
The system automatically distributes annual budgets across months with precise tracking:

**Example Implementation:**
- **Item:** Office Equipment Purchase
- **Annual Budget:** 12,000 EGP
- **Monthly Distribution:** 8.33% per month (1,000 EGP/month)

```
January: 8.33% (1,000 EGP)
February: 8.33% (1,000 EGP)
...
December: 8.33% (1,000 EGP)
```

---

## How It Works

### Smart Budget Tracking
ERPNext budget management goes beyond annual limits by providing monthly distribution for more precise control. When a month's budget is exhausted, the system can:

- ❌ **Stop** transactions completely
- ⚠️ **Warn** users while allowing transactions

Configuration options:
- `Action Action if Monthly Budget Exceeded on PO = Stop`
- `Action Action if Monthly Budget Exceeded on PO = Warn`

---

## Usage Examples

### ✅ Approved Transaction
**January Scenario:**
- Employee creates Purchase Order for 850 EGP
- **Result:** ✅ Approved (under 1,000 EGP monthly limit)

### ❌ Blocked/Warning Transaction
**January Scenario:**
- Employee attempts Purchase Order for 1,200 EGP
- **Result:** ❌ Blocked or ⚠️ Warning shown (exceeds 8.33% monthly allocation)

### System Behavior
When attempting Purchase Orders exceeding the monthly limit (1,000 EGP in January), the system will:
- Block the transaction if set to "Stop"
- Show warning if set to "Warn"

---

## Configuration

### Budget Actions
Configure system behavior when monthly budgets are exceeded:

| Action | Description |
|--------|-------------|
| **Stop** | Completely prevent transactions exceeding monthly budget |
| **Warn** | Show warning but allow transaction to proceed |

---


# Budget Control & Monitoring - Detailed Scenarios

📊 Current Budget Status (Example)

    Department: Sales Department
    Month: January 2024
    Budget Items Status:
    Office Equipment:
        Monthly Allocation: 1,000 EGP
        Spent to Date: 350 EGP
        Remaining: 650 EGP (65%)

    Marketing Materials:
        Monthly Allocation: 667 EGP
        Spent to Date: 200 EGP
        Remaining: 467 EGP (70%)

    Travel Expenses:
        Monthly Allocation: 1,250 EGP
        Spent to Date: 800 EGP
        Remaining: 450 EGP (36%)
    Sales Department - Budget Control Panel
    Date: January 25, 2024, 3:45 PM
═══════════════════════════════════════════════════════

🎯 Scenario 1: Normal Transaction (Within Budget)

    Document Type: Material Request
    Date: January 15, 2024
    Employee: Ahmed Mohamed (Sales Executive)
    Department: Sales Department
    Cost Center: Sales - Head Office

    Items Requested:
    - Printer Cartridge: 150 EGP
    - Office Supplies: 100 EGP
    Total Amount: 250 EGP
    Account: Office Equipment
═══════════════════════════════════════════════════════

User Experience:
    ✅ SUCCESS MESSAGE:
    "Material Request MR-2024-00123 approved successfully.
    Budget Status: Office Equipment - 60% utilized (400 EGP remaining)"
═══════════════════════════════════════════════════════

⚠️ Scenario 2: Transaction Exceeding Monthly Budget (Warn Mode)

🚫 Scenario 3: Transaction Blocked (Stop Mode)

═══════════════════════════════════════════════════════

🔔 Scenario 4: Budget Threshold Alerts

    Trigger: When monthly budget reaches 75%
    Account: Marketing Materials
    Budget: 667 EGP
    Consumed: 500 EGP (75%)

    Email Alert:
    To: Sales Manager, Finance Manager
    Subject: "Budget Alert: Marketing Materials 75% Consumed"

    Message: "
    Marketing Materials budget for January 2024 has reached 75% utilization.
    Current Status: 500/667 EGP used (167 EGP remaining)
    Please monitor spending for the remainder of the month.
    "
═══════════════════════════════════════════════════════
System Budget Check Process:

    Step 1 - Budget Validation:
    Target Account: Office Equipment
    Monthly Budget: 1,000 EGP
    Already Consumed: 350 EGP
    Available Balance: 650 EGP
    Request Amount: 250 EGP

    Step 2 - Validation Result:
    Check: 250 ≤ 650 ✅
    Percentage Used: 60% (600/1000)
    Status: APPROVED

    Step 3 - System Action:
    ✅ Allow Transaction
    📝 Update Budget Balance
    📊 New Balance: 400 EGP remaining
    🔔 No alerts triggered
═══════════════════════════════════════════════════════

📈 Real-time Budget Dashboard

    Sales Department - Budget Control Panel
    Date: January 25, 2024, 3:45 PM
    ═══════════════════════════════════════════════════════
    MONTHLY BUDGET STATUS:

    🔴 Office Equipment: [████████▓░] 120% (OVER BUDGET)
    Budget: 1,000 EGP | Spent: 1,200 EGP | Over: -200 EGP

    🟡 Travel Expenses: [█████████░] 90% (CRITICAL)
    Budget: 1,250 EGP | Spent: 1,125 EGP | Remaining: 125 EGP

    🟢 Marketing Materials: [██████░░░░] 60% (ON TRACK)
    Budget: 667 EGP | Spent: 400 EGP | Remaining: 267 EGP

    ═══════════════════════════════════════════════════════
    RECENT TRANSACTIONS:

    ⚠️ 2:30 PM - PO-2024-00456 - Laptop (1,200 EGP) - WARNING ISSUED
    ✅ 1:15 PM - MR-2024-00234 - Stationery (85 EGP) - APPROVED
    🚫 12:45 PM - PO-2024-00455 - Furniture (4,300 EGP) - BLOCKED

    ═══════════════════════════════════════════════════════
    PENDING APPROVALS:

    📋 Budget Override Request - Office Equipment (+2,000 EGP)
        Requested by: Fatima Hassan
        Status: Awaiting Finance Manager approval

═══════════════════════════════════════════════════════

🔄 Override & Exception Process

    Budget Override Workflow:

    Scenario: Department needs to exceed monthly budget

    Step 1 - Override Request:
    User: Department Manager
    Reason: "Urgent laptop replacement for key client presentation"
    Amount: 1,200 EGP
    Account: Office Equipment
    Justification: "Client meeting tomorrow, laptop crashed"

    Step 2 - Approval Chain:
    Level 1: Department Head ✅
    Level 2: Finance Manager (Pending...)
    Level 3: General Manager (if > 5,000 EGP)

    Step 3 - If Approved:
    🔓 Temporary budget increase
    📝 Updated monthly allocation
    ✅ Allow specific transaction
    📊 Log exception in reports



#ERPNext #FrappeFramework #BudgetManagement #FinancialControl #Innovation #TechSolution #DigitalTransformation #StartupLife #AppDevelopment #BusinessIntelligence
