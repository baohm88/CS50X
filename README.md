# CS50 Final Project - BH$Xchange
#### Video Demo:  <URL https://youtu.be/CVp_b8-4hPU>
#### Description:
This is a stock exchange platform where users can buy and sell stocks from Yahoo Finance.

Typical features include:
1. Register, where new users register an account to trade stocks.
Password must contain the following:
- 01 lowercase letter: a-z
- 01 uppercase letter: A-Z
- 01 numbers: 0-9
- 01 special characters: #$%^&+=
- minimum 08 characters
Once the registration is done, user will get $10,000 in their account to trade stocks.

2. Get a quote for stocks - it allows a user to look up a stock’s current price.
It requires that a user input a stock’s symbol and will display a message if wrong symbol is provided.
Once correct symbol is inputted, user will the price for that particular stock.


3. Buy stocks - it allows users to buy various stocks they like.
The user must input correct symbol and a positive integer number of shares to make the purchase.
The purchase can't be completed if the user can't afford the numbers of shares they entered at the current price.
 Once the purchase is done, user will be redirected to the homepage where they can see all stocks they own, the numbers of shares owned, the current price of each stock, and the total value of each holding (i.e., shares times price). Also display the user’s current cash balance along with a grand total (i.e., stocks’ total value plus cash).

4. Sell stocks - it allows the user to sell shares of a stock (that he or she owns).
The user is required to select a symbole from a select menu which includes only the stock symbols he/she currently owns.
If the user enter a negative number or not an interger number, the user will get a message saying invalid number.
The sale is only completed once they user enters a positive number of shares less than or equal to the number of shares he/she owns.
Upon completion of the sale, the user is redirected to the home page.


5. History - it displays an HTML table summarizing all of a user’s transactions ever, listing row by row each and every buy and every sell.
For each row, it shows whether a stock was bought or sold and include the stock’s symbol, the (purchase or sale) price, the number of shares bought or sold, and the date and time at which the transaction occurred.


6. Homepage - it displays an HTML table summarizing, for the user currently logged in, which stocks the user owns, the numbers of shares owned, the current price of each stock, and the total value of each holding (i.e., shares times price). Also display the user’s current cash balance along with a grand total (i.e., stocks’ total value plus cash).

6. Other features include:
- users can change their passwords. again, new password must contain the following:
    * 01 lowercase letter: a-z
    * 01 uppercase letter: A-Z
    * 01 numbers: 0-9
    * 01 special characters: #$%^&+=
    * minimum 08 characters

- users can add additional cash to their account.

- users can buy more shares or sell shares of stocks they already own via index itself, without having to type stocks’ symbols manually.

