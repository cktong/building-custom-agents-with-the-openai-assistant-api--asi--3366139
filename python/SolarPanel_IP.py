from pulp import LpMaximize, LpMinimize, LpProblem, LpVariable, lpSum, value

# Define the model
model = LpProblem(name="solar-system-optimization", sense=LpMinimize)

# Types of components
types = range(3)  # Example with 3 types

# Define the decision variables
x_p = {t: LpVariable(f"solar_panels_{t}", lowBound=0,
                     cat='Integer') for t in types}
x_b = {t: LpVariable(f"batteries_{t}", lowBound=0, cat='Integer')
       for t in types}
x_i = {t: LpVariable(f"inverters_{t}", lowBound=0, cat='Integer')
       for t in types}
y_p = {t: LpVariable(f"select_panel_{t}", cat='Binary') for t in types}
y_b = {t: LpVariable(f"select_battery_{t}", cat='Binary') for t in types}
y_i = {t: LpVariable(f"select_inverter_{t}", cat='Binary') for t in types}

# Given loan rate and term
loan_rate = 0.07  # Example loan rate
loan_term = 10  # Fixed loan term in years

# Costs for each type (example data)
C_p = [1000, 1500, 2000]  # Cost per panel
C_b = [500, 750, 1000]    # Cost per battery
C_i = [300, 450, 600]     # Cost per inverter
C_e = 0.10                # Cost of electricity from the grid in USD/kWh

# Capacities for each type (example data)
panel_capacity = [5, 6, 7]  # kW per panel type per day
battery_capacity = [10, 12, 14]  # kW storage per battery type
inverter_capacity = [20, 25, 30]  # kW per inverter type

# Capital cost
capital_cost = lpSum(C_p[t] * x_p[t] + C_b[t] *
                     x_b[t] + C_i[t] * x_i[t] for t in types)

# Interest cost calculation based on fixed loan term
interest_cost = loan_rate * capital_cost * loan_term

# Objective function
model += (capital_cost + interest_cost)

# Add constraints
E_required_daily = 100  # Daily energy requirement in kWh
backup_energy_required = 50  # Backup energy requirement in kWh
total_budget = 100000  # Total budget in USD

# Energy constraints
model += (lpSum(x_p[t] * panel_capacity[t] for t in types)
          >= E_required_daily, "panel_capacity_constraint")
model += (lpSum(x_b[t] * battery_capacity[t] for t in types)
          >= backup_energy_required, "battery_capacity_constraint")
model += (lpSum(x_i[t] * inverter_capacity[t] for t in types)
          >= E_required_daily, "inverter_capacity_constraint")

# Connection between solar panels and batteries (storage capacity should be greater than or equal to generated energy)
model += (lpSum(x_p[t] * panel_capacity[t] for t in types) <= lpSum(x_b[t]
          * battery_capacity[t] for t in types), "battery_storage_constraint")

# Budget constraint
model += (capital_cost + interest_cost <= total_budget, "budget_constraint")

# Selection constraints
model += (lpSum(y_p[t] for t in types) == 1, "panel_selection_constraint")
model += (lpSum(y_b[t] for t in types) == 1, "battery_selection_constraint")
model += (lpSum(y_i[t] for t in types) == 1, "inverter_selection_constraint")

# Ensure number of components selected corresponds to the selected type
M = 100  # A sufficiently large number
for t in types:
    model += (x_p[t] <= M * y_p[t], f"panel_type_{t}_constraint")
    model += (x_b[t] <= M * y_b[t], f"battery_type_{t}_constraint")
    model += (x_i[t] <= M * y_i[t], f"inverter_type_{t}_constraint")

# Solve the model
status = model.solve()

# Get results
solar_panels = {t: x_p[t].value() for t in types}
batteries = {t: x_b[t].value() for t in types}
inverters = {t: x_i[t].value() for t in types}
selected_panels = {t: y_p[t].value() for t in types}
selected_batteries = {t: y_b[t].value() for t in types}
selected_inverters = {t: y_i[t].value() for t in types}

# Calculate total daily energy generated
total_energy_generated_daily = sum(
    panel_capacity[t] * solar_panels[t] for t in types)

# Calculate total cost
capital_cost_value = sum(C_p[t] * solar_panels[t] + C_b[t]
                         * batteries[t] + C_i[t] * inverters[t] for t in types)
interest_cost_value = loan_rate * capital_cost_value * loan_term
total_cost = capital_cost_value + interest_cost_value

# Calculate total annual savings from solar energy
total_annual_energy_generated = total_energy_generated_daily * 365
total_annual_savings = total_annual_energy_generated * C_e

# Cost per kilowatt-hour
cost_per_kwh = total_cost / \
    total_annual_energy_generated if total_annual_energy_generated != 0 else float(
        'inf')

# Breakeven point calculation
breakeven_years = total_cost / \
    total_annual_savings if total_annual_savings != 0 else float('inf')

# Print results
print("Optimal number of solar panels by type:", solar_panels)
print("Optimal number of batteries by type:", batteries)
print("Optimal number of inverters by type:", inverters)
print("Selected solar panel types:", selected_panels)
print("Selected battery types:", selected_batteries)
print("Selected inverter types:", selected_inverters)
print("Total daily energy generated (kWh):", total_energy_generated_daily)
print("Capital cost (USD):", capital_cost_value)
print("Interest cost (USD):", interest_cost_value)
print("Total cost (USD):", total_cost)
print("Total annual energy generated (kWh):", total_annual_energy_generated)
print("Total annual savings (USD):", total_annual_savings)
print("Cost per kilowatt-hour (USD/kWh):", cost_per_kwh)
print("Breakeven point (years):", breakeven_years)
