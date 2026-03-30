import math
import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


BG = "#f8fafc"
CARD = "#ffffff"
TEXT = "#0f172a"
SUBTLE = "#475569"
ACCENT = "#2563eb"
ACCENT_2 = "#0f766e"
BORDER = "#e2e8f0"


@dataclass
class ProjectionInputs:
    current_age: int
    retirement_age: int
    starting_salary: float
    salary_growth: float
    current_savings: float
    contribution_rate: float
    employer_match: float
    annual_return: float


class RetirementProjectionApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Retirement Projection Dashboard")
        self.root.geometry("1450x920")
        self.root.minsize(1220, 760)
        self.root.configure(bg=BG)

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._configure_styles()

        self.metric_labels = {}
        self.summary_labels = {}
        self.rows = []

        self._build_ui()
        self.update_dashboard()

    def _configure_styles(self):
        self.style.configure("TFrame", background=BG)
        self.style.configure("Card.TFrame", background=CARD)
        self.style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 22, "bold"))
        self.style.configure("SubTitle.TLabel", background=BG, foreground=SUBTLE, font=("Segoe UI", 10))
        self.style.configure("CardTitle.TLabel", background=CARD, foreground=TEXT, font=("Segoe UI", 12, "bold"))
        self.style.configure("Body.TLabel", background=CARD, foreground=SUBTLE, font=("Segoe UI", 10))
        self.style.configure("MetricLabel.TLabel", background=CARD, foreground=SUBTLE, font=("Segoe UI", 10))
        self.style.configure("MetricValue.TLabel", background=CARD, foreground=TEXT, font=("Segoe UI", 18, "bold"))
        self.style.configure("Small.TLabel", background=CARD, foreground=SUBTLE, font=("Segoe UI", 9))
        self.style.configure("TButton", font=("Segoe UI", 10), padding=8)
        self.style.configure("Treeview", rowheight=28, font=("Segoe UI", 10), background=CARD, fieldbackground=CARD)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=18)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(1, weight=1)

        header = ttk.Frame(container)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        ttk.Label(header, text="Retirement Projection Dashboard", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="",
            style="SubTitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        self.left = ttk.Frame(container, style="Card.TFrame", padding=16)
        self.left.grid(row=1, column=0, sticky="nsw", padx=(0, 14))
        self.left.columnconfigure(1, weight=1)

        self.right = ttk.Frame(container)
        self.right.grid(row=1, column=1, sticky="nsew")
        self.right.columnconfigure(0, weight=1)
        self.right.rowconfigure(1, weight=1)

        self._build_inputs()
        self._build_dashboard()

    def _build_inputs(self):
        ttk.Label(self.left, text="Inputs", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(self.left, text="Adjust assumptions to model your retirement path.", style="Body.TLabel").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(2, 12)
        )

        defaults = [
            ("Current age", "25"),
            ("Retirement age", "65"),
            ("Starting salary", "70000"),
            ("Salary growth %", "3"),
            ("Current savings", "15000"),
            ("Contribution rate %", "10"),
            ("Employer match %", "4"),
            ("Annual return %", "7"),
        ]

        self.inputs = {}
        for i, (label, default) in enumerate(defaults, start=2):
            ttk.Label(self.left, text=label, style="Body.TLabel").grid(row=i, column=0, sticky="w", pady=4)
            entry = ttk.Entry(self.left)
            entry.insert(0, default)
            entry.grid(row=i, column=1, sticky="ew", pady=4)
            self.inputs[label] = entry

        btn_row = ttk.Frame(self.left, style="Card.TFrame")
        btn_row.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(12, 10))
        ttk.Button(btn_row, text="Update Projection", command=self.update_dashboard).pack(side="left")
        ttk.Button(btn_row, text="Reset Defaults", command=self.reset_defaults).pack(side="left", padx=(8, 0))

        ttk.Label(self.left, text="Projection Summary", style="CardTitle.TLabel").grid(row=11, column=0, columnspan=2, sticky="w", pady=(8, 6))
        self.summary_box = ttk.Frame(self.left, style="Card.TFrame")
        self.summary_box.grid(row=12, column=0, columnspan=2, sticky="ew")

        summary_fields = [
            "Years to retirement",
            "Total employee contributions",
            "Total employer contributions",
            "Projected retirement balance",
            "Estimated first-year withdrawal (4%)",
        ]
        for field in summary_fields:
            row = ttk.Frame(self.summary_box, style="Card.TFrame")
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=field, style="Body.TLabel").pack(side="left")
            value = ttk.Label(row, text="-", style="Body.TLabel")
            value.pack(side="right")
            self.summary_labels[field] = value

    def _build_dashboard(self):
        metrics = ttk.Frame(self.right)
        metrics.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        for i in range(4):
            metrics.columnconfigure(i, weight=1)

        cards = [
            ("Final Balance", "final_balance"),
            ("Total Contributions", "total_contributions"),
            ("Investment Growth", "growth"),
            ("Retirement Income (4%)", "income"),
        ]
        for idx, (label, key) in enumerate(cards):
            card = ttk.Frame(metrics, style="Card.TFrame", padding=14)
            card.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 10, 0))
            ttk.Label(card, text=label, style="MetricLabel.TLabel").pack(anchor="w")
            value = ttk.Label(card, text="-", style="MetricValue.TLabel")
            value.pack(anchor="w", pady=(8, 0))
            self.metric_labels[key] = value

        body = ttk.Frame(self.right)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)

        chart_card = ttk.Frame(body, style="Card.TFrame", padding=12)
        chart_card.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 14))
        ttk.Label(chart_card, text="Charts", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(chart_card, text="Savings growth, yearly contributions, and account value trajectory.", style="Body.TLabel").pack(anchor="w", pady=(2, 8))

        self.fig = Figure(figsize=(10, 7), dpi=100)
        self.ax_balance = self.fig.add_subplot(221)
        self.ax_contrib = self.fig.add_subplot(222)
        self.ax_growth = self.fig.add_subplot(223)
        self.ax_area = self.fig.add_subplot(224)
        self.fig.tight_layout(pad=2.5)

        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_card)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        table_card = ttk.Frame(body, style="Card.TFrame", padding=12)
        table_card.grid(row=0, column=1, rowspan=2, sticky="nsew")
        ttk.Label(table_card, text="Year-by-Year Projection", style="CardTitle.TLabel").pack(anchor="w")

        cols = ("Age", "Salary", "Employee", "Employer", "Balance")
        self.tree = ttk.Treeview(table_card, columns=cols, show="headings", height=22)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=110)
        self.tree.pack(fill="both", expand=True, pady=(8, 0))

    def reset_defaults(self):
        values = ["25", "65", "70000", "3", "15000", "10", "4", "7"]
        for entry, value in zip(self.inputs.values(), values):
            entry.delete(0, tk.END)
            entry.insert(0, value)
        self.update_dashboard()

    def _read_inputs(self) -> ProjectionInputs:
        current_age = int(self.inputs["Current age"].get())
        retirement_age = int(self.inputs["Retirement age"].get())
        starting_salary = float(self.inputs["Starting salary"].get())
        salary_growth = float(self.inputs["Salary growth %"].get())
        current_savings = float(self.inputs["Current savings"].get())
        contribution_rate = float(self.inputs["Contribution rate %"].get())
        employer_match = float(self.inputs["Employer match %"].get())
        annual_return = float(self.inputs["Annual return %"].get())

        if retirement_age <= current_age:
            raise ValueError("Retirement age must be greater than current age.")
        if min(starting_salary, current_savings) < 0:
            raise ValueError("Salary and current savings must be non-negative.")

        return ProjectionInputs(
            current_age=current_age,
            retirement_age=retirement_age,
            starting_salary=starting_salary,
            salary_growth=salary_growth,
            current_savings=current_savings,
            contribution_rate=contribution_rate,
            employer_match=employer_match,
            annual_return=annual_return,
        )

    def _project(self, data: ProjectionInputs):
        years = data.retirement_age - data.current_age
        salary = data.starting_salary
        balance = data.current_savings
        rows = []

        total_employee = 0.0
        total_employer = 0.0

        for i in range(years + 1):
            age = data.current_age + i
            employee = salary * data.contribution_rate / 100
            employer = salary * data.employer_match / 100
            contribution = employee + employer

            if i > 0:
                balance = balance * (1 + data.annual_return / 100) + contribution

            rows.append({
                "age": age,
                "salary": salary,
                "employee": employee,
                "employer": employer,
                "contribution": contribution,
                "balance": balance,
            })

            total_employee += employee
            total_employer += employer
            salary *= 1 + data.salary_growth / 100

        return rows, total_employee, total_employer

    def update_dashboard(self):
        try:
            data = self._read_inputs()
            rows, total_employee, total_employer = self._project(data)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Input Error", str(e))
            return

        final_balance = rows[-1]["balance"]
        total_contributions = total_employee + total_employer
        investment_growth = final_balance - data.current_savings - total_contributions
        income_4 = final_balance * 0.04

        self.metric_labels["final_balance"].config(text=self.money(final_balance))
        self.metric_labels["total_contributions"].config(text=self.money(total_contributions))
        self.metric_labels["growth"].config(text=self.money(investment_growth))
        self.metric_labels["income"].config(text=self.money(income_4))

        self.summary_labels["Years to retirement"].config(text=str(data.retirement_age - data.current_age))
        self.summary_labels["Total employee contributions"].config(text=self.money(total_employee))
        self.summary_labels["Total employer contributions"].config(text=self.money(total_employer))
        self.summary_labels["Projected retirement balance"].config(text=self.money(final_balance))
        self.summary_labels["Estimated first-year withdrawal (4%)"].config(text=self.money(income_4))

        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert(
                "",
                "end",
                values=(
                    row["age"],
                    self.money0(row["salary"]),
                    self.money0(row["employee"]),
                    self.money0(row["employer"]),
                    self.money0(row["balance"]),
                ),
            )

        self.draw_charts(rows)

    def draw_charts(self, rows):
        ages = [r["age"] for r in rows]
        balances = [r["balance"] for r in rows]
        employees = [r["employee"] for r in rows]
        employers = [r["employer"] for r in rows]
        contributions = [r["contribution"] for r in rows]

        self.ax_balance.clear()
        self.ax_contrib.clear()
        self.ax_growth.clear()
        self.ax_area.clear()

        self.ax_balance.plot(ages, balances, linewidth=2.5)
        self.ax_balance.set_title("Projected Balance")
        self.ax_balance.grid(True, alpha=0.3)

        self.ax_contrib.bar(ages, employees, label="Employee")
        self.ax_contrib.bar(ages, employers, bottom=employees, label="Employer")
        self.ax_contrib.set_title("Annual Contributions")
        self.ax_contrib.legend(fontsize=8)
        self.ax_contrib.grid(True, axis="y", alpha=0.3)

        self.ax_growth.plot(ages, contributions, linewidth=2, label="Contribution")
        self.ax_growth.set_title("Total Annual Contribution")
        self.ax_growth.grid(True, alpha=0.3)

        self.ax_area.fill_between(ages, balances, alpha=0.3)
        self.ax_area.plot(ages, balances, linewidth=2)
        self.ax_area.set_title("Balance Growth Area")
        self.ax_area.grid(True, alpha=0.3)

        self.fig.tight_layout(pad=2.2)
        self.canvas.draw()

    @staticmethod
    def money(value: float) -> str:
        return f"${value:,.2f}"

    @staticmethod
    def money0(value: float) -> str:
        return f"${value:,.0f}"


def main():
    root = tk.Tk()
    RetirementProjectionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
