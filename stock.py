"""
Fees calculation updated according to 2022 Bursa Transaction Cost:
https://www.bursamalaysia.com/trade/trading_resources/equities/transaction_costs


The price is RM75. The following is the full capital requirement:

Broker payment:
Say your broker charges 0.08% or a minimum of RM8.
RM75 (capital needed to invest in AHP stock) x 0.08% = RM6 (not enough for minimum payment)
= RM8 being the minimum broker charge

SST: #Note: SST is no longer applicable
RM8 (broker fee) x 6% = RM0.48

Clearance Fee:
Fixed by Bursa at 0.03% of the total of share trade
RM75 (investment capital) x 0.03% = RM0.0225

Stamp Duty: 
Fixed by Bursa at RM1.50 for each transaction amounting to RM1,000.
Total stamp duty = RM1.50

Grand total:
RM75 + (RM8 + RM0.0225 + RM1.50) = RM84.52
"""


from helper import *

# Change these 2 variables according to your brokerage commission rates
INTEREST = 0.001  # The commission your brokerage charges (0.1% = 0.001)
MINIMUM = 12 # Most brokerage have a minimum fee

# SST = 0.06
CLEARANCE = 0.0003
STAMP_DUTY = 1.5 # RM1.50 per RM1000 of transaction

def main():
    print("Reminder: Change interest rate and minimum brokerage fee.")
    while True:
        # Prompts user to continue or terminate
        # Calls choice function for validation check
        options = [0, -1]
        option = choice("Do you want to continue? [‘0’ to Continue ‘-1’ to Terminate]: ", options)

        # If choice entered is '-1', break out of loop and end the program.
        if (option == -1):
            break

        print("Your options are: ")
        print("1.	Calculate Stock Fees.")
        print("2.	How many shares can I buy with my budget?")
        print("3.	Calculate Profit.")

        # Prompt user to enter option
        # Calls choice function for validation check
        options = [1, 2, 3]
        option = choice("Enter your option: ", options)

        # Calculate Stock Fees - Buy / Sell
        if (option == 1): 
            status = choice('Buy(1) or Sell(0)? ', [0, 1])
            stockPrice = get_float('Stock Price: ')
            numShares = get_int('Number of Shares: ')
            initial, totalFee = calculateFee(stockPrice, numShares)
            if status == 1:
                print(f"Cost = RM{initial:.2f}, Fee = RM{totalFee:.2f}, Final cost = RM{initial + totalFee:.2f}\n")
            else:
                print(f"Original = RM{initial:.2f}, Fee = RM{totalFee:.2f}, Final gain = RM{initial - totalFee:.2f}\n")

        # How many shares can I buy?
        elif (option == 2):
            stockPrice = get_float('Buy Price: ')
            budget = get_float('Budget: ')
            numStocks, initial, totalFee = calcNumShares(stockPrice, budget)
            print()
            print(f"Number of Stocks Purchasable: {numStocks}, cost = RM{initial:.2f}, total cost = RM{initial + totalFee:.2f}")
            print()

        # Calculate Profit
        else:
            calcProfit()

    
def calculateFee(stockPrice, numShares):
    initial = stockPrice * numShares
    brokerFee = initial * INTEREST
    brokerFee = MINIMUM if brokerFee <= MINIMUM else brokerFee
    # sst = brokerFee * SST

    clearance = initial * CLEARANCE
    stampDuty = initial / 1000
    stampDuty = int(stampDuty) + 1 if stampDuty % 1 != 0 else int(stampDuty)
    stampDuty *= STAMP_DUTY
    totalFee = brokerFee + clearance + stampDuty
    return initial, totalFee


def calcNumShares(stockPrice, budget):
    numStocks = int(budget / stockPrice)
    _, totalFee = calculateFee(stockPrice, numStocks)
    budget -= totalFee
    numStocks = int(budget / stockPrice)
    initial, totalFee = calculateFee(stockPrice, numStocks)
    return numStocks, initial, totalFee


def calcProfit():
    print("Your options: ")
    print("1. Calculate profit given my purchase and disposal price.")
    print("2. Calculate how many rounds I have to buy and sell at a particular price to reach my goal.")
    print("Option 2 is purely for souls who are curious, it is not advisable to take this approach in your investment strategy.")
    option = choice('Your choice: ', [1, 2])

    if option == 1:
        buyPrice = get_float('Buy Price: ')
        numShares = get_int('Number of Shares: ')
        sellPrice = get_float('Sell Price: ')
        initialCost, buyFee = calculateFee(buyPrice, numShares)
        initialGain, sellFee = calculateFee(sellPrice, numShares)

        totalBuyCost = initialCost + buyFee
        totalSellGain = initialGain - sellFee
        totalProfit = totalSellGain - totalBuyCost
        percentageGained = totalProfit / totalBuyCost * 100

        print()
        print(f"Total Buy Cost = RM{totalBuyCost:.2f}, Total Sell Gain = RM{totalSellGain:.2f}, Total Profit = RM{totalProfit:.2f}")
        print(f"Percentage Gained (Accounted for Fees): {percentageGained:.2f}%")
        print()
    
    else:
        buyPrice = get_float('Buy Price: ')
        numShares = get_int('Number of Shares: ')
        sellPrice = get_float('Sell Price: ')
        goal = get_float('What is your goal (RM)? ')

        if sellPrice < buyPrice:
            print("Selling price is less than buying price. A mistake?") 
            return

        current = None
        count = 0
        while current is None or current < goal:
            count += 1
            if count > 50:
                print("Hmm.. It seems your goal takes more than 50 rounds to complete.")
                return

            initialCost, buyFee = calculateFee(buyPrice, numShares)
            initialGain, sellFee = calculateFee(sellPrice, numShares)
            numStocks, initial, totalFee = calcNumShares(buyPrice, initialGain - sellFee)
            numShares = numStocks
            current = initial - totalFee

        print()
        print(f"{count} rounds required.")
        print(f"Final round leftover - RM{current:.2f}.")
        print()


if __name__ == "__main__":
    main()
