The TravianBot is a bot written for the game Travian.
It is written solely for my own learning purposes and not for actual botting.
It uses Python and Selenium to run the code.

## Features ##
This bot has the following features and their relevant information are described in TravianInfo.py:
1. Sending hero out on adventure
2. Checking for attacks and dodging them
3. Pre-queuing buildings or resource fields that wants to be upgraded
4. Sending out raids from farm list

However, all features are very primitive and there are still many areas for improvement.

## Improvements ##
The following are some possible improvements:
1. Use randomized timings instead of fixed timings
2. Separate the features into their own classes instead of having them all in a class under main.py
3. Raiding system can be done using a class with village and time attributes instead of having user specify the details in the name of farm list. This gives users the liberty to name their farm lists.
4. Add a diagram of the village resource fields with their corresponding URL ID numbers for easier referencing.
5. Change the build function to enable building of new buildings.
