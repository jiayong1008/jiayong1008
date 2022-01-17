from helper import *


INTEREST_RATE = 0.0322
MONTHLY_INTEREST = INTEREST_RATE / 12

def calculateMonthlyPayment(balance, loan_period):
    denominator = (((1+MONTHLY_INTEREST)**loan_period) - 1) / (MONTHLY_INTEREST*((1+MONTHLY_INTEREST)**loan_period))
    monthly_payment = round(balance / denominator, 2)
    count = 0
    sum_principal = sum_interest = cumulative_principal = cumulative_interest = 0
    
    while True:
        count += 1
        interest = round(balance * MONTHLY_INTEREST, 2)
        principal = round(monthly_payment - interest, 2)
        month = count % 12

        if count == 1:
            display_header()
        elif month == 1:
            print(f"Total:\t\t{sum_principal:.2f}\t\t{sum_interest:.2f}")
            print(f"Cumulative:\t{cumulative_principal:.2f}\t\t{cumulative_interest:.2f}")
            sum_principal = sum_interest = 0
            input("Press any key to continue...")
            print()
            print(f"Year {int((count / 12) + 1)}:")
            print(f"Month\tPrincipal Paid\t\tInterest Paid\tBalance")

        sum_interest += interest
        sum_principal += principal
        cumulative_interest += interest
        cumulative_principal += principal
        balance = round(balance - principal, 2)
        month = month if month != 0 else 12
        print(f"{month}\t\t{principal:.2f}\t\t{interest:.2f}\t\t{balance:.2f}")

        if count == loan_period:
            break


def display_header():
    print("Year 1:")
    print(f"Month\t\tPrincipal Paid\t\tInterest Paid\tBalance")


def calculateLoanPeriod(balance, monthly_payment, display):
    count = 0
    sum_principal = sum_interest = cumulative_principal = cumulative_interest = 0
    while True:
        count += 1
        interest = round(balance * MONTHLY_INTEREST, 2)
        principal = round(monthly_payment - interest, 2)
        month = count % 12

        if count == 1:
            if principal / interest < 0.17:
                print("Monthly payment too low, try increasing your monthly payment.")
                input("Press any key to continue...")
                return
            if display:
                display_header()
        elif month == 1:
            if display:
                print(f"Total:\t\t{sum_principal:.2f}\t\t{sum_interest:.2f}")
                print(f"Cumulative:\t{cumulative_principal:.2f}\t\t{cumulative_interest:.2f}")
                input("Press any key to continue...")
                print()
                print(f"Year {int((count / 12) + 1)}:")
                print(f"Month\tPrincipal Paid\t\tInterest Paid\tBalance")
            sum_principal = sum_interest = 0

        sum_interest += interest
        sum_principal += principal
        cumulative_interest += interest
        cumulative_principal += principal
        balance = round(balance - principal, 2)
        month = month if month != 0 else 12
        if balance <= 0:
            total_paid = cumulative_principal + cumulative_interest
            print(f"Loan Duration: {int((count / 12) + 1)} Years, {month} Months")
            print(f"Cumulative Interest: {cumulative_interest:.2f}")
            print(f"Principal Percentage: {(cumulative_principal / total_paid * 100):.2f}%, Interest Percentage: {(cumulative_interest / total_paid * 100):.2f}%, Total Paid: RM{total_paid:.2f}")
            break
        if display:
            print(f"{month}\t\t{principal:.2f}\t\t{interest:.2f}\t\t{balance:.2f}")
    

options = [0,1]
price = get_float("Enter Property Price / Balance: ")
option = choice("Provide Loan Period (0) or Monthly Repayment (1)? ", options)
if option == 0:
    loan_period = get_int("Enter Loan Period (in months): ", positive=True)
    calculateMonthlyPayment(price, loan_period)
else:
    monthly_payment = get_float("Enter Monthly Repayment: ")
    option = choice("Display Details Year by Year? Yes(1), No(0)", options)
    calculateLoanPeriod(price, monthly_payment, display = True if option == 1 else False)

