# CashYourRun
#### Video Demo: https://youtu.be/7It8rtDeqKM
#### Description:

CashYourRun is a web application to help motivate individuals to run regularly by letting them cash their run as if they were to cash a cheque. This app consists of a side-scroller video game and a run tracker.
The run tracker tracks the distance the user travels and time for which they run. As the user tracks their run, they are rewarded with collectables such as coins along their journey.
The game is a 2D side-scroller game with the objective being to help a square named Bob complete his journey while avoiding obstacles along his way. This collectables can be spent to buy upgrades in the shop to help progress in the game.
The user is also able to create an account to store their progress in the run tracker and the game and can also their their overall run history.

## [application.py](./application.py)

This file is the controller of the whole web application. It uses the Flask framework and is incharge of processing the users' HTTP requests and render the appropriate templates for the user. This file also updates the SQL database called [project.db](#projectdb) in the `project` directory. This web app makes use of the following routes with coresponding HTML templates:
- [index](#index)
- [register](#register)
- [login](#login)
- [run](#run)
- [game](#game)
- [shop](#shop)
- [history](#history)
- [logout](#logout)

## [Layout](./templates/layout.html)

Before exploring all the routes and their coresponding templates, it is worth mentioning that all templates used are extensions of a common layout defined in `layout.html`. This file defines the meta data of this site and imports some CSS files and libraries to style the web pages. This file also defines a navigation bar in the `header` to help the user navvigate between each page. The route specific template is leaded into the `main` tag in the `body`.

## [Index](./templates/index.html)

This is the home page, introducting the user to the run tracker (Run and Collect) and the game (Game and Spend) with links to both pages. The user also has access to the navigation bar to directly navigate to a specific page if need be.

## [Register](./templates/register.html)

The registration page allows the user to create a new account to store their progress in their runs and the game. The account requires a `username` and `password` to be entered as well as a verification in the form of the `Confirm Password` field. This page has various security measures ensuring none of the fields are left empty, the `username` is unique and the `password` is strong. Once the user as successfully registered, the `username` and `password` are inserted into the `users` table in the `project` database. If the user already has an account, they can click on the `login` button to log into their account.

## [Login](./templates/login.html)

The login page allows the user to log into an existing account in the database. The user also has the option to use the features of the app as a `guest`, which creates a randomised username and password for the to use temporarily. The user specific data is stored on their session. If the user does not have an account, they can click on the `Create an account` button which leads them to the `register`

## [Run](./templates/run.html)

This page helps the user track the distance and time of their run as well as collect cois along their journey. This page first requies permission from the user to use their device's accelerometer to track distance travelled. If request is not granted, only the time is tracked. The user is then able to click `Start Run` to start tracking their run and click `Stop Run` to stop tracking. They can then click `Reset run` to reset the run and store the distance travelled in and the duration of the run in the `run_log` table in the `project` database if the user has an account. When on their run, the app dynamically generates distance and time milestones for the user to reach at which the user can find coins to collect. The total number of coins collected is updated in the `user_colectables` table in the `project` database if the user has an account or updated in the session if user is a guest.

## [Game](./templates/game.html)

The game, as described earlier, is a simple side-scroller game with the objective being to help a square named Bob reach as far as possible by running and jumping over obstacles in his way. Bob can jump by pressing the `Space Bar`, `Up Arraw` or `Left Mouse Button`. If Bob gets hit by an obstacle, he loses all of his momentum. While he is still, his `tolerance` slowly decreases (as indicated by the orange bar in the top-right corner). If his tolerance reaches 0, the player loses and must `Play Again`.

## [Shop](./templates/shop.html)

This is the shop page, which allows the user to purchase `upgrades` using their coins which they have earned by running. Currently there is only one upgrade which can be bought to increase Bob's tolerance. Once the upgrade is bought, the user must `Confirm Purchase` to save their upgrades in the `user_items` table in the `project` database.

## [History](./templates/history.html)

The user can view their running history in this page. This is done by reading all entries of the `run_log` table in the `project` database which consists of the timestamp of the run was started, the distance travelled in the run and the duraction of the run. This page requires the user to be logged into an existing account to be used.

## Logout

This action clears the user's current session and let them log into an account or start a new session as a guest. This action does not load a coresponding template.

## [Project.db](./project.db)

This is a database contaniing many linked tables to store user-specific as well as backend data.
The folowing is the list of tables in this database:
- users
    - stores the autogenerated id, `username` and `password` of each account as well as a `timestamp` of when the account was created
- item_types
    - stores the possible types of shop items that the user can purchase, namely upgrades and powerups
- shop_items
    - stores the name, type (as an id from item_types), description and costs at different levels of the item. This is used to display all of the items in the shop
- collectable_types
    - stores the possible types of collectables that the user can collect, namely coins
- user_items
    - creates a many-to-many relationship between the users' ids and shop item ids from shop_items
    - stores the level of each item bought by each user
- user_collectables
    - creates a many-to-many relationship between the users' ids and all the collectable ids from collectable_types
    - stores the amount of each collectable owned by each user
- run_log
    - keeps a log of all of the users runs
    - Stores a timestamp of the start of the run, the total distance of the run and the duration of the run

